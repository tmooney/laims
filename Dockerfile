#########
# LAIMS #
#########

# Based on ... told by Broad to use this version
FROM broadinstitute/gatk:4.0.6.0

# MAINTAINER
LABEL maintainer ebelter@wustl.edu

# Build ARGs
ARG laims_config=/gscmnt/gc2802/halllab/ccdg_resources/laims/prod.json

# DEPS
RUN apt-get update -qq && \
    apt-get -y install --no-install-recommends \
        apt-transport-https \
        git \
        libnss-sss \
        rsync \
        vim \
        wget

# Install LAIMS
RUN pip install --upgrade pip
WORKDIR /tmp/laims
COPY . ./
RUN pip install .

# GATK 3.5
WORKDIR /opt/
COPY gatk/GenomeAnalysisTK-3.5-0-g36282e4.jar ./

# Cromwell 47
RUN wget https://github.com/broadinstitute/cromwell/releases/download/47/cromwell-47.jar && mv cromwell-47.jar /opt/cromwell.jar

# BASH PROFILE
WORKDIR /etc/profile.d/
COPY /etc/profile.d/laims.sh ./

# Templates
WORKDIR /usr/local/share/laims
COPY share/ ./

# CLEANUP
WORKDIR /tmp/
RUN rm -rf laims/

# ENV
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    MGI_NO_GAPP=1 \
    LAIMS_CONFIG="${laims_config}" \
    LSF_SERVERDIR=/opt/lsf9/9.1/linux2.6-glibc2.3-x86_64/etc \
    LSF_LIBDIR=/opt/lsf9/9.1/linux2.6-glibc2.3-x86_64/lib \
    LSF_BINDIR=/opt/lsf9/9.1/linux2.6-glibc2.3-x86_64/bin \
    LSF_ENVDIR=/opt/lsf9/conf
ENV PATH="${LSF_BINDIR}:${PATH}"

WORKDIR /
