from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.chat import ChatHistory
from ..models.crop import Crop
from ..models.user import User
from ..schemas.chat import ChatMessage, ChatResponse
from ..utils.auth import get_current_user
from ..services.gemini_ai import gemini_service

router = APIRouter(prefix="/chat", tags=["chat"])


def determine_message_type(message: str) -> str:
    """Determine the type of chat message based on content."""
    message_lower = message.lower()

    # Keywords for different message types
    weather_keywords = ["weather", "rain", "temperature", "climate", "ಹವಾಮಾನ", "ಮಳೆ"]
    disease_keywords = ["disease", "pest", "sick", "problem", "ರೋಗ", "ಕೀಟ"]
    market_keywords = ["price", "sell", "market", "buyer", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ"]
    farm_keywords = ["farm", "crop", "plant", "harvest", "ಬೆಳೆ", "ಕೃಷಿ"]

    if any(keyword in message_lower for keyword in weather_keywords):
        return "weather"
    elif any(keyword in message_lower for keyword in disease_keywords):
        return "disease"
    elif any(keyword in message_lower for keyword in market_keywords):
        return "market"
    elif any(keyword in message_lower for keyword in farm_keywords):
        return "farm_specific"
    else:
        return "general"


def generate_mock_ai_response(message: str, message_type: str, user: User) -> str:
    """Generate a mock AI response based on message type."""
    # This is a placeholder - in production, this would call Gemini API
    responses = {
        "weather": f"ನಮಸ್ಕಾರ {user.name}, ಇಂದಿನ ಹವಾಮಾನ ಮಾಹಿತಿ: ತಾಪಮಾನ 28°C, ಮಳೆಯ ಸಾಧ್ಯತೆ 30%. ನೀರಾವರಿ ಮಾಡಬಹುದು.",
        "disease": f"ನಮಸ್ಕಾರ {user.name}, ನಿಮ್ಮ ಬೆಳೆಯ ಸಮಸ್ಯೆಯನ್ನು ಪರಿಶೀಲಿಸಲು ಚಿತ್ರ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ. ನೀಮ್ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ.",
        "market": f"ನಮಸ್ಕಾರ {user.name}, ಇಂದಿನ ಟೊಮೇಟೊ ಬೆಲೆ: ₹25/ಕೆಜಿ. ಮಾರುಕಟ್ಟೆ ಬೇಡಿಕೆ ಚೆನ್ನಾಗಿದೆ.",
        "farm_specific": f"ನಮಸ್ಕಾರ {user.name}, ನಿಮ್ಮ ಕೃಷಿ ಚಟುವಟಿಕೆಗಳಿಗೆ ಸಹಾಯ ಮಾಡಲು ಸಿದ್ಧ. ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಬೇಕಿದ್ದರೆ ಹೇಳಿ.",
        "general": f"ನಮಸ್ಕಾರ {user.name}, ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ಬೆಳೆ, ಹವಾಮಾನ, ಮಾರುಕಟ್ಟೆ ಬಗ್ಗೆ ಕೇಳಿ.",
    }

    return responses.get(message_type, responses["general"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    chat_data: ChatMessage,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ChatHistory:
    """Send a chat message and get AI response."""
    # Verify farm ownership if crop_id is provided
    if chat_data.crop_id:
        farm = (
            db.query(Crop)
            .filter(Crop.id == chat_data.crop_id, Crop.user_id == current_user.id)
            .first()
        )
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
            )

    # Determine message type
    message_type = determine_message_type(chat_data.message)

    # Generate AI response (mock for now)
    ai_response = generate_mock_ai_response(
        chat_data.message, message_type, current_user
    )

    # Create chat history entry
    db_chat = ChatHistory(
        user_id=current_user.id,
        crop_id=chat_data.crop_id,
        user_message=chat_data.message,
        ai_response=ai_response,
        message_type=message_type,
        language=chat_data.language,
        is_voice_message=False,  # Always False since voice is removed
        follow_up_needed=False,
    )

    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)

    return db_chat


@router.get("/history", response_model=List[ChatResponse])
def get_chat_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    crop_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> List[ChatHistory]:
    """Get chat history for the current user."""
    query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)

    if crop_id:
        query = query.filter(ChatHistory.crop_id == crop_id)

    return query.order_by(ChatHistory.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat_message(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ChatHistory:
    """Get a specific chat message."""
    chat = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == chat_id, ChatHistory.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found"
        )

    return chat


@router.put("/{chat_id}/feedback")
def provide_chat_feedback(
    chat_id: int,
    rating: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    feedback: str | None = None,
) -> dict[str, str]:
    """Provide feedback on a chat response."""
    if not 1 <= rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5",
        )

    chat = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == chat_id, ChatHistory.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found"
        )

    chat.user_rating = rating
    chat.user_feedback = feedback

    db.commit()

    return {"message": "Feedback recorded successfully"}


@router.delete("/{chat_id}")
def delete_chat_message(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Delete a chat message."""
    chat = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == chat_id, ChatHistory.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat message not found"
        )

    db.delete(chat)
    db.commit()

    return {"message": "Chat message deleted successfully"}
