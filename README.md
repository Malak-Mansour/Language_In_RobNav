# Does Language Affect Reasoning Tasks in Robotic Navigation?

## Introduction
This repository contains our AI701 course project at MBZUAI. The project investigates whether language impacts the reasoning capabilities of large language models (LLMs) in robotic navigation tasks. By running experiments on both Arabic and English datasets, we compare the performance of NavGPT and evaluate its reasoning abilities across languages.

## Setup Instructions

Follow these steps to set up the environment and run the experiments:

### 1. Install Anaconda (if using WSL for Windows)
Run the commands below to install Anaconda and set up the environment:

```bash
wget https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
bash Anaconda3-2024.10-1-Linux-x86_64.sh
source ~/.bashrc
conda --version



2. Set Up the Environment
Create a new environment and install dependencies:

conda create --name NavGPT python=3.9
conda activate NavGPT
pip install -r requirements.txt
3. Run the Model
Use the following command to run the experiment. Adjust the variables as needed:

{model_name}: Specify the LLM to use (options listed in _agent.py_).
{output_folder_of_model}: Name of the folder where the output will be saved.
{number_of_trajectories}: Number of trajectories the robot will execute.
--translated True: Use this flag for the Arabic dataset; omit for the English dataset.
cd nav_src
python NavGPT.py --llm_model_name {model_name} \
  --output_dir ../datasets/R2R/exprs/{output_folder_of_model} \
  --val_env_name R2R_val_unseen_instr \
  --iters {number_of_trajectories} {--translated True}
Example

To run an experiment using the Llama 3.1 8B model with the Arabic dataset and a shortened annotations directory (R2R_val_unseen_instr_100):

cd nav_src
python NavGPT.py --llm_model_name custom-llama_3.1_8B \
  --output_dir ../datasets/R2R/exprs/llama_3.1_8B_ar \
  --val_env_name R2R_val_unseen_instr_100 \
  --iters 100 --translated True
Experiments

Below are the experiments conducted for our project, ensuring consistent comparisons between models and datasets:

Experiment Name	LLM (via Azure AI)	Dataset
custom-gpt	GPT-4o-mini	English, Arabic
custom-llama_3.1_8B	Llama-3-1-8B-Instruct	English, Arabic
custom-phi	Phi medium 14B Instruct (4K or 128K context length)	English, Arabic
Acknowledgments

We thank the contributors of the NavGPT repository for their open-source efforts, which were instrumental to the success of our project.

