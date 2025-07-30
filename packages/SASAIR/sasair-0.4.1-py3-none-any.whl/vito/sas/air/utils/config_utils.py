import os
from pathlib import Path
from typing import Any, Dict, Type, TypeVar
from collections.abc import MutableMapping
from pydantic import BaseModel, ValidationError


def get_env_vars() -> Dict[str, str]:
    """
    Returns:
        All environment variables as a dictionary.
    """
    return dict(os.environ)

T = TypeVar("T", bound=BaseModel)


def pydentify(settings, model_class: Type[T]) -> T:
    """
    Convert settings to a validated Pydantic model instance.

    Args:
        settings: Dynaconf settings object or a dictionary-like object containing configuration.
        model_class: The Pydantic model class to instantiate

    Returns:
        An instance of the specified Pydantic model

    Raises:
        ValidationError: If the settings don't match the model requirements
        KeyError: If a required field is missing from settings
    """

    def settings_to_dict(settings, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Recursively convert settings to a dictionary structure matching the model.
        Args:
            settings: The settings object (Dynaconf or dict).
            model_class: The Pydantic model class to match against.
        """
        if not hasattr(model_class, "model_fields"):
            return settings  # Not a Pydantic model, return as is

        config_dict = {}
        model_fields = model_class.model_fields

        for field_name, field_info in model_fields.items():
            # Try different case variations
            field_value = None
            for name_variant in [field_name, field_name.upper(), field_name.lower()]:
                if hasattr(settings, name_variant):
                    field_value = getattr(settings, name_variant)
                    break
                elif hasattr(settings, "get") and settings.get(name_variant) is not None:
                    field_value = settings.get(name_variant)
                    break

            if field_value is None:
                # Skip optional fields
                if not field_info.is_required():
                    continue
                # If we reach here, it's a required field that's missing
                continue  # Let Pydantic validation handle the error

            # Handle nested models
            field_type = field_info.annotation
            if hasattr(field_type, "model_fields"):
                # It's a nested Pydantic model
                config_dict[field_name] = settings_to_dict(field_value, field_type)
            else:
                config_dict[field_name] = field_value

        return config_dict

    try:
        settings_dict: Dict[str, Any] = settings_to_dict(settings, model_class)
        model_instance = model_class(**settings_dict)
        return model_instance
    except ValidationError as e:
        print(f"Validation error in configuration: {e}")
        raise e
    except Exception as e:
        print(f"Unexpected error processing configuration: {e}")
        raise e


def read_file_type_settings(settings: MutableMapping) -> MutableMapping:
    """
    All configuration keys with postfix _file are processed here:
     - The value is read from the file and the key is removed from the settings.
     - The key without the _file postfix is set to the value of the file.
    """
    for key, value in settings.items():
        if isinstance(value, dict):
            read_file_type_settings(value)
        if  str(key).upper().endswith("_FILE"):
            file_path = Path(value)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    value = f.read()
                    # remove \n and \r from the value
                    value = value.replace('\n', '').replace('\r', '')
                    settings[key[:-5]] = value
            else:
                raise FileNotFoundError(f"File {file_path} not found.")
            del settings[key]
    return settings