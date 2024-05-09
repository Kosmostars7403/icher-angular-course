from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from application.account.routers.auth_router import router as auth_router
from application.account.routers.user_router import router as user_router
from application.personal_chat.router import router as personal_router
from application.message.router import router as message_router
from fastapi_pagination import add_pagination


app = FastAPI(
    title='AngularCourse'
)
add_pagination(app)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(personal_router)
app.include_router(message_router)
