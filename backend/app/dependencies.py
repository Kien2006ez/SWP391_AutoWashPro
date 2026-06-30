from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def require_admin(token: str = Depends(oauth2_scheme)):
    return {"role": "admin"}