import logging
import logging_control
import psycopg2

# TODO: port 5432
class Database_Connector():
    def __init__(self) -> None:
        self.database = None
        self.schema_name = "VM_schema"
        self.table_name = "results"
    
    def run(self, ip:str, user:str, password:str, database:str, schema:str, table:str, database_mode:bool) -> int:
        self.schema_name = schema
        self.table_name = table
        self.database_mode = database_mode
        self.connect(ip, user, password)
        self.create_database(database)
        self.close_connection()
        self.connect(ip, user, password, database = database)
        self.create_schema()
        self.create_table()
    
    # подключение к postgres. если передан параметр database, подключение идет к переданной базе данных
    def connect(self, ip:str, user:str, password:str, **kwargs) -> None:
        database = kwargs.get("database", None)
        if database:
            logging.info(f"SQL: Connecting to PostgreSQL on host {ip} as user {user} with database {database}")
            self.database = database.lower()
        else:
            logging.info(f"SQL: Connecting to PostgreSQL on host {ip} as user {user} without database")
        logging.debug(f"SQL: Password {password}")
        try:
            self.connector = psycopg2.connect(host = ip, user = user, password = password, dbname = self.database)
            
            self.connector.autocommit = True
            self.cursor = self.connector.cursor()
            logging.info("SQL: Connection successful")
        except Exception as error:
            logging.error("SQL: An error occured while connecting to PostgreSQL")
            logging.error(f"SQL: Error: {error}")
    
    # выполнить запрос с помощью курсора, созданного при помощи connect
    def _execute_(self, sql_statement:str) -> int:
        logging.info("SQL: Performing a query to PostgreSQL")
        logging.info(f"SQL: Query: {sql_statement}")
        try:
            self.cursor.execute(sql_statement)
            logging.info("SQL: Query successful")
            return 0
        except psycopg2.errors.DuplicateDatabase as existing_database: # обработка исключения на повторное создание бд (для метода create_database)
            return 1
        except psycopg2.errors.DuplicateTable as existing_table: # обработка исключения на повторное создание таблицы (для метода create_table)
            return 1
        except Exception as error:
            logging.error("SQL: An error occured while querying to PostgreSQL")
            logging.error(f"SQL: Error: {error}")
            return -1

    # создать бд, в случае если уже создана - указать в логах
    def create_database(self, db_name:str = "VM") -> int:
        sql_statement = """CREATE DATABASE {0};""".format(db_name)
        logging.info(f"SQL: Creating database {db_name}")
        res = self._execute_(sql_statement)
        if res == 1: 
            logging.warn(f"SQL: Database {db_name} already exists")
    
    # создание схемы в случае, если еще не создана
    def create_schema(self) -> int:
        sql_statement = """CREATE SCHEMA IF NOT EXISTS {0};""".format(self.schema_name)
        logging.info(f"SQL: Creating schema {self.schema_name}")
        self._execute_(sql_statement)
    
    def create_table(self) -> int:
        sql_statement =f"""
            CREATE TABLE {self.schema_name}.{self.table_name}(
            ID  SERIAL PRIMARY KEY,
            IP           TEXT      NOT NULL,
            OS           TEXT       NOT NULL,
            version      TEXT       NOT NULL,
            architecture TEXT       NOT NULL
        );"""
        sql_statement_drop = f"""
            DROP TABLE {self.schema_name}.{self.table_name};
        """
        logging.info(f"SQL: Creating table {self.table_name} in schema {self.schema_name}")
        res = self._execute_(sql_statement)
        if res == 1 and not self.database_mode: 
            logging.warn("Results table already exists. Recreating...")
            self._execute_(sql_statement_drop)
            self._execute_(sql_statement)
    
    def write_values(self, values:list[str]) -> int:
        sql_statement = """
            INSERT INTO %s.%s
            (IP, OS, version, architecture) VALUES
            (%s);
            """ % (self.schema_name,  self.table_name,  
            "".join(f"'{item}'," for item in values)[:-1])
        logging.info(f"SQL: Inserting values into database {self.database}")
        self._execute_(sql_statement)
        return 0
        
    def get_table(self) -> int:
        sql_statement = f"""
            SELECT * FROM {self.schema_name}.{self.table_name};
        """
        logging.info(f"Getting values from table {self.schema_name}.{self.table_name}")
        self._execute_(sql_statement)
        return 0
        
    # разорвать подключение к Postgres
    def close_connection(self) -> None:
        logging.info(f"SQL: Closing connection to PostgreSQL. Database: {self.database}")
        self.cursor.close()

