# Language_In_RobNav
AI701 Project

https://github.com/GengzeZhou/NavGPT/tree/master

Run the following commands on Linux terminal or Ubuntu (WSL) for Windows:

<pre>
  conda create --name NavGPT python=3.9
  conda activate NavGPT
  pip install -r requirements.txt
</pre>

<pre>
  cd nav_src
  python NavGPT.py --llm_model_name {model_name} \
    --output_dir ../datasets/R2R/exprs/{output_folder_of_model} \
    --val_env_name R2R_val_unseen_instr \
    --iters {number_of_trajectories} --translated {True_or_False}
</pre>

Example
<pre>
  cd nav_src
  python NavGPT.py --llm_model_name custom-mistral \
    --output_dir ../datasets/R2R/exprs/mistral_ar \
    --val_env_name R2R_val_unseen_instr_100 \
    --iters 100 --translated True
</pre>
