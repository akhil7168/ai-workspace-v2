from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)

    email: EmailStr

    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr

    password: str


class UserResponse(BaseModel):
    id: UUID

    full_name: str

    email: EmailStr

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)