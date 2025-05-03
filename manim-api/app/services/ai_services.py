import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Define prompt templates
MOVIE_PROMPT = """
Can you explain {math_problem} to a {audience_type}? Please be visual and interesting. Consider using a meme if the audience is younger.

Please create python code for a manim video for the same. 

Please do not use any external dependencies like mp3s or svgs or graphics. Do not create any sound effects. 

If you need to draw something, do so using exclusively manim. Always add a title and an outro. Narrate the title and outro.

Please try to visually center or attractively lay out all content. Please also keep the margins in consideration. If a sentence is long please wrap it by splitting it into multiple lines. 

Please add actual numbers and formulae wherever appropriate as we want our audience of {audience_type} to learn math.

Do use voiceovers to narrate the video. The following is an example of how to do that:
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

The voice for the "{language}" is "{voice_label}". Please use this voice for the narration. 

Please do not use any external dependencies like svgs or mp3s or grpahics since they are not available. Draw with shapes and use colored letters, but keep it simple. There are no external assets. Constraints are liberating. 

First write the script explicitly and refine the contents and then write the code.

Please draw and animate things, using the whole canvas. Use color in a restrained but elegant way, for educational purposes.

Please add actual numbers and formulae wherever appropriate as we want our audience of {audience_type} to learn math. Please do not leave large blank gaps in the video. Make it visual and interesting. PLEASE ENSURE ELEMENTS FADE OUT AT THE APPROPRIATE TIME. DO NOT LEAVE ARTIFACTS ACROSS SCENES AS THEY OVERLAP AND ARE JARRING. WRAP TEXT IF IT IS LONG. FORMAT TABLES CORRECTLY. ENSURE LABELS, FORMULAE, TEXT AND OBJECTS DO NOT OVERLAP OR OCCLUDE EACH OTHER. Be elegant video designer. Scale charts and numbers to fit the screen. And don't let labels run into each other or overlap, or take up poor positions. For example, do not label a triangle side length at the corners, but the middle. Do not write equations that spill across the Y axis bar or X axis bar, etc.

If the input is math that is obviously wrong, do not generate any code.

Please use only manim for the video. Please write ALL the code needed since it will be extracted directly and run from your response. 

Take a deep breath and consider all the requirements carefully, then write the code.
"""

IMPROVEMENT_PROMPT = """
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
{initial_code}

After enumerating actionable insights tersely, please write updated code. Please write ONE block of ALL Manim code that includes ALL the code needed since it will be extracted directly and run from your response. Do not write any other blocks of code except the final single output manim code block as it will be extracted and run directly from your response.

Please do not use any external dependencies like svgs or sound effects since they are not available. There are no external assets. 
        
Remember, your goal is to explain {math_problem} to {audience_type}. Please stick to explaining the right thing in an interesting way appropriate to the audience. The goal is to make a production grade math explainer video that will help viewers quickly and thoroughly learn the concept. You are a great AI video editor and educator. Keep the video speed 1.15x. Thank you so much! Take a deep breath and get it right!
"""

def extract_code_blocks(text):
    """Extract code blocks from text surrounded by triple backticks"""
    import re
    
    pattern = r"```python(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    return matches

def generate_manim_code(math_problem, audience_type, language="English", voice_label="en-US-AriaNeural", error_message=None):
    """
    Generate Manim code for a math educational video using Google's Gemini
    
    If error_message is provided, try to fix the code based on the error
    """
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    # Create the prompt
    prompt = MOVIE_PROMPT.format(
        math_problem=math_problem,
        audience_type=audience_type,
        language=language,
        voice_label=voice_label
    )
    
    # If there's an error message, append it to the prompt
    if error_message:
        prompt += f"\n\nYour last code iteration created an error, this is the text of the error: {error_message}\nPlease write ALL the code in one go so that it can be extracted and run directly."
    
    # Generate the response
    response = model.generate_content(prompt)
    
    # Extract code from the response
    code_blocks = extract_code_blocks(response.text)
    if not code_blocks:
        raise Exception("No code block found in the AI response")
    
    return code_blocks[0].strip()

def improve_video_with_ai(initial_code, frame_extraction_directory, math_problem, audience_type):
    """
    Improve the video based on extracted frames using AI feedback
    """
    import os
    from pathlib import Path
    import cv2
    
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    # Get statistics about the frames
    video_duration = 0
    frame_extraction_rate = 1
    
    # Find all frames
    frames = list(Path(frame_extraction_directory).glob("*.jpg"))
    
    # Upload a subset of frames to Gemini
    uploaded_frames = []
    for i, frame_path in enumerate(frames):
        if i % 5 == 0:  # Upload every 5th frame to reduce API load
            try:
                response = genai.upload_file(path=str(frame_path))
                uploaded_frames.append(response)
            except Exception as e:
                print(f"Error uploading frame: {e}")
    
    if not uploaded_frames:
        # If no frames were successfully uploaded, just return the original code
        return initial_code
    
    # Create prompt with frame information
    prompt = IMPROVEMENT_PROMPT.format(
        frame_extraction_rate=frame_extraction_rate,
        video_duration=video_duration,
        initial_code=initial_code,
        math_problem=math_problem,
        audience_type=audience_type
    )
    
    # Send request with frames and prompt
    response = model.generate_content([prompt, *uploaded_frames])
    
    # Extract improved code
    code_blocks = extract_code_blocks(response.text)
    if not code_blocks:
        return initial_code  # Return original if no code block found
    
    return code_blocks[0].strip()