import uuid
import os
import subprocess
import glob
import re
import time
from app.services.ai_services import generate_manim_code, improve_video_with_ai
from pathlib import Path

def generate_math_video(math_problem, audience_age, language="English", voice_label="en-US-AriaNeural"):
    """
    Generate a math educational video using Manim and AI
    
    Returns dict with video details
    """
    # Format audience age
    if str(audience_age).isdigit():
        audience_age = f"{audience_age} year old"
    
    # Generate initial Manim code using AI
    initial_code = generate_manim_code(math_problem, audience_age, language, voice_label)
    
    # Create a unique ID for this video
    video_id = f"MathMovie_{uuid.uuid4().hex[:8]}"
    
    # Save the Manim code to a file
    with open(f"{video_id}.py", 'w') as file:
        file.write(initial_code)
    
    # Run Manim to generate the video
    manim_bin = os.getenv('MANIM_BIN', 'manim')
    command = f"{manim_bin} -ql {video_id}.py --disable_caching"
    
    max_attempts = 8
    for attempt in range(max_attempts):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            break
        
        if attempt < max_attempts - 1:
            # If failed, try to fix the code with AI
            error_message = result.stderr
            fixed_code = generate_manim_code(
                math_problem, 
                audience_age, 
                language, 
                voice_label, 
                error_message=error_message
            )
            
            with open(f"{video_id}.py", 'w') as file:
                file.write(fixed_code)
        else:
            raise Exception(f"Failed to generate video after {max_attempts} attempts")
    
    # Find the generated video file
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    path_pattern = os.path.join(current_script_dir, f"../../../media/videos/{video_id}/480p15/*.mp4")
    mp4_files = glob.glob(path_pattern)
    
    if not mp4_files:
        raise Exception("Video file not found after successful Manim execution")
    
    video_file_path = mp4_files[0]
    
    # Extract frames for AI improvement (optional in API version)
    # This part can be simplified or removed if not needed
    frame_extraction_directory = Path(current_script_dir) / f"../../../media/frames/{video_id}/"
    frame_extraction_directory.mkdir(parents=True, exist_ok=True)
    
    # Extract key frames
    extract_frames(video_file_path, frame_extraction_directory)
    
    # Improve the video with AI feedback
    improved_code = improve_video_with_ai(
        initial_code, 
        frame_extraction_directory, 
        math_problem, 
        audience_age
    )
    
    # Generate the final improved video
    with open(f"{video_id}_improved.py", 'w') as file:
        file.write(improved_code)
    
    command = f"{manim_bin} -ql {video_id}_improved.py --disable_caching"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        # If improved version fails, use the original
        return {
            "video_id": video_id,
            "video_path": video_file_path,
            "video_url": f"/media/videos/{video_id}/480p15/{os.path.basename(video_file_path)}"
        }
    
    # Find the improved video file
    path_pattern = os.path.join(current_script_dir, f"../../../media/videos/{video_id}_improved/480p15/*.mp4")
    improved_mp4_files = glob.glob(path_pattern)
    
    final_video_path = improved_mp4_files[0] if improved_mp4_files else video_file_path

    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    relative_path = f"/media/videos/{os.path.basename(os.path.dirname(os.path.dirname(final_video_path)))}/480p15/{os.path.basename(final_video_path)}"
    
    return {
        "video_id": video_id,
        "video_path": final_video_path,
        "video_url": f"{base_url}{relative_path}"
    }

def extract_frames(video_file_path, output_dir, max_frames=60):
    """Extract frames from a video file for AI analysis"""
    import cv2
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the video
    vidcap = cv2.VideoCapture(video_file_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    
    # Calculate frame extraction rate
    if duration <= 60:
        frame_extraction_rate = 1  # 1 fps for videos under 60 seconds
    else:
        frame_extraction_rate = max(1, int(total_frames / max_frames))
    
    # Extract frames
    output_file_prefix = os.path.basename(video_file_path).replace('.', '_')
    frame_count = 0
    count = 0
    
    while vidcap.isOpened():
        success, frame = vidcap.read()
        if not success:
            break
            
        if count % frame_extraction_rate == 0:
            # Calculate timestamp
            time_in_seconds = count / fps
            min = int(time_in_seconds // 60)
            sec = int(time_in_seconds % 60)
            time_string = f"{min:02d}:{sec:02d}"
            
            # Save frame
            image_name = f"{output_file_prefix}_frame{time_string}.jpg"
            output_filename = os.path.join(output_dir, image_name)
            cv2.imwrite(output_filename, frame)
            frame_count += 1
            
        count += 1
        
    vidcap.release()
    
    return {
        "video_duration": duration,
        "frame_count": frame_count,
        "frame_extraction_rate": frame_extraction_rate
    }