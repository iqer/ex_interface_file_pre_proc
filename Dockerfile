FROM ubuntu:22.04

RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list &&  \
    sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list &&  \
    apt-get update --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-dev ghostscript python3 python3-pip
COPY .  /app/
WORKDIR /app/
RUN pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD python3 main.py