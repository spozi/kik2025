FROM ubuntu:22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install dependencies
# RUN apt-get update && apt-get install -y \
#     curl \
#     default-mariadb-client \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository universe \
    && add-apt-repository multiverse \
    && apt-get update && apt-get install -y \
    curl \
    mariadb-server \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN curl -o /miniconda.sh -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh \
    && chmod +x /miniconda.sh \
    && /miniconda.sh -b -p /opt/conda \
    && rm /miniconda.sh

# Set path for conda
ENV PATH="/opt/conda/bin:$PATH"

# Create and set the working directory
WORKDIR /app

# # Copy environment file and create conda environment
# COPY environment.yml /app/
# RUN conda env create -f /app/environment.yml && conda clean --all -y

# Activate environment
ENV CONDA_DEFAULT_ENV=flask_env
ENV PATH="/opt/conda/envs/flask_env/bin:$PATH"

# Expose the Flask default port
EXPOSE 5000

# Set volume for app folder
VOLUME ["/app"]
