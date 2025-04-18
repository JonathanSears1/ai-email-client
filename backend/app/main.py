from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from auth import router as auth_router
from gmail import router as gmail_router
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.include_router(auth_router, prefix="/api/auth")
app.include_router(gmail_router, prefix="/api/gmail")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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