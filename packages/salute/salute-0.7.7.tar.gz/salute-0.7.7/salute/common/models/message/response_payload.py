from enum import Enum

from pydantic import BaseModel

from salute.common.models.message.payload import Payload


class Suggestion(BaseModel):
    buttons: list[dict] = []


class PronounceType(Enum):
    TEXT = "application/text"
    SSML = "application/smml"


class ResponsePayload(Payload):
    pronounceText: str = ""
    pronounceTextType: PronounceType = PronounceType.SSML
    items: list = []
    suggestions: Suggestion = Suggestion()
    auto_listening: bool = False
