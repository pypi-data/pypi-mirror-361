import json

try:
    from jsonschema import validate as jsonschema_validate
    VALIDATION_ENABLED = True
except ImportError:
    def jsonschema_validate(*args, **kwargs) -> None:
        pass
    VALIDATION_ENABLED = False

from . import data
from .pkg_resources import data_location_as_path


def validate_quotes_json(obj: object) -> bool:
    """
    Validate quote JSON data

    NOTE: If jsonschema is not installed, this function
          turns into a no-op and has no effect. It returns False
          in this case
    Parameters
    ----------
    obj : object
        The quotes object unserialized from JSON

    Returns
    -------
    bool
        Whether validation was enabled and actually occured, or was a no-op
    """
    schema_src = data_location_as_path(data, data.QUOTES_SCHEMA_JSON)
    schema = json.load(open(schema_src))
    jsonschema_validate(obj, schema)
    return VALIDATION_ENABLED
