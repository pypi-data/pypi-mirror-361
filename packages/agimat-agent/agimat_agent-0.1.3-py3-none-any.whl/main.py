from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.agent import router as api_router
import uvicorn
import logging

# 加载环境变量
from lib.env_loader import load_agimat_env

load_agimat_env()


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AGI-MAT Agent Management Platform",
        description="AGI-MAT Agent Management Platform",
        version="1.0.0",
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册API路由
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "Welcome to AGI-MAT Agent Management Platform"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
