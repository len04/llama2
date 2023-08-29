import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Dream Analysis")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Dream Analysis Chatbot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your dream description!', icon='👉')
    
    # Model and parameters selection
    st.subheader('Dream Analysis Model and Parameters')
    selected_model = st.sidebar.selectbox('Choose a Dream Analysis Model', ['Model 1', 'Model 2', 'Model 3'], key='selected_model')
    temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=5.0, value=0.5, step=0.01)
    # Add other parameter sliders if needed

# Set the Replicate API token
os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Store generated dream analysis
if "dream_analysis" not in st.session_state.keys():
    st.session_state.dream_analysis = []

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Clear dream analysis history button
def clear_analysis_history():
    st.session_state.dream_analysis = []
st.sidebar.button('Clear Dream Analysis History', on_click=clear_analysis_history)

# Function for generating LLaMA2 response
# Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":0.1, "top_p":0.9, "max_length":512, "repetition_penalty":1})
    return "Dream Analysis: " + output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
