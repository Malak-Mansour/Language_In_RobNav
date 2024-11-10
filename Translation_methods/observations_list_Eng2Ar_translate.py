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

# Function to translate all text data within a given file and write to output file
async def translate_data_in_file(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(f"Processing file: {file_path}")

    translated_data = {}
    
    # Open the output file in write mode initially to clear any previous content
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump({}, outfile)  # Initialize an empty JSON object

    # Translate each key-value pair and write it to the output file incrementally
    for key, text in data.items():
        # Handle cases where 'text' is a list of strings
        if isinstance(text, list):
            translated_text = []
            for item in text:
                translated_text.append(await translate_sections(item))
        else:
            # Translate as a single string if 'text' is not a list
            translated_text = await translate_sections(text)

        # Save the translated text for the current key
        translated_data[key] = translated_text
        
        # Write the current translation progress to the output file
        with open(output_file_path, 'r+', encoding='utf-8') as outfile:
            current_data = json.load(outfile)
            current_data[key] = translated_text
            outfile.seek(0)
            json.dump(current_data, outfile, ensure_ascii=False, indent=2)
            outfile.truncate()  # Remove any remaining old data

    return translated_data

# Helper function to handle translation of sections within a text block
async def translate_sections(text):
    translated_text = ""
    
    # Split text based on specific keywords (sections)
    sections = re.split(r"(heading \d+ - \d+:|down:|\nmiddle:|\ntop:)", text)
    in_translation_block = False

    # Iterate over sections to translate only designated parts
    for i in range(1, len(sections), 2):
        section_header = sections[i].strip()
        content = sections[i + 1].strip()

        # Start translating if within specified sections
        if section_header in ["down:", "middle:", "top:"]:
            in_translation_block = True
        elif re.match(r"heading \d+ - \d+:", section_header):
            in_translation_block = False

        # Translate content if within a translation block
        if in_translation_block:
            lines = content.splitlines()
            translated_lines = []
            for line in lines:
                if line.strip():
                    translated_line = await translate_text(line)
                    translated_lines.append(translated_line)
                else:
                    translated_lines.append(line)

            # Update content with translated lines
            content = '\n'.join(translated_lines)

        # Append the translated or original content to the cumulative translated text
        translated_text += f"{section_header}{content}"
        
        # Add a newline after each section except for the last one
        if i + 2 < len(sections):
            translated_text += "\n"  # Only add newline if it's not the last element


    return translated_text

# API endpoint to translate all JSON files in a directory
@app.get("/translate-files/")
async def translate_files():
    try:
        # Define the output directory for translated files
        output_dir = "datasets/Arabic_translated_R2R/observations_list"
        os.makedirs(output_dir, exist_ok=True)

        # Process each file in the specified directory
        for file_path in glob.glob("datasets/R2R/observations_list/*.json"):
            output_file_path = os.path.join(output_dir, os.path.basename(file_path).replace('.json', '.translated.json'))
            await translate_data_in_file(file_path, output_file_path)
        
        return {"message": "Translations completed and saved line-by-line."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Run the FastAPI app if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
