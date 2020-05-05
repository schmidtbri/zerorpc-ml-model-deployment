# ZeroRPC ML Model Deployment

![Test and Build](https://github.com/schmidtbri/zerorpc-ml-model-deployment/workflows/Test%20and%20Build/badge.svg)
![Build Docker Image](https://github.com/schmidtbri/zerorpc-ml-model-deployment/workflows/Build%20Docker%20Image/badge.svg)

Deploying an ML model in a ZeroRPC service.

This code is used in this [blog post]().

## Requirements
Docker

## Installation 
The Makefile included with this project contains targets that help to automate several tasks.

To download the source code execute this command:

```bash
git clone https://github.com/schmidtbri/zerorpc-ml-model-deployment
```

Then create a virtual environment and activate it:

```bash
# go into the project directory
cd zerorpc-ml-model-deployment

make venv

source venv/bin/activate
```

Install the dependencies:

```bash
make dependencies
```

Start the development server:
```bash
export PYTHONPATH=./
export APP_SETTINGS=ProdConfig
python model_zerorpc_service/service.py
```

## Running the Unit Tests
To run the unit test suite execute these commands:
```bash
# first install the test dependencies
make test-dependencies

# run the test suite
make test

# clean up the unit tests
make clean-test
```

## Docker
To build a docker image for the service, run this command:
```bash
docker build -t model-zerorpc-service:latest .
```

To run the image, execute this command:
```bash
docker run -d -p 4242:4242 --env APP_SETTINGS=ProdConfig model-zerorpc-service
```

To watch the logs coming from the image, execute this command:
```bash
docker logs $(docker ps -lq)
```

To get the latest build of this image from Dockerhub, execute this command:

```bash
docker pull bschmidt135/zerorpc-ml-model-deployment
```