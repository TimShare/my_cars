from typing import List
from uuid import UUID
from pydantic import BaseModel, Field


class ScopesRequest(BaseModel):
    scopes: List[str] = Field(..., description="Список прав доступа")

class ScopesResponse(BaseModel):
    scopes: List[str] = Field(..., description="Список прав доступа")
    user_id: UUID = Field(..., description="ID пользователя")