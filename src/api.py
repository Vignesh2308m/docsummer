import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

app = FastAPI(title="OpenAI-Compatible Llama Bridge API")

# Target backend running llama-server (default port for llama.cpp server is 8080)
LLAMA_SERVER_URL = "http://localhost:8080"


# -------------------------------------------------------------------
# Pydantic Schemas (OpenAI v1 Spec)
# -------------------------------------------------------------------
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "llama-3"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None


# -------------------------------------------------------------------
# OpenAI Models Endpoint
# -------------------------------------------------------------------
@app.get("/v1/models")
async def list_models():
    """Lists available models for compatibility with OpenAI SDK."""
    return {
        "object": "list",
        "data": [
            {
                "id": "qwen2.5-1.5b",
                "object": "model",
                "created": 1700000000,
                "owned_by": "local-llama-server"
            }
        ]
    }


# -------------------------------------------------------------------
# Helper: Forward Non-Streaming Request
# -------------------------------------------------------------------
async def forward_non_stream(payload: dict):
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Forward to llama-server native completion endpoint
        response = await client.post(f"{LLAMA_SERVER_URL}/v1/chat/completions", json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()


# -------------------------------------------------------------------
# Helper: Forward SSE Streaming Request
# -------------------------------------------------------------------
async def forward_stream(payload: dict):
    client = httpx.AsyncClient(timeout=120.0)
    async with client.stream("POST", f"{LLAMA_SERVER_URL}/v1/chat/completions", json=payload) as response:
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Upstream error")
        
        async for chunk in response.aiter_text():
            if chunk:
                yield chunk


# -------------------------------------------------------------------
# Main OpenAI Chat Completion Endpoint
# -------------------------------------------------------------------
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # Convert Pydantic payload to dict
    payload = request.model_dump(exclude_none=True)

    if request.stream:
        return StreamingResponse(
            forward_stream(payload),
            media_type="text/event-stream"
        )
    else:
        result = await forward_non_stream(payload)
        return result


if __name__ == "__main__":
    import uvicorn
    # Runs the FastAPI server on http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)