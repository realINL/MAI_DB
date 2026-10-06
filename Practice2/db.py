import os

import pyodbc
from dotenv import load_dotenv


class Database:
    LOOKUP_COLUMNS = {
        "fam": "f_val",
        "nam": "n_val",
        "otc": "o_val",
        "street": "s_val",
    }

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_DRIVER: str
    connected = False
    connection: pyodbc.Connection
    cursor: pyodbc.Cursor

    PEOPLE_SELECT = """
        SELECT p.u_id, f.f_val, n.n_val, o.o_val, s.s_val,
               p.bldn, p.bldn_k, p.appr, p.telef_n
        FROM people p
        JOIN fam f ON p.fam = f.u_id
        JOIN nam n ON p.nam = n.u_id
        JOIN otc o ON p.otc = o.u_id
        JOIN street s ON p.street = s.u_id
    """

    def __init__(self):
        load_dotenv()

        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASS = os.getenv("DB_PASS")
        self.DB_DRIVER = os.getenv("DB_DRIVER")

    def connect(
        self,
        DB_HOST=None,
        DB_PORT=None,
        DB_NAME=None,
        DB_USER=None,
        DB_PASS=None,
        DB_DRIVER=None,
    ) -> bool:
        DB_HOST = DB_HOST if DB_HOST is not None else self.DB_HOST
        DB_PORT = DB_PORT if DB_PORT is not None else self.DB_PORT
        DB_NAME = DB_NAME if DB_NAME is not None else self.DB_NAME
        DB_USER = DB_USER if DB_USER is not None else self.DB_USER
        DB_PASS = DB_PASS if DB_PASS is not None else self.DB_PASS
        DB_DRIVER = DB_DRIVER if DB_DRIVER is not None else self.DB_DRIVER

        try:
            connection_string = (
                f"DRIVER={DB_DRIVER};"
                f"SERVER={DB_HOST};"
                f"PORT={DB_PORT};"
                f"DATABASE={DB_NAME};"
                f"UID={DB_USER};"
                f"PWD={DB_PASS};"
            )
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            self.connected = True
            self.connection = connection
            self.cursor = cursor
            print("Connection successful!")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
        return False

    def test(self, table_name: str):
        rows = self.connection.cursor().execute(f"SELECT * FROM {table_name}").fetchall()
        for row in rows:
            print(row)

    def get_tables(self):
        tables_cursor = self.cursor.tables(tableType="TABLE")
        table_names = []
        for row in tables_cursor:
            table_names.append(row.table_name)
        print("Список ваших таблиц:")
        print(table_names)

    # выполнение любого sql запроса
    def execute_sql(self, sql_request: str) -> dict:
        sql_request = sql_request.strip()
        if not sql_request:
            raise ValueError("Пустой SQL-запрос")
        cursor = self.connection.cursor()
        cursor.execute(sql_request)
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return {
                "kind": "result",
                "columns": columns,
                "rows": rows,
                "rowcount": len(rows),
            }
        affected = cursor.rowcount
        self.connection.commit()
        return {
            "kind": "command",
            "columns": [],
            "rows": [],
            "rowcount": affected,
        }

    # получение из справочника
    def fetch_lookup(self, table: str, value_column: str | None = None):
        value_column = value_column or self.LOOKUP_COLUMNS[table]
        sql = f"SELECT u_id, {value_column} FROM {table} ORDER BY {value_column}"
        return self.cursor.execute(sql).fetchall()

    # добавление в справочники
    def insert_lookup(self, table: str, value: str) -> int:
        value = value.strip()
        if not value:
            raise ValueError("Пустое значение справочника")
        col = self.LOOKUP_COLUMNS[table]
        sql = f"INSERT INTO {table} ({col}) VALUES (?) RETURNING u_id"
        cursor = self.connection.cursor()
        cursor.execute(sql, (value,))
        new_id = cursor.fetchone()[0]
        self.connection.commit()
        return new_id

    # добавление человека
    def insert_person(
        self,
        fam_id,
        nam_id,
        otc_id,
        street_id,
        bldn=None,
        bldn_k=None,
        appr=None,
        telef_n=None,
    ) -> int:
        if None in (fam_id, nam_id, otc_id, street_id):
            raise ValueError("Выберите фамилию, имя, отчество и улицу")
        sql = """
            INSERT INTO people (fam, nam, otc, street, bldn, bldn_k, appr, telef_n)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING u_id
        """
        cursor = self.connection.cursor()
        cursor.execute(
            sql,
            (fam_id, nam_id, otc_id, street_id, bldn, bldn_k, appr, telef_n),
        )
        new_id = cursor.fetchone()[0]
        self.connection.commit()
        return new_id

    def _people_where(self, fam_id=None, nam_id=None, otc_id=None, street_id=None):
        clauses = []
        params = []
        if fam_id is not None:
            clauses.append("p.fam = ?")
            params.append(fam_id)
        if nam_id is not None:
            clauses.append("p.nam = ?")
            params.append(nam_id)
        if otc_id is not None:
            clauses.append("p.otc = ?")
            params.append(otc_id)
        if street_id is not None:
            clauses.append("p.street = ?")
            params.append(street_id)
        if not clauses:
            return "", []
        return " WHERE " + " AND ".join(clauses), params

    def fetch_people(self, fam_id=None, nam_id=None, otc_id=None, street_id=None):
        where, params = self._people_where(fam_id, nam_id, otc_id, street_id)
        sql = self.PEOPLE_SELECT + where + " ORDER BY p.u_id"
        return self.cursor.execute(sql, params).fetchall()

    def delete_people(self, fam_id=None, nam_id=None, otc_id=None, street_id=None):
        where, params = self._people_where(fam_id, nam_id, otc_id, street_id)
        if not where:
            return 0
        sql = f"DELETE FROM people p{where}"
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        deleted = cursor.rowcount
        self.connection.commit()
        return deleted

    def delete_people_by_ids(self, ids):
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        sql = f"DELETE FROM people WHERE u_id IN ({placeholders})"
        cursor = self.connection.cursor()
        cursor.execute(sql, ids)
        deleted = cursor.rowcount
        self.connection.commit()
        return deleted
