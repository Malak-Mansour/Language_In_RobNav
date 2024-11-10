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

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq model with the specified parameters
model = ChatGroq(model="llama-3.2-90b-text-preview", groq_api_key='your_api_key_here', temperature=0.35)

# Define the system prompt template for concise translation to Arabic
sys_template = "Translate the following sentence into Arabic concisely, ensuring no extra words."

# Parser for processing model output
parser = StrOutputParser()

# Define the FastAPI app with metadata
app = FastAPI(
    title="Language Translator",
    version="1.0",
    description="Simple Language Translator using Langchain runnable interfaces and Fast API Server"
)

# Function to clean and adjust the translation output by removing unwanted characters
def clean_translation(text):
    # Remove non-Arabic characters using regex
    arabic_text = re.sub(r'[^\u0600-\u06FF\s.,/؛؟!،]', '', text).strip()
    return arabic_text.strip()

# Translate a list of instructions
async def translate_instructions(instructions):
    translations = []
    for instruction in instructions:
        if isinstance(instruction, list):
            # Handle a list of sentences separately
            translated_sentences = []
            for sentence in instruction:
                # Create and format prompt for each sentence
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", sys_template),
                    ("user", sentence)
                ])
                
                # Execute the translation process
                chain = prompt_template | model | parser

                try:
                    # Get translated sentence
                    translated_sentence = chain.invoke({"input": sentence})
                    
                    # Clean the translation result
                    cleaned_translated = clean_translation(translated_sentence)

                    # Add cleaned translation to list
                    translated_sentences.append(cleaned_translated)
                except Exception as e:
                    print(f"Error translating sentence '{sentence}': {e}")

            # Append the list of translated sentences
            translations.append(translated_sentences)
        else:
            # Handle a single instruction
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", sys_template),
                ("user", instruction)
            ])
            
            chain = prompt_template | model | parser
            
            try:
                # Get translated instruction
                translated_instruction = chain.invoke({"input": instruction})
                cleaned_translated = clean_translation(translated_instruction)
                translations.append(cleaned_translated) 
            except Exception as e:
                print(f"Error translating instruction '{instruction}': {e}")

    # Return the translations, handling both single and multiple instructions
    return translations[0] if len(translations) == 1 else translations

# Endpoint to translate files and save the translated data
@app.get("/translate-files/")
async def translate_data():
    try:
        # Create output directory for translated files
        output_dir = "datasets/Arabic_translated_R2R/annotations"
        os.makedirs(output_dir, exist_ok=True)

        # Process each JSON file in the specified directory
        for file_path in glob.glob("datasets/R2R/annotations/*.json"):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"Processing file: {file_path}")

                # Define output path for translated file
                output_file_path = os.path.join(output_dir, os.path.basename(file_path).replace('.json', '.translated.json'))
                
                # Write translated data to output file
                with open(output_file_path, 'w', encoding='utf-8') as outfile:
                    outfile.write('[\n')  # Start the JSON array

                    for idx, item in enumerate(data):
                        # Check if the item contains "instruction" or "instructions" key
                        instructions_key = "instruction" if "instruction" in item else "instructions" if "instructions" in item else None
                        
                        if instructions_key:
                            instructions = [item[instructions_key]]
                            translated = await translate_instructions(instructions)
                            item[instructions_key] = translated  # Replace with translated content
                        
                        # Write the modified item to the output file with 2-space indentation
                        json.dump(item, outfile, ensure_ascii=False, indent=2)

                        # Add comma after each item except the last one
                        if idx < len(data) - 1:
                            outfile.write(',\n')
                        else:
                            outfile.write('\n')

                    outfile.write(']')  # Close the JSON array


                # Now, read the contents and shift indentation 2 units to the right
                with open(output_file_path, 'r', encoding='utf-8') as outfile:
                    content = outfile.read()

                # Split the content into lines
                lines = content.split('\n')

                # Add 2 spaces to the beginning of each line except the first and last
                shifted_content = '\n'.join([lines[0]] + ['  ' + line for line in lines[1:-1]] + [lines[-1]])

                # Write the shifted content back to the file
                with open(output_file_path, 'w', encoding='utf-8') as outfile:
                    outfile.write(shifted_content)


        # Return a success message
        return {"message": "Translations completed and saved with original file structure intact."}

    except Exception as e:
        # Return error message if an exception occurs
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
