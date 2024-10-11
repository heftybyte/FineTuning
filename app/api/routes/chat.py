from fastapi import APIRouter, FastAPI, HTTPException
import uuid
import os
from pydantic import BaseModel
from app.controllers.chat_controllers import get_gpt_response
from app.controllers.exceptions_controller import BadRequestException, NotFoundException
from app.model.chat_model import create_chat_session, get_chat_history, save_message_to_db, update_threshold


app = FastAPI()
router = APIRouter()

class MessageRequest(BaseModel):
    session_id: str
    message: str


@router.post("/send-message")
async def send_message(request: MessageRequest):
    model = "gpt-4o"
    mini_model = "gpt-4o-mini"

    try:    
        # get chat history from db with session_id
        chat_history = get_chat_history(request.session_id)

        # check threshold & call openai
        threshold = chat_history[0][1]
        if threshold == 0:
            model_response = get_gpt_response(request.message, mini_model)
        else:
            model_response = get_gpt_response(request.message, model)

        # save message to db
        model_used = mini_model if threshold == 0 else model
        save_message_to_db(request.session_id, request.message, model_response, chat_history[0][2], model_used)

        # reduce threshold
        update_threshold(request.session_id, threshold - 1)

        return {"message": model_response}

    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/create-session")
async def create_session():
    session_id = str(uuid.uuid4())
    try:
        create_chat_session(session_id, os.getenv("THRESHOLD"), [])
        return {"session_id": session_id, "threshold": 10}
    except Exception as e:
        print(f"Unexpected error baby: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

app.include_router(router)



