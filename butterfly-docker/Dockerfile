FROM ubuntu:latest

ENV DEBIAN_FRONTEND  noninteractive
ENV PYTHONUNBUFFERED true
ENV VIRTUAL_ENV      /usr/local/virtualenv
ENV PATH             $VIRTUAL_ENV/bin:$PATH
ENV PYTHONPATH       $PYTHONPATH:$VIRTUAL_ENV/lib/python2.7/site-packages
ENV HOME             /root
RUN echo 'source /usr/local/virtualenv/bin/activate' >> /etc/bash.bashrc

RUN apt-get update \
  && apt-get --yes dist-upgrade \
  && apt-get --yes install \
    apt-transport-https \
    aptitude \
    bash \
    bash-completion \
    build-essential \
    ca-certificates \
    curl \
    git \
    gnupg2 \
    pandoc \
    htop \
    cmake \
    less \
    openssh-client \
    libc6-dev \
    libevent-dev \
    libffi-dev \
    libgit2-dev \
    libmysqlclient-dev \
    libnacl-dev \
    libnacl-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libzmq3-dev \
    emacs \
    openssl \
    pkg-config \
    python-pip \
    python2.7 \
    python2.7-dev \
    redis-tools \
    rng-tools \
    rsync \
    software-properties-common \
    telnet \
    unrar \
    vim \
    virtualenvwrapper \
    wget \
    zip \
  && rm -rf /var/lib/apt/lists/*

RUN test -f "${VIRTUAL_ENV}" || pip install virtualenv \
  && mkdir -p "${VIRTUAL_ENV}" \
  && virtualenv "${VIRTUAL_ENV}" \
  && pip install -U pip

WORKDIR /root
