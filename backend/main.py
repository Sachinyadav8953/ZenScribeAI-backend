from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes.auth import router as auth_router
from db.session import init_db
from routes.consultation import router as consultation_router
from routes.audio import router as audio_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(consultation_router)
app.include_router(audio_router)
@app.get("/")
def root():
    return {"message":"Zenscribe Backend is running"}
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}