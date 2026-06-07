from fastapi import APIRouter, Depends, HTTPException, status, Request
from api.schemas.auth_schemas import LoginRequest, TokenResponse
from application.auth.use_cases import LoginUseCase
from api.v1.deps import get_login_use_case
from core.exceptions import CredenciaisInvalidasError
import time

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Dicionário em memória para rate limiting: {ip_address: [timestamps]}
_RATE_LIMIT = {}
MAX_ATTEMPTS_PER_MINUTE = 5

def check_rate_limit(request: Request):
    # Only bypass for the internal TestClient (not from headers)
    if request.client and request.client.host == "testclient":
        return

    # [Security Fix] Previne bypass do Rate Limit via spoofing do header X-Forwarded-For.
    # O X-Forwarded-For pode conter uma lista de IPs (ex: "spoofed_ip, real_ip").
    # Pegamos sempre o último IP da lista, que é o IP real adicionado pelo proxy reverso,
    # suportando ambientes de nuvem/docker onde o proxy não é necessariamente localhost.
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[-1].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    now = time.time()

    # Limpa tentativas mais antigas que 60 segundos
    if client_ip in _RATE_LIMIT:
        _RATE_LIMIT[client_ip] = [t for t in _RATE_LIMIT[client_ip] if now - t < 60]
    else:
        _RATE_LIMIT[client_ip] = []

    if len(_RATE_LIMIT[client_ip]) >= MAX_ATTEMPTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Tente novamente em 1 minuto."
        )

    _RATE_LIMIT[client_ip].append(now)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case)
):
    # Aplica o Rate Limiting na rota de login
    check_rate_limit(request)

    import re
    telefone_normalizado = re.sub(r'\D', '', payload.telefone) if payload.telefone else payload.telefone

    try:
        token = await use_case.executar(telefone_normalizado, payload.senha)
        return {"access_token": token, "token_type": "bearer"}
    except CredenciaisInvalidasError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)
