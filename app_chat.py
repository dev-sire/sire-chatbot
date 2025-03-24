import time
import os
import joblib
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

st.set_page_config(page_title='Sire\'s Gemini Assistant')
load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

new_chat_id = f'{time.time()}'
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data/')
except:
    # data/ folder already exists
    pass

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}

# Apply night theme styles
st.markdown(
    """
    <style>
    body {
        color: #e0e0e0;
        background-color: #121212;
    }
    .stTextInput>div>div>input {
        color: #e0e0e0;
        background-color: #333;
        border: 1px solid #555;
    }
    .stTextArea>div>div>textarea {
        color: #e0e0e0;
        background-color: #333;
        border: 1px solid #555;
    }
    .stButton>button {
        color: #e0e0e0;
        background-color: #1e88e5;
        border: 1px solid #1e88e5;
    }
    .stSelectbox>div>div>div>div {
        color: #e0e0e0;
        background-color: #333;
    }
    .stSelectbox>div>div>div>div:hover {
        background-color: #444;
    }
    .stChatMessage {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage[data-testid="stChatMessageContent"] p {
        color: #e0e0e0;
    }
    .stSidebar {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6, .stSidebar p, .stSidebar label{
        color: #e0e0e0;
    }
    .css-1y4p823{ /* Dropdown arrow */
        color: #e0e0e0;
    }
    .css-164nlkn{ /* Chevron icon */
        color: #e0e0e0;
    }
    .gradient-header {
        background: linear-gradient(90deg, #FF4F4F, #FF6A6A, #3B82F6);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        font-weight: bold;
        animation: gradientAnimation 4s linear infinite;
    }
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .subtitle {
        color: #9e9e9e;
        font-size: 1em;
        margin-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}

# Initialize session state variables
if 'chat_title' not in st.session_state:
    st.session_state.chat_title = 'New Chat'  # Default title

if 'chat_id' not in st.session_state:
    st.session_state.chat_id = None  # Initialize chat_id if not set

with st.sidebar:
    st.write('# Your Recent Chats')
    
    # Input for naming the chat session
    chat_name = st.text_input("Name your chat session:", value=st.session_state.get('chat_title', ''))

    if st.session_state.get('chat_id') is None:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id] + list(past_chats.keys()),
            format_func=lambda x: past_chats.get(x, 'New Chat'),
            placeholder='_',
        )
    else:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
            index=1,
            format_func=lambda x: past_chats.get(x, 'New Chat' if x != st.session_state.chat_id else chat_name),
            placeholder='_',
        )

    # Save new chats after a message has been sent to AI
    if chat_name:
        st.session_state.chat_title = chat_name
        past_chats[st.session_state.chat_id] = chat_name
        joblib.dump(past_chats, 'data/past_chats_list')

    # Button to delete the selected chat session
    if st.button("Delete Selected Chat"):
        if st.session_state.chat_id in past_chats:
            del past_chats[st.session_state.chat_id]
            joblib.dump(past_chats, 'data/past_chats_list')
            st.session_state.chat_id = None  # Reset chat_id to allow new selection
            st.success("Chat session deleted successfully.")
            st.rerun()
        else:
            st.error("No chat session selected for deletion.")
    st.markdown(
        """
            <div style="text-align: center; margin-top: 20px; color: #9e9e9e;">
                <p>Chatbot powered by <strong>Gemini Flash 2.0 Model</strong></p>
                <p>Developed by <strong>Aman Shahid</strong></p>
                <p>github.com/dev-sire</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<h1 class="gradient-header">Sire\'s ChatBot</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Code, debug, and learn with Google\'s advanced AI.</p>', unsafe_allow_html=True)

# Chat history (allows to ask multiple questions)
try:
    st.session_state.messages = joblib.load(
        f'data/{st.session_state.chat_id}-st_messages'
    )
    st.session_state.gemini_history = joblib.load(
        f'data/{st.session_state.chat_id}-gemini_messages'
    )
    print('old cache')
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []
    print('new_cache made')
st.session_state.model = genai.GenerativeModel('gemini-2.0-flash')
st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history,
)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(
        name=message['role'],
        avatar=message.get('avatar'),
    ):
        st.markdown(message['content'])

# React to user input
if prompt := st.chat_input('Your message here...'):
    # Save this as a chat for later
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/past_chats_list')
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append(
        dict(
            role='user',
            content=prompt,
        )
    )
    ## Send message to AI
    response = st.session_state.chat.send_message(
        prompt,
        stream=True,
    )
    # Display assistant response in chat message container
    with st.chat_message(
        name=MODEL_ROLE,
        avatar=AI_AVATAR_ICON,
    ):
        message_placeholder = st.empty()
        full_response = ''
        assistant_response = response
        # Streams in a chunk at a time
        for chunk in response:
            # Simulate stream of chunk
            # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
                time.sleep(0.05)
                # Rewrites with a cursor at end
                message_placeholder.write(full_response + '▌')
        # Write full message with placeholder
        message_placeholder.write(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        dict(
            role=MODEL_ROLE,
            content=st.session_state.chat.history[-1].parts[0].text,
            avatar=AI_AVATAR_ICON,
        )
    )
    st.session_state.gemini_history = st.session_state.chat.history
    # Save to file
    joblib.dump(
        st.session_state.messages,
        f'data/{st.session_state.chat_id}-st_messages',
    )
    joblib.dump(
        st.session_state.gemini_history,
        f'data/{st.session_state.chat_id}-gemini_messages',
    )