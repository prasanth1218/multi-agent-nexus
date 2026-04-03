"""Chat API endpoint with SSE streaming."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.orchestrator import process_message
from services.database import (
    create_conversation, save_message, get_messages,
    update_conversation_title
)


router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@router.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint — returns SSE stream of agent responses."""

    # Get or create conversation
    conv_id = request.conversation_id
    if not conv_id:
        conv = await create_conversation(title=request.message[:50])
        conv_id = conv["id"]
    else:
        # Update title if it's still "New Chat"
        pass

    # Save user message
    await save_message(conv_id, "user", request.message)

    # Get conversation context
    history = await get_messages(conv_id)
    context = [{"role": m["role"], "content": m["content"]} for m in history[:-1]]

    # Stream response
    async def generate():
        full_response = ""
        agents_used = []

        async for event in process_message(request.message, context):
            yield event

            # Collect the full response for saving
            if '"content":' in event and "event: token" in event:
                import json
                try:
                    data_line = event.split("data: ", 1)[1].split("\n")[0]
                    data = json.loads(data_line)
                    full_response += data.get("content", "")
                except (json.JSONDecodeError, IndexError):
                    pass

            if "event: done" in event:
                import json
                try:
                    data_line = event.split("data: ", 1)[1].split("\n")[0]
                    data = json.loads(data_line)
                    agents_used = data.get("agents_used", [])
                except (json.JSONDecodeError, IndexError):
                    pass

        # Save assistant response
        if full_response:
            await save_message(
                conv_id, "assistant", full_response,
                agent_type=",".join(agents_used) if agents_used else None,
                metadata={"agents_used": agents_used}
            )

        # Auto-generate title from first message
        if len(history) <= 1:
            title = request.message[:60]
            if len(request.message) > 60:
                title += "..."
            await update_conversation_title(conv_id, title)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-Id": conv_id,
        }
    )
