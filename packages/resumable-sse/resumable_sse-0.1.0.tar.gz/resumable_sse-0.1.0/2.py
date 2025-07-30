from resumable_sse.factory import get_streamer
from redis.asyncio import Redis
import asyncio
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse


app = FastAPI()
r = Redis(port=56379, password='redis')
streamer = get_streamer(backend="memory", redis_client=r)

@app.get("/stream")
async def stream(conversation_id: str):
    async def generator():
        for word in ["这", "是", "统一", "接口"]:
            await asyncio.sleep(1.2)
            yield word

    return EventSourceResponse(
        streamer.stream(conversation_id, generator=generator())
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)