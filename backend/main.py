from fastapi import FastAPI

from routes.auth import router

app=FastAPI()
app.include_router(router)
@app.get("/")
def root():
    return {"message":"Zenscribe Backend is running"}
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}