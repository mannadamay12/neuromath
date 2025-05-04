import json
import os
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.models import VideoRequest, VideoResponse
from app.services.video_generator import generate_math_video
import uuid
import os

router = APIRouter(
    prefix="/api/videos",
    tags=["videos"],
)

# Create a function to save and load jobs
def save_jobs():
    jobs_dir = Path("jobs")
    jobs_dir.mkdir(exist_ok=True)
    
    with open(jobs_dir / "jobs.json", "w") as f:
        # Convert any non-serializable items to strings
        serializable_jobs = {}
        for job_id, job in video_jobs.items():
            serializable_jobs[job_id] = {
                "status": job["status"],
                "video_url": job.get("video_url", ""),
                "message": job.get("message", "")
            }
        json.dump(serializable_jobs, f)

def load_jobs():
    jobs_dir = Path("jobs")
    jobs_file = jobs_dir / "jobs.json"
    
    if jobs_file.exists():
        with open(jobs_file, "r") as f:
            return json.load(f)
    return {}

# Initialize video_jobs from file
video_jobs = load_jobs()


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
    
    # Save jobs to file
    save_jobs()
    
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
    
    # Ensure video_url is never None
    video_url = job.get("video_url") or f"/api/videos/{video_id}"
    
    return VideoResponse(
        video_id=video_id,
        video_url=video_url,
        status=job["status"],
        message=job.get("message", "Video generation in progress")
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
        save_jobs()  # Save after update
        
        # Call your video generation service
        result = generate_math_video(math_problem, audience_age, language, voice_label)
        
        # Update job status with the result
        video_jobs[video_id]["status"] = "completed"
        video_jobs[video_id]["video_url"] = result["video_url"]
        video_jobs[video_id]["message"] = "Video generation completed successfully"
        save_jobs()  # Save after update
        
    except Exception as e:
        video_jobs[video_id]["status"] = "failed"
        video_jobs[video_id]["message"] = f"Video generation failed: {str(e)}"
        save_jobs()  # Save after update


@router.get("/{video_id}/play")
async def play_video(video_id: str):
    """
    Stream the generated video
    """
    from fastapi.responses import FileResponse
    
    if video_id not in video_jobs or video_jobs[video_id]["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or not completed yet"
        )
    
    # Get the physical path to the video file
    job = video_jobs[video_id]
    video_path = job.get("video_path")  # You'd need to store this in your job data
    
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found"
        )
    
    return FileResponse(video_path, media_type="video/mp4")