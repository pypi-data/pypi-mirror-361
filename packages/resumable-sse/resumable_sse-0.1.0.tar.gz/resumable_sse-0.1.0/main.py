import asyncio
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as redis
from typing import Optional

app = FastAPI()
r = redis.Redis(port=56379, password='redis')


async def simulate_model_output(conversation_id: str, query: str):
    """模拟 AI 模型输出，实际项目中替换为真实的 AI 模型调用"""
    key = f"stream:chat:{conversation_id}"

    # 根据不同的 query 生成不同的响应（示例）
    if "你好" in query:
        chunks = ["你好，", "我是一个", "AI 模型。", "很高兴见到你。"]
    elif "天气" in query:
        chunks = ["今天", "天气", "很好，", "适合出行。"]
    else:
        chunks = ["我理解", "你的问题，", "让我", "为你详细", "解答。"]

    # 设置一个标记表示正在生成
    await r.hset(f"status:{conversation_id}", "generating", "true")
    await r.hset(f"status:{conversation_id}", "query", query)

    try:
        for i, chunk in enumerate(chunks):
            await r.xadd(key, {"data": chunk, "index": i})
            await asyncio.sleep(1)  # 模拟流式输出间隔

        # 添加结束标记
        await r.xadd(key, {"data": "[END]", "index": len(chunks)})

    finally:
        # 生成完成后清除状态
        await r.hset(f"status:{conversation_id}", "generating", "false")


@app.get("/stream")
async def stream_chat(conversation_id: str, query: Optional[str] = None, last_id: str = "0-0"):
    key = f"stream:chat:{conversation_id}"
    status_key = f"status:{conversation_id}"

    # 检查是否有正在进行的生成或未读完的消息
    status = await r.hgetall(status_key)
    is_generating = status.get(b"generating", b"false") == b"true"

    # 检查是否有未读的消息
    existing_messages = await r.xread({key: last_id}, count=1000)
    has_unread = len(existing_messages) > 0 and len(existing_messages[0][1]) > 0

    async def event_generator():
        nonlocal last_id

        # 如果有未读消息，先返回这些消息
        if has_unread:
            print(f"发现未读消息，从 {last_id} 开始恢复")
            while True:
                resp = await r.xread({key: last_id}, count=10)
                if resp:
                    _, messages = resp[0]
                    for msg_id, msg in messages:
                        last_id = msg_id
                        data = msg[b"data"].decode("utf-8")

                        if data == "[END]":
                            yield {"event": "end", "data": ""}
                            # 清理已完成的对话数据
                            await r.delete(key)
                            await r.delete(status_key)
                            return
                        else:
                            yield {
                                "event": "message",
                                "id": msg_id.decode("utf-8"),
                                "data": data
                            }
                else:
                    # 没有更多消息了，检查是否还在生成
                    current_status = await r.hget(status_key, "generating")
                    if current_status != b"true":
                        break
                    await asyncio.sleep(0.5)  # 等待新消息

        # 如果没有未读消息且没有正在生成，开始新的生成
        elif not is_generating and query:
            print(f"开始新的对话生成: {query}")
            # 启动新的生成任务
            asyncio.create_task(simulate_model_output(conversation_id, query))

            # 等待并返回新生成的消息
            while True:
                resp = await r.xread({key: last_id}, block=3000, count=1)
                if resp:
                    _, messages = resp[0]
                    for msg_id, msg in messages:
                        last_id = msg_id
                        data = msg[b"data"].decode("utf-8")

                        if data == "[END]":
                            yield {"event": "end", "data": ""}
                            # 清理已完成的对话数据
                            await r.delete(key)
                            await r.delete(status_key)
                            return
                        else:
                            yield {
                                "event": "message",
                                "id": msg_id.decode("utf-8"),
                                "data": data
                            }
                else:
                    # 超时或没有更多消息
                    break

        # 如果正在生成但没有新消息，等待
        elif is_generating:
            print("检测到正在生成中，等待消息...")
            while True:
                resp = await r.xread({key: last_id}, block=3000, count=1)
                if resp:
                    _, messages = resp[0]
                    for msg_id, msg in messages:
                        last_id = msg_id
                        data = msg[b"data"].decode("utf-8")

                        if data == "[END]":
                            yield {"event": "end", "data": ""}
                            await r.delete(key)
                            await r.delete(status_key)
                            return
                        else:
                            yield {
                                "event": "message",
                                "id": msg_id.decode("utf-8"),
                                "data": data
                            }
                else:
                    # 检查是否还在生成
                    current_status = await r.hget(status_key, "generating")
                    if current_status != b"true":
                        break

        else:
            # 没有查询参数且没有未完成的对话
            yield {"event": "error", "data": "需要提供 query 参数来开始新对话"}

    return EventSourceResponse(event_generator())


# 获取对话状态的辅助接口
@app.get("/status/{conversation_id}")
async def get_conversation_status(conversation_id: str):
    key = f"stream:chat:{conversation_id}"
    status_key = f"status:{conversation_id}"

    status = await r.hgetall(status_key)
    message_count = await r.xlen(key)

    return {
        "conversation_id": conversation_id,
        "generating": status.get(b"generating", b"false").decode("utf-8") == "true",
        "query": status.get(b"query", b"").decode("utf-8"),
        "message_count": message_count,
        "has_unfinished": message_count > 0
    }


# 清理对话数据的接口
@app.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    key = f"stream:chat:{conversation_id}"
    status_key = f"status:{conversation_id}"

    await r.delete(key)
    await r.delete(status_key)

    return {"message": "对话数据已清理"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)