#########
# LAIMS #
#########

# Based on ... told by Broad to use this version
FROM broadinstitute/gatk:4.0.6.0

# MAINTAINER
LABEL maintainer ebelter@wustl.edu

# DEPS
RUN apt-get update -qq && \
    apt-get -y install --no-install-recommends \
        apt-transport-https \
        libnss-sss \
        mysql-server \
        vim

# Install LAIMS
RUN pip install --upgrade pip
WORKDIR /tmp/laims
COPY . ./
RUN pip install .

# BASH PROFILE
WORKDIR /etc/profile.d/
COPY /etc/profile.d/laims.sh ./

# CLEANUP
WORKDIR /
RUN rm -rf /tmp/laims/

# ENV
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV MGI_NO_GAPP=1
