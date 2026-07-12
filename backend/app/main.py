from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import get_db
from app.core.redis import close_redis
from app.api.v1.router import api_router
from app.core.response import add_code_wrapper 
from app.api.admin.router import admin_router
from app.tasks import create_scheduler
from app.core.exceptions import api_exception_handler, api_other_exception_handler
from fastapi.responses import JSONResponse

app = FastAPI(title="Mall API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(add_code_wrapper)

# 注册全局异常处理器
app.add_exception_handler(HTTPException, api_exception_handler)

app.add_exception_handler(Exception, api_other_exception_handler)

app.include_router(api_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/admin")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown():
    await close_redis()


scheduler = create_scheduler()

@app.on_event("startup")
async def startup():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()
