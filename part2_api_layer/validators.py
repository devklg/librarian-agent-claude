from pydantic import BaseModel, Field, field_validator
import html
import re

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    requester_id: str = Field(default="user", max_length=100)
    requester_type: str = Field(default="human", pattern="^(human|agent|application)$")

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        v = html.escape(v)
        v = v.replace('\x00', '')
        return v.strip()

    @field_validator('requester_id')
    @classmethod
    def validate_requester_id(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('requester_id must be alphanumeric')
        return v

class DocumentUploadRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="general")

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return html.escape(v.strip())
