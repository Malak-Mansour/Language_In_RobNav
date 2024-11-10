# Run this in Windows Command Prompt after executing the FastAPI server:
# curl -X GET "http://localhost:8000/translate-files/"

from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
import json
import glob
from dotenv import load_dotenv
import re
import shutil

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq model with the specified parameters
model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='your_api_key_here', temperature=0.35) 


# Define the system prompt template for concise translation to Arabic
sys_template = "Translate the following sentence into Arabic concisely, ensuring no extra words."

# Parser for processing model output
parser = StrOutputParser()

app = FastAPI(
    title="Language Translator",
    version="1.0",
    description="Simple Language Translator using Langchain and Fast API Server"
)
# Function to clean non-Arabic characters from the translation output
def clean_translation(text):
    arabic_text = re.sub(r'[^\u0600-\u06FF\s.,/؛؟!،]', '', text).strip()
    return arabic_text.strip()

# Function to translate individual text lines using the model
async def translate_text(text):
    # Set up the prompt template for translation
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", sys_template),
        ("user", text)
    ])
    
    # Chain the prompt through the model and parse the output
    chain = prompt_template | model | parser
    translated_text = chain.invoke({"input": text})
    return clean_translation(translated_text)

# Function to translate object names in the JSON data
async def translate_object_names(data):
    translated_data = {}

    # Traverse the data structure to find and translate object names
    for key, items in data.items():
        if isinstance(items, list):
            translated_items = []
            for item in items:
                translated_item = {}
                for obj_name, attributes in item.items():
                    if obj_name:
                        # Translate the object name
                        translated_obj_name = await translate_text(obj_name)
                        # Keep the attributes unchanged
                        translated_item[translated_obj_name] = attributes
                translated_items.append(translated_item)
            translated_data[key] = translated_items
        else:
            # If items are not in a list, skip translating
            translated_data[key] = items

    return translated_data

# Update the `translate_data_in_file` function to handle the described issues
async def translate_data_in_file(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(f"Processing file: {file_path}")

    # Open the output file for writing and set it to append mode
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        outfile.write('{\n')

        # Track the number of keys processed to manage JSON formatting
        total_keys = len(data.keys())
        processed_keys = 0

        # Translate object names and write each translation to the file as it completes
        for key, items in data.items():
            if isinstance(items, list):
                outfile.write(f'    "{key}": [\n')  # Indent list opening by 4 spaces

                for idx, item in enumerate(items):
                    if not item:  # Check if the item is empty
                        outfile.write('        {},\n')  # Write empty object in one line
                        continue

                    outfile.write('        {\n')  # Additional 4 spaces for opening each item
                    translated_item = {}
                    
                    for obj_name, attributes in item.items():
                        translated_obj_name = await translate_text(obj_name)
                        translated_item[translated_obj_name] = attributes
                        
                        # Write translated object with additional indentation
                        outfile.write(f'            "{translated_obj_name}": {{\n')
                        outfile.write(f'                "heading": {attributes["heading"]},\n')
                        outfile.write(f'                "distance": {attributes["distance"]}\n')
                        outfile.write('            }')

                        if list(item.keys())[-1] != obj_name:
                            outfile.write(',')

                        outfile.write('\n')

                    outfile.write('        }')  # Closing bracket for each item

                    if idx < len(items) - 1:
                        outfile.write(',\n')  # Add comma if not the last item
                    else:
                        outfile.write('\n')  # No comma for the last item

                outfile.write('    ]')  # Indent list closing by 4 spaces
                if processed_keys < total_keys - 1:
                    outfile.write(',\n')  # Append a comma for separation between objects
                else:
                    outfile.write('\n')  # No comma for the last item in the object

            processed_keys += 1

        outfile.write('}\n')  # Close the JSON object in the file


# FastAPI endpoint to translate JSON files
@app.get("/translate-files/")
async def translate_files():
    try:
        # Define the output directory for translated files
        output_dir = "datasets/Arabic_translated_R2R/objects_list"
        os.makedirs(output_dir, exist_ok=True)

        # Process each file in the specified directory
        for file_path in glob.glob("datasets/R2R/objects_list/*.json"):
            output_file_path = os.path.join(output_dir, os.path.basename(file_path).replace('.json', '.translated.json'))
            await translate_data_in_file(file_path, output_file_path)
        
        return {"message": "Object name translations completed and saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    

# Run the FastAPI app if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
