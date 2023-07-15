from openai.embeddings_utils import get_embedding
from openai.embeddings_utils import cosine_similarity
import numpy as np
import json
import openai
import os
prev_history = []
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_context(inputPrompt,top_k):
    # openai.api_key = apiKey
    search_term_vector = get_embedding(inputPrompt,engine='text-embedding-ada-002')
    
    with open("knowledge_base.json",encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
        for item in data:
            item['embeddings'] = np.array(item['embeddings'])

        for item in data:
            item['similarities'] = cosine_similarity(item['embeddings'], search_term_vector)

        sorted_data = sorted(data, key=lambda x: x['similarities'], reverse=True)
        context = ''
        referencs = []
        for i in sorted_data[:top_k]:
            context += i['chunk'] + '\n'
            # referencs.append({"pdf_name":i['pdf_name'],"page_num":i['page_num']})
    return context

def get_answer(user_input):


    context = get_context(user_input,3)

    prompt = "context:\n\n{}.\n\n Answer the following user query according to above given context:\nuser_input: {}".format(context,user_input)

    myMessages = []
    myMessages.append({"role": "system", "content": "You are expert article generator"})
    

    myMessages.append({"role": "user", "content": "context:\n\n{}.\n\n Answer the following user query according to above given context:\nuser_input: {}".format(context,user_input)})

    
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        # model='gpt-4',
        messages=myMessages,
        max_tokens=None,
        stream=False
    )
    
    return response['choices'][0]['message']['content']





def get_answer_using_function_call(user_input,prev_history):
    # print("prev_history::: ",prev_history)
    messages = []
    for i in prev_history:
        if i['ai'] != 'null': 
            messages.append({"role": "user", "content": i['user']})
            messages.append({"role": "assistant", "content": i['ai']})

    messages.append({"role": "user", "content": user_input})

    functions = [
        {
            "name": "get_answer",
            "description": "Get Answer to any query to which you don't know the answer your self. You will also call this function whenever the user ask some query or question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "A User query with complete intentsion as per the conversation history.",
                    },
                },
                "required": ["user_input"],
            },
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]
    print("response_message: ",response_message)

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_answer": get_answer,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        user_input=function_args.get("user_input")

        print("generated_query: ",user_input)
        res = get_answer(user_input)
        return res
    else:
        return response_message['content']



print("--------- Code by Sohail ------------")
print("--------- Subscribe: https://www.youtube.com/@ddotpy?sub_confirmation=1 ------------")
