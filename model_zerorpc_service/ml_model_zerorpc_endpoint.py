"""Class to host an MlModel object in a ZeroRPC endpoint."""
import logging

from model_zerorpc_service import __name__
from model_zerorpc_service.model_manager import ModelManager

logger = logging.getLogger(__name__)


class MLModelZeroRPCCEndpoint(object):
    """Class for MLModel ZeroRPC endpoints.

    .. note::
        This class will behave as a callable when it is instantiated. When attached to an object as a property is will
        look like a method. This allows the ZeroRPC service to host any number of ML models.

    """

    def __init__(self, model_qualified_name):
        """Create a ZeroRPC endpoint for a model.

        :param model_qualified_name: The qualified name of the model that will be hosted in this endpoint.
        :type model_qualified_name: str
        :returns: An instance of MLModelZeroRPCCEndpoint.
        :rtype: MLModelZeroRPCCEndpoint

        """
        model_manager = ModelManager()

        model_instance = model_manager.get_model(model_qualified_name)

        if model_instance is None:
            raise ValueError("'{}' not found in ModelManager instance.".format(model_qualified_name))

        self._model = model_manager.get_model(model_qualified_name)

        # overriding the docstring of the object
        self.__doc__ = "Predict with the {}.".format(self._model.display_name)

        logger.info("Initializing endpoint for model: {}".format(self._model.qualified_name))

    def __call__(self, data):
        """Make a prediction with the model."""
        # making a prediction with the model
        prediction = self._model.predict(data=data)

        return prediction
