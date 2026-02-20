from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Beauty Salon")

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
