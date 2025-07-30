# To build the docker image:
#  docker build -t smiffer-image .
#
# To run it:
#  docker run -it smiffer-image
#  (opens a shell in the docker container, then you can use the software:
#   perfassess -h
# 

# Start from the Ubuntu 24.04 base image
FROM ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    pipx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure pipx binaries are in PATH
ENV PATH=/root/.local/bin:$PATH

# Clone the git repository
RUN git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git /opt/smiffer

# Install the Python tool using pipx
RUN pipx install /opt/smiffer

# Default command to run when starting the container
CMD ["bash"]

