FROM python:3.8
RUN pip install --upgrade pip
RUN pip install requests==2.23.0 nbformat==4.4.0 nbconvert==5.6.1
ADD convert.py /
ENTRYPOINT ["python","/convert.py"]