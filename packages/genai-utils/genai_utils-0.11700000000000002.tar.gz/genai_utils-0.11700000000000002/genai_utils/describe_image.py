#!/usr/bin/env python 

'''
python -m genai_utils.index_imges --directory </path/to/images>

'''
from ollama import generate

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DEFAULT_MODEL = 'qwen2.5'

DEFAULT_SYSTEM_PROMPT = """
You are an image analyst who has been tasked with describing images.
Your goal is to enable retrieving the images based on the content of your descriptions.
"""

DEFAULT_USER_PROMPT = """
Describe this image.
Provide a thorough and detailed description, focusing on identifying and describing objects in the image.
Use denotative rather than connotative language. 
Read the text in the images and include it in the description without including the location of font name.
Do not explain how you are describing the image. Do not use any "I" statements.
"""

def describe_image(image_data, prompt=DEFAULT_USER_PROMPT, system=DEFAULT_SYSTEM_PROMPT, model=DEFAULT_MODEL):
    print(f"Describe image: {model}")
    result = generate(model=model, prompt=prompt, images=[image_data])
    return result['response']



def checkMatched(query, descritpion):
    prompt=f"""
You are a great critic who can rank query and descritpion on the scale of 1 to 5.
You will give 0 if the query is not answered by the descritpion.
You will give a rank of 5 if query perfectly matches the descritpion.
Give a rank of intemediate number from 0 to 5 if there is a partial match of key concepts in the descritpion to query.
A perfect match is when the query matches the description very closely.
if query does not entail the description give a score of 3

Please rank the following query and descritpion and just return the rank and explain why you gave the ranking

query: {query}\n 

descritpion: {descritpion}.
"""
    result=generate(model=DEFAULT_MODEL, prompt=prompt)
    return result['response']
