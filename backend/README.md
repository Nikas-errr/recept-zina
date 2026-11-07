# Recept_zina — backend

Подбор рецептов по продуктам: пользователь выбирает, что лежит в холодильнике
(`refrigerator`) или в шкафу (`wardrobe`), указывает нежелательные продукты
(аллергены) и получает рецепты из [TheMealDB](https://www.themealdb.com).

## Стек

- Python 3.11+
- FastAPI + Pydantic v2
- requests — запросы к TheMealDB
- Uvicorn — сервер
- pytest — тесты

## Структура

```
backend/
├── app/
│   ├── main.py             # собирает приложение: FastAPI, CORS, роутеры
│   ├── config.py           # все настройки в одном месте + чтение .env
│   ├── schemas.py          # Pydantic-модели: форма входных и выходных данных
│   ├── routers/
│   │   ├── health.py       # GET  /api/health
│   │   ├── ingredients.py  # GET  /api/ingredients
│   │   └── recipes.py      # POST /api/recipes/search
│   └── services/
│       ├── mealdb.py       # только запросы к TheMealDB
│       └── recipe_logic.py # очистка, сравнение, avoid-фильтр, шаги инструкции
├── data/
│   └── ingredients.json    # каталог продуктов (локальный файл, без БД)
├── tests/                  # pytest-тесты (работают без интернета)
├── requirements.txt        # список библиотек
├── .env.example            # шаблон настроек; настоящий .env в git не попадает
└── .gitignore
```

## Запуск

Команды выполнять из папки `backend`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> Если работаешь в Git Bash, активация такая: `source .venv/Scripts/activate`

После запуска открой интерактивную документацию:
**http://127.0.0.1:8000/docs** — там можно вызывать все endpoint-ы кнопкой
«Try it out», без curl и без фронтенда.

## Примеры запросов и ответов

### 1. Каталог продуктов

```
GET http://127.0.0.1:8000/api/ingredients?furnitureType=refrigerator&search=мол
```

- `furnitureType` **необязателен**: `refrigerator`, `wardrobe` или `oven`
  (пока пустая). Без параметра вернётся весь каталог — удобно, если нужно
  показывать все продукты сразу.
- `search` **необязателен**: регистронезависимый поиск по имени и slug.
  Подходит для подсказок при вводе: сначала совпадения с начала слова
  («мо» → Молоко, Морковь, Моцарелла), потом совпадения в середине
  («лимон»), внутри групп — по алфавиту.

Ответ:

```json
{
  "data": [
    {
      "slug": "milk",
      "name": "Молоко",
      "image": "https://www.themealdb.com/images/ingredients/Milk.png"
    }
  ]
}
```

### 2. Поиск рецептов

```
POST http://127.0.0.1:8000/api/recipes/search
Content-Type: application/json
```

Тело запроса (slug-и брать из каталога, максимум 4 продукта):

```json
{
  "ingredients": ["chicken-breast", "garlic"],
  "avoid": ["milk"]
}
```

Успешный ответ:

```json
{
  "recipes": [
    {
      "id": "52772",
      "title": "Название блюда",
      "imageUrl": "https://www.themealdb.com/images/media/meals/...",
      "ingredients": [
        { "name": "Chicken Breast", "amount": "500g" }
      ],
      "steps": ["Шаг 1", "Шаг 2"]
    }
  ],
  "count": 1,
  "message": "ok"
}
```

Если подходящих рецептов нет — код всё равно 200, но список пустой:

```json
{ "recipes": [], "count": 0, "message": "Подходящие рецепты не найдены" }
```

### 3. Ошибки

Неизвестный продукт — HTTP 400:

```json
{ "message": "Неизвестные продукты: unicorn-meat. Полный список смотрите в GET /api/ingredients." }
```

TheMealDB недоступен — HTTP 503:

```json
{ "message": "Сервис рецептов временно недоступен, попробуйте позже" }
```

Ошибки валидации (пустой `ingredients`, больше 4 продуктов, неверный
`furnitureType`, нестроковые значения) FastAPI проверяет сам и возвращает
стандартный ответ с кодом HTTP 422.

## Тесты

Из папки `backend`:

```bash
python -m pytest
python -m pytest -v   # подробный вывод: список всех тестов
```

Тесты не ходят в интернет: они проверяют `/api/health`, каталог ингредиентов,
правила валидации и функции `recipe_logic`.

## CORS: что поменять перед публикацией

Сейчас в `app/main.py` стоит `allow_origins=["*"]` — «разрешено всем».
Для разработки это нормально, но перед публикацией замени `*` на точный
адрес фронтенда, например:

```python
allow_origins=["http://localhost:5173"]
```

(можно перечислить несколько адресов списком). Если этого не сделать,
любой сайт сможет отправлять запросы к твоему API от имени посетителей.

## Безопасность

- В коде нет ключей и паролей. Если появится ключ TheMealDB — он кладётся
  в `.env` (копия `.env.example`) и читается в `config.py` через
  переменную окружения.
- `.env` добавлен в `.gitignore` и в репозиторий не попадёт.
- Адрес TheMealDB вынесен в настройки, а не «вшит» в код запросов.

## Авторизация

Исходное ТЗ запрещало авторизацию и базу — она появилась по решению
команды: фронтенд (Next.js + NextAuth) уже отправляет email и пароль.
Пользователи хранятся в SQLite-файле `data/users.db`, пароли — только
в виде хешей, вход — по JWT-токену (неделя).

Адреса (префикс `/api`, для фронта baseURL = `http://127.0.0.1:8000/api`):

| Метод | Адрес | Тело | Ответ |
|---|---|---|---|
| POST | `/api/auth/register` | `{"email": "...", "password": "..."}` | токен + пользователь (400 — email занят) |
| POST | `/api/auth/login` | то же | токен + пользователь (401 — неверные данные) |
| GET | `/api/auth/me` | — | пользователь по токену (401 — токена нет/истёк) |

Пример:

```json
POST http://127.0.0.1:8000/api/auth/register
{ "email": "vasya@mail.ru", "password": "super-secret-123" }

{
  "access_token": "eyJhbGciOi... ",
  "token_type": "bearer",
  "user": { "id": 1, "email": "vasya@mail.ru" }
}
```

Дальше каждый защищённый запрос сопровождается заголовком:

```
Authorization: Bearer <access_token>
```

Перед публикацией обязательно задать свой `AUTH_SECRET` в `.env`
(шаблон — в `.env.example`; на Render — переменная окружения из
`render.yaml`). Иначе кто угодно сможет подделывать токены.

## Загрузка на GitHub и публичный URL

Код разбит на модули — так требует ТЗ («Не делай всё в одном main.py»).
GitHub и хостингу количество файлов не важно: они работают с папкой целиком.
Файл `render.yaml` в корне проекта описывает, как поднять сайт на Render.

### 1. Загрузить на GitHub

Из папки `recept-zina`:

```bash
git add .
git commit -m "Backend Recept_zina: модульный FastAPI-проект по ТЗ"
git branch -M main
git remote add origin https://github.com/Nikas-errr/recept-zina.git
git push -u origin main
```

(Сначала создай пустой репозиторий `recept-zina` на github.com без README.)

### 2. Публичный URL через Render

1. Зайди на [render.com](https://render.com) → **New +** → **Blueprint**
   → выбери репозиторий `recept-zina`.
2. Render сам прочитает `render.yaml` и создаст сервис — ничего заполнять
   не нужно.
3. Через пару минут появится адрес вида
   `https://recept-zina.onrender.com`.

Проверка после деплоя: открой `https://…/api/health` — должно быть
`{"status": "ok"}`.

Нюансы бесплатного тарифа:

- сервис «засыпает» без трафика: первый запрос может идти ~50 секунд,
  следующие — быстро;
- когда появится фронтенд на другом адресе, в `app/main.py` заменят
  `allow_origins=["*"]` на адрес фронтенда (см. раздел CORS выше).
