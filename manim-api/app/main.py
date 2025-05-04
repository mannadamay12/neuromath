import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import videos

app = FastAPI(
    title="Manim Video Generator API",
    description="API for generating educational math videos using Manim and AI",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

media_dir = os.getenv("MEDIA_DIR", "media")
os.makedirs(media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_dir), name="media")

# Register routers
app.include_router(videos.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Manim Video Generator API"}