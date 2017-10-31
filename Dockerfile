FROM ubuntu:16.04
LABEL maintainer "Dave Larson <delarson@wustl.edu>"

RUN apt-get update -qq \
    && apt-get -y install apt-transport-https \
    && apt-get update -qq \
    && apt-get -y install --no-install-recommends \
        python \
        python-pip \
    && pip install --process-dependency-links . \
    && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
