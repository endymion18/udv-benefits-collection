from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.admin.router import router as admin_router
from src.benefits.router import router as benefits_router

app = FastAPI(
    title="UDV Benefits API"
)


@app.get("/ping",
         status_code=200)
async def ping():
    return {"success": "pong"}

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(benefits_router)

