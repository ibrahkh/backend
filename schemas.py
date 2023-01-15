from typing import List, Optional
from pydantic import BaseModel
from datetime import date


class Clothes(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    image: Optional[str] = None
    weather: Optional[str] = None
    owner_id:int 
    category_id: int | None = None
    class Config:
        orm_mode = True


class Events(BaseModel):
    name: Optional[str] = None
    date: date
    owner_id:int 

    class Config:
        orm_mode = True

class Events_create(BaseModel):
    name: Optional[str] = None
    date: date

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int | None = None
    username:str
    email:str
    hashed_password:str
    birth_date:date
    sexe:str
    wardrobe: list[Clothes] = []
    image: Optional[str] = None
    disabled: bool | None = None

    class Config:
        orm_mode = True


class User_id(BaseModel):
    id: int | None = None

    class Config:
        orm_mode = True


class Event_id(BaseModel):
    id: int | None = None

    class Config:
        orm_mode = True


class Event_User(BaseModel):
    id: int
    event: list[Events] = []
    
    class Config:
        orm_mode = True

class ShowUser(BaseModel):
    username:str
    email:str
    sexe:str
    age:int
    image: Optional[str] = None
    class Config():
        orm_mode = True


    

class User_image(BaseModel):
    username:str
    image:Optional[str] = None
    class Config():
        orm_mode = True


class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None

class user_login(BaseModel):
    username: str
    password : str



class CategoryBase(BaseModel):
    name: str
class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    items: List[Clothes] = []

    class Config:
        orm_mode = True


class ShowItems(BaseModel):
    items: List[Clothes] = []

    class Config:
        orm_mode = True

