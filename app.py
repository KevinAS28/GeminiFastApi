
from conf import *
from utils import *
from db import *

import json

from fastapi import Request
from fastapi import FastAPI, Request
import aioredis

app = FastAPI()
redis = None

@app.on_event("startup")
async def startup_event():
    global redis
    redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    if redis:
        await redis.close()

@app.post("/register")
async def register(request: Request):
    request_body = await request.json()
    username = request_body.get("username")
    hashed_password = hashmd5(request_body.get("password"))
    existing_user = get_user_from_database(username=username)
    if existing_user:
        return {"message": "User exists"}
    add_user_to_database(username, hashed_password)
    return {"message": "User created successfully"}

@app.get("/get-token")
async def get_token(request:Request):
    try:
        request_body = await request.json()
        username = request_body.get("username")
        hashed_password = hashmd5(request_body.get("password"))
        user = get_user_from_database(username=username)
        print('user:', user)
        if not user:
            return {"message": "Invalid credential"}
        elif user[2]!=hashed_password:
            return {"message": "Invalid credential"}
        else:
            return {"token": generate_access_token(username, hashed_password)}
            
    except json.JSONDecodeError:
        return {"message": "Not a json"}



@app.post('/generate')
async def generate_text_endpoint(request: Request):
    try:
        token_is_valid, obj = await check_token(request)
        if not token_is_valid:
            return obj
        request_body = await request.json()
        
        conv_id = request_body.get("conversation_id")
        conv_history = await redis.get(conv_id)
        if not conv_history:
            return {"message": "Invalid conversation id"}
        
        conv_history = json.loads(conv_history)
        all_warnings = []

        prompt = request_body.get("prompt")
        if not prompt:
            return {"error": "Missing 'prompt' in request body."}, 400 
        
        if len(prompt)>MAX_PROMPT_LENGTH:
            prompt = prompt[:MAX_PROMPT_LENGTH]
            all_warnings.append(f"The prompt length exceeding the max prompt length, the prompt has been cropped ({MAX_PROMPT_LENGTH})")

        conv_history["history"].append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        api_params = request_body.get("api_params", {})
        history = conv_history["history"]
        print(history)
        response = await generate_text_async(API_KEY, history, api_params)
        print(response)
        conv_history["history"].append(response["candidates"][0]["content"])     
        await redis.set(conv_id, json.dumps(conv_history))   
        response['warnings'] = all_warnings
        return response

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format."}, 400

@app.get("/new-conversation")
async def new_conversation(request: Request):
    token_is_valid, obj = await check_token(request)
    if not token_is_valid:
        return obj
    conv_id = hashmd5(obj[1])
    await redis.set(conv_id, json.dumps({"history":[]}))
    return {"conversation_id": conv_id}

@app.delete("/del-conversation")
async def del_conversation(request: Request):
    token_is_valid, obj = await check_token(request)
    if not token_is_valid:
        return obj
    conv_id = hashmd5(obj[1])
    await redis.delete(conv_id)
    return {"conversation_id": conv_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)