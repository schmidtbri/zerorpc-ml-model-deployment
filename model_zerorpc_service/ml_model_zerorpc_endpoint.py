"""Class to host an MlModel object in a ZeroRPC endpoint."""
import logging

from model_zerorpc_service import __name__
from model_zerorpc_service.model_manager import ModelManager

logger = logging.getLogger(__name__)


class MLModelZeroRPCCEndpoint(object):
    """Class for MLModel ZeroRPC endpoints."""

    def __init__(self, model_qualified_name):
        """Create a ZeroRPC endpoint for a model.

        :param model_qualified_name: The qualified name of the model that will be hosted in this endpoint.
        :type model_qualified_name: str
        :returns: An instance of MLModelZeroRPCCEndpoint.
        :rtype: MLModelZeroRPCCEndpoint

        """
        model_manager = ModelManager()
        self._model = model_manager.get_model(model_qualified_name)

        if self._model is None:
            raise ValueError("'{}' not found in ModelManager instance.".format(model_qualified_name))

        logger.info("Initializing endpoint for model: {}".format(self._model.qualified_name))

    def __call__(self, data):
        """Make a prediction with the model."""
        # making a prediction with the model
        # TODO: check if model exists
        # TODO: check input schema
        prediction = self._model.predict(data=data)

        return prediction
