from pydantic import BaseModel

class UserDto(BaseModel):
    username: str
    password: str

class NewsDto(BaseModel):
    author: str
    title: str
    urlToImage: str
    category: str = ""
    user_id: int

class TokenDto(BaseModel):
    access_token: str
    token_type: str

class TokenDataDto(BaseModel):
    username: str = None