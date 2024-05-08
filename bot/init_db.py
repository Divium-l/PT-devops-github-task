import psycopg2, os, dotenv
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from pt_logger import logger 

def init_db():
    logger.debug("Trying to initialize database")
    connection = None
    dotenv.load_dotenv()
    HOST = os.getenv("SQL_HOST")
    PORT = os.getenv("SQL_PORT")
    USER = os.getenv("SQL_USER")
    PASS = os.getenv("SQL_PASS")
    DATABASE = os.getenv("SQL_DATABASE")

    try:
        connection = psycopg2.connect(user=USER, password=PASS, host=HOST, port=PORT)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Checking if database exist
        cursor.execute(f"SELECT datname FROM pg_catalog.pg_database WHERE datname = '{DATABASE}';")
        data = cursor.fetchall()
        # Abort if exist
        if (len(data) != 0):
            logger.debug(f"Database '{DATABASE}' already exists")
            # cursor.execute(f"DROP DATABASE {DATABASE}")
            return
        
        # Creating database      
        logger.debug(f"Database '{DATABASE}' doesn't exist creating...")
        cursor.execute(f"CREATE DATABASE {DATABASE}")
        
        # Closing connection
        cursor.close()
        connection.close()

        # Opening new connection to created database
        logger.debug(f"Oppening connection to {DATABASE}")
        connection = psycopg2.connect(user=USER, password=PASS, host=HOST, port=PORT, database=DATABASE)
        cursor = connection.cursor()
        logger.debug("Creating tables")
        cursor.execute("""CREATE TABLE emails (
                       email_id INT PRIMARY KEY,
                       email VARCHAR(255)         
        );""")
        cursor.execute("CREATE SEQUENCE email_id_seq OWNED BY emails.email_id")
        cursor.execute("ALTER TABLE emails ALTER COLUMN email_id SET DEFAULT nextval('email_id_seq')")

        cursor.execute("""CREATE TABLE phones (
                       phone_id INT PRIMARY KEY,
                       phone VARCHAR(24)
        );""")
        cursor.execute("CREATE SEQUENCE phone_id_seq OWNED BY phones.phone_id")
        cursor.execute("ALTER TABLE phones ALTER COLUMN phone_id SET DEFAULT nextval('phone_id_seq')")

        logger.debug("Inserting data into tables tables")
        cursor.execute("INSERT INTO emails (email_id, email) VALUES (DEFAULT, 'generated_1@email.me'), (DEFAULT, 'generated_2@email.me')")
        cursor.execute("INSERT INTO phones (phone_id, phone) VALUES (DEFAULT, '8 800 555 35 35'), (DEFAULT, '+7 911 228 14 87')")
        connection.commit()
    except (Exception, Error) as error:
        logger.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

if (__name__ == '__main__'):
    init_db()