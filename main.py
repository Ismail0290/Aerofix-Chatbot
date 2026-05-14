import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.logs import router as logs_router
from routes.analytics import router as analytics_router
from routes.context import router as context_router
from routes.priority import router as priority_router
from routes.devices import router as devices_router
from routes.chat import router as chat_router

app = FastAPI(
    title="AeroFix AI Backend"
)

_cors_extra = os.getenv("CORS_EXTRA_ORIGINS", "")
_extra_origins = [o.strip() for o in _cors_extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        *_extra_origins,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs_router)
app.include_router(analytics_router)
app.include_router(context_router)
app.include_router(priority_router)
app.include_router(devices_router)
app.include_router(chat_router)


@app.get("/")
def home():

    return {
        "message": "AeroFix Backend Running"
    }