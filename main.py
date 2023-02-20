import json
import openai
import os
import pinecone 

def lambda_handler(event, context):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # MODEL = "text-similarity-babbage-001"
    # MODEL = "text-embedding-ada-002"
    MODEL = "text-search-ada-query-001"

    # extract the query parameter from the event
    query = event['queryStringParameters']['query']
    print("Query: ",query)
    # create the query embedding
    xq = openai.Embedding.create(input=query, engine=MODEL)['data'][0]['embedding']

    # initialize connection to pinecone (get API key at app.pinecone.io)
    pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment="us-east1-gcp")
    index_name = "pinebrooke"
    index = pinecone.Index(index_name)

    # query, returning the top 5 most similar results
    res = index.query([xq], top_k=5, include_metadata=True, namespace="pinebrooke")
    
    # extract required information from the query result
    matches = res['matches']
    data = []
    content = []
    for match in matches:
        metadata = match['metadata']
        data.append({
            'score': match['score'],
            'title': metadata['title'],
            'content': metadata['content']
        })
        content.append(metadata['content'])
    
    full_content = '\n\n'.join(content)

    # create the response with the query and matching results
    response = {
        "statusCode": 200,
        "body": json.dumps({
            'query': query,
            'matches': data,
            'chat_gpt': openai_ask_question1(full_content, query)
        })
    }

    return response
   
def openai_ask_question(context, question):
    prompt = f"Context: {context}\n\nQ: {question}\nA:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=100,
        n=1,
        stop=None,
    )["choices"][0]["text"].strip(" \n")
    
    if not response:
        return {
            "prompt": prompt,
            "gpt_answer": "Sorry, I couldn't find an answer to that question.",
        }
    
    return {
        "prompt": prompt,
        "gpt_answer": response,
    }

def openai_ask_question1(context, question):
    prompt = f"Context: {context}\n\nQ: {question}\nA:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=100,
        n=1,
        stop=None,
    )["choices"][0]["text"].strip(" \n")
    
    if not response:
        response = "Sorry, I couldn't find an answer to that question."
        return {
            "question": question,
            "prompt": prompt,
            "gpt_answer": "Sorry, I couldn't find an answer to that question.",
            "html_preview": '<div class="container"><div class="question">'+question+'</div><div class="answer">'+response+"</div></div>"
        }
    
    return {
        "question": question,
        "prompt": prompt,
        "gpt_answer": response,
        "html_preview": '<div class="container"><div class="question">'+question+'</div><div class="answer">'+response+"</div></div>"
    }
