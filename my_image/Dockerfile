# Choose a docker template
# This will set what OS, CUDA, and perhaps even packages / python versions 
# you can preemptly have. You can find more templates in 
# ex: FROM python
FROM --platform=linux/amd64 nvidia/cuda:11.0.3-devel-ubuntu18.04

# Set default shell to /bin/bash
SHELL ["/bin/bash", "-cu"]

# NOTE: IF YOU ARE NOT USING THE NFS FEEL FREE TO REMOVE THE FOLLOWING 2 INSTRUCTIONS
# Setup your user profile with the right group permission to access NFS folder
# For the RUN command that sets up the ids and names you would need fill out the .env file
WORKDIR /
# Find your username by running `id -un` on HaaS and fill it here
ENV USER_NAME=halevy
RUN --mount=type=secret,id=my_env source /run/secrets/my_env && \
    groupadd -g ${GROUP_ID} ${GROUP_NAME} && \
    useradd -rm -d /home/${USER_NAME} -s /bin/bash -g ${GROUP_ID} -u ${USER_ID} ${USER_NAME} && \
    chown ${USER_ID} -R /home/${USER_NAME} && \
    # Change the password
    echo -e "${USER_NAME}\n${USER_NAME}" | passwd ${USER_NAME} && \
    usermod -a -G ${GROUP_NAME} ${USER_NAME}

# Set some basic ENV vars for readability
# NOTE: IF YOU ARE NOT USING THE NFS FEEL FREE TO MAKE THE FOLLOWING HOME VAR JUST ROOT
ENV HOME=/home/${USER_NAME}
ENV CONDA_PREFIX=${HOME}/.conda
ENV CONDA=${CONDA_PREFIX}/condabin/conda
ENV REPO_DIR=${HOME}/flextape

# Install dependencies
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
        build-essential \
        cmake \
        g++-4.8 \
        git \
        curl \
        vim \
        unzip \
        wget \
        tmux \
        screen \
        ca-certificates \
        apt-utils \
        libjpeg-dev \
        libpng-dev

# WORKDIR instruction sets the directory the following instructions should be run from
WORKDIR ${HOME}

# Install conda (optional)
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
RUN bash miniconda.sh -b -p ${CONDA_PREFIX}
RUN ${CONDA} config --set auto_activate_base false
RUN ${CONDA} init bash
RUN ${CONDA} create --name myenv python=3.10

# Git configuration (optional, you can also use a repo saved in the NFS)
RUN --mount=type=secret,id=my_env source /run/secrets/my_env && \
	git config --global user.name "Karina Halevy"
RUN --mount=type=secret,id=my_env source /run/secrets/my_env && \
	git config --global user.email "karina.halevy@gmail.com"
# RUN git config --global pull.rebase false

# Clone your github repo (optional)
RUN --mount=type=secret,id=my_env source /run/secrets/my_env && \
	git clone https://${GITHUB_PERSONAL_TOKEN}@github.com/${GITHUB_USERNAME}/flextape.git
# Make this repo your WORKDIR
WORKDIR ${REPO_DIR}/REMEDI-main

# Setup github repo dependencies
# Note that, you cannot activate an environment with the RUN command, as each RUN command is like a new session.
# Thus we instead call conda at the beginning of the pip or python command the way shown here:
RUN ${CONDA} install black
RUN ${CONDA} install isort
RUN ${CONDA} install mypy
RUN ${CONDA} install pytest
RUN ${CONDA} install types-requests
RUN ${CONDA} run -n myenv pip install git+https://github.com/davidbau/baukit
RUN ${CONDA} run -n myenv pip install accelerate
RUN ${CONDA} run -n myenv pip install dataclasses_json
RUN ${CONDA} run -n myenv pip install datasets
RUN ${CONDA} run -n myenv pip install invoke
RUN ${CONDA} run -n myenv pip install jupyter
RUN ${CONDA} run -n myenv pip install jupyter_http_over_ws
RUN ${CONDA} run -n myenv pip install matplotlib
RUN ${CONDA} run -n myenv pip install nltk
RUN ${CONDA} run -n myenv pip install requests
RUN ${CONDA} run -n myenv pip install scikit-learn==1.0.2
RUN ${CONDA} run -n myenv pip install scipy==1.7.3
RUN ${CONDA} run -n myenv pip install seaborn
RUN ${CONDA} run -n myenv pip install spacy
RUN ${CONDA} run -n myenv pip install tqdm
RUN ${CONDA} run -n myenv pip install transformers
RUN ${CONDA} run -n myenv pip install torch
RUN ${CONDA} run -n myenv pip install wget
RUN ${CONDA} run -n myenv pip install jsonlines

WORKDIR ${REPO_DIR}
# Install OpenSSH for MPI to communicate between containers
RUN apt-get update && apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd
# RUN echo 'root:root' | chpasswd
RUN sed -i 's/#*PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
# SSH login fix. Otherwise user is kicked off after login
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd
ENV NOTVISIBLE="in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
EXPOSE 22

# Install the Run:AI Python library and its dependencies
RUN ${CONDA} run -n myenv pip install runai prometheus_client==0.7.1

# Prepare the NFS mount folder
RUN mkdir /mnt/nlpdata1
RUN mkdir /mnt/scratch

# To rebuild from this point on (e.g. checking out a branch, pulling ...) and 
# not have to rerun heavy system installation change a dummy arg as shown in build.sh
ARG DUMMY=unknown
RUN DUMMY=${DUMMY}
RUN git pull
RUN git checkout main
RUN git pull

# The ENTRYPOINT describes which file to run once the node is setup.
# This can be your experiment script
COPY ./entrypoint.sh .

# NOTE: IF YOU ARE NOT USING THE NFS FEEL FREE TO REMOVE THE FOLLOWING 2 INSTRUCTIONS
# Changing the ownership of the /home/USER folder, so that the files created by root can be accesible (e.g. git cloned repo)
# Otherwise by default, they are owned by root
RUN --mount=type=secret,id=my_env source /run/secrets/my_env && \
	chown ${USER_ID} -R /home/${USER_NAME} 
    
# Switch to user instead of root for NFS + home directory access
USER ${USER_NAME}

RUN chmod +x ./entrypoint.sh
# ENTRYPOINT ["/usr/sbin/sshd", "-D"] # useful if you are **not** using the USER command and using the image just as root
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
