# Basded on ... told by Broad to use this version
FROM broadinstitute/gatk:4.0.6.0

# MAINTAINER
LABEL maintainer ebelter@wustl.edu

# DEPS
RUN apt-get update -qq && \
    apt-get -y install --no-install-recommends \
        apt-transport-https \
        libnss-sss \
        vim

# Install LAIMS
#WORKDIR /tmp/laims
WORKDIR /app/laims
COPY . ./
RUN pip install --upgrade pip && \
    pip install -e /app/laims .
RUN find . -type d -exec chmod 777 {} \; && \
      find . -type f -exec chmod 666 {} \;

# CLEANUP
WORKDIR /
#RUN rm -rf /tmp/laims/

# ENV
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
