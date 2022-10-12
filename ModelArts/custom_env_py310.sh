#!/bin/bash
#Create env
conda create --quiet --yes -n my-env python=3.10.0
#source to env
source /home/ma-user/anaconda3/bin/activate /opt/conda/envs/my-env
#Mandatory package
pip install jupyter
python3 -m ipykernel install --user --name "my-custum-env"
> /home/ma-user/.local/share/jupyter/kernels/my-custum-env/kernel.json
cat <<EOT >> /home/ma-user/.local/share/jupyter/kernels/my-custum-env/kernel.json
{
 "argv": [
  "/opt/conda/envs/my-env/bin/python3",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "my-custum-env",
 "language": "python",
 "env": {
        "PATH": "/opt/conda/envs/my-env/bin/:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/",
        "http_proxy": "http://proxy-notebook.modelarts.com:8083",
        "https_proxy": "http://proxy-notebook.modelarts.com:8083",
        "ftp_proxy": "http://proxy-notebook.modelarts.com:8083",
        "HTTP_PROXY": "http://proxy-notebook.modelarts.com:8083",
        "HTTPS_PROXY": "http://proxy-notebook.modelarts.com:8083",
        "FTP_PROXY": "http://proxy-notebook.modelarts.com:8083"
        }
}
EOT