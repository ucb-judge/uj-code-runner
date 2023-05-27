FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.8

COPY app.py ./
# Include C++ compiler
RUN yum install -y gcc-c++ epel-release centos-release-scl clang-tools-extra


# You can overwrite command in `serverless.yml` template
CMD ["app.handler"]
