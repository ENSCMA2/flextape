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
RUN ${CONDA} create -n myenv \
_libgcc_mutex=0.1=main \
argon2-cffi=20.1.0=py38h7b6447c_1 \
async_generator=1.10=py_0 \
attrs=20.3.0=pyhd3eb1b0_0 \
backcall=0.2.0=py_0 \
blas=1.0=mkl \
bleach=3.2.1=py_0 \
bokeh=2.2.3=py38_0 \
boto3=1.16.0=py_0 \
botocore=1.19.1=py_0 \
brotlipy=0.7.0=py38h7b6447c_1000 \
ca-certificates=2020.10.14=0 \
certifi=2020.6.20=py38_0 \
cffi=1.14.3=py38he30daa8_0 \
chardet=3.0.4=py38_1003 \
click=7.1.2=py_0 \
cloudpickle=1.6.0=py_0 \
cryptography=3.1.1=py38h1ba5d50_0 \
cudatoolkit=10.1.243=h6bb024c_0 \
cycler=0.10.0=py38_0 \
cytoolz=0.11.0=py38h7b6447c_0 \
dask=2.30.0=py_0 \
dask-core=2.30.0=py_0 \
dbus=1.13.18=hb2f20db_0 \
decorator=4.4.2=py_0 \
defusedxml=0.6.0=py_0 \
distributed=2.30.0=py38_0 \
docutils=0.15.2=py38_0 \
entrypoints=0.3=py38_0 \
expat=2.2.10=he6710b0_2 \
fontconfig=2.13.0=h9420a91_0 \
freetype=2.10.4=h5ab3b9f_0 \
fsspec=0.8.3=py_0 \
glib=2.66.1=h92f7085_0 \
gst-plugins-base=1.14.0=hbbd80ab_1 \
gstreamer=1.14.0=hb31296c_0 \
heapdict=1.0.1=py_0 \
icu=58.2=he6710b0_3 \
idna=2.10=py_0 \
importlib-metadata=2.0.0=py_1 \
importlib_metadata=2.0.0=1 \
iniconfig=1.1.1=py_0 \
intel-openmp=2020.2=254 \
ipykernel=5.3.4=py38h5ca1d4c_0 \
ipython=7.18.1=py38h5ca1d4c_0 \
ipython_genutils=0.2.0=py38_0 \
ipywidgets=7.5.1=py_1 \
jedi=0.17.2=py38_0 \
jinja2=2.11.2=py_0 \
jmespath=0.10.0=py_0 \
 joblib=0.17.0=py_0 \
jpeg=9b=h024ee3a_2 \
json5=0.9.5=py_0 \
jsonschema=3.2.0=py_2 \
jupyter=1.0.0=py38_7 \
jupyter_client=6.1.7=py_0 \
jupyter_console=6.2.0=py_0 \
jupyter_core=4.6.3=py38_0 \
jupyterlab=2.2.6=py_0 \
jupyterlab_pygments=0.1.2=py_0 \
jupyterlab_server=1.2.0=py_0 \
kiwisolver=1.3.0=py38h2531618_0 \
lcms2=2.11=h396b838_0 \
ld_impl_linux-64=2.33.1=h53a641e_7 \
libedit=3.1.20191231=h14c3975_1 \
libffi=3.3=he6710b0_2 \
libgcc-ng=9.1.0=hdf63c60_0 \
libgfortran-ng=7.3.0=hdf63c60_0 \
libpng=1.6.37=hbc83047_0 \
libsodium=1.0.18=h7b6447c_0 \
libstdcxx-ng=9.1.0=hdf63c60_0 \
libtiff=4.1.0=h2733197_1 \
libuuid=1.0.3=h1bed415_2 \
libxcb=1.14=h7b6447c_0 \
libxml2=2.9.10=hb55368b_3 \
locket=0.2.0=py38_1 \
lz4-c=1.9.2=heb0550a_3 \
markupsafe=1.1.1=py38h7b6447c_0 \
matplotlib=3.3.1=0 \
matplotlib-base=3.3.1=py38h817c723_0 \
mistune=0.8.4=py38h7b6447c_1000 \
mkl=2020.2=256 \
mkl-service=2.3.0=py38he904b0f_0 \
mkl_fft=1.2.0=py38h23d657b_0 \
mkl_random=1.1.1=py38h0573a6f_0 \
more-itertools=8.5.0=py_0 \
msgpack-python=1.0.0=py38hfd86e86_1 \
nbclient=0.5.1=py_0 \
nbconvert=6.0.7=py38_0 \
nbformat=5.0.8=py_0 \
ncurses=6.2=he6710b0_1 \
nest-asyncio=1.4.1=py_0 \
ninja=1.10.1=py38hfd86e86_0 \
nltk=3.5=py_0 \
notebook=6.1.4=py38_0 \
numpy=1.19.1=py38hbc911f0_0 \
numpy-base=1.19.1=py38hfa32c7d_0 \
olefile=0.46=py_0 \
openssl=1.1.1h=h7b6447c_0 \
packaging=20.4=py_0 \
pandas=1.1.3=py38he6710b0_0 \
pandoc=2.11=hb0f4dca_0 \
pandocfilters=1.4.2=py38_1 \
parso=0.7.0=py_0 \
partd=1.1.0=py_0 \
pcre=8.44=he6710b0_0 \
pexpect=4.8.0=py38_0 \
pickleshare=0.7.5=py38_1000 \
pillow=8.0.1=py38he98fc37_0 \
pip=20.2.3=py38_0 \
pluggy=0.13.1=py38_0 \
prometheus_client=0.8.0=py_0 \
prompt-toolkit=3.0.8=py_0 \
prompt_toolkit=3.0.8=0 \
psutil=5.7.2=py38h7b6447c_0 \
ptyprocess=0.6.0=py38_0 \
py=1.9.0=py_0 \
pycparser=2.20=py_2 \
pygments=2.7.2=pyhd3eb1b0_0 \
pyopenssl=19.1.0=py_1 \
pyparsing=2.4.7=py_0 \
pyqt=5.9.2=py38h05f1152_4 \
pyrsistent=0.17.3=py38h7b6447c_0 \
pysocks=1.7.1=py38_0 \
pytest=6.1.1=py38_0 \
python=3.8.5=h7579374_1 \
python-dateutil=2.8.1=py_0 \
pytz=2020.1=py_0 \
pyyaml=5.3.1=py38h7b6447c_1 \
pyzmq=19.0.2=py38he6710b0_1 \
qt=5.9.7=h5867ecd_1 \
qtconsole=4.7.7=py_0 \
qtpy=1.9.0=py_0 \
readline=8.0=h7b6447c_0 \
regex=2020.10.15=py38h7b6447c_0 \
requests=2.24.0=py_0 \
s3transfer=0.3.3=py38_0 \
scikit-learn=0.23.2=py38h0573a6f_0 \
scipy=1.5.2=py38h0b6359f_0 \
send2trash=1.5.0=py38_0 \
setuptools=50.3.1=py38h06a4308_1 \
sip=4.19.13=py38he6710b0_0 \
six=1.15.0=py_0 \
sortedcontainers=2.2.2=py_0 \
sqlite=3.33.0=h62c20be_0 \
tblib=1.7.0=py_0 \
terminado=0.9.1=py38_0 \
testpath=0.4.4=py_0 \
threadpoolctl=2.1.0=pyh5ca1d4c_0 \
tk=8.6.10=hbc83047_0 \
toolz=0.11.1=py_0 \
tornado=6.0.4=py38h7b6447c_1 \
tqdm=4.50.2=py_0 \
traitlets=5.0.5=py_0 \
typing_extensions=3.7.4.3=py_0 \
urllib3=1.25.11=py_0 \
wcwidth=0.2.5=py_0 \
webencodings=0.5.1=py38_1 \
wheel=0.35.1=py_0 \
widgetsnbextension=3.5.1=py38_0 \
xz=5.2.5=h7b6447c_0 \
yaml=0.2.5=h7b6447c_0 \
zeromq=4.3.3=he6710b0_3 \
zict=2.0.0=py_0 \
zipp=3.4.0=pyhd3eb1b0_0 \
zlib=1.2.11=h7b6447c_3 \
zstd=1.4.5=h9ceee32_0

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
WORKDIR ${REPO_DIR}

# Setup github repo dependencies
# Note that, you cannot activate an environment with the RUN command, as each RUN command is like a new session.
# Thus we instead call conda at the beginning of the pip or python command the way shown here:
RUN ${CONDA} run -n myenv pip install -r requirements.txt

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
ENTRYPOINT ["/bin/bash"]
