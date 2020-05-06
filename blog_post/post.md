Title: A ZeroRPC ML Model Deployment
Date: 2020-05-04 09:26
Category: Blog
Slug: zerorpc-ml-model-deployment
Authors: Brian Schmidt
Summary: There are many different ways for two software processes to communicate with each other. When deploying a machine learning model, it's often simpler to isolate the model code inside of its own process. Any code that needs to use the model to make predictions then needs to communicate with the process that is running the model code to make predictions. This approach is easier than embedding the model code in the process that needs the predictions because it saves us the trouble of recreating the model's algorithm in the programming language of the process that needs the predictions. RPC calls are also used widely to connect code that is executing in different processes. In the last few years, the rise in popularity of microservice architectures has also caused the rise in popularity of RPC for integrating systems.

This blog post builds on the ideas started in
[three]({filename}/articles/a-simple-ml-model-base-class/post.md)
[previous]({filename}/articles/improving-the-mlmodel-base-class/post.md)
[blog posts]({filename}/articles/using-ml-model-abc/post.md).

In this blog post I'll show how to deploy the same ML model that we
deployed as a batch job in this [blog post]({filename}/articles/etl-job-ml-model-deployment/post.md),
as a task queue in this [blog post]({filename}/articles/task-queue-ml-model-deployment/post.md),
inside an AWS Lambda in this [blog post]({filename}/articles/lambda-ml-model-deployment/post.md),
as a Kafka streaming application in this [blog post]({filename}/articles/streaming-ml-model-deployment/post.md),
a gRPC service in this [blog post]({filename}/articles/grpc-ml-model-deployment/post.md),
as a MapReduce job in this [blog post]({filename}/articles/map-reduce-ml-model-deployment/post.md),
and as a Websocket service in this [blog post]({filename}/articles/websocket-ml-model-deployment/post.md).

The code in this blog post can be found in this [github
repo](https://github.com/schmidtbri/zerorpc-ml-model-deployment).

# Introduction

There are many different ways for two software processes to communicate
with each other. When deploying a machine learning model, it's often
simpler to isolate the model code inside of its own process. Any code
that needs to use the model to make predictions then needs to
communicate with the process that is running the model code to make
predictions. This approach is easier than embedding the model code in
the process that needs the predictions because it saves us the trouble
of recreating the model's algorithm in the programming language of the
process that needs the predictions. RPC calls are also used widely to
connect code that is executing in different processes. In the last few
years, the rise in popularity of microservice architectures has also
caused the rise in popularity of RPC for integrating systems.

RPC stands for Remote Procedure Call. A remote procedure is just a
function call that is executed in a different process from the process
that initiated the call. The input parameters for the call come from the
calling process and the result of the call is returned to the calling
process. The function call looks as if it was executed locally. RPC
therefore executes as a request-response protocol. The process that
initiates the call is called the client and the process that executes
the call is the server. RPC is useful when you want to call a function
that is not implemented in the local process and you don't want to worry
about the complexities of inter-process communication. RPC is similar to
but a lot simpler than REST and HTTP-based inter-process communication.

An RPC call follows a series of steps to complete the call. First, the
client code will call a piece of code called the "stub" in the client
process. The stub behaves like a normal function but actually calls the
remote procedure in the server. The stub then takes the parameters
provided by the client code and serializes them so that they can be
transported over the communication channel. The stub uses the
communication channel to communicate with the remote process, sending
the necessary information to execute the procedure. The server stub
receives the information and deserializes the parameters, then executes
the procedure. The series of steps are then executed in reverse order to
return the results of the procedure to the client code.

In previous blog posts we showed how to do RPC with a RESTful service
and a gRPC service. In this blog post we'll continue exploring the
options available to us for interprocess communication with a ZeroRPC
service that can host machine learning models.

# ZeroRPC

ZeroRPC is a simple RPC framework that works in many different
languages. ZeroRPC uses
[MessagePack](https://msgpack.org/index.html) for
parameter serialization and deserialization, and it uses
[ZeroMQ](https://zeromq.org/) for transporting data
between processes. ZeroRPC supports advanced features such as streamed
responses, heartbeats, and timeouts. The framework also supports
introspection of the service and exceptions.

The ZeroRPC framework uses the ZeroMQ messaging framework to transport
messages between processes. ZeroMQ is a high-performance low-level
messaging framework that can be used in many different types of
communication patterns. The ZeroRPC framework uses the ZeroMQ framework
in a request-response pattern to do RPC calls. ZeroMQ also supports the
publish-subscribe pattern along with other patterns. ZeroMQ is designed
to support highly distributed and concurrent applications. ZeroMQ works
in many different programming languages and in many operating systems.

The ZeroRPC framework uses the MessagePack format for serialization.
This format is similar to JSON but is binary, which makes it more space
efficient and allows for faster serialization and deserialization. The
MessagePack format is similar to the Protocol Buffer format that is used
by gRPC, but it allows us to serialize arbitrary data structures. This
is different from Protocol Buffers which require a schema for the data
to be serialized. MessagePack is also dynamically typed which makes
developing code with it faster and simpler, but lacks the documentation
and code generation features of Protocol Buffers.

# Package Structure

The service codebase is structured like this:

```
- model_zerorpc_service ( python package for the zerorpc service )
    -  __init__.py
    -  config.py
    -  ml_model_zerorpc_endpoint.py
    -  ml_model_manager.py
    -  service.py
-  scripts (scripts for testing the service)
-  tests (unit tests)
-  Dockerfile (used to build a docker image of the service)
-  Makefle
-  README.md
-  requirements.txt
-  setup.py
-  test_requirements.txt
```

This structure can be seen in the [github
repository](https://github.com/schmidtbri/zerorpc-ml-model-deployment).

# Installing the Model

Our aim for this blog post is to show how to build a ZeroRPC service
that is able to host any ML model that works with the MLModel base
class. To show how this can be done, we'll use the same model that we've
deployed in previous blog posts. To install the model into the Python
environment, execute this command:

```bash
pip install git+[https://github.com/schmidtbri/ml-model-abc-improvements](https://github.com/schmidtbri/ml-model-abc-improvements%5C)
```

This command installs the model code and parameters from the model's git
repository. To understand how the model code works, check out [this blog post]({filename}/articles/improving-the-mlmodel-base-class/post.md).
Once the model is installed, we can test it out by executing this Python
code in an interactive session:

```python
>>> from iris_model.iris_predict import IrisModel
>>> model = IrisModel()
>>> model.predict({"sepal_length":1.1, "sepal_width": 1.2, "petal_width": 1.3, "petal_length": 1.4})
{'species': 'setosa'}
```

The code above imports the class that implements the MLModel interface,
instantiates it, and sends the model object a prediction request. The
model successfully responds with a prediction for the flower species.

In order for the ZeroRPC service to find the model that we want to
deploy, we'll create a configuration module that points to the model's
package and module:

```python
class Config(dict):
    models = [{
        "module_name": "iris_model.iris_predict",
        "class_name": "IrisModel"
    }]
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/config.py#L4-L12).

This configuration gives us the flexibility to add and remove models
from the service dynamically. A service can host any number of models if
they are installed in the environment and added to the configuration.
The module\_name and class\_name fields in the configuration point to a
class that implements the MLModel interface, which allows the service to
make predictions using the model.

As in previous blog posts, we'll use a singleton object to manage the
ML model objects that will be used to make predictions. The class that
the singleton object is instantiated from is called ModelManager. The
class is responsible for instantiating MLModel objects, managing the
instances, returning information about the MLModel objects, and
returning references to the objects when needed. The code for the
ModelManager class can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/model_manager.py).
A complete explanation of the ModelManager class can be found in [this
blog
post]({filename}/articles/using-ml-model-abc/post.md).

# ZeroRPC Endpoint

In order to host a machine learning model, we have to handle incoming
prediction requests, produce responses for them, and integrate with the
ZeroRPC framework. The class described in this section will handle these
aspects of the service.

First, we'll declare the class:

```python
class MLModelZeroRPCCEndpoint(object):
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/ml_model_zerorpc_endpoint.py#L10).

Next, we'll add the code that will initialize the object when the class
is instantiated:

```python
def __init__(self, model_qualified_name):
    model_manager = ModelManager()
    model_instance = model_manager.get_model(model_qualified_name)

    if model_instance is None:
        raise ValueError("'{}' not found in ModelManager instance.".format(model_qualified_name))

    self._model = model_manager.get_model(model_qualified_name)
    self.__doc__ = "Predict with the {}.".format(self._model.display_name)
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/ml_model_zerorpc_endpoint.py#L19-L40).

The \_\_init\_\_ method has one argument called
"model\_qualified\_name" which tells the endpoint class which model it
will be hosting. The \_\_init\_\_ method first gets a reference to the
ModelManager singleton instance that is initialized when the service
starts up. Then we get a reference to the specific model that is being
hosted by this instance of the MLModelZeroRPCCEndpoint class. Next, we
check if the model reference is equal to None which happens when the
ModelManager can't find a model with the name requested, if there is no
model by the name we raise an exception. If the model exists, we save a
reference to it in the self variable which will make it easier to access
in the future. Lastly, we modify the docstring property of the self
variable which will cause the service to return it when doing
introspection, we'll see how this works later.

Now that we have an instance of the endpoint, we need to handle incoming
prediction requests:

```python
def __call__(self, data):
    prediction = self._model.predict(data=data)
    return prediction
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/ml_model_zerorpc_endpoint.py#L42-L47).

The code in the method is very simple, it receives a parameter called
"data" from the client, sends it to the model's predict method, and
returns the prediction object that is returned by the model. Behind the
scenes, the ZeroRPC framework is handling serialization and
deserialization, the connection between the client and the server, and
any exceptions raised by the server.

This class uses a special feature of Python which is the [callable
magic
method](https://www.journaldev.com/22761/python-callable-__call__).
The \_\_call\_\_ method is a special method that turns any instance of
the MLModelZeroRPCCEndpoint class into a callable, which allows
instances of the class to be used as functions or methods. This will be
useful later when we need to initialize a dynamic number of endpoints in
the gRPC service.

# ZeroRPC Service

Now that we have a model and a way to host the model within an endpoint,
we can go ahead and write the code that will create the service. Before
we can do that, we have to load the configuration:

```python
configuration = getattr(config, os.environ["APP_SETTINGS"])
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/service.py#L15-L16).

The configuration is loaded dynamically by importing a class from the
config.py module. The name of the class is received through an
environment variable called APP\_SETTINGS.

A ZeroRPC service is built as a class that provides methods that are
exposed to the outside world as RPC calls. The class that will become
the service is defined like this:

```python
class ModelZeroRPCService(object):
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/service.py#L19).

When the model service is started the \_\_init\_\_ method will be
executed:

```python
def __init__(self):
    self.model_manager = ModelManager()
    self.model_manager.load_models(configuration=configuration.models)

    for model in self.model_manager.get_models():
        endpoint = MLModelZeroRPCCEndpoint(model_qualified_name=model["qualified_name"])
        operation_name = "{}_predict".format(model["qualified_name"])
        setattr(self, operation_name, endpoint)
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/service.py#L22-L30).

The service starts by instantiating the ModelManager singleton, and
loading the models from the configuration. Next the service instantiates
one MLModelZeroRPCCEndpoint class for each model in the ModelManager and
attaches it to the "self" parameter with a dynamically created operation
name. The service method is mapped to the model's "predict" method by
the endpoint object that wraps it. The reason for this is so that we are
able to host any number of MLModel objects in the service, this code
allows us to attach them to the service object dynamically. At the end
of the initialization method, we have one service method for each model
that is hosted by the service.

The service is now able to receive prediction requests for the models
and return the predictions to the clients, but we can add some
functionality by exposing metadata about the models being hosted, the
get\_models method does this:

```python
def get_models(self):
    models = self.model_manager.get_models()
    return models
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/service.py#L32-L36).

The get\_models procedure returns a list of models available for use,
but does not return all of the metadata available for a model. To
provide all of the metadata for a model, we'll add the
get\_model\_metadata method:

```python
def get_model_metadata(self, qualified_name):
    model_metadata = self.model_manager.get_model_metadata(qualified_name=qualified_name)

    if model_metadata is not None:
        return model_metadata
    else:
        raise ValueError("Metadata not found for this model.")
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/model_zerorpc_service/service.py#L38-L44).

# Using the Service

To show now to use the service, we wrote a few scripts in the [scripts
folder](https://github.com/schmidtbri/zerorpc-ml-model-deployment/tree/master/scripts)
of the project. To execute the scripts we first have to start up the
service with these commands:

```bash
export PYTHONPATH=./
export APP_SETTINGS=ProdConfig
python model_zerorpc_service/service.py
```

The ZeroRPC Python package has a utility that allows for communication
with a ZeroRPC service from the command line. Now that we have a ZeroRPC
service running, we can execute this command to get a list of procedures
available on the service:

```bash
zerorpc tcp://127.0.0.1:4242
connecting to "tcp://127.0.0.1:4242"
[ModelZeroRPCService]
get_model_metadata  Return metadata about a model hosted by the service.
get_models          Return list of models hosted in this service.
iris_model_predict  Predict with the Iris Model.
```

The ZeroRPC tool will return a description of the methods available in
the service. The iris\_model\_predict procedure's documentation string
was generated when we instantiated the model's endpoint.

Next, we'll call a procedure on the service with Python code. Getting a
list the models available by calling the "get\_models" procedure is very
simple:

```python
client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")
result = client.get_models()
print("Result: {}".format(result))
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/scripts/get_models.py).

Executing the code able should print out a list of models that are being
hosted by the service:

```bash
Result: [{'display_name': 'Iris Model', 'qualified_name':
'iris_model', 'description': 'A machine learning model for
predicting the species of a flower based on its measurements.',
'major_version': 0, 'minor_version': 1}]
```

Making a prediction with the service is just as easy:

```python
client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")
result = client.iris_model_predict({"sepal_length": 1.1, "sepal_width": 1.2, "petal_length": 1.4, "petal_width": 1.5})
print("Result: {}".format(result))
```

The code above can be found
[here](https://github.com/schmidtbri/zerorpc-ml-model-deployment/blob/master/scripts/predict_with_model.py#L5-L11).

To see how exceptions are handled by the ZeroRPC service, we'll change
the code of the client to purposefully cause an exception in the MLModel
class:

```python
client = zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")
result = client.iris_model_predict({"sepal_length": 1.1, "sepal_width": 1.2, "petal_length": 1.4, "petal_width": "abc"})
print("Result: {}".format(result))
```

When we execute the client code, we get this exception being thrown:

```bash
python scripts/predict_with_model.py
Traceback (most recent call last):
File "scripts/predict_with_model.py", line 15, in <module>
...
File /Users/brian/Code/zerorpc-ml-model-deployment/venv/lib/python3.7/site-packages/iris_model/iris_predict.py",
line 51, in predict
raise MLModelSchemaValidationException("Failed to validate input data:
{}".format(str(e)))
ml_model_abc.MLModelSchemaValidationException: Failed to validate
input data: Key 'petal_width' error: 'abc' should be instance of 'float'
```

# Closing

In this blog post we've shown how it is possible to deploy a machine
learning model using the ZeroRPC framework. The service is able to host
any number of models that implement the MLModel interface. The service
codebase is simpler than a RESTful service, and is more lightweight than
the JSON serialization format that is usually used by REST web services.
RPC services are also simpler to understand than REST services, since
they mimic a normal function call on the client side.

The ZeroRPC service has some benefits, but also has some drawbacks when
compared to gRPC. The ZeroRPC framework does not have any way to provide
schema information for the data structures that make up the request and
responses of the service. In comparison, gRPC Protocol Buffers require
the developer of the service to provide a full data contract for the
service, and REST services have JSON Schema and the OpenAPI
specification that can provide this information about the service. By
building the get\_model\_metadata endpoint, we've been able to provide
this information for each model hosted in the service, but not for the
whole service.

The ZeroRPC framework provides more functionality for RPC calls by
allowing the server to stream responses back to the client. This allows
the server to send back prediction responses as they become available at
the server and provides a simple interface. In the future, it would be
interesting to leverage this feature of ZeroRPC to stream prediction
responses to the client.
