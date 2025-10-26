"""
Conversation API Endpoints for Gemini

These endpoints demonstrate the conversational capabilities of Gemini,
allowing multi-turn conversations with context preservation.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from app.specialists.gemini_adapter import GeminiAdapter

router = APIRouter()

# Store active conversations (in production, use Redis or database)
active_conversations: Dict[str, GeminiAdapter] = {}


class ConversationStartRequest(BaseModel):
    """Request to start a new conversation"""
    system_instruction: Optional[str] = Field(
        None, 
        description="Optional system instruction to set the AI's role and behavior"
    )
    initial_message: str = Field(..., description="The first message to send")
    conversation_id: Optional[str] = Field(None, description="Optional custom conversation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "system_instruction": "You are a legal assistant helping with personal injury cases.",
                "initial_message": "What are the key elements I need to prove negligence?"
            }
        }


class ConversationContinueRequest(BaseModel):
    """Request to continue an existing conversation"""
    conversation_id: str = Field(..., description="The ID of the conversation to continue")
    message: str = Field(..., description="The message to send")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv-1234567890",
                "message": "Can you give me a specific example?"
            }
        }


class ChatMessage(BaseModel):
    """A single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="The message content")


class MultiTurnChatRequest(BaseModel):
    """Request for a multi-turn chat without storing conversation state"""
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    system_instruction: Optional[str] = Field(None, description="Optional system instruction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "system_instruction": "You are a legal research assistant.",
                "messages": [
                    {"role": "user", "content": "What is negligence?"},
                    {"role": "assistant", "content": "Negligence is a legal concept..."},
                    {"role": "user", "content": "Can you give an example?"}
                ]
            }
        }


@router.post("/conversation/start", status_code=status.HTTP_200_OK)
async def start_conversation(request: ConversationStartRequest):
    """
    Start a new conversation with Gemini
    
    This creates a stateful conversation that maintains context across multiple messages.
    The conversation is stored server-side and can be continued using the conversation_id.
    
    Returns:
        - conversation_id: ID to use for continuing the conversation
        - response: The AI's response to the initial message
        - message_count: Number of messages in the conversation
    """
    try:
        # Check for API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key not configured. Please set GOOGLE_AI_API_KEY."
            )
        
        # Generate conversation ID
        conversation_id = request.conversation_id or f"conv-{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Create new Gemini adapter with system instruction
        adapter = GeminiAdapter(
            api_key=api_key,
            system_instruction=request.system_instruction
        )
        
        # Get first response
        response = await adapter.add_to_conversation(request.initial_message)
        
        # Store conversation
        active_conversations[conversation_id] = adapter
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "response": response,
            "message_count": len(adapter.conversation_history),
            "system_instruction": request.system_instruction
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting conversation: {str(e)}"
        )


@router.post("/conversation/continue", status_code=status.HTTP_200_OK)
async def continue_conversation(request: ConversationContinueRequest):
    """
    Continue an existing conversation
    
    Sends a new message in an ongoing conversation, maintaining all previous context.
    
    Returns:
        - response: The AI's response
        - message_count: Total number of messages in the conversation
    """
    try:
        # Get the conversation
        if request.conversation_id not in active_conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{request.conversation_id}' not found. It may have expired."
            )
        
        adapter = active_conversations[request.conversation_id]
        
        # Continue the conversation
        response = await adapter.add_to_conversation(request.message)
        
        return {
            "status": "success",
            "conversation_id": request.conversation_id,
            "response": response,
            "message_count": len(adapter.conversation_history)
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error continuing conversation: {str(e)}"
        )


@router.get("/conversation/{conversation_id}/history", status_code=status.HTTP_200_OK)
async def get_conversation_history(conversation_id: str):
    """
    Get the full history of a conversation
    
    Returns all messages in the conversation.
    """
    try:
        if conversation_id not in active_conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found"
            )
        
        adapter = active_conversations[conversation_id]
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "message_count": len(adapter.conversation_history),
            "history": adapter.conversation_history,
            "system_instruction": adapter.system_instruction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.delete("/conversation/{conversation_id}", status_code=status.HTTP_200_OK)
async def end_conversation(conversation_id: str):
    """
    End and delete a conversation
    
    Clears the conversation history and removes it from memory.
    """
    try:
        if conversation_id not in active_conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{conversation_id}' not found"
            )
        
        # Remove the conversation
        del active_conversations[conversation_id]
        
        return {
            "status": "success",
            "message": f"Conversation '{conversation_id}' ended and deleted",
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending conversation: {str(e)}"
        )


@router.post("/chat/multi-turn", status_code=status.HTTP_200_OK)
async def multi_turn_chat(request: MultiTurnChatRequest):
    """
    Have a multi-turn conversation without storing state
    
    This is a stateless endpoint that processes a complete conversation history
    and returns the next response. Useful for when you want to manage conversation
    state on the client side.
    
    Returns:
        - response: The AI's response to the last message
    """
    try:
        # Check for API key
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key not configured"
            )
        
        # Create adapter
        adapter = GeminiAdapter(
            api_key=api_key,
            system_instruction=request.system_instruction
        )
        
        # Convert messages to proper format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get response
        response = await adapter.chat(messages, request.system_instruction)
        
        return {
            "status": "success",
            "response": response,
            "message_count": len(messages) + 1
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in multi-turn chat: {str(e)}"
        )


@router.get("/conversations/active", status_code=status.HTTP_200_OK)
async def list_active_conversations():
    """
    List all active conversations
    
    Returns a list of conversation IDs that are currently active.
    """
    return {
        "status": "success",
        "total_conversations": len(active_conversations),
        "conversations": [
            {
                "conversation_id": conv_id,
                "message_count": len(adapter.conversation_history),
                "has_system_instruction": adapter.system_instruction is not None
            }
            for conv_id, adapter in active_conversations.items()
        ]
    }


@router.post("/conversations/clear-all", status_code=status.HTTP_200_OK)
async def clear_all_conversations():
    """
    Clear all active conversations
    
    Use with caution - this removes all stored conversations.
    """
    count = len(active_conversations)
    active_conversations.clear()
    
    return {
        "status": "success",
        "message": f"Cleared {count} conversation(s)",
        "cleared_count": count
    }


