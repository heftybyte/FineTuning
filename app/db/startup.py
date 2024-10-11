import psycopg2
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = psycopg2.connect(host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'), 
                        dbname=os.getenv('DB_NAME'), 
                        user=os.getenv('DB_USER'), 
                        password=os.getenv('DB_PASSWORD')
                    )
    return conn

def create_database_if_not_exists():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_session (
                session_id VARCHAR(255) PRIMARY KEY,
                threshold INT,
                chat_history JSONB
            )
        """)
        logger.info(f"Table 'person' created in database {os.getenv('DB_NAME')}")
    except psycopg2.errors.DuplicateTable:
        logger.warning(f"Table already exists in database {os.getenv('DB_NAME')}")
    except psycopg2.Error as e:
        logger.error(f"An error occurred: {str(e)}")

    conn.commit()

    cur.close()
    conn.close()
    