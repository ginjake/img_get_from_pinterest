# OSはCentOS
FROM centos:latest
# 各パッケージをインストール

RUN yum -y update
RUN yum -y groupinstall "Development Tools"
RUN yum -y install \ 
           kernel-devel \
           kernel-headers \
           gcc-c++ \
           patch \
           libyaml-devel \
           libffi-devel \
           autoconf \
           automake \
           make \
           libtool \
           bison \
           tk-devel \
           zip \
           wget \
           tar \
           gcc \
           zlib \
           zlib-devel \
           bzip2 \
           bzip2-devel \
           readline \
           readline-devel \
           sqlite \
           sqlite-devel \
           openssl \
           openssl-devel \
           git \
           gdbm-devel \
           python-devel  \
           locales \
           locales-all \
           language-pack-ja \


# install pyenv
WORKDIR /root

RUN curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
ENV PATH ~/.pyenv/bin:$PATH
RUN echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile
RUN source ~/.bash_profile

RUN pyenv install 3.6.0
RUN pyenv global 3.6.0
ENV PATH /root/.pyenv/versions/3.6.0/bin/:$PATH


ENV LANG=ja_JP.UTF-8  
ENV LANGUAGE=ja_JP:ja  
ENV LC_ALL=ja_JP.UTF-8
ENV PYTHONIOENCODING utf-8

# pipインストール(最新版)
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

# 必要なものインストール
RUN pip install virtualenv
RUN pip install beautifulsoup4
RUN pip install jupyter
RUN pip install Pillow
RUN pip install requests
RUN pip install urllib3

# コンテナのワークディレクトリの指定
WORKDIR /app

# ローカルのカレントディレクトリの中身を全て コンテナのワークディレクトリにコピーする
# コンテナ実行時ではなく、イメージ作成時にコピーされる
ADD . /app

