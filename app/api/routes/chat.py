from fastapi import APIRouter, FastAPI, HTTPException, Body
import uuid
import os
from pydantic import BaseModel
from app.controllers.chat_controllers import get_gpt_response
from app.controllers.exceptions_controller import BadRequestException, NotFoundException
from app.model.chat_model import create_chat_session, get_chat_history, get_user_data, save_message_to_db, update_has_accepted_policy, update_threshold


app = FastAPI()
router = APIRouter()

class MessageRequest(BaseModel):
    user_id: str
    message: str


@router.post("/send-message")
async def send_message(request: MessageRequest):
    model = "gpt-4o"
    mini_model = "gpt-4o-mini"
    
    try:   
        # get chat history from db with user_id
        chat_history = get_chat_history(request.user_id)

        # check threshold & call openai
        threshold = chat_history[1]
        if threshold == 0:
            model_response = get_gpt_response(request.message, mini_model)
        else:
            model_response = get_gpt_response(request.message, model)

        # save message to db
        model_used = mini_model if threshold == 0 else model
        save_message_to_db(request.user_id, request.message, model_response, chat_history[2], model_used)

        # reduce threshold
        update_threshold(request.user_id, threshold - 1)

        return {"message": model_response, "threshold": threshold - 1}

    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


class UserInfo(BaseModel):
    user_id: int
    username: str
    name: str
    language: str
    is_bot: bool

@router.post("/create-session")
async def create_session(user_info: UserInfo):
    try:
        user_info_dict = user_info.model_dump() # convert to dict
        create_chat_session(os.getenv("THRESHOLD"), [], user_info_dict)
        return {"threshold": os.getenv("THRESHOLD")}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



@router.post("/accept-policy")
async def accept_policy(user_id: str):
    try:
        update_has_accepted_policy(user_id, True)
        return {"message": "Policy accepted"}
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



class UserID(BaseModel):
    user_id: int

@router.get("/get-user-info")
async def get_user_info(user_id: str):
    try:
        user_info = get_user_data(user_id)
        return {"user_info": user_info}
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


app.include_router(router)



