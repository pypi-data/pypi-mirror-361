from typing import Optional
from django.http import HttpRequest

from nkunyim_util.models.session_model import SessionModel



class HttpSession:
    def __init__(self, req: HttpRequest) -> None:
        self.req = req
    
    def _key(self) -> str:
        parts = self.req.get_host().lower().split('.')
        if len(parts) >= 2:
            domain = '.'.join(parts[-2:])
            subdomain = parts[-3] if len(parts) > 2 else "www"
            return f"{subdomain}.{domain}"
        return "www.localhost"
    
    def set(self, model: SessionModel) -> None:
        self.req.session[self._key()] = model.model_dump()
        self.req.session.modified = True
        
    def get(self) -> Optional[SessionModel]:
        key = self._key()
        if not bool(key in self.req.session):
            return None

        session = self.req.session[key]
        return SessionModel(**session)
    
    def kill(self) -> None:
        self.req.session.clear()
        self.req.session.flush()
        

