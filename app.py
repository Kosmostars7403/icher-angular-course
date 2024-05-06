from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from application.account.router import router as account_router

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

app.include_router(account_router)



