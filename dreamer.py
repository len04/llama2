import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Dreamer")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Dreamer')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Enter your dream!', icon='👉')

os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Tell me about your dream!"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Tell me about your dream!"}]
st.sidebar.button('Clear Dream History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    # Define a default input to be included before the user's prompt
    default_input = "You are a dream analysis assistant. Analyze the following dream:"

    # Concatenate the default input and user's prompt
    input_text = default_input + "\n\n" + prompt_input

    # Construct the string dialogue based on user and assistant messages
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    # Construct the complete prompt including the string dialogue and input
    complete_prompt = f"{string_dialogue} {input_text} Assistant: "

    # Call the AI model using replicate.run() or any other method
    output = replicate.run(
        'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
        input={"prompt": complete_prompt, "temperature": 0.1, "top_p": 0.9, "max_length": 512, "repetition_penalty": 1}
    )

    # # Extract the generated response from the AI's reply
    # generated_response = response[0]['generated_text']

    # Return the generated response
    # return generated_response
    return output


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your dream..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
