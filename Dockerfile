FROM python:3.8
RUN pip install --upgrade pip
RUN pip install nbformat==4.4.0 nbconvert==5.6.1 jupyter-client ipykernel
RUN python -m ipykernel install --user --name 3.8.2
ADD convert.py run.py /
ENTRYPOINT ["python","/convert.py"]