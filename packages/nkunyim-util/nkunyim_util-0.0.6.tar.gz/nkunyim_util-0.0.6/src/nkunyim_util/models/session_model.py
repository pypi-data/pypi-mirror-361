from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class XanModel(BaseModel):
    client_id: str
    nation_code: str
    service_name: Optional[str]
    is_authenticated: bool
    
    
class TokenModel(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime


class SessionModel(BaseModel):
    token: Optional[TokenModel]
    xan: Optional[XanModel]