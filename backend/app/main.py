from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db_init import init_db
from app.api import routes

app = FastAPI(
    title="GILOS - 全球智能获客操作系统",
    description="Global Intelligence Lead Acquisition OS",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(routes.router, prefix="/api/v1", tags=["core"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "gilos-backend"}
