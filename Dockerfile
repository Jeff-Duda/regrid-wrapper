FROM continuumio/miniconda3

RUN apt-get update --yes && apt-get install --yes tmux vim less

RUN conda install -c conda-forge mamba

COPY environment-*.yaml .
RUN mamba env create --file environment-dev.yaml
RUN mamba env create --file environment-uxarray.yaml

#WORKDIR /opt
#RUN git clone --depth 1 https://github.com/UXARRAY/uxarray.git

WORKDIR /opt/project

# Activate environment by default
RUN echo "conda activate regrid-wrapper-dev" >> ~/.bashrc
