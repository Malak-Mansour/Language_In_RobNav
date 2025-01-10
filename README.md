# Does Language Affect Reasoning Tasks in Robotic Navigation?

This repository explores the role of language in robotic navigation tasks, focusing on reasoning and action planning using advanced language models. It examines the performance of Arabic and English in Vision-Language Navigation (VLN) tasks.

## Prerequisites 
### Microsoft Azure account
A Microsoft Azure account is required to set up and run the experiments in this project. Once you have setup your account visit the [Azure AI portal](https://ai.azure.com/) and deploy your model.

You will need the ENDPOINT URL and API key for your deployed model. Add them to your environment variables: 
<pre>
<code>
  # prepare your Endpoint URL and API key (for linux)
  export ENDPOINT_URL="{ENDPOINT-URL}"
  export API_KEY="{API-KEY}"

  # prepare your Endpoint URL and API key (for windows)
  set ENDPOINT_URL="{ENDPOINT-URL}"
  set API_KEY="{API-KEY}"
</code>
</pre>

### Installation
Run the following to setup the conda environment and install the requirements:
<pre>
<code>
  conda create --name NavGPT python=3.9
  conda activate NavGPT
  pip install -r requirements.txt
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>

## Usage 
To Run the experiments please run the following code, 
- {model_name}: your deployed model name. Use "custom-gpt" for any openai model
- {output_folder_of_model}: what you want to call the folder that the output results are saved into
- {number_of_trajectories}: number of trajectories that the robot will take from the map
- {--translated}: write --translated if you want to use the Arabic translated dataset, and remove it if you will be using the english dataset

<pre>
<code>
  cd nav_src
  python NavGPT.py --llm_model_name {model_name} \
    --output_dir ../datasets/R2R/exprs/{output_folder_of_model} \
    --val_env_name R2R_val_unseen_instr \
    --iters {number_of_trajectories} {--translated}
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>



Here is an example of an experiment with Llama 3 8B model, Arabic dataset, and using _R2R_val_unseen_instr_100_: the shortened version of the annotations directory that contains the translated scene for inference:
<pre>
<code>
 cd nav_src
  python NavGPT.py --llm_model_name custom-llama_3_8B \
    --output_dir ../datasets/R2R/exprs/llama_3_8B_ar \
    --val_env_name R2R_val_unseen_instr_100 \
    --iters 100 --translated 
</code>
<button onclick="copyToClipboard(this.previousElementSibling.innerText)"></button>
</pre>


## Experiments
For our paper, we ran the following experiments to perform consistent comparisons

| Experiment Name | LLM (API access from https://ai.azure.com/)                     | Dataset             |
|-----------------|--------------------------|---------------------|
| custom-gpt      | GPT-4o mini              | English and Arabic  |
| custom-llama_3_8B    | Llama 3 8B Instruct   | English and Arabic  |
| custom-phi    | Phi medium 14B Instruct 128K  | English and Arabic  |
| custom-jais    | Jais 30B  | English and Arabic  |

## Acknowledgement
A large part of the code is used from [NavGPT](https://github.com/GengzeZhou/NavGPT). Many thanks for their wonderful work.

