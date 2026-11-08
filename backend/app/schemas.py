
from pydantic import BaseModel, Field, field_validator

from app.services.recipe_logic import clean_slug_list


class IngredientItem(BaseModel):
    slug: str
    name: str
    image: str | None = None


class IngredientsResponse(BaseModel):
    data: list[IngredientItem]


class RecipeSearchRequest(BaseModel):
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
        return clean_slug_list(value)


class RecipeIngredientItem(BaseModel):
    name: str
    amount: str


class RecipeItem(BaseModel):
    id: str
    title: str
    imageUrl: str | None = None
    ingredients: list[RecipeIngredientItem]
    steps: list[str]


class RecipeSearchResponse(BaseModel):
    recipes: list[RecipeItem]
    count: int
    message: str


class ErrorResponse(BaseModel):
    message: str


class UserCreate(BaseModel):
    email: str = Field(description="Электронная почта, например name@mail.ru")
    password: str = Field(min_length=8, description="Минимум 8 символов")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        email = value.strip().lower()
        if " " in email or "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Похоже, это не электронная почта")
        return email


class UserOut(BaseModel):
    id: int
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
