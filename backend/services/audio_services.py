import asyncio
from deepgram.core import EventType
from deepgram.listen.v1 import ListenV1Results
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.consultation import Consultation, ConsultationStatus
from models.transcript import Transcript, SpeakerEnum
from utils.deepgram_client import get_deepgram_client, get_live_options
from fastapi import HTTPException, status
import logging

logger = logging.getLogger("doctor_zenz.audio")


async def handle_audio_stream(
    websocket: WebSocket,
    consultation_uuid: str,
    current_doctor_uuid: str,
    db: AsyncSession
):

    
    result = await db.execute(
        select(Consultation).where(Consultation.uuid == consultation_uuid)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        await websocket.close(code=4004, reason="Consultation not found")
        return

    if str(consultation.doctor_id) != str(current_doctor_uuid):
        await websocket.close(code=4003, reason="Not authorized")
        return

    if consultation.status != ConsultationStatus.IN_PROGRESS:
        await websocket.close(code=4000, reason="Consultation is not in progress")
        return


    deepgram      = get_deepgram_client()
    transcript_buffer = []

    async def on_transcript(result, **kwargs):
        if not isinstance(result, ListenV1Results):
            return
        if not result.channel.alternatives:
            return
        alternative = result.channel.alternatives[0]
        sentence = alternative.transcript

        if not sentence:
            return

        if result.is_final:
            words = alternative.words
            speaker_id = words[0].speaker if words else 0
            speaker = SpeakerEnum.DOCTOR if speaker_id == 0 else SpeakerEnum.PATIENT

            transcript_buffer.append({
                "speaker"         : speaker,
                "text"            : sentence,
                "timestamp_start" : result.start,
                "timestamp_end"   : result.start + result.duration,
                "confidence"      : alternative.confidence,
            })

    async def on_error(error, **kwargs):
        logger.error(f"Deepgram error: {error}")

    async with deepgram.listen.v1.connect(**get_live_options()) as dg_connection:
        dg_connection.on(EventType.MESSAGE, on_transcript)
        dg_connection.on(EventType.ERROR,   on_error)

        listener_task = asyncio.create_task(dg_connection.start_listening())

        try:
            while True:
                audio_chunk = await websocket.receive_bytes()
                await dg_connection.send_media(audio_chunk)

        except Exception as e:
            logger.info(f"WebSocket disconnected: {e}")

        finally:
            try:
                await dg_connection.send_close_stream()
            except Exception as close_err:
                logger.error(f"Error sending CloseStream to Deepgram: {close_err}")
            
            await listener_task

        
        for chunk in transcript_buffer:
            transcript = Transcript(
                consultation_id = consultation.uuid,
                speaker         = chunk["speaker"],
                text            = chunk["text"],
                timestamp_start = chunk["timestamp_start"],
                timestamp_end   = chunk["timestamp_end"],
                confidence      = chunk["confidence"],
            )
            db.add(transcript)

        await db.commit()
        logger.info(f"Saved {len(transcript_buffer)} transcript chunks")