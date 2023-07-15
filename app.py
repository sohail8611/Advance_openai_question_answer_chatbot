import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from hugchat import hugchat

from answer import *


# Sidebar contents
with st.sidebar:
    st.title('💬 Custom Data Advance Chatbot')

    

# Generate empty lists for generated and past.
## generated stores AI generated responses
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
## past stores User's questions
if 'past' not in st.session_state:
    st.session_state['past'] = []

# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='blue-30')
response_container = st.container()

# User input
## Function for taking user provided prompt as input
def get_text():
    input_text = st.text_input("You: ", "", key="input")
    return input_text
## Applying the user input box
with input_container:
    user_input = get_text()

# Response output
## Function for taking user prompt as input followed by producing AI generated responses
def generate_response(user_input):
    for i in range(len(st.session_state['past'])):
        try:
            prev_history.append({"user":st.session_state['past'][i],"ai":st.session_state["generated"][i]})
        except:
            prev_history.append({"user":st.session_state['past'][i],"ai":"null"})


    answer = get_answer_using_function_call(user_input,prev_history)
    
    return answer

## Conditional display of AI generated responses as a function of user provided prompts
with response_container:
    if user_input:
        st.session_state.past.append(user_input)
        response = generate_response(user_input)
        st.session_state.generated.append(response)
        
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            prev_history.append({"user":st.session_state['past'][i],"ai":st.session_state["generated"][i]})