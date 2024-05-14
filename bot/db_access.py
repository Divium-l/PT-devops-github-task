import psycopg2, os, dotenv
from psycopg2 import Error

from pt_logger import logger 

def query_database(query: str, noReturn = False) -> list:
    logger.debug("Trying to initialize database")
    connection = None
    dotenv.load_dotenv()
    HOST = os.getenv("SQL_HOST")
    PORT = os.getenv("SQL_PORT")
    USER = os.getenv("SQL_USER")
    PASS = os.getenv("SQL_PASS")
    DATABASE = os.getenv("SQL_DATABASE")

    try:
        connection = psycopg2.connect(user=USER, password=PASS, host=HOST, port=PORT, database=DATABASE)
        cursor = connection.cursor()

        cursor.execute(query)
        connection.commit()
        if (noReturn):
            return ""
        else:
            return cursor.fetchall()

    except (Exception, Error) as error:
        logger.error("Ошибка при работе с PostgreSQL: %s", error)
        raise Exception(error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_emails() -> str:
    resultString = ""
    rowList = query_database("SELECT * FROM emails;")

    for row in rowList:
        id, email = row
        resultString += f"{id}: {email}\n"

    return resultString

def get_phone_numbers() -> str:
    resultString = ""
    rowList = query_database("SELECT * FROM phones;")

    for row in rowList:
        id, phone = row
        resultString += f"{id}: {phone}\n"
        
    return resultString

def list_to_string(list: list[str]):
    values = ""

    for string in list:
        values += f"(DEFAULT ,'{string}'),"

    return values[:-1]

def save_emails(list: list[str]):
    logger.debug("Trying to save emails")

    values = list_to_string(list)

    logger.debug(f"Inserting into emails {values}")
    query_database(f"INSERT INTO emails (email_id, email) VALUES {values};", True)

def save_phone_numbers(list: list[str]):
    logger.debug("Trying to save phone numbers")

    values = list_to_string(list)

    logger.debug(f"Inserting into phones {values}")
    query_database(f"INSERT INTO phones (phone_id, phone) VALUES {values};", True)