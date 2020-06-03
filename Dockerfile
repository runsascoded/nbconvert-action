FROM python:3.8
RUN pip install --upgrade pip
RUN pip install nbformat==4.4.0 nbconvert==5.6.1 jupyter-client ipykernel
RUN python -m ipykernel install --name 3.8.2
RUN jupyter kernelspec list
ADD args_parser.py convert.py run.py /
ENTRYPOINT ["/convert.py"]