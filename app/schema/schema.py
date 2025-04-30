from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    birthdate: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True
