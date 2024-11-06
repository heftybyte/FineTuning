import os
import json
from app.db.startup import get_db_connection
from app.controllers.exceptions_controller import BadRequestException, NotFoundException


def create_chat_session(threshold: int, chat_history: list, user_info: dict):
    if threshold < os.getenv("THRESHOLD"):
        raise BadRequestException("Threshold cannot be less than 10")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try: 
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_session (
                user_id VARCHAR(255),
                threshold INT,
                chat_history JSONB,
                user_info JSONB,
                has_accepted_policy BOOLEAN
            )
        """)
        cur.execute("""
            INSERT INTO chat_session (user_id, threshold, chat_history, user_info, has_accepted_policy) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_info.get('user_id'), threshold, json.dumps(chat_history), json.dumps(user_info), False))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_chat_history(user_id: str):
    if not user_id:
        raise BadRequestException("User ID is required")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT * FROM chat_session WHERE user_id = %s
        """, (user_id,))
        chat_history = cur.fetchone()

        conn.commit()

        if not chat_history:
            raise NotFoundException("Session / Chat history not found")

        return chat_history
    finally:
        cur.close()
        conn.close()

def get_user_data(user_id: str):
    if not user_id:
        raise BadRequestException("Invalid user ID")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT * FROM chat_session WHERE user_id = %s
        """, (user_id,))
        user_info = cur.fetchone()
        conn.commit()
        
        if not user_info:
            raise NotFoundException("User not found")

        return user_info
    finally:
        cur.close()
        conn.close()


def save_message_to_db(user_id: str, message: str, response: str, chat_history: list, model_used: str):
    if not user_id or not message or not response:
        raise BadRequestException("Invalid user ID or message")
    
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
            UPDATE chat_session SET chat_history = %s WHERE user_id = %s
        """, (json.dumps(chat_history_list), user_id))

        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_threshold(user_id: str, threshold: int):
    if not user_id or threshold < 0:
        raise BadRequestException("Invalid user ID or threshold")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE chat_session SET threshold = %s WHERE user_id = %s
        """, (threshold, user_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_has_accepted_policy(user_id: str, has_accepted_policy: bool):
    if not user_id:
        raise BadRequestException("Invalid user ID")
    
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE chat_session SET has_accepted_policy = %s WHERE user_id = %s
        """, (has_accepted_policy, user_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()

