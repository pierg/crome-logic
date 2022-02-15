# using ubuntu LTS version
FROM ubuntu:latest AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install --no-install-recommends -y  \
    curl \
    g++ \
    libclang-dev \
    zlib1g \
    openjdk-13-jdk \
    cmake \
    make \
    libboost-dev \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-iostreams-dev \
    zlib1g-dev \
    openjdk-13-jdk \
    gnupg2 \
    unzip \
    git \
    ca-certificates \
    wget \
    build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

RUN wget https://github.com/graalvm/graalvm-ce-builds/releases/download/vm-21.1.0/graalvm-ce-java11-linux-amd64-21.1.0.tar.gz
RUN tar -C /usr/lib/jvm/ -zxvf graalvm-ce-java11-linux-amd64-21.1.0.tar.gz
RUN mv /usr/lib/jvm/graalvm-ce-java11-21.1.0/ /usr/lib/jvm/java-11-graalvm/
RUN cd /usr/lib/jvm && ln -s java-11-graalvm graalvm
RUN /usr/lib/jvm/java-11-graalvm/bin/gu install native-image


WORKDIR /home

RUN git clone https://github.com/meyerphi/strix.git
WORKDIR /home/strix
RUN git submodule init
RUN git submodule update
RUN cargo dist build


#
#RUN apt-get update && apt-get install --no-install-recommends -y  \
#    python3.10  \
#    python3.10-dev  \
#    python3.10-venv  \
#    python3-pip  \
#    python3-wheel  && \
#	apt-get clean && rm -rf /var/lib/apt/lists/*



CMD ["bash"]
