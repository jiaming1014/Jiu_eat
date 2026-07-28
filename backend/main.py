from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import activities, applications, auth, members, recommendations

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jiu-Eat API", version="1.1.0")
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(activities.router)
app.include_router(applications.router)
app.include_router(recommendations.router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def frontend_home():
    return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", reload=True)
