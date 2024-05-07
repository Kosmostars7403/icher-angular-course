from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from application.account.routers.auth_router import router as auth_router
from application.account.routers.user_router import router as user_router

app = FastAPI(
    title='AngularCourse'
)


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
