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
# salma sat
model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35)

# salma gmail
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35) #salma nyu

# salma nyu
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35) 


#mbzuai
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35) 
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35) 

#nyu
# model = ChatGroq(model = "llama-3.1-70b-versatile", groq_api_key = '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', temperature=0.35)
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35) 

# gmail
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35)
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35)
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35) 
# model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='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', temperature=0.35)


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
    prompt_template = ChatPromptTemplate.from_messages([("system", sys_template), ("user", text)])
    chain = prompt_template | model | parser
    translated_text = chain.invoke({"input": text})
    return clean_translation(translated_text)

# Function to copy the file and translate specific text within it
async def translate_data_in_file(file_path, output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(f"Processing file: {file_path}")

    translated_data = {}

    # Copy the original data into the output file directory
    shutil.copy(file_path, output_file_path)

    # Translate only values of keys that match the pattern
    for key, text in data.items():
        if re.match(r"^[a-f0-9]{32}$", key) and isinstance(text, list):
            translated_text = []
            for item in text:
                translated_text.append(await translate_text(item))
            translated_data[key] = translated_text
        else:
            translated_data[key] = text

    # Write the updated JSON file with translations for specified keys
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(translated_data, outfile, ensure_ascii=False, indent=2)

    return translated_data

# API endpoint to translate all JSON files in a directory
@app.get("/translate-files/")
async def translate_files():
    try:
        # Define the output directory for translated files
        output_dir = "datasets/Arabic_translated_R2R/observations_list_summarized"
        os.makedirs(output_dir, exist_ok=True)

        # Process each file in the specified directory
        for file_path in glob.glob("datasets/R2R/observations_list_summarized/*.json"):
            output_file_path = os.path.join(output_dir, os.path.basename(file_path).replace('.json', '.translated.json'))
            await translate_data_in_file(file_path, output_file_path)
        
        return {"message": "Translations completed and saved with original files copied."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=1000)
