from app.controllers.exceptions_controller import BadRequestException
from openai import OpenAI
import os

def get_gpt_response(message: str, model: str):
    client = OpenAI(api_key=os.getenv('OPENAI_SECRET_KEY'))
    system_prompt = os.getenv('SYSTEM_PROMPT')
    print(f"system_prompt: {system_prompt}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise BadRequestException(f"Failed to get response from OpenAI: {e}")
