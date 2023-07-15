from concurrent.futures import ThreadPoolExecutor
from openai.embeddings_utils import get_embedding
from openai.embeddings_utils import cosine_similarity
import uuid
import json
import time
import openai
import numpy as np
import os
from functools import partial
import PyPDF2
import concurrent.futures



def process_chunk(chunk_text):
    embd = get_embedding(chunk_text,engine='text-embedding-ada-002')
    return embd


def generate_json_with_embeddings(data):

            ##### Sending and calculating embeddings concurrently ######
    with ThreadPoolExecutor() as executor:
        futures = []
        n = 1
        for ind, i in enumerate(data):
            future = executor.submit(process_chunk, i["chunk"])
            futures.append((ind, future))
            n += 1
            if n >= 100:
                print("embedding 100 done.",flush=True)
                n = 1
                time.sleep(14)
        for ind, future in futures:
            data[ind]["embeddings"] = future.result()
    return data
            





def extract_pdf_content(pdf_path):
    try:
        pdf_file = open(pdf_path, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_name = os.path.basename(pdf_path)
        content_chunks = []

        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            content = page.extract_text()
            
            _content = content.split('\n')
            half_page = len(_content)//2
            chunk = ''
            for i in range(half_page):
                chunk+=_content[i]+'\n'
            page_chunk = {
                "chunk_id": str(uuid.uuid4()),
                "chunk": chunk,
                "page_num": page_num,
                "pdf_name": pdf_name,
            }
            content_chunks.append(page_chunk)

            chunk = ''
            for j in range(half_page,len(_content)):
                chunk+=_content[j]+'\n'
            page_chunk = {
                "chunk_id": str(uuid.uuid4()),
                "chunk": chunk,
                "page_num": page_num,
                "pdf_name": pdf_name
            }
            content_chunks.append(page_chunk)
            

        pdf_file.close()
    except Exception as e:
        print(e)
        try:
            pdf_file.close()
        except:
            pass
    return content_chunks

        
       



data = extract_pdf_content('my_pdf_data/my-cv.pdf')
data = generate_json_with_embeddings(data)

print("--------- Code by Sohail ------------")
print("--------- Subscribe: https://www.youtube.com/@ddotpy?sub_confirmation=1 ------------")

knowledgeBase = 'knowledge_base.json'
with open(knowledgeBase, 'r' ,encoding='utf-8') as file:
    existing_data = json.load(file)

newData = []
for i in existing_data:
    newData.append(i)
for i in data:
    newData.append(i)

with open(knowledgeBase, 'w' , encoding='utf-8') as file:
    json.dump(newData, file, indent=4, ensure_ascii=False)
    
   
    