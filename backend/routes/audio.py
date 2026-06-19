from fastapi import APIRouter, WebSocket, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from db.session import get_db
from services.audio_services import handle_audio_stream
from config import settings

router = APIRouter(prefix="/audio", tags=["Audio Streaming"])


@router.websocket("/stream/{consultation_uuid}")
async def audio_stream(
    websocket: WebSocket,
    consultation_uuid: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        doctor_uuid: str | None = payload.get("uuid")

        if not doctor_uuid:
            await websocket.close(code=4001, reason="Invalid token")
            return

    except JWTError:
        await websocket.close(code=4001, reason="Token invalid or expired")
        return

    
    await websocket.accept()

   
    await handle_audio_stream(
        websocket           = websocket,
        consultation_uuid   = consultation_uuid,
        current_doctor_uuid = doctor_uuid,
        db                  = db
    )