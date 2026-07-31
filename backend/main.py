"""FastAPI 應用程式主入口"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import activities, applications, auth, members, recommendations

# 自動建立資料表（若不存在）
models.Base.metadata.create_all(bind=engine)

# 建立 FastAPI 應用程式實例
app = FastAPI(title="Jiu-Eat API", version="1.1.0")

# 設定 CORS（允許所有來源，方便開發測試）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 API 路由
app.include_router(auth.router)               # 認證相關（登入/登出/註冊）
app.include_router(members.router)            # 會員資料
app.include_router(activities.router)         # 活動管理
app.include_router(applications.router)       # 活動申請
app.include_router(recommendations.router)    # 推薦系統

# 前端靜態檔案目錄
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/api/health", tags=["system"])
def health():
    """健康檢查端點，回傳 API 是否正常運作"""
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend_home():
    """首頁：回傳前端 index.html"""
    return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", reload=True)
