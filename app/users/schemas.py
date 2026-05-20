import re

from pydantic import BaseModel, Field, StringConstraints, field_validator, EmailStr
from typing import Optional, Annotated

from app.core.validators import validate_cpf_or_raise
from app.core.sanitize import sanitize_text


class CpfValidatorMixin(BaseModel):
    @field_validator("cpf", mode="before", check_fields=False)
    @classmethod
    def validate_cpf(cls, cpf):
        if cpf is None:
            return cpf
        cpf = re.sub(r'\D', '', cpf)
        validate_cpf_or_raise(cpf)
        return cpf


class UserBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True)] = Field(..., min_length=2, max_length=50)
    age: Optional[int] = Field(None, ge=16, le=100)
    email: EmailStr = Field(..., min_length=10, max_length=50)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    bio: Optional[str] = Field(None, max_length=200)
    avatar_id: Optional[str] = None
    cover_id: Optional[str] = None
    pronouns: Optional[str] = Field(None, max_length=30)
    favorite_genres: Optional[str] = Field(None, max_length=200)

    # strip HTML from free-text fields before storing
    @field_validator("bio", "pronouns", "favorite_genres", mode="before")
    @classmethod
    def sanitize_text_fields(cls, v):
        return sanitize_text(v)

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        if v is None:
            return v
        return sanitize_text(v)


class UserCreate(CpfValidatorMixin, UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(CpfValidatorMixin, UserBase):
    pass


class UserPatch(CpfValidatorMixin, BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = Field(None, min_length=2, max_length=50)
    age: Optional[int] = Field(None, ge=16, le=100)
    email: Optional[EmailStr] = Field(None, min_length=10, max_length=50)
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    bio: Optional[str] = Field(None, max_length=200)
    avatar_id: Optional[str] = None
    cover_id: Optional[str] = None
    pronouns: Optional[str] = Field(None, max_length=30)
    favorite_genres: Optional[str] = Field(None, max_length=200)

    @field_validator("bio", "pronouns", "favorite_genres", mode="before")
    @classmethod
    def sanitize_text_fields(cls, v):
        return sanitize_text(v)

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        if v is None:
            return v
        return sanitize_text(v)


class UserOut(UserBase):
    id: int
    # follow stats populated by the router when fetching a specific user
    followers_count: int = 0
    following_count: int = 0
    is_following: bool = False


class UserPublicOut(BaseModel):
    """Returned by list endpoints — omits email and CPF to protect user privacy."""
    id: int
    name: str
    bio: Optional[str] = None
    pronouns: Optional[str] = None
    favorite_genres: Optional[str] = None
    avatar_id: Optional[str] = None
    cover_id: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
