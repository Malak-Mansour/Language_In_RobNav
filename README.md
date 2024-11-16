# Does Language Affect Reasoning Tasks in Robotic Navigation?

## Introduction
This is the repository of our AI701 course project at MBZUAI.

We are inferencing different LLMs with the Arabic and English datasets (in this repository) to see if language affects the reasoning capabilities of the LLMs by comparing the NavGPT (https://github.com/GengzeZhou/NavGPT/tree/master) performance results.


## Setup instructions
Run the following commands on Linux terminal or Ubuntu (WSL) for Windows:

If WSL, run the following block first:
<pre>
<code>
  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash Miniconda3-latest-Linux-x86_64.sh
  source ~/.bashrc
  conda --version
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>

Run the following to setup the environment and install the requirements:
<pre>
<code>
  conda create --name NavGPT python=3.9
  conda activate NavGPT
  pip install -r requirements.txt
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>

Then paste the following and adjust the variables depending on 
- {model_name}: which LLM you are running (the list is in _agent.py_)
- {output_folder_of_model}: what you want to call the folder that the output results are saved into
- {number_of_trajectories}: number of trajectories that the robot will take from the map
- {True_or_False}: True if you want to use the Arabic translated dataset, False otherwise

<pre>
<code>
  cd nav_src
  python NavGPT.py --llm_model_name {model_name} \
    --output_dir ../datasets/R2R/exprs/{output_folder_of_model} \
    --val_env_name R2R_val_unseen_instr \
    --iters {number_of_trajectories} --translated {True_or_False}
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>



Here is an example of an experiment with Llama 3.1 8B model, Arabic dataset, and using _R2R_val_unseen_instr_100_: the shortened version of the annotations directory that contains the translated scene for inference:
<pre>
<code>
 cd nav_src
  python NavGPT.py --llm_model_name custom-llama_3.1_8B \
    --output_dir ../datasets/R2R/exprs/llama_3.1_8B_ar \
    --val_env_name R2R_val_unseen_instr_100 \
    --iters 100 --translated True
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>


## Experiments
For our paper, we ran the following experiments to perform consistent comparisons

| Experiment Name | LLM                      | Dataset             |
|-----------------|--------------------------|---------------------|
| custom-gpt      | GPT-4o-mini              | English and Arabic  |
| custom-llama_3.1_8B    | Llama-3-1-8B-Instruct   | English and Arabic  |
| custom-phi    | Phi medium 14B Instruct (4K or 128K ?)  | English and Arabic  |

