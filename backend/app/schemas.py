"""Pydantic-модели — «формы» данных.

Каждая модель описывает, как выглядят данные на входе или на выходе API.
FastAPI по этим моделям сам проверяет данные (и сам отдаёт ошибку 422,
если форма заполнена неправильно) и сам рисует документацию /docs.
"""

from pydantic import BaseModel, Field, field_validator

from app.services.recipe_logic import clean_slug_list


class IngredientItem(BaseModel):
    """Один ингредиент каталога в ответе API."""

    slug: str
    name: str
    image: str | None = None


class IngredientsResponse(BaseModel):
    """Ответ GET /api/ingredients."""

    data: list[IngredientItem]


class RecipeSearchRequest(BaseModel):
    """Тело запроса POST /api/recipes/search."""

    ingredients: list[str] = Field(
        min_length=1,
        max_length=4,
        description="От 1 до 4 slug-ов продуктов из каталога",
    )
    avoid: list[str] = Field(
        default_factory=list,
        description="Slug-ы продуктов, которые нужно исключить (аллергии)",
    )

    @field_validator("ingredients", "avoid", mode="before")
    @classmethod
    def clean_lists(cls, value):
        """Убирает пробелы, пустые строки и дубли ещё до остальных проверок."""
        return clean_slug_list(value)


class RecipeIngredientItem(BaseModel):
    """Ингредиент внутри рецепта: название и количество."""

    name: str
    amount: str


class RecipeItem(BaseModel):
    """Один рецепт в ответе."""

    id: str
    title: str
    imageUrl: str | None = None
    ingredients: list[RecipeIngredientItem]
    steps: list[str]


class RecipeSearchResponse(BaseModel):
    """Ответ POST /api/recipes/search."""

    recipes: list[RecipeItem]
    count: int
    message: str


class ErrorResponse(BaseModel):
    """Понятная ошибка вместо traceback — используется для кодов 400 и 503."""

    message: str


class UserCreate(BaseModel):
    """Тело запроса на регистрацию и вход (email + пароль)."""

    email: str = Field(description="Электронная почта, например name@mail.ru")
    password: str = Field(min_length=8, description="Минимум 8 символов")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Убираем пробелы и приводим к нижнему регистру, чтобы
        «Vasya@Mail.RU» и «vasya@mail.ru» были одним пользователем."""
        email = value.strip().lower()
        if " " in email or "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Похоже, это не электронная почта")
        return email


class UserOut(BaseModel):
    """Данные пользователя, которые можно показывать (без пароля!)."""

    id: int
    email: str


class TokenResponse(BaseModel):
    """Ответ на регистрацию и вход: JWT-токен + данные пользователя.

    Фронтенд ждёт именно access_token (NextAuth, LoginResponse).
    """

    access_token: str
    token_type: str = "bearer"
    user: UserOut
