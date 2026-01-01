FROM ubuntu:20.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update --fix-missing
RUN apt-get install tzdata git tar \
        libx11-6 \
        libxi6 \
        x11-apps \
        ffmpeg \
        libsm6 \
        python3-pip \
        libxext6 -y

RUN apt install build-essential cmake vim-nox python3-dev -y 
RUN apt install wget curl sudo -y 
#RUN wget https://download.blender.org/release/Blender2.93/blender-2.93.6-linux-x64.tar.xz

## install code
#RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg && \
#install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/ && \
#sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list' && \
#rm -f packages.microsoft.gpg && \
#apt install -y apt-transport-https && \
#apt update -y && \
#apt install -y code # or code-insiders

# matplotlib visualisation
RUN apt-get -y install python3-tk


# create user
ENV USER=vinayaka

RUN useradd -u 1000 ${USER} && echo "${USER}:${USER}" | chpasswd && adduser ${USER} sudo
RUN mkdir -p /home/${USER} && chown -R ${USER}:${USER} /home/${USER}

COPY ./default_bash_rc /home/${USER}/.bashrc
COPY ./default_vim_rc /home/${USER}/.vimrc


USER ${USER}

RUN python3 -m pip install h5py
RUN python3 -m pip install pascal_voc_writer
RUN python3 -m pip install pypng


WORKDIR /home/${USER}

# install vim vundle
#RUN git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
#
#RUN git clone --recursive https://github.com/ycm-core/YouCompleteMe.git ~/.vim/bundle/YouCompleteMe
#
#WORKDIR /home/${USER}/.vim/bundle/YouCompleteMe
#
#RUN python3 install.py --clangd-completer
#
WORKDIR /home/${USER}


#RUN vim +PluginInstall +qall

# install blainder
COPY ./range_scanner.zip /home/${USER}

COPY ./blender-2.93.6-linux-x64.tar.xz /home/${USER}
RUN tar -xf blender-2.93.6-linux-x64.tar.xz

ENV PATH ${PATH}:/home/${USER}/blender-2.93.6-linux-x64
ENV PATH=${PATH}:/home/${USER}/.local/bin

RUN mkdir -p /home/${USER}/blender-2.93.6-linux-x64/2.93/scripts/addons_contrib/range_scanner

COPY --chown=${USER} ./range_scanner /home/${USER}/blender-2.93.6-linux-x64/2.93/scripts/addons_contrib/range_scanner

RUN ./blender-2.93.6-linux-x64/2.93/python/bin/python3.9 -m ensurepip
RUN /home/${USER}/blender-2.93.6-linux-x64/2.93/python/bin/python3.9 -m pip install --upgrade pip==22.0.4
RUN ./blender-2.93.6-linux-x64/2.93/python/bin/python3.9 -m pip install -r /home/${USER}/blender-2.93.6-linux-x64/2.93/scripts/addons_contrib/range_scanner/requirements.txt

# install blendtorch
RUN mkdir /home/${USER}/arbeitsraumerkundung/
COPY --chown=${USER} ./arbeitsraumerkundung/pytorch-blender /home/${USER}/arbeitsraumerkundung/pytorch-blender

RUN blender --background --python /home/${USER}/arbeitsraumerkundung/pytorch-blender/scripts/install_btb.py
RUN python3 -m pip install -r /home/${USER}/arbeitsraumerkundung/pytorch-blender/pkg_blender/requirements.txt

RUN pip3 install -e /home/${USER}/arbeitsraumerkundung/pytorch-blender/pkg_pytorch

RUN rm -rf /home/${USER}/arbeitsraumerkundung/pytorch-blender
