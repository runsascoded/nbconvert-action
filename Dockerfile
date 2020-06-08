FROM python:3.8
RUN pip install --upgrade pip
RUN pip install nbformat==4.4.0 nbconvert==5.6.1 jupyter-client ipykernel papermill
RUN python -m ipykernel install --name 3.8.2
RUN jupyter kernelspec list
ADD args_parser.py convert.py run.py /
ENV PATH=.:$PATH
# pip cache will go here (even when $HOME is set to /github/home), avoiding warnings about the cache dir not being owned by the current user
ENV XDG_CACHE_HOME=/root
ENTRYPOINT ["/convert.py"]
