from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.models import VideoRequest, VideoResponse
from app.services.video_generator import generate_math_video
import uuid
import os

router = APIRouter(
    prefix="/api/videos",
    tags=["videos"],
)

# In-memory storage for job status (replace with a database in production)
video_jobs = {}

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Generate a math educational video with Manim
    """
    video_id = str(uuid.uuid4())
    
    # Initialize job status
    video_jobs[video_id] = {
        "status": "queued",
        "video_url": None,
        "message": "Video generation has been queued"
    }
    
    # Start the video generation in the background
    background_tasks.add_task(
        process_video_generation,
        video_id,
        request.math_problem,
        request.audience_age,
        request.language.value,
        request.voice_label
    )
    
    return VideoResponse(
        video_id=video_id,
        video_url=f"/api/videos/{video_id}",
        status="queued",
        message="Video generation has been queued"
    )

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video_status(video_id: str):
    """
    Get the status of a video generation job
    """
    if video_id not in video_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video job not found"
        )
    
    job = video_jobs[video_id]
    
    return VideoResponse(
        video_id=video_id,
        video_url=job.get("video_url", f"/api/videos/{video_id}"),
        status=job["status"],
        message=job["message"]
    )

@router.get("/{video_id}/download")
async def download_video(video_id: str):
    """
    Download the generated video
    """
    if video_id not in video_jobs or video_jobs[video_id]["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or not completed yet"
        )
    
    # In a real implementation, return the video file
    # This is a placeholder
    return {"url": video_jobs[video_id]["video_url"]}

async def process_video_generation(video_id: str, math_problem: str, audience_age: str, language: str, voice_label: str):
    """
    Process the video generation in the background
    """
    try:
        video_jobs[video_id]["status"] = "processing"
        video_jobs[video_id]["message"] = "Video generation in progress"
        
        # Call your video generation service
        result = generate_math_video(math_problem, audience_age, language, voice_label)
        
        # Update job status with the result
        video_jobs[video_id]["status"] = "completed"
        video_jobs[video_id]["video_url"] = result["video_url"]
        video_jobs[video_id]["message"] = "Video generation completed successfully"
        
    except Exception as e:
        video_jobs[video_id]["status"] = "failed"
        video_jobs[video_id]["message"] = f"Video generation failed: {str(e)}"