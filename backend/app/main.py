
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.routers import auth, health, ingredients, recipes

app = FastAPI(
    title="Recept_zina",
    description="Подбор рецептов по продуктам из холодильника и шкафа с учётом аллергий",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

database.init_db()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
