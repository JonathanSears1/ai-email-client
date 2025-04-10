from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from auth import router as auth_router

load_dotenv()

app = FastAPI()
app.include_router(auth_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(
        app = "main:app",
        host = "localhost",
        port = 8000,
        reload = True,
    )