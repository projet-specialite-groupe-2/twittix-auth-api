from pydantic import BaseModel, EmailStr


class UserCredentials(BaseModel):
    email: EmailStr
    password: str


class TwoFactorCode(BaseModel):
    email: EmailStr
    code: int


class token_is_valid_response(BaseModel):
    email: EmailStr
    token: str
    exp_time: int


class temporary_token_response(BaseModel):
    refresh_token: str


class Token(BaseModel):
    token: str


class TokenAndRefresh(BaseModel):
    token: str
    refresh_token: str


class BackendUser(BaseModel):

    id: int
    createdAt: str
    updatedAt: str
    email: EmailStr
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
