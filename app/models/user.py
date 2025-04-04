from pydantic import BaseModel, EmailStr


class UserCredentials(BaseModel):
    email: EmailStr
    username: str
    password: str


class TwoFactorCode(BaseModel):
    email: EmailStr
    code: int


class Token(BaseModel):
    token: str


class User(BaseModel):

    id: int
    createdAt: str
    updatedAt: str
    email: EmailStr
    password: str
    roles: list[str]
    username: str
    profileImgPath: str
    private: bool
    active: bool
    banned: bool
    twits: list[str]
    conversations: list[str]
    messages: list[str]
    followers: list[str]
    followings: list[str]
    likes: list[str]
    reposts: list[str]
    userIdentifier: str
