from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column

class Flow(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    data: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    status: int = 1  # 1: offline, 2: online
    logo: Optional[str] = None
    update_time: Optional[str] = None
    create_time: Optional[str] = None
    user_id: Optional[str] = None

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
