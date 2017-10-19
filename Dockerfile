# OSはCentOS
FROM centos:latest
RUN  export PYTHONIOENCODING="utf-8"
# 各パッケージをインストール
# pipやvirtualenvインストールも想定しています。

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

# Python3.5.2をインストール
# Python3.5.2をダウンロード
WORKDIR /root
RUN wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
RUN tar xzvf Python-3.5.2.tgz

# makeでインストール
WORKDIR ./Python-3.5.2
RUN ./configure --with-threads
RUN make install

# pipインストール(最新版)
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py

# 必要なものインストール
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

EXPOSE 80

# 環境変数の指定
# Docker コンテナで export NAME=World した状態になる
ENV NAME World

