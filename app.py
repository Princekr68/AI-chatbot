import html

import streamlit as st

from chatbot import get_response

# Page settings
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

# Custom styling
st.markdown(
    """
    <style>
    .stApp { background-color: #ffffff; }
    .block-container { max-width: 900px; padding-top: 7rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu, footer { visibility: hidden; }

    .title { text-align: center; font-size: 32px; font-weight: 700;
             color: #202020; margin-bottom: 30px; }

    .user-message { display: flex; justify-content: flex-end; margin: 12px 0; }
    .user-bubble { background-color: #eeeeee; color: #202020; padding: 10px 16px;
                   border-radius: 18px; max-width: 75%; font-size: 16px; }
    .bot-message { color: #202020; font-size: 16px; margin: 12px 0 20px 0;
                   line-height: 1.5; }

    .stTextInput input { border: 2px solid #202020 !important;
                         border-radius: 28px !important; padding: 14px 18px !important;
                         font-size: 16px !important; background-color: #ffffff !important;
                         color: #202020 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main chatbot box
with st.container(border=True):
    st.markdown('<div class="title">AI Chatbot</div>', unsafe_allow_html=True)

    # Chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="user-message"><div class="user-bubble">'
                f'{html.escape(message["content"])}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="bot-message">{message["content"]}</div>',
                unsafe_allow_html=True,
            )

    # Message input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        user_input = col1.text_input(
            "Message", placeholder="Type message", label_visibility="collapsed"
        )
        send = col2.form_submit_button("↑", use_container_width=True)

        if send and user_input.strip():
            response, _ = get_response(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # Clear conversation
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
