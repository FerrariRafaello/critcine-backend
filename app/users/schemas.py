# _ IMPORTS
import re

from pydantic import BaseModel, Field, StringConstraints, field_validator, EmailStr
from typing import Optional, Annotated

from app.core.validators import validate_cpf_or_raise


# _ Cpf mixin
class CpfValidatorMixin(BaseModel):
    @field_validator("cpf", mode="before", check_fields=False)
    @classmethod
    def validate_cpf(cls, cpf):
        if cpf is None:
            return cpf
        cpf=re.sub(r'\D', '', cpf)
        validate_cpf_or_raise(cpf)
        return cpf



# _ pydantic Classes
class UserBase(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True,
        pattern=r'^[A-Za-z ]+$'
    )] = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=18, le=100)
    email: EmailStr = Field(..., min_length=10, max_length=50)
    cpf: str = Field(..., min_length=11, max_length=11)


class UserCreate(CpfValidatorMixin, UserBase):
    password:str=Field(..., min_length=6)
    pass


class UserUpdate(CpfValidatorMixin, UserBase):
    pass


class UserPatch(CpfValidatorMixin, BaseModel):
    name:Optional[Annotated[str, StringConstraints(
        strip_whitespace=True,
        pattern=r'^[A-Za-z ]+$'
    )]]=Field(None, min_length=2, max_length=50)
    age:Optional[int]=Field(None, ge=18, le=100)
    email: Optional[EmailStr] = Field(None, min_length=10, max_length=50)
    cpf:Optional[str]=Field(None, min_length=11, max_length=11)
    pass


class UserOut(UserBase):
    id:int
