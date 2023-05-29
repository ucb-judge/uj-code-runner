FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.8

# Include common tools
RUN yum install -y bc
RUN yum install -y procps-ng

# Include C++ compiler
RUN yum install -y gcc-c++ epel-release centos-release-scl clang-tools-extra
# Include Java 11
RUN yum install -y java-17-amazon-corretto-devel
# Include Python 3.8
# RUN yum install -y python

# Copy function code
COPY app.py ./

# Copy Scripts for each language
RUN mkdir ./cpp 
COPY cpp ./cpp

RUN mkdir ./java
COPY java ./java

RUN mkdir ./python
COPY python ./python

# app.handler is the name of the handler function in the code, it will be overwritten by the template for each language
CMD ["app.handler"]


