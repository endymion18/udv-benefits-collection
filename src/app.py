from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from src.auth.router import router as auth_router
from src.admin.router import router as admin_router
from src.benefits.router import router as benefits_router
from src.analitycs.router import router as analytics_router

app = FastAPI(
    title="UDV Benefits API"
)

origins = [
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "localhost:8000",
    "http://localhost:5173",
    "https://udv-urfu.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping",
         status_code=200)
async def ping():
    return {"success": "pong"}


@app.get("/logo")
async def get_logo():
    return FileResponse("./static/logo.png")

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(benefits_router)
app.include_router(analytics_router)
