# Modelarts 
*ModelArts is a one-stop development platform for AI developers. With data preprocessing, distributed training, automated model building and on-demand model deployment, ModelArts helps AI developers build models quickly and manage the AI development lifecycle.*

*ModelArts integrates the open-source Jupyter Notebook to provide you with online interactive development and debugging environments. You can use the Notebook on the ModelArts management console to compile and debug code and train models based on the code, without concerning installation and configurations.*

## Create custom environment for ModelArts Notebooks

### By custum script for Python 3.10.0 
Open a terminal in the Notebbok
```shell
wget -O - https://raw.githubusercontent.com/Hasardine/FlexibleEngine/main/ModelArts/custom_env_py310.sh | bash
```

### Details 
Open a terminal in the Notebbok 
Create the conda environment
```shell
conda create --quiet --yes -n my-env python=3.10.0
#List all conda environments
conda info --envs
```

Source into it and install 
```shell
source /home/ma-user/anaconda3/bin/activate /opt/conda/envs/my-env
```
