from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas.auth_schemas import LoginRequest, TokenResponse
from application.auth.use_cases import LoginUseCase
from api.v1.deps import get_login_use_case
from core.exceptions import CredenciaisInvalidasError

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case)
):
    try:
        token = await use_case.executar(payload.telefone, payload.senha)
        return {"access_token": token, "token_type": "bearer"}
    except CredenciaisInvalidasError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)
