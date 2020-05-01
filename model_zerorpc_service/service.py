"""ZeroRPC service that hosts MLModel classes."""
import os
import logging
import time
import zerorpc

from model_zerorpc_service.config import Config
from model_zerorpc_service.model_manager import ModelManager
from model_zerorpc_service.ml_model_zerorpc_endpoint import MLModelZeroRPCCEndpoint

logging.basicConfig(level=logging.INFO)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ModelZeroRPCService(object):
    """Provides methods that implement functionality of Model ZeroRPC Service."""

    def __init__(self, settings):
        """Initialize an instance of the service."""
        self.model_manager = ModelManager()
        self.model_manager.load_models(configuration=settings.models)

        for model in self.model_manager.get_models():
            endpoint = MLModelZeroRPCCEndpoint(model_qualified_name=model["qualified_name"])
            operation_name = "{}_predict".format(model["qualified_name"])
            setattr(self, operation_name, endpoint)

    def get_models(self):
        """Return list of models hosted in this service."""
        models = self.model_manager.get_models()
        return models

    def get_model_metadata(self, qualified_name):
        """Return metadata about a model hosted by the service."""
        model_metadata = self.model_manager.get_model_metadata(qualified_name=qualified_name)
        # TODO: check if metadata is returned
        return model_metadata


def serve():
    """Start the model service."""
    # importing the right configuration
    configuration = __import__("model_zerorpc_service"). \
        __getattribute__("config"). \
        __getattribute__(os.environ["APP_SETTINGS"])

    server = zerorpc.Server(ModelZeroRPCService(settings=configuration))
    server.bind("tcp://0.0.0.0:4242")
    server.run()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
