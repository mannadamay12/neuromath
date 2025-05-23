import time
import json
import glob
import subprocess
import uuid
import argparse
import re
import os
import cv2
import shutil
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


def extract_code_blocks(text):
    # Regular expression pattern to find code blocks surrounded by triple backticks
    pattern = r"```python(.*?)```"

    # Using re.DOTALL to make the dot match newlines as well
    matches = re.findall(pattern, text, re.DOTALL)

    # 'matches' will be a list of all the code blocks found in the text
    return matches


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a math movie based on the given problem, audience age, and language."
    )
    parser.add_argument("--math_problem", type=str, default="Explain the pythagorean theorem",
                        help="The math problem to be visualized in the movie.")
    parser.add_argument("--audience_type", type=int, default=10,
                        help="The target audience age for the math movie.")
    parser.add_argument("--language", type=str, default="English",
                        help="The language for the movie narration (default is English).")
    parser.add_argument("--voice_label", type=str, default="en-US-AriaNeural",
                        help="The voice label for the narration (default is en-US-AriaNeural).")
    args = parser.parse_args()
    return args.math_problem, args.audience_type, args.language, args.voice_label


def main():
    # math_problem, audience_type, language, voice_label = parse_arguments()
    print(f"Math Problem: {math_problem}")
    print(f"Audience Type: {audience_type}")
    print(f"Language: {language}")
    print(f"Voice Label: {voice_label}")


MOVIE_PROMPT = """

Can you explain {math_problem} to a {audience_type}? Please be visual and interesting. Consider using a meme if the audience is younger.

Please create python code for a manim video for the same. 

Please do not use any external dependencies like mp3s or svgs or graphics. Do not create any sound effects. 

If you need to draw something, do so using exclusively manim. Always add a title and an outro. Narrate the title and outro.

Please try to visually center or attractively lay out all content. Please also keep the margins in consideration. If a sentence is long please wrap it by splitting it into multiple lines. 

Please add actual numbers and formulae wherever appropriate as we want our audience of {audience_type} to learn math.

Do use voiceovers to narrate the video. The following is an example of how to do that:

```
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService


class AzureExample(VoiceoverScene):
    def construct(self):
        self.set_speech_service(
            AzureService(
                voice="en-US-AriaNeural",
                style="newscast-casual",
                global_speed=1.15
            )
        )

        circle = Circle()
        square = Square().shift(2 * RIGHT)

        with self.voiceover(text="This circle is drawn as I speak.") as tracker:
            self.play(Create(circle), run_time=tracker.duration)

        with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
            self.play(circle.animate.shift(2 * LEFT),
                      run_time=tracker.duration)

        with self.voiceover(text="Now, let's transform it into a square.") as tracker:
            self.play(Transform(circle, square), run_time=tracker.duration)

        with self.voiceover(
            text="You can also change the pitch of my voice like this.",
            prosody={{"pitch": "+40Hz"}},
        ) as tracker:
            pass

        with self.voiceover(text="Thank you for watching."):
            self.play(Uncreate(circle))

        self.wait()
```

The voice for the "{language}" is "{voice_label}". Please use this voice for the narration. 

Please do not use any external dependencies like svgs or mp3s or grpahics since they are not available. Draw with shapes and use colored letters, but keep it simple. There are no external assets. Constraints are liberating. 

First write the script explicitly and refine the contents and then write the code.

Please draw and animate things, using the whole canvas. Use color in a restrained but elegant way, for educational purposes.

Please add actual numbers and formulae wherever appropriate as we want our audience of {audience_type} to learn math. Please do not leave large blank gaps in the video. Make it visual and interesting. PLEASE ENSURE ELEMENTS FADE OUT AT THE APPROPRIATE TIME. DO NOT LEAVE ARTIFACTS ACROSS SCENES AS THEY OVERLAP AND ARE JARRING. WRAP TEXT IF IT IS LONG. FORMAT TABLES CORRECTLY. ENSURE LABELS, FORMULAE, TEXT AND OBJECTS DO NOT OVERLAP OR OCCLUDE EACH OTHER. Be elegant video designer. Scale charts and numbers to fit the screen. And don't let labels run into each other or overlap, or take up poor positions. For example, do not label a triangle side length at the corners, but the middle. Do not write equations that spill across the Y axis bar or X axis bar, etc.

If the input is math that is obviously wrong, do not generate any code.

Please use only manim for the video. Please write ALL the code needed since it will be extracted directly and run from your response. 

Take a deep breath and consider all the requirements carefully, then write the code.


"""


TRANSLATION_PROMPT = """
Ok. now translate the text to {language}, and replace the voice_label for azureservice with {voice_label}. Please write ALL the code in one go so that it can be extracted and run directly.
"""

#       hindi_text = Text('नमस्ते', font='Lohit Devanagari')  
# Create or cleanup existing extracted image frames directory.


def create_frame_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


FRAME_PREFIX = "_frame"


def extract_frame_from_video(video_file_path, frame_extraction_directory):
    print(
        f"Extracting {video_file_path} at 1 frame per second. This might take a bit...")
    create_frame_output_dir(frame_extraction_directory)
    vidcap = cv2.VideoCapture(video_file_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    # Calculate the ideal number of frames to extract
    max_frames = 60  # Maximum number of frames to extract
    if duration <= 60:
        frame_extraction_rate = 1  # 1 fps for videos under 60 seconds
    else:
        frame_extraction_rate = max(1, int(total_frames / max_frames))

    output_file_prefix = os.path.basename(video_file_path).replace('.', '_')
    frame_count = 0
    count = 0
    while vidcap.isOpened():
        success, frame = vidcap.read()
        if not success:  # End of video
            break
        if count % frame_extraction_rate == 0:  # Extract a frame at the calculated rate
            # Calculate the actual time for the frame
            time_in_seconds = count / fps
            min = int(time_in_seconds // 60)
            sec = int(time_in_seconds % 60)
            time_string = f"{min:02d}:{sec:02d}"
            image_name = f"{output_file_prefix}{FRAME_PREFIX}{time_string}.jpg"
            output_filename = os.path.join(
                frame_extraction_directory, image_name)
            cv2.imwrite(output_filename, frame)
            frame_count += 1
        count += 1
    vidcap.release()
    print(
        f"Completed video frame extraction!\n\nExtracted: {frame_count} frames at a rate of {frame_extraction_rate} frames per second.")
    return {"video_duration": duration, "frame_count": frame_count, "frame_extraction_rate": frame_extraction_rate}


class File:
    def __init__(self, file_path: str, display_name: str = None):
        self.file_path = file_path
        if display_name:
            self.display_name = display_name
        self.timestamp = get_timestamp(file_path)

    def set_file_response(self, response):
        self.response = response


def get_timestamp(filename):
    """Extracts the frame count (as an integer) from a filename with the format
       'output_file_prefix_frame00:00.jpg'.
    """
    parts = filename.split(FRAME_PREFIX)
    if len(parts) != 2:
        return None  # Indicates the filename might be incorrectly formatted
    return parts[1].split('.')[0]


def create_python_file(response):
    code_blocks = extract_code_blocks(response.text)
    for block in code_blocks:
        print("Found code block:")
        print(block.strip())
        code = block.strip()
    # exec(code)
    filename = f"MathMovie_{uuid.uuid4().hex[:8]}"

    # Open the file in write mode ('w') which will overwrite the file if it already exists
    with open(f"{filename}.py", 'w') as file:
        file.write(code)
    return filename


def make_request(prompt, files):
    request = [prompt]
    for file in files:
        request.append(file.timestamp)
        request.append(file.response)
    return request


def send_message_with_retries(chat, request, max_retries=3):
    retry_wait = 60  # upped to 60 seconds cos of 504s grr
    for attempt in range(max_retries):
        try:
            response = chat.send_message(request)
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(retry_wait)
            retry_wait *= 2  # exponential backoff
    raise Exception("Max retries exceeded")


def create_math_matrix_movie(math_problem, audience_type, language="English", voice_label="en-US-AriaNeural"):
    # Check if audience_type is a digit and format it as "x years old", otherwise leave as is
    if str(audience_type).isdigit():
        audience_type = f"{audience_type} year old"

    # Fill up the MOVIE_PROMPT with the provided arguments
    filled_prompt = MOVIE_PROMPT.format(
        math_problem=math_problem, audience_type=audience_type, language=language, voice_label=voice_label)

    # Print the filled prompt to the console
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    chat = model.start_chat(history=[])

    attempt_count = 0
    success = False

    next_prompt = filled_prompt

    while attempt_count < 8 and not success:
        print(f"attempt #{attempt_count+1} next_prompt: {next_prompt}")
        response = send_message_with_retries(chat, next_prompt)
        print(response.text)
        filename = create_python_file(response)
        command = f"{os.getenv('MANIM_BIN')} -ql {filename}.py --disable_caching"
        result = subprocess.run(command, shell=True,
                                capture_output=True, text=True)
        print(f"result: {result.returncode}")

        if result.returncode == 0:
            success = True
        else:
            attempt_count += 1
            error_prompt = f"Your last code iteration created an error, this is the text of the error: {result.stderr}\nPlease write ALL the code in one go so that it can be extracted and run directly."
            next_prompt = "\n\n" + error_prompt

    if not success:
        print("Failed to generate a successful output after 8 attempts.")
        raise Exception(
            "Failed to generate a successful output after 8 attempts.")

    # call llama3 with response.text, math_problem, audience_type and language ... to generate youtube metadata

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    path_pattern = os.path.join(
        current_script_dir, f"media/videos/{filename}/480p15/*.mp4")
    mp4_files = glob.glob(path_pattern)

    video_file_path = mp4_files[0]
    with open(f"{filename}.py", 'r') as file:
        initial_code = file.read()
    video_url = os.getenv('BASE_URL') + video_file_path.split("media")[1]

    yield {
        "stage": "initial",
        "video_path": video_file_path,
        "video_id": filename,
        "video_url": video_url,
        "original_prompt": filled_prompt,
        "initial_code": initial_code
    }

    frame_extraction_directory = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), f"media/frames/{filename}/")
    frame_stats = extract_frame_from_video(
        video_file_path, frame_extraction_directory)

    files = os.listdir(frame_extraction_directory)
    files = sorted(files)
    files_to_upload = []
    for file in files:
        if file:
            files_to_upload.append(
                File(file_path=os.path.join(frame_extraction_directory, file)))

    print(files_to_upload)
    # Upload the files to the API
    # Only upload a 10 second slice of files to reduce upload time.
    # Change full_video to True to upload the whole video.
    full_video = True

    uploaded_files = []
    print(
        f'Uploading {len(files_to_upload) if full_video else 10} files. This might take a bit...')

    for file in files_to_upload if full_video else files_to_upload[40:50]:
        print(f'Uploading: {file.file_path}...')
        response = genai.upload_file(path=file.file_path)
        file.set_file_response(response)
        uploaded_files.append(file)

    print(f"Completed file uploads!\n\nUploaded: {len(uploaded_files)} files")
    frame_count = frame_stats['frame_count']
    frame_extraction_rate = frame_stats['frame_extraction_rate']
    video_duration = frame_stats['video_duration']

    prompt = """
        Watch the video keyframes, study the code you generated previously and make tweaks to make the video more appealing, if needed. Ask yourself: is there anything wrong with the attached images? How are the text colors, spacing and so on. How are the animations? How is their placement? be extremely terse and focus on actionable insights. This is for an AI video editor.
        
        Remember to:
        - center titles
        - center all action
        - no text should roll off screen
        - no text should be too small
        - no text should be too big
        - diagrams should be labelled correctly
        - diagrams should be placed correctly
        - diagrams should be animated correctly
        - there should not be any artifacts
        - there should not be significant stretches of blank screen
        - leave some padding at the bottom to allow for where subtitles would appear
        
        These frames were extracted at a rate of {frame_extraction_rate} frames per second, for a video of {video_duration} seconds. Keep the video speed 1.15x.
        
        Previous code:
        ```
        {initial_code}
        ```
        
        After enumerating actionable insights tersely, please write updated code. Please write ONE block of ALL Manim code that includes ALL the code needed since it will be extracted directly and run from your response. Do not write any other blocks of code except the final single output manim code block as it will be extracted and run directly from your response.

        Please do not use any external dependencies like svgs or sound effects since they are not available. There are no external assets. 
                
        Remember, your goal is to explain {math_problem} to {audience_type}. Please stick to explaining the right thing in an interesting way appropriate to the audience. The goal is to make a production grade math explainer video that will help viewers quickly and thoroughly learn the concept. You are a great AI video editor and educator. Keep the video speed 1.15x. Thank you so much! Take a deep breath and get it right!
    """

    # Make the LLM request.
    request = make_request(prompt, uploaded_files)
    response = send_message_with_retries(chat, request)
    print(response.text)

    filename = create_python_file(response)
    # Assuming filename is already defined as shown previously
    command = f"{os.getenv('MANIM_BIN')} -ql {filename}.py --disable_caching"
    result = subprocess.run(command, shell=True)

    if result.returncode != 0:
        attempt_count = 0
        success = False
        error_prompt = f"Your last code iteration created an error, this is the text of the error: {result.stderr}\nPlease write ALL the code in one go so that it can be extracted and run directly."
        next_prompt = "\n\n" + error_prompt
        while attempt_count < 8 and not success:
            print(f"attempt #{attempt_count+1} next_prompt: {next_prompt}")
            response = send_message_with_retries(chat, next_prompt)
            print(response.text)
            filename = create_python_file(response)
            command = f"{os.getenv('MANIM_BIN')} -ql {filename}.py --disable_caching"
            result = subprocess.run(command, shell=True,
                                    capture_output=True, text=True)
            print(f"result: {result.returncode}")

            if result.returncode == 0:
                success = True
            else:
                attempt_count += 1
                error_prompt = f"Your last code iteration created an error, this is the text of the error: {result.stderr}\nPlease write ALL the code in one go so that it can be extracted and run directly."
                next_prompt = "\n\n" + error_prompt

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    path_pattern = os.path.join(
        current_script_dir, f"media/videos/{filename}/480p15/*.mp4")
    mp4_files = glob.glob(path_pattern)

    video_file_path = mp4_files[0]

    with open(f"{filename}.py", 'r') as file:
        final_code = file.read()

    video_url = os.getenv('BASE_URL') + video_file_path.split("media")[1]

    yield {
        "stage": "final",
        "video_path": video_file_path,
        "video_id": filename,
        "video_url": video_url,
        "original_prompt": filled_prompt,
        "final_code": final_code,
    }

    # Write subprocess
if __name__ == "__main__":
    main()
