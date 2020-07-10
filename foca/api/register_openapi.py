"""Register OpenAPI specs with a Connexion app instance.
"""

import logging
from typing import List

from connexion import App
from connexion.exceptions import InvalidSpecification
import yaml

from foca.models.config import SpecConfig
from foca.config.config_parser import ConfigParser

# Get logger instance
logger = logging.getLogger(__name__)


def register_openapi(
        app: App,
        specs: List[SpecConfig],
) -> App:
    """
    Register OpenAPI specs with Connexion app.

    Args:
        app: A Connexion app instance.
        specs: A sequence of `SpecConfig` config models describing OpenAPI 2.x
            and/or 3.x specifications to be registered with `app`.

    Returns:
        A Connexion app instance.

    Raises:
        OSError: File cannot be read from or written to.
        InvalidSpecification: Specification file is not valid OpenAPI 2.x or
            3.x.
        yaml.YAMLError: YAML cannot be (de)serialized.
    """
    # Iterate over OpenAPI specs
    for spec in specs:
        spec_modified = False
        spec_parsed = dict()
        if isinstance(spec.path, list):
            # if the list contains a single path, treat it as str
            if len(spec.path) == 1:
                spec.path = str(spec.path[0])
            else:
                spec_modified = True
                spec_parsed = _mergeSpecs(*spec.path)
        else:
            spec_parsed = ConfigParser.parse_yaml(spec.path)

        # Add/replace root objects
        if spec.append is not None:
            for item in spec.append:
                spec_parsed.update(item)
            spec_modified = True

        # Add/replace fields to Operation Objects
        if spec.add_operation_fields is not None:
            for key, val in spec.add_operation_fields.items():
                try:
                    for path_item_object in spec_parsed['paths'].values():
                        for operation_object in path_item_object.values():
                            operation_object[key] = val
                except KeyError:
                    raise InvalidSpecification("invalid Operation Object")
            spec_modified = True

        # Write modified specs
        if spec_modified:
            try:
                with open(spec.path_out, 'w') as out_file:  # type: ignore
                    try:
                        yaml.safe_dump(spec_parsed, out_file)
                    except yaml.YAMLError as e:
                        raise yaml.YAMLError(
                            "could not encode modified specification"
                        ) from e
            except OSError as e:
                raise OSError(
                    "modified specification could not be written to file "
                    f"'{spec.path_out}'"
                ) from e
            spec_use = spec.path_out
        else:
            spec_use = spec.path

        # Attach specs to connexion App
        if spec.connexion is None:
            spec.connexion = {}
        app.add_api(
            specification=spec_use,
            **spec.dict()['connexion'],
        )

        logger.info(f"API endpoints specified in '{spec.path_out}' added.")

    return app


def _mergeSpecs(original, *args, **kwargs):
    # first element of the list is the main file
    original_data = ConfigParser.parse_yaml(original)

    for arg in args:
        with open(arg):
            to_merge = ConfigParser.parse_yaml(arg)
        for key1 in to_merge:
            if key1 in original_data:
                for key2 in to_merge[key1]:
                    if key2 in original_data[key1]:
                        original_data[key1][key2].update(to_merge[key1][key2])
                        to_merge[key1][key2].update(original_data[key1][key2])
                    else:
                        original_data[key1].update(to_merge[key1])
            else:
                original_data[key1].update(to_merge[key1])

    return original_data
