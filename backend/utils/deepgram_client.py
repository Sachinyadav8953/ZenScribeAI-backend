# utils/deepgram_client.py

from deepgram import AsyncDeepgramClient
from config import settings
import typing


def get_deepgram_client() -> AsyncDeepgramClient:
    return AsyncDeepgramClient(api_key=settings.DEEPGRAM_API_KEY)


def get_live_options() -> typing.Dict[str, typing.Any]:
    return {
        "model"           : "nova-2-medical",     
        "language"        : "en-IN",              
        "smart_format"    : True,                
        "punctuate"       : True,                 
        "diarize"         : True,                 
        "interim_results" : True,                 
        "utterance_end_ms": "1000",              
        "vad_events"      : True,                 
    }