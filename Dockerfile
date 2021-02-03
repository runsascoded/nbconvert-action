ARG PYTHON_VERSION=3.8.6
FROM python:${PYTHON_VERSION}
RUN pip install --upgrade pip
RUN pip install nbformat nbconvert jupyter papermill
RUN jupyter kernelspec list
ADD args_parser.py convert.py run.py /
ENV PATH=.:$PATH
# pip cache will go here (even when $HOME is set to /github/home), avoiding warnings about the cache dir not being owned by the current user
ENV XDG_CACHE_HOME=/root
ENTRYPOINT ["/convert.py"]
