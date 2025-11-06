from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from logger import logger
from groq import Groq
import time

router = APIRouter()

# Adjust this value to control streaming speed (in seconds)
# Higher values = slower streaming
STREAM_DELAY = 0.05  # 50ms delay between chunks


@router.post("/groq_stream/")
async def groq_stream(question: str = Form(...)):
    """Stream completion tokens from Groq for a simple chat prompt."""
    logger.info("groq_stream request received")

    def token_generator():
        client = Groq()
        stream = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stop=None,
            stream=True,
        )
        for chunk in stream:
            delta = getattr(chunk.choices[0], "delta", None)
            if delta and getattr(delta, "content", None):
                yield delta.content
                time.sleep(STREAM_DELAY)  # Delay between chunks to slow down streaming

    return StreamingResponse(token_generator(), media_type="text/plain")


