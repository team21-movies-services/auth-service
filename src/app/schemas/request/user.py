from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field
from pydantic.networks import EmailStr

regex_password = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,32}$'


class UserRegistrationSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str = Field(..., regex=regex_password)

    password_confirm: str

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    def safe_data(self):
        return self.dict(exclude={'password', 'password_confirm'})


class UserChangeInfoSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserChangePasswordSchema(BaseModel):
    password: str
    new_password: str = Field(..., regex=regex_password)
    new_password_confirm: str

    @validator('new_password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
