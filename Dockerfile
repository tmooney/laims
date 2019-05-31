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
        vim

# Install LAIMS
RUN pip install --upgrade pip
WORKDIR /tmp/laims
COPY . ./
RUN pip install .

WORKDIR /etc/laims/
COPY prod.json ./

# BASH PROFILE
WORKDIR /etc/profile.d/
COPY /etc/profile.d/laims.sh ./

# CLEANUP
WORKDIR /tmp/
RUN rm -rf laims/

# ENV
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    MGI_NO_GAPP=1 \
    LAIMS_CONFIG=/etc/laims/prod.json
WORKDIR /
