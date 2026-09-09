from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from typing import Optional


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
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

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None


class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class UserResponse(BaseModel):

    id: UUID
    full_name: str
    email: EmailStr
    is_active: bool
    role: str

    model_config = ConfigDict(
        from_attributes=True
    )