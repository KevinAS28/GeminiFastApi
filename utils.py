from db import *

from typing import Dict
import json

import aiohttp
from fastapi import Request

async def check_token(request: Request):
    try:
        request_body = await request.json()
        token = request_body.get("token")
        if not token:
            return False, {"message":"invalid token"}
        
        db_user = get_user_from_database(token=token)

        if not db_user:
            return False, {"message": "Invalid token"}
    
        return True, db_user
    except json.JSONDecodeError:
        return False, {"message":"invalid request (not json)"}

async def generate_text_async(api_key, conv_history: list, api_params: Dict = None):
    if api_params is None:
        api_params = {}
                    
    model = api_params.get("model", "gemini-pro")
    temperature = api_params.get("temperature", 0.7)
    max_output_tokens = api_params.get("max_output_tokens", 1024)
    top_p = api_params.get("top_p", 1.0)
    top_k = api_params.get("top_k", 100)

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "contents": conv_history,
        "model": model,
        "generation_config": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
            "topP": top_p,
            "topK": top_k
            # "stop_sequences": ""
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                api_response = await response.json()                
                return api_response  
            else:
                error_message = f"Error: {response.status} - {await response.text()}"
                return {"error": error_message} 