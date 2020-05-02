"""Configuration for the application."""


class Config(dict):
    """Configuration for all environments."""

    models = [
        {
            "module_name": "iris_model.iris_predict",
            "class_name": "IrisModel"
        }
    ]


class ProdConfig(Config):
    """Configuration for the prod environment."""

    service_port = "tcp://0.0.0.0:4242"


class BetaConfig(Config):
    """Configuration for the beta environment."""

    service_port = "tcp://0.0.0.0:4242"


class TestConfig(Config):
    """Configuration for the test environment."""

    service_port = "tcp://0.0.0.0:4242"


class DevConfig(Config):
    """Configuration for the dev environment."""

    service_port = "tcp://0.0.0.0:4242"
