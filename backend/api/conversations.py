"""Conversations API — CRUD for conversation history."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.database import (
    get_conversations, get_conversation, get_messages,
    create_conversation, delete_conversation, update_conversation_title
)


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class ConversationUpdate(BaseModel):
    title: str


@router.get("")
async def list_conversations():
    """List all conversations, newest first."""
    conversations = await get_conversations()
    return {"conversations": conversations}


@router.post("")
async def new_conversation():
    """Create a new conversation."""
    conv = await create_conversation()
    return conv


@router.get("/{conv_id}")
async def get_conv(conv_id: str):
    """Get a conversation with its messages."""
    conv = await get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await get_messages(conv_id)
    return {**conv, "messages": messages}


@router.patch("/{conv_id}")
async def update_conv(conv_id: str, update: ConversationUpdate):
    """Update conversation title."""
    conv = await get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await update_conversation_title(conv_id, update.title)
    return {"status": "updated"}


@router.delete("/{conv_id}")
async def delete_conv(conv_id: str):
    """Delete a conversation."""
    await delete_conversation(conv_id)
    return {"status": "deleted"}
