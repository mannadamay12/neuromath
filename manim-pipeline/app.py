import json
from google_auth_oauthlib.flow import Flow
import os
import streamlit as st
from create_lesson import create_math_matrix_movie
from google.oauth2.credentials import Credentials

from test_pipeline import llama3_call, upload_video_to_youtube

st.set_page_config(page_title='MathMatrixMovies', page_icon='favicon.png')

st.markdown("""
    <style>
    .title {
        font-size: 40px;
        color: #ff6347;  # This is a tomato color
        font-family: 'Helvetica', sans-serif;  # Font style
        text-align: center;
        margin-bottom: 20px;
    }
    .textbox {
        font-family: 'Verdana', sans-serif;
        font-size: 18px;
        color: #333;
    }
    .btn {
        font-size: 20px;
        color: white;
        background-color: #0078D4;  # This is a blue color
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# Use HTML for the title with custom class for styling
st.markdown("<div class='title'>MathMatrixMovies</div>",
            unsafe_allow_html=True)

# Check for URL parameters
query_params = st.query_params
# admin_mode = query_params.get('admin', None)
admin_mode = True

if not admin_mode:
    st.video('https://youtu.be/-4-M8YwAlhU')
    iframe = '<iframe class="airtable-embed" src="https://airtable.com/embed/appJHjHaquTmMQ82e/pagAMECsTYqX6unw9/form" frameborder="0" onmousewheel="" width="100%" height="1066" style="background: transparent;"></iframe>'
    st.markdown(iframe, unsafe_allow_html=True)
else:

    # Text input for the prompt
    prompt = st.text_input(
        "Enter the topic you wanna generate video on", key="video_prompt")

    # Create columns for the dropdowns and the button
    col1, col2, col3 = st.columns([1, 1, 1])

    # Dropdown 1 in the first column
    with col1:
        option1 = st.selectbox(
            'Age',
            ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', 'Undergraduate', 'Graduate'], key="1")

    # Dropdown 2 in the second column
    with col2:
        option2 = st.selectbox(
            'Language',
            ['English', 'Hindi', 'Spanish', 'Mandarin', 'Turkish', 'Tamil'], key="2")

    # Button in the third column, spanning the third and fourth columns
    with col3:
        generate_pressed = st.button("Generate")
        st.write(f"You entered: {prompt}")
        st.write(f"Audience Age selected: {option1}")
        st.write(f"Language selected: {option2}")

    if generate_pressed:
        st.session_state['video_generated'] = True
        video_result_generator = create_math_matrix_movie(
            prompt, option1, option2)
        for result in video_result_generator:
            if result['stage'] == 'initial':
                st.write("Initial Video:")
                print(f"Initial movie generated: {result['video_path']}")
                st.session_state['video_result'] = result
                st.video(result["video_path"])
                st.write(result["video_url"])
            elif result['stage'] == 'final':
                st.write("\n\n\n\n\n")
                st.write("Final Video:")
                print(f"Final movie generated: {result['video_path']}")
                st.session_state['video_result'] = result
                st.video(result["video_path"])
                st.write(result["video_url"])

    def log_fine_tune_entry(result):
        with open('fine-tune/dataset.jsonl', 'a') as file:
            # Define the new entry with the actual filled prompt and the assistant's response
            new_fine_tune_entry = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": result['original_prompt']},
                    {"role": "assistant", "content": result['final_code']}
                ]
            }
            file.write(json.dumps(new_fine_tune_entry) + '\n')

    if 'video_generated' in st.session_state and st.session_state['video_generated'] and st.session_state.get('video_result', {}).get('stage') == 'final':
        # we paused updating to YouTube while we figure out prod Oauth
        if st.button("Generate YouTube Metadata"):
            print("LLAMA3 CALL")
            if st.session_state['video_result']['stage'] == 'final':
                st.write("Final movie generated:")
                st.video(st.session_state['video_result']["video_path"])

            llama_result = llama3_call(
                prompt, option1, option2, "en-US-AriaNeural")
            st.write("LLAMA3 RESULT: YouTube Metadata")
            st.write(llama_result)

            st.write("Logging fine-tune dataset entry")
            log_fine_tune_entry(st.session_state['video_result'])
            # print("UPLOADING VIDEO")
            # response = upload_video_to_youtube(st.session_state['video_result']["video_url"], llama_result['title'],
            #                         llama_result['description'], llama_result['category_id'], llama_result['tags'])
            # link = "https://www.youtube.com/watch?v=" + response['id']
            # st.markdown(
            #     f'<a href="{link}" target="_blank">Watch on YouTube</a>',
            #     unsafe_allow_html=True
            # )
    # Setup environment variable for Google credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_secrets.json'

    # Define the OAuth flow function

    def authenticate_user():
        scopes = ['https://www.googleapis.com/auth/youtube']
        flow = Flow.from_client_secrets_file(
            'client_secrets.json',
            scopes=scopes,
            redirect_uri='https://math.auto.movie')  # Ensure this is correctly registered in Google Cloud Console
        auth_url, state = flow.authorization_url(
            prompt='consent', include_granted_scopes='true')
        return flow, auth_url, state

    # Sidebar for connecting to YouTube OAuth
    with st.sidebar:
        st.write("Connect to Services")
        if st.button('Connect to YouTube'):
            flow, auth_url, state = authenticate_user()
            # Save the state token in session state
            st.session_state['auth_state'] = state
            st.session_state['auth_url'] = auth_url
            st.write('Please go to this URL: ', auth_url)

        # Text input for authorization code
        code = st.text_input(
            'Enter the authorization code here', key="auth_code")
        if st.button('Authenticate', key="authenticate"):
            if 'auth_state' in st.session_state and code:
                try:
                    # Rebuild the flow object using saved state
                    flow = Flow.from_client_secrets_file(
                        'client_secrets.json',
                        scopes=['https://www.googleapis.com/auth/youtube'],
                        state=st.session_state['auth_state'],
                        redirect_uri='https://math.auto.movie')
                    flow.fetch_token(code=code)
                    credentials = flow.credentials

                    # Saving the credentials for later use
                    credentials_json = credentials.to_json()
                    with open('credentials.json', 'w') as cred_file:
                        cred_file.write(credentials_json)

                    st.success('You are now authenticated!')
                except Exception as e:
                    st.error(f"Failed to authenticate: {str(e)}")
            else:
                st.error(
                    "Please reconnect and provide a valid authorization code.")
