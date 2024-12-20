FROM kbase/kbase:sdkbase2.latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

# Here we install a python coverage tool and an
# https library that is out of date in the base image.

RUN pip install coverage

# update security libraries in the base image
#RUN pip install cffi --upgrade \
#    && pip install pyopenssl --upgrade \
#    && pip install ndg-httpsclient --upgrade \
#    && pip install pyasn1 --upgrade \
#    && pip install requests --upgrade \
#    && pip install 'requests[security]' --upgrade

# -----------------------------------------
WORKDIR /kb/module
# Install Trimmomatic
RUN curl http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.36.zip -o Trimmomatic-0.36.zip && \
    unzip Trimmomatic-0.36.zip


COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module


RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
