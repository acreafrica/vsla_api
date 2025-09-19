from typing import List, Optional

from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True
class HubBase(BaseModel):
    hub_mode:str
    hub_challenge:int
    hub_verify_token:str

class Hub(HubBase):
    id:int
    
    class Config:
        orm_mode = True