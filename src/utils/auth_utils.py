from fastapi import Header, HTTPException, status

def get_bearer_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó un Bearer Token válido"
        )
    return authorization.split(" ")[1]
