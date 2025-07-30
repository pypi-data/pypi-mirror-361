from typing import Union
from dataclasses import dataclass

from jsonschema import validate, ValidationError


@dataclass
class FillConfig:
    """Configuration for `fill_default` and its private methods

    Args:
        create_missing_parents (bool): If a parent is missing in the instance
            and the schema has sub-defaults in the parent, then create that
            parent in the instance and fill its sub-defaults.
    """
    create_missing_parents: bool = True


def fill_default(
        instance: Union[dict, list],
        schema: dict,
        config: Union[FillConfig, None] = None
        ) -> Union[dict, list]:
    """Fill a JSON instance with schema defaults

    Recursively fills a JSON instance with the defaults of a schema with
    keywords:
    - "properties",
    - "if-then(-else)",
    - "allOf",
    - "anyOf",
    - "oneOf",
    - "dependentSchemas",
    - "items", and
    - "prefixItems".

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict, list): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12
        config (FillConfig | None): Configuration for filling. If None, uses
            default `FillConfig`.

    Returns:
        instance (dict, list): Mutated filled instance (not a copy).
    """
    if config is None:
        config = FillConfig()
    for keyword in schema:  # Apply keywords in order for predictable defaults
        if keyword == "properties":
            _fill_properties(instance, schema, config)
        if keyword == "allOf":
            _fill_allof(instance, schema, config)
        if keyword == "anyOf":
            _fill_anyof(instance, schema, config)
        if keyword == "if":
            _fill_ifthenelse(instance, schema, config)
        if keyword == "oneOf":
            _fill_oneof(instance, schema, config)
        if keyword == "dependentSchemas":
            _fill_dependentschemas(instance, schema, config)
        if keyword == "default":
            if not instance:
                if isinstance(schema["default"], dict):
                    instance.update(schema["default"])
                else:
                    instance = schema["default"]
    if isinstance(instance, list):  # Handle "(prefix)Items" for lists (arrays)
        _fill_prefixitems_and_items(instance, schema, config)
    return None


def _fill_prefixitems_and_items(
        instance: list, schema: dict, config: FillConfig):
    """Recursively fill a list with schema "prefixItems" and "items" defaults

    Fills all nested structures.

    Mutates the instance input items, so None is returned.

    Args:
        instance (array): List of items valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "prefixItems" keyword and/or "items" keyword

    Returns:
        None
    """
    # Get quantities
    n_instance = len(instance)
    n_schema_prefixitems = 0
    n_schema_non_default_prefixitems = 0
    if "prefixItems" in schema:
        n_schema_prefixitems = len(schema["prefixItems"])

        # Find number of non-continuously-default prefixItems by looping
        # in reverse until that prefixItem does not resolve to a default.
        # How do we determine if something resolves to a default? Provide
        # an empty instance.
        n_schema_non_default_prefixitems = n_schema_prefixitems
        for prefixitem_schema in reversed(schema["prefixItems"]):
            # If an empty property filled with something from the schema
            # returns something, then it resolves to a default. If not, it has
            # no default.
            if _fill_empty_property(prefixitem_schema, config) is not None:
                n_schema_non_default_prefixitems -= 1
            else:
                break
    n_missing_prefixitems = 0
    n_instance_items = max(n_instance - n_schema_prefixitems, 0)
    if n_instance_items > 0:  # Fill items
        if "items" in schema:
            for item in instance[-n_instance_items:]:
                fill_default(item,  schema["items"], config)
    elif n_instance >= n_schema_non_default_prefixitems:  # Fill missing prefixItems
        n_missing_prefixitems = len(schema["prefixItems"][n_instance:])
        for schema_of_missing_prefixitem in schema["prefixItems"][n_instance:]:
            _property = _fill_empty_property(
                schema_of_missing_prefixitem, config)
            instance.append(_property)

    # For all existing prefixitems, fill default if dict or list
    n_existing_prefixitems = n_schema_prefixitems - n_missing_prefixitems
    if n_existing_prefixitems > 0:
        for existing_instance, existing_schema in zip(instance[:n_existing_prefixitems], schema["prefixItems"][:n_existing_prefixitems]):  
            if isinstance(existing_instance, (dict, list)):
                fill_default(existing_instance, existing_schema, config)

    return None


def _fill_empty_property(schema: dict, config: FillConfig):
    """Return the default value of an empty property filled with a schema"""
    mock_schema = {"properties": {"property": schema}}
    mock_instance = {}
    fill_default(mock_instance, mock_schema, config)
    if "property" in mock_instance:
        return mock_instance["property"]
    else:
        return None


def _is_empty_object(x):
    """True if an empty object, False if not empty and/or not an object"""
    if not isinstance(x, (list, tuple, dict, set, range)):
        return False
    return not x


def _fill_properties(instance: dict, schema: dict, config: FillConfig):
    """Recursively fill a JSON instance with schema "properties" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Adapted from https://stackoverflow.com/a/76686673/20921535 by Tom-tbt.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "properties" keyword
        config (FillConfig): Fill configuration

    Returns:
        None
    """
    for _property, subschema in schema["properties"].items():
        if any(key in ["properties", "oneOf", "allOf", "anyOf", "if", "dependentSchemas"] for key in subschema):  # Recursion
            if _property not in instance:
                _was_missing = True
                instance[_property] = dict()
                _was_empty = False
            else:
                _was_missing = False
                _was_empty = _is_empty_object(instance[_property])
            fill_default(instance[_property], subschema, config)
            if (not _was_empty and _is_empty_object(instance[_property])) or \
                    _was_missing and not config.create_missing_parents:
                del instance[_property]
        if _property not in instance \
                and "default" in subschema:
            instance[_property] = subschema["default"]
        # Fill missing keys if instance already exists as object
        elif _property in instance \
                and isinstance(instance[_property], dict) \
                and "default" in subschema \
                and isinstance(subschema["default"], dict):
            for default_key in subschema["default"]:
                if default_key not in instance[_property]:
                    instance[_property][default_key] = \
                        subschema["default"][default_key]
        if "prefixItems" in subschema or "items" in subschema:
            if _property in instance:  # Instance must have array to fill
                fill_default(instance[_property], subschema, config)
    return None


def _fill_oneof(instance: dict, schema: dict, config: FillConfig):
    """Recursively fill a JSON instance with schema "oneOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "oneOf" keyword

    Returns:
        None
    """
    i = 0
    n = len(schema["oneOf"])
    while i < n:  # Iterate subschemas until the instance is valid to it
        subschema = schema["oneOf"][i]
        try:
            validate(instance, subschema)
        except ValidationError:  # If not valid, go to next subschema
            i += 1
        else:  # If valid, fill with that subschema
            fill_default(instance, subschema, config)
            return None
    return None


def _fill_allof(instance: dict, schema: dict, config: FillConfig):
    """Recursively fill a JSON instance with schema "allOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "allOf" keyword

    Returns:
        None
    """
    for subschema in schema["allOf"]:  # Instance is valid to all, so fill all
        fill_default(instance, subschema, config)
    return None


def _fill_anyof(instance: dict, schema: dict, config: FillConfig):
    """Recursively fill a JSON instance with schema "anyOf" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "anyOf" keyword

    Returns:
        None
    """
    # Fill instance with defaults of all subschemas it is valid to
    for subschema in schema["anyOf"]:
        try:
            validate(instance, subschema)
        except ValidationError:
            continue  # Skip to next subschema if instance is not valid to it
        else:
            fill_default(instance, subschema, config)
    return None


def _fill_dependentschemas(instance: dict, schema: dict, config: FillConfig):
    """Recursively fill a JSON instance with schema "dependentSchemas" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "dependentSchemas" keyword

    Returns:
        None
    """
    for _property, subschema in schema["dependentSchemas"].items():
        if _property in instance:
            fill_default(instance, subschema, config)
    return None


def _fill_ifthenelse(instance: dict, schema: dict, config: FillConfig):
    """Recursively fill a JSON instance with schema "if-then(-else)" defaults

    Fills all nested structures.

    Mutates the instance input, so None is returned.

    Args:
        instance (dict): JSON instance valid against the given schema
        schema (dict): JSON schema adhering to Draft 2020-12 with a top-level
            "if", "then", and (optionally) "else" keyword

    Returns:
        None
    """
    try:
        validate(instance, schema["if"])
    except ValidationError:  # If invalid, fill instance with else if it exists
        if "else" in schema:
            fill_default(instance, schema["else"], config)
    else:
        fill_default(instance, schema["then"], config)
    return None
