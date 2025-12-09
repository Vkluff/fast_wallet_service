from pydantic import EmailStr
from schemas.common import ORMBase

class Token(ORMBase):
    access_token: str
    token_type: str = "bearer"

class TokenData(ORMBase):
    user_id: str | None = None
    email: EmailStr | None = None
