
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse

from app import database, security
from app.schemas import ErrorResponse, TokenResponse, UserCreate, UserOut

router = APIRouter()

bearer = HTTPBearer(auto_error=False)

auth_errors = {
    400: {"model": ErrorResponse, "description": "Email уже занят"},
    401: {"model": ErrorResponse, "description": "Неверные данные или токен"},
}


def _token_response(user_id: int, email: str) -> dict:
    return {
        "access_token": security.create_token(user_id, email),
        "token_type": "bearer",
        "user": {"id": user_id, "email": email},
    }


@router.post("/auth/register", response_model=TokenResponse, responses=auth_errors)
def register(payload: UserCreate):
    """Регистрация: создаёт пользователя и сразу возвращает токен"""
    with database.get_connection() as conn:
        already = conn.execute(
            "SELECT id FROM users WHERE email = ?", (payload.email,)
        ).fetchone()
        if already:
            return JSONResponse(
                status_code=400,
                content={"message": "Пользователь с таким email уже зарегистрирован"},
            )
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (payload.email, security.hash_password(payload.password)),
        )
        user_id = cursor.lastrowid

    return _token_response(user_id, payload.email)


@router.post("/auth/login", response_model=TokenResponse, responses=auth_errors)
def login(payload: UserCreate):
    """Вход по email и паролю, возвращает токен"""
    with database.get_connection() as conn:
        user = conn.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (payload.email,),
        ).fetchone()

    if user is None or not security.verify_password(payload.password, user["password_hash"]):
        return JSONResponse(
            status_code=401,
            content={"message": "Неверный email или пароль"},
        )

    return _token_response(user["id"], user["email"])


@router.get("/auth/me", response_model=UserOut, responses=auth_errors)
def me(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    """Данные текущего пользователя по его токену"""
    if credentials is None:
        return JSONResponse(
            status_code=401,
            content={"message": "Нужен заголовок Authorization: Bearer <токен>"},
        )

    payload = security.decode_token(credentials.credentials)
    if payload is None:
        return JSONResponse(
            status_code=401,
            content={"message": "Токен недействителен или истёк — войдите заново"},
        )

    with database.get_connection() as conn:
        user = conn.execute(
            "SELECT id, email FROM users WHERE id = ?", (int(payload["sub"]),)
        ).fetchone()

    if user is None:
        return JSONResponse(
            status_code=401,
            content={"message": "Пользователь не найден — войдите заново"},
        )

    return {"id": user["id"], "email": user["email"]}
