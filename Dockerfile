FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------

# Temporary trick updating of SDK to latest develop commit inside image
RUN . /kb/dev_container/user-env.sh && cd /kb/dev_container/modules && \
  rm -rf kb_sdk && git clone https://github.com/kbase/kb_sdk -b develop && \
  cd /kb/dev_container/modules/kb_sdk && make && make deploy

# Insert apt-get instructions here to install
# any required dependencies for your module.

# RUN apt-get update

WORKDIR /kb/module

RUN curl http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.33.zip -o Trimmomatic-0.33.zip && \
    unzip Trimmomatic-0.33.zip

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work

WORKDIR /kb/module

RUN make

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
