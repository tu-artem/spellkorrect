FROM pytorch/pytorch

COPY . /workspace

WORKDIR /workspace

RUN ["pip" , "install", "-r", "requirements-docker.txt"]

CMD [ "uvicorn", "app:app", "--reload", "--host", "0.0.0.0" ]
