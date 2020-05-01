FROM python:3.7

MAINTAINER Brian Schmidt "6666331+schmidtbri@users.noreply.github.com"

WORKDIR ./service

COPY ./model_zerorpc_service ./model_zerorpc_service
COPY ./Makefile ./Makefile
COPY ./requirements.txt ./requirements.txt

RUN make dependencies

ENV PATH="./:$PATH"
ENV PYTHONPATH "./"

CMD [ "gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:80", "model_zerorpc_service:app" ]
