FROM python:3

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y swig
RUN mkdir /home/docker/simple_cloud -p
RUN mkdir /home/docker/simple_cloud/run -p
RUN mkdir /home/docker/simple_cloud/logs -p
WORKDIR /home/docker/simple_cloud

COPY . /home/docker/simple_cloud

COPY requirements.txt /home/docker/simple_cloud/
COPY uwsgi.ini /home/docker/simple_cloud/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
