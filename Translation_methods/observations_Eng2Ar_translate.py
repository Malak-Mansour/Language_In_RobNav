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

# Load environment variables from .env file (e.g., API keys)
load_dotenv()

# Initialize the Groq model with the specified parameters for text translation
model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='your_api_key_here', temperature=0.35)

# Define the system prompt template for concise translation to Arabic
sys_template = "Translate the following sentence into Arabic concisely, ensuring no extra words."

# Parser for processing model output
parser = StrOutputParser()

# Initialize the FastAPI app
app = FastAPI(
    title="Language Translator",
    version="1.0",
    description="Simple Language Translator using Langchain and FastAPI Server"
)

# Function to clean translated Arabic text, removing any unwanted characters
def clean_translation(text):
    arabic_text = re.sub(r'[^\u0600-\u06FF\s.,/؛؟!،]', '', text).strip()
    return arabic_text.strip()

# Asynchronous function to handle the translation of text
async def translate_text(text):
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", sys_template),  # System prompt for translation
        ("user", text)  # User input text to be translated
    ])
    
    # Create a chain to process translation using the model and parser
    chain = prompt_template | model | parser
    translated_text = chain.invoke({"input": text})  # Invoke translation chain
    return clean_translation(translated_text)

# Asynchronous function to translate content within a JSON file and save to an output file
async def translate_data_in_file(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(f"Processing file: {file_path}")

    translated_data = {}
    
    # Open the output file in write mode initially to clear any previous content
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump({}, outfile)  # Initialize an empty JSON object
    
    # Translate each key-value pair in the JSON file
    for key, text in data.items():
        translated_text = ""
        
        # Split text based on specific keywords and section headers
        sections = re.split(r"(heading \d+ - \d+:|\ndown:|\nmiddle:|\ntop:)", text)
        in_translation_block = False

        # Process sections and determine if they should be translated
        for i in range(1, len(sections), 2):
            section_header = sections[i].strip()
            content = sections[i + 1].strip()

            # Identify sections to translate based on headers
            if section_header in ["down:", "middle:", "top:"]:
                in_translation_block = True
            elif re.match(r"heading \d+ - \d+:", section_header):
                in_translation_block = False

            # Translate content within the selected translation blocks
            if in_translation_block:
                lines = content.splitlines()
                translated_lines = []
                for line in lines:
                    if line.strip():  # Only translate non-empty lines
                        translated_line = await translate_text(line)
                        translated_lines.append(translated_line)
                    else:
                        translated_lines.append(line)  # Keep empty lines unchanged

                # Combine translated lines into the content
                content = '\n'.join(translated_lines)

            # Append translated or original content to the cumulative translated text
            translated_text += f"{section_header}{content}\n"

        # Update the translated data dictionary with the translated text
        translated_data[key] = translated_text
        
        # Write the current translation progress to the output file
        with open(output_file_path, 'r+', encoding='utf-8') as outfile:
            # Load current JSON data and update with the latest translation
            current_data = json.load(outfile)
            current_data[key] = translated_text
            outfile.seek(0)
            json.dump(current_data, outfile, ensure_ascii=False, indent=4)
            outfile.truncate()  # Remove any remaining old data

    return translated_data


# Endpoint to handle translation requests for all JSON files in a specified directory
@app.get("/translate-files/")
async def translate_files():
    try:
        # Create directory for translated files if it does not exist
        output_dir = "datasets/Arabic_translated_R2R/observations"
        os.makedirs(output_dir, exist_ok=True)

        # Iterate over JSON files in the specified directory and translate each one
        for file_path in glob.glob("datasets/R2R/observations/*.json"):
            output_file_path = os.path.join(output_dir, os.path.basename(file_path).replace('.json', '.translated.json'))
            await translate_data_in_file(file_path, output_file_path)
        
        return {"message": "Translations completed and saved line-by-line."}
    except Exception as e:
        # Raise an HTTP exception if there is an error during translation
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
