# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.


import os
import re
import json
import time
import tempfile
import typing
import itertools
import logging
import numpy as np
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.schema
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import ifcpatch
from pathlib import Path
from typing import Any, TYPE_CHECKING, Literal, Union
from typing_extensions import assert_never

SQLTypes = typing.Literal["SQLite", "MySQL"]

if TYPE_CHECKING:
    import sqlite3
    import mysql.connector
    import mysql.connector.abstracts
else:
    try:
        import sqlite3
    except:
        print("No SQLite support")
        SQLTypes = typing.Literal["MySQL"]

    try:
        import mysql.connector
        import mysql.connector.abstracts
    except:
        print("No MySQL support")
        SQLTypes = typing.Literal["SQLite"]

DEFAULT_DATABASE_NAME = "database"


class Patcher(ifcpatch.BasePatcher):
    def __init__(
        self,
        file: ifcopenshell.file,
        logger: Union[logging.Logger, None] = None,
        sql_type: SQLTypes = "SQLite",
        host: str = "localhost",
        username: str = "root",
        password: str = "pass",
        database: str = DEFAULT_DATABASE_NAME,
        full_schema: bool = True,
        is_strict: bool = False,
        should_expand: bool = False,
        should_get_inverses: bool = True,
        should_get_psets: bool = True,
        should_get_geometry: bool = True,
        should_skip_geometry_data: bool = False,
    ):
        """Convert an IFC-SPF model to SQLite or MySQL.

        :param sql_type: Choose between "SQLite" or "MySQL"
        :param database: Database filepath / name.
            For SQLite - database path to save the SQL database to (already existing or not).
            Could also be a directory, then the database will be stored
            using default filename (e.g. 'database.sqlite').
            If filepath is missing fitting suffix, it will be added.
            For MySQL - database name.
        :filter_glob database: *.db;*.sqlite
        :param full_schema: if True, will create tables for all IFC classes,
            regardless if they are used or not in the dataset. If False, will
            only create tables for classes in the dataset.
        :param is_strict: whether or not to enforce null or not null. If your
            dataset might contain invalid data, set this to False.
        :param should_expand: if True, entities with attributes containing lists of
            entities will be separated into multiple rows. This means the ifc_id
            is no longer a unique primary key. If False, lists will be stored as
            JSON.
        :param should_get_inverses: if True, a list of entity inverses ids will be stored
            in a separate column as a json string.
        :param should_get_psets: if True, a separate psets table will be created to
            make it easy to query properties. This is in addition to regular IFC
            tables like IfcPropertySet.
        :param should_get_geometry: Whether or not to process and store explicit
            geometry data as a blob in a separate geometry and shape table.
        :param should_skip_geometry_data: Whether or not to also create tables for
            IfcRepresentation and IfcRepresentationItem classes. These tables are
            unnecessary if you are not interested in geometry.


        Example:

        .. code:: python

            # Convert to SQLite, SQLite databse will be saved to a temporary file.
            sqlite_temp_filepath = ifcpatch.execute(
                {"input": "input.ifc", "file": model, "recipe": "Ifc2Sql", "arguments": ["sqlite"]}
            )
        """
        super().__init__(file, logger)
        self.logger = logger
        self.sql_type: Literal["sqlite", "mysql"] = sql_type.lower()
        self.host = host
        self.username = username
        self.password = password
        self.database = database

        # Configuration Values
        self.full_schema = full_schema
        self.is_strict = is_strict
        self.should_expand = should_expand
        self.should_get_inverses = should_get_inverses
        self.should_get_psets = should_get_psets
        self.should_get_geometry = should_get_geometry
        self.should_skip_geometry_data = should_skip_geometry_data

    geometry_rows: dict[str, tuple[str, bytes, bytes, bytes, bytes, str]]
    shape_rows: dict[int, tuple[int, list[float], list[float], list[float], bytes, str]]

    def get_output(self) -> Union[str, None]:
        """Return resulting database filepath for sqlite and ``None`` for mysql."""
        return self.file_patched

    my_sql_classes_json_attrs: dict[str, list[int]]
    """Mapping ifc_class -> list of attr indices.

    Needed to mark json attributes
    that should be converted to string explicitly
    (mysql doesn't convert them automatically, unlike sqlite)"""

    def patch(self) -> None:
        if self.sql_type == "sqlite":
            database = Path(self.database)
            if database.is_dir():
                database = database / DEFAULT_DATABASE_NAME
            elif not database.parent.exists():
                database.parent.mkdir(parents=True, exist_ok=True)
            else:
                # Assume it's a filepath - existing or not.
                pass

            if database.suffix.lower() not in (".sqlite", ".db", ".ifcsqlite"):
                database = database.with_suffix(database.suffix + ".sqlite")
            database = str(database)
        elif self.sql_type == "mysql":
            database = self.database
        else:
            assert False

        self.schema = ifcopenshell.schema_by_name(self.file.schema_identifier)

        if self.sql_type == "sqlite":
            self.db = sqlite3.connect(database)
            self.c = self.db.cursor()
            self.file_patched = database
        elif self.sql_type == "mysql":
            self.db = mysql.connector.connect(
                host=self.host, user=self.username, password=self.password, database=database
            )
            self.c = self.db.cursor()
            self.file_patched = None
        else:
            assert False

        self.check_existing_ifc_database()
        self.create_id_map()
        self.create_metadata()

        if self.should_get_psets:
            self.create_pset_table()

        if self.should_get_geometry:
            self.create_geometry_table()
            self.create_geometry()

        if self.full_schema:
            ifc_classes = [
                d.name() for d in self.schema.declarations() if isinstance(d, ifcopenshell.ifcopenshell_wrapper.entity)
            ]
        else:
            ifc_classes = self.file.wrapped_data.types()

        for ifc_class in ifc_classes:
            declaration = self.schema.declaration_by_name(ifc_class)

            if self.should_skip_geometry_data:
                if ifcopenshell.util.schema.is_a(declaration, "IfcRepresentation") or ifcopenshell.util.schema.is_a(
                    declaration, "IfcRepresentationItem"
                ):
                    continue

            if self.sql_type == "sqlite":
                self.create_sqlite_table(ifc_class, declaration)
            elif self.sql_type == "mysql":
                self.my_sql_classes_json_attrs = {}
                self.create_mysql_table(ifc_class, declaration)
            self.insert_data(ifc_class)

        if self.should_get_geometry:
            if self.sql_type == "sqlite":
                assert isinstance(self.c, sqlite3.Cursor)
                if self.shape_rows:
                    self.c.executemany("INSERT INTO shape VALUES (?, ?, ?, ?, ?, ?);", self.shape_rows.values())
                if self.geometry_rows:
                    self.c.executemany("INSERT INTO geometry VALUES (?, ?, ?, ?, ?, ?);", self.geometry_rows.values())
            elif self.sql_type == "mysql":
                assert isinstance(self.c, mysql.connector.abstracts.MySQLCursorAbstract)
                if self.shape_rows:
                    # mysql is requiring it to be a list or a tuple.
                    values = list(self.shape_rows.values())
                    self.c.executemany("INSERT INTO shape VALUES (%s, %s, %s, %s, %s, %s);", values)
                # Do row by row in case of max_allowed_packet
                for row in self.geometry_rows.values():
                    self.c.execute("INSERT INTO geometry VALUES (%s, %s, %s, %s, %s, %s);", row)

        self.db.commit()
        self.c.close()  # Important for static use of Patcher on Windows.
        self.db.close()

    def create_geometry(self) -> None:
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        self.shape_rows = {}
        self.geometry_rows = {}

        if self.file.schema in ("IFC2X3", "IFC4"):
            self.elements = self.file.by_type("IfcElement") + self.file.by_type("IfcProxy")
        else:
            self.elements = self.file.by_type("IfcElement")

        self.settings = ifcopenshell.geom.settings()
        self.settings.set("apply-default-materials", False)

        self.body_contexts = [
            c.id()
            for c in self.file.by_type("IfcGeometricRepresentationSubContext")
            if c.ContextIdentifier in ["Body", "Facetation"]
        ]
        # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
        self.body_contexts.extend(
            [
                c.id()
                for c in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
                if c.ContextType == "Model"
            ]
        )
        self.settings.set("context-ids", self.body_contexts)

        products = self.elements
        iterator = ifcopenshell.geom.iterator(self.settings, self.file, multiprocessing.cpu_count(), include=products)
        valid_file = iterator.initialize()
        if not valid_file:
            # If there were no elements, iterator will also fail and it's okay not to report it.
            if products:
                print("WARNING. Geometry iterator failed to initialize.")
            return
        checkpoint = time.time()
        progress = 0
        total = len(products)
        while True:
            progress += 1
            if progress % 250 == 0:
                percent_created = round(progress / total * 100)
                percent_preprocessed = iterator.progress()
                percent_average = (percent_created + percent_preprocessed) / 2
                print(
                    "{} / {} ({}% created, {}% preprocessed) elements processed in {:.2f}s ...".format(
                        progress, total, percent_created, percent_preprocessed, time.time() - checkpoint
                    )
                )
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                assert isinstance(shape, W.TriangulationElement)
                shape_id = shape.id
                geometry = shape.geometry
                geometry_id = geometry.id
                if geometry_id not in self.geometry_rows:
                    v = geometry.verts_buffer
                    e = geometry.edges_buffer
                    f = geometry.faces_buffer
                    mids = geometry.material_ids_buffer
                    m = json.dumps([m.instance_id() for m in geometry.materials])
                    self.geometry_rows[geometry_id] = (geometry_id, v, e, f, mids, m)
                # Copy required since otherwise it is read-only
                m = ifcopenshell.util.shape.get_shape_matrix(shape).copy()
                m[:3, 3] /= self.unit_scale
                x, y, z = m[:, 3][0:3].tolist()
                self.shape_rows[shape_id] = (shape_id, x, y, z, m.tobytes(), geometry_id)
            if not iterator.next():
                break

    def check_existing_ifc_database(self) -> None:
        if self.sql_type == "sqlite":
            cursor = self.c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='id_map'")
            assert cursor is not None
            row = cursor.fetchone()
        elif self.sql_type == "mysql":
            cursor = self.c.execute(
                f"""
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = '{self.database}' AND table_name = 'id_map'
                LIMIT 1;
                """
            )
            row = self.c.fetchone()
        else:
            assert_never(self.sql_type)

        if row is not None:
            # TODO: convert to error as it's unsafe?
            print(
                f"WARNING. {self.sql_type} database ('{self.database}') was already used for ifc2sql patch before ('id_map' table found). "
                "Which could lead to mixed up ids and other unexpected results."
            )

    def create_id_map(self) -> None:
        if self.sql_type == "sqlite":
            statement = (
                "CREATE TABLE IF NOT EXISTS id_map (ifc_id integer PRIMARY KEY NOT NULL UNIQUE, ifc_class text);"
            )
        elif self.sql_type == "mysql":
            statement = """
            CREATE TABLE `id_map` (
              `ifc_id` int(10) unsigned NOT NULL,
              `ifc_class` varchar(255) NOT NULL,
              PRIMARY KEY (`ifc_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
            """
        else:
            assert False
        self.c.execute(statement)

    def create_metadata(self) -> None:
        # There is no "standard" SQL serialisation, so we propose a convention
        # of a "metadata" table to hold high level metadata. This includes the
        # preprocessor field to uniquely identify the "variant" of SQL schema
        # used. If someone wants their own SQL schema variant, they can
        # identify it using the preprocessor field.
        # IfcOpenShell-1.0.0 represents a schema where 1 table = 1 declaration.
        # IfcOpenShell-2.0.0 represents a schema where tables represent types.
        metadata = ["IfcOpenShell-1.0.0", self.file.schema, self.file.header.file_description.description[0]]
        if self.sql_type == "sqlite":
            statement = "CREATE TABLE IF NOT EXISTS metadata (preprocessor text, schema text, mvd text);"
            self.c.execute(statement)
            self.c.execute("INSERT INTO metadata VALUES (?, ?, ?);", metadata)
        elif self.sql_type == "mysql":
            statement = """
            CREATE TABLE `metadata` (
              `preprocessor` varchar(255) NOT NULL,
              `schema` varchar(255) NOT NULL,
              `mvd` varchar(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
            """
            self.c.execute(statement)
            self.c.execute("INSERT INTO metadata VALUES (%s, %s, %s);", metadata)

    def create_pset_table(self) -> None:
        statement = """
        CREATE TABLE IF NOT EXISTS psets (
            ifc_id integer NOT NULL,
            pset_name text,
            name text,
            value text
        );
        """
        self.c.execute(statement)

    def create_geometry_table(self) -> None:
        statement = """
        CREATE TABLE IF NOT EXISTS shape (
            ifc_id integer NOT NULL,
            x real,
            y real,
            z real,
            matrix blob,
            geometry text
        );
        """
        self.c.execute(statement)

        statement = """
        CREATE TABLE IF NOT EXISTS geometry (
            id text NOT NULL,
            verts blob,
            edges blob,
            faces blob,
            material_ids blob,
            materials json
        );
        """

        if self.sql_type == "mysql":
            # mediumblob holds up to 16mb, longblob holds up to 4gb
            statement = statement.replace("blob", "mediumblob")

        self.c.execute(statement)

    def create_sqlite_table(self, ifc_class: str, declaration: ifcopenshell.ifcopenshell_wrapper.declaration) -> None:
        statement = f"CREATE TABLE IF NOT EXISTS {ifc_class} ("

        if self.should_expand:
            statement += "ifc_id INTEGER NOT NULL"
        else:
            statement += "ifc_id INTEGER PRIMARY KEY NOT NULL UNIQUE"

        assert isinstance(declaration, ifcopenshell.ifcopenshell_wrapper.entity)
        total_attributes = declaration.attribute_count()

        if total_attributes:
            statement += ","

        derived = declaration.derived()
        for i in range(0, total_attributes):
            attribute = declaration.attribute_by_index(i)
            primitive = ifcopenshell.util.attribute.get_primitive_type(attribute)
            data_type = "TEXT"
            if primitive in ("string", "enum"):
                data_type = "TEXT"
            elif primitive in ("entity", "integer", "boolean"):
                data_type = "INTEGER"
            elif primitive == "float":
                data_type = "REAL"
            elif self.should_expand and self.is_entity_list(attribute):
                data_type = "INTEGER"
            elif isinstance(primitive, tuple):
                data_type = "JSON"
            elif primitive == "binary":
                data_type = "TEXT"
            else:
                print("Possibly not implemented attribute data type:", attribute, primitive)
            if not self.is_strict or derived[i]:
                optional = ""
            else:
                optional = "" if attribute.optional() else " NOT NULL"
            comma = "" if i == total_attributes - 1 else ","
            statement += f" `{attribute.name()}` {data_type}{optional}{comma}"
        if self.should_get_inverses:
            statement += ", inverses JSON"
        statement += ");"
        self.c.execute(statement)

    def create_mysql_table(self, ifc_class: str, declaration: ifcopenshell.ifcopenshell_wrapper.declaration) -> None:
        declaration = self.schema.declaration_by_name(ifc_class)
        statement = f"CREATE TABLE IF NOT EXISTS {ifc_class} ("
        statement += "`ifc_id` int(10) unsigned NOT NULL,"

        assert isinstance(declaration, ifcopenshell.ifcopenshell_wrapper.entity)
        derived = declaration.derived()
        json_attrs: list[int] = []
        for i, attribute in enumerate(declaration.all_attributes(), 1):
            primitive = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if primitive in ("string", "enum"):
                if "IfcText" in str(attribute.type_of_attribute()):
                    data_type = "text"
                else:
                    data_type = "varchar(255)"
            elif primitive == "entity":
                data_type = "int(10) unsigned"
            elif primitive == "boolean":
                data_type = "tinyint(1)"
            elif primitive == "integer":
                data_type = "int(10)"
                if "Positive" in str(attribute.type_of_attribute()):
                    data_type += " unsigned"
            elif primitive == "float":
                data_type = "decimal(10,0)"
            elif self.should_expand and self.is_entity_list(attribute):
                data_type = "int(10) unsigned"
            elif isinstance(primitive, tuple):
                data_type = "JSON"
                json_attrs.append(i)
            else:
                print("Possibly not implemented attribute data type:", attribute, primitive)
            if not self.is_strict or derived[i]:
                optional = "DEFAULT NULL"
            else:
                optional = "DEFAULT NULL" if attribute.optional() else "NOT NULL"
            statement += f" `{attribute.name()}` {data_type} {optional},"

        if json_attrs:
            # Don't add inverses column to json attrs, as it is json by definition.
            self.my_sql_classes_json_attrs[ifc_class] = json_attrs

        if self.should_get_inverses:
            statement += "inverses JSON, "

        if self.should_expand:
            statement = statement.removesuffix(",")
        else:
            statement += " PRIMARY KEY (`ifc_id`)"

        statement += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;"
        self.c.execute(statement)

    def insert_data(self, ifc_class: str) -> None:
        elements = self.file.by_type(ifc_class, include_subtypes=False)

        rows: list[list[Any]] = []
        id_map_rows: list[tuple[int, str]] = []
        pset_rows: list[tuple[int, str, str, Any]] = []

        for element in elements:
            nested_indices: list[int] = []
            values: list[Any] = [element.id()]
            for i, attribute in enumerate(element):
                if isinstance(attribute, ifcopenshell.entity_instance):
                    if attribute.id():
                        values.append(attribute.id())
                    else:
                        values.append(json.dumps({"type": attribute.is_a(), "value": attribute.wrappedValue}))
                elif (
                    self.should_expand
                    and attribute
                    and isinstance(attribute, tuple)
                    and isinstance(attribute[0], ifcopenshell.entity_instance)
                ):
                    nested_indices.append(i + 1)
                    serialised_attribute = self.serialise_value(element, attribute)
                    if attribute[0].id():
                        values.append(serialised_attribute)
                    else:
                        values.append(json.dumps(serialised_attribute))
                elif isinstance(attribute, tuple):
                    attribute = self.serialise_value(element, attribute)
                    values.append(json.dumps(attribute))
                else:
                    values.append(attribute)

            if self.should_get_inverses:
                values.append(json.dumps([e.id() for e in self.file.get_inverse(element)]))

            if self.should_expand:
                rows.extend(self.get_permutations(values, nested_indices))
            else:
                rows.append(values)

            id_map_rows.append((element.id(), ifc_class))

            if self.should_get_psets:
                psets = ifcopenshell.util.element.get_psets(element)
                for pset_name, pset_data in psets.items():
                    for prop_name, value in pset_data.items():
                        if prop_name == "id":
                            continue
                        if isinstance(value, list):
                            value = json.dumps(value)
                        pset_rows.append((element.id(), pset_name, prop_name, value))

            if self.should_get_geometry:
                if element.id() not in self.shape_rows and (placement := getattr(element, "ObjectPlacement", None)):
                    m = ifcopenshell.util.placement.get_local_placement(placement)
                    x, y, z = m[:, 3][0:3].tolist()
                    self.shape_rows[element.id()] = [element.id(), x, y, z, m.tobytes(), None]

        if self.sql_type == "sqlite":
            if rows:
                self.c.executemany(f"INSERT INTO {ifc_class} VALUES ({','.join(['?']*len(rows[0]))});", rows)
                self.c.executemany("INSERT INTO id_map VALUES (?, ?);", id_map_rows)
            if pset_rows:
                self.c.executemany("INSERT INTO psets VALUES (?, ?, ?, ?);", pset_rows)
        elif self.sql_type == "mysql":
            if rows:
                if json_attrs := self.my_sql_classes_json_attrs.get(ifc_class):
                    for attr_i in json_attrs:
                        for row in rows:
                            # None automatically converted to null.
                            if (value := row[attr_i]) is None:
                                continue
                            row[attr_i] = str(row[attr_i])
                self.c.executemany(f"INSERT INTO {ifc_class} VALUES ({','.join(['%s']*len(rows[0]))});", rows)
                self.c.executemany("INSERT INTO id_map VALUES (%s, %s);", id_map_rows)
            if pset_rows:
                self.c.executemany("INSERT INTO psets VALUES (%s, %s, %s, %s);", pset_rows)

    def serialise_value(self, element: ifcopenshell.entity_instance, value: Any) -> Any:
        return element.walk(
            lambda v: isinstance(v, ifcopenshell.entity_instance),
            lambda v: v.id() if v.id() else {"type": v.is_a(), "value": v.wrappedValue},
            value,
        )

    def get_permutations(self, lst: list[Any], indexes: list[int]) -> list[Any]:
        """
        Original row (`lst`):
        ```
        ifc_id, x, (a, b), (c,d)
        ```

        Resulting permutations:
        ```
        ifc_id, x, a, c
        ifc_id, x, a, d
        ifc_id, x, b, c
        ifc_id, x, b, d
        ```
        """
        nested_lists = [lst[i] for i in indexes]

        # Generate the Cartesian product of the nested lists
        products = list(itertools.product(*nested_lists))

        # Place the elements of each product back in their original positions
        final_lists = []
        for product in products:
            temp_list = lst[:]
            for i, index in enumerate(indexes):
                temp_list[index] = product[i]
            final_lists.append(temp_list)

        return final_lists

    def is_entity_list(self, attribute: ifcopenshell.ifcopenshell_wrapper.attribute) -> bool:
        attribute = str(attribute.type_of_attribute())
        if (attribute.startswith("<list") or attribute.startswith("<set")) and "<entity" in attribute:
            for data_type in re.findall("<(.*?) .*?>", attribute):
                if data_type not in ("list", "set", "select", "entity"):
                    return False
            return True
        return False
