FROM ubuntu:22.04

COPY . /app/
WORKDIR /app
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list &&  \
    sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list &&  \
    apt-get update --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 python3-pip && \
    pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    rm -rf /root/.cache/pip/* \
CMD python3 proc_ex_sz.py