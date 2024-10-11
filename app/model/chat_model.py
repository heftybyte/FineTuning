import os
import json
from app.db.startup import get_db_connection
from app.controllers.exceptions_controller import BadRequestException, NotFoundException


def create_chat_session(session_id: str, threshold: int, chat_history: list):
    if not session_id:
        raise BadRequestException("Invalid session ID")
    if threshold < os.getenv("THRESHOLD"):
        raise BadRequestException("Threshold cannot be less than 10")
    
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
        cur.execute("""
            INSERT INTO chat_session (session_id, threshold, chat_history) 
            VALUES (%s, %s, %s)
        """, (session_id, threshold, chat_history))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_chat_history(session_id: str):
    if not session_id:
        raise BadRequestException("Session ID is required")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT * FROM chat_session WHERE session_id = %s
        """, (session_id,))
        chat_history = cur.fetchall()

        conn.commit()

        if not chat_history:
            raise NotFoundException("Session / Chat history not found")

        return chat_history
    finally:
        cur.close()
        conn.close()


def save_message_to_db(session_id: str, message: str, response: str, chat_history: list, model_used: str):
    if not session_id or not message or not response:
        raise BadRequestException("Invalid session ID or message")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        chat_history_list = []
        if chat_history:
            chat_history_list = chat_history

        chat_history_list.append({
            "user_message": message,
            "model_response": response,
            "model_used": model_used
        })

        cur.execute("""
            UPDATE chat_session SET chat_history = %s WHERE session_id = %s
        """, (json.dumps(chat_history_list), session_id))

        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_threshold(session_id: str, threshold: int):
    if not session_id or threshold < 0:
        raise BadRequestException("Invalid session ID or threshold")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE chat_session SET threshold = %s WHERE session_id = %s
        """, (threshold, session_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()



