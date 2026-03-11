FROM continuumio/miniconda3

RUN apt-get update --yes && apt-get install --yes tmux vim less

COPY environment-*.yaml .
RUN conda env create --file environment-dev.yaml
RUN #conda env create --file environment-prod.yaml
RUN #conda env create --file environment-dev-nc4-serial.yaml

WORKDIR /opt
RUN git clone --depth 1 https://github.com/UXARRAY/uxarray.git

WORKDIR /opt/project

# Activate environment by default
RUN echo "conda activate regrid-wrapper-dev" >> ~/.bashrc
