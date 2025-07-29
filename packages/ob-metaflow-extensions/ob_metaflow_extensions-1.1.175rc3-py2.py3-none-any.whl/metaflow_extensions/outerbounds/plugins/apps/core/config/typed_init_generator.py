"""
Typed Init Generator for ConfigMeta Classes

This module provides a mechanism to dynamically generate explicit typed classes
from ConfigMeta classes that IDEs can understand and provide autocomplete for.
"""

from typing import Any, Dict, List, Optional, Union, Type

from .config_utils import ConfigMeta

import os

current_dir = os.path.dirname(__file__)


def generate_typed_class_code(config_class: Type) -> str:
    """
    Generate the actual Python code for a typed class that IDEs can understand.

    Args:
        config_class: A class that inherits from ConfigMeta

    Returns:
        Python code string for the typed class
    """
    if not hasattr(config_class, "_fields"):
        raise ValueError(f"Class {config_class.__name__} is not a ConfigMeta class")

    class_name = f"Typed{config_class.__name__}"

    # Generate TypedDict for nested configs
    nested_typeddict_code = []

    # First pass: collect all nested configs
    nested_configs = {}
    for field_name, field_info in config_class._fields.items():
        if ConfigMeta.is_instance(field_info.field_type):
            nested_configs[field_info.field_type.__name__] = field_info.field_type

    # Generate TypedDict classes for nested configs
    for nested_name, nested_class in nested_configs.items():
        dict_name = f"{nested_name}Dict"
        fields = []

        for field_name, field_info in nested_class._fields.items():
            field_type = _get_type_string(field_info.field_type)
            if not field_info.required:
                field_type = f"Optional[{field_type}]"
            fields.append(f"    {field_name}: {field_type}")

        typeddict_code = f"""class {dict_name}(TypedDict, total=False):
{chr(10).join(fields)}"""
        nested_typeddict_code.append(typeddict_code)

    # Generate __init__ method signature
    required_params = []
    optional_params = []
    all_assignments = []

    for field_name, field_info in config_class._fields.items():
        field_type = field_info.field_type

        # Handle nested ConfigMeta classes
        if ConfigMeta.is_instance(field_type):
            type_hint = f"Optional[{field_type.__name__}Dict]"
            param_line = f"        {field_name}: {type_hint} = None"
            optional_params.append(param_line)
        else:
            # All params will be set as options here even if the are required in the
            # configMeta
            type_hint = _get_type_string(field_type)
            param_line = f"        {field_name}: Optional[{type_hint}] = None"
            optional_params.append(param_line)

        all_assignments.append(f'            "{field_name}": {field_name}')

    # Combine required params first, then optional params
    all_params = required_params + optional_params

    # Generate the class code
    newline = "\n"
    comma_newline = ",\n"

    # Add **kwargs to the parameter list
    if all_params:
        params_with_kwargs = all_params + ["        **kwargs"]
    else:
        params_with_kwargs = ["        **kwargs"]

    class_code = f"""class {class_name}:
    def __init__(
        self,
{comma_newline.join(params_with_kwargs)}
    ) -> None:
        self._kwargs = {{
{comma_newline.join(all_assignments)}
        }}
        # Add any additional kwargs
        self._kwargs.update(kwargs)
        # Remove None values
        self._kwargs = {{k: v for k, v in self._kwargs.items() if v is not None}}
        self._config_class = {config_class.__name__}
        self._config = self.create_config()

    def create_config(self) -> {config_class.__name__}:
        return {config_class.__name__}.from_dict(self._kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return self._config.to_dict()"""

    # Combine all code
    full_code = []
    if nested_typeddict_code:
        full_code.extend(nested_typeddict_code)
        full_code.append("")  # Empty line
    full_code.append(class_code)

    return (newline + newline).join(full_code)


def _get_type_string(field_type: Type) -> str:
    """Convert a type to its string representation for code generation."""
    if field_type == str:
        return "str"
    elif field_type == int:
        return "int"
    elif field_type == float:
        return "float"
    elif field_type == bool:
        return "bool"
    elif hasattr(field_type, "__origin__"):
        # Handle generic types like List[str], Dict[str, str], etc.
        origin = field_type.__origin__
        args = getattr(field_type, "__args__", ())

        if origin == list:
            if args:
                return f"List[{_get_type_string(args[0])}]"
            return "List[Any]"
        elif origin == dict:
            if len(args) == 2:
                return f"Dict[{_get_type_string(args[0])}, {_get_type_string(args[1])}]"
            return "Dict[str, Any]"
        elif origin == Union:
            # Handle Optional types
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return f"Optional[{_get_type_string(non_none_type)}]"
            return f"Union[{', '.join(_get_type_string(arg) for arg in args)}]"

    # Default case - use the type name
    return getattr(field_type, "__name__", str(field_type))


def generate_typed_classes_module(
    config_classes: List[Type], module_name: str = "typed_configs"
) -> str:
    """
    Generate a complete Python module with typed classes for multiple ConfigMeta classes.

    Args:
        config_classes: List of ConfigMeta classes
        module_name: Name for the generated module

    Returns:
        Complete Python module code
    """
    imports = [
        "from typing import Optional, List, Dict, Any, TypedDict",
        "from .unified_config import "
        + ", ".join(cls.__name__ for cls in config_classes),
    ]

    class_codes = []
    for config_class in config_classes:
        class_codes.append(generate_typed_class_code(config_class))

    # Use string concatenation instead of f-string with backslashes
    newline = "\n"
    module_code = (
        '"""'
        + newline
        + "Auto-generated typed classes for ConfigMeta classes."
        + newline
        + newline
        + "This module provides IDE-friendly typed interfaces for all configuration classes."
        + newline
        + '"""'
        + newline
        + newline
        + newline.join(imports)
        + newline
        + newline
        + (newline + newline).join(class_codes)
        + newline
    )

    return module_code


def create_typed_init_class_dynamic(config_class: Type) -> Type:
    """
    Dynamically create a typed init class with proper IDE support.

    This creates the class at runtime but with proper type annotations
    that IDEs can understand.
    """
    if not hasattr(config_class, "_fields"):
        raise ValueError(f"Class {config_class.__name__} is not a ConfigMeta class")

    class_name = f"Typed{config_class.__name__}"

    # Create the init method with proper signature
    def create_init_method():
        # Build the signature dynamically
        sig_params = []
        annotations = {"return": None}

        for field_name, field_info in config_class._fields.items():
            field_type = field_info.field_type

            # Handle nested ConfigMeta classes
            if ConfigMeta.is_instance(field_type):
                field_type = Dict[str, Any]  # Use Dict for nested configs

            # Handle Optional fields
            if not field_info.required:
                field_type = Optional[field_type]

            annotations[field_name] = field_type

        def __init__(self, **kwargs):
            # Validate kwargs
            required_fields = {
                name for name, info in config_class._fields.items() if info.required
            }
            provided_fields = set(kwargs.keys())
            valid_fields = set(config_class._fields.keys())

            # Check required fields
            missing_fields = required_fields - provided_fields
            if missing_fields:
                raise ValueError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Check for unknown fields - but allow them for flexibility
            unknown_fields = provided_fields - valid_fields
            if unknown_fields:
                print(
                    f"Warning: Unknown fields will be passed through: {', '.join(unknown_fields)}"
                )

            self._kwargs = kwargs
            self._config_class = config_class

        # Set annotations
        __init__.__annotations__ = annotations
        return __init__

    def create_config(self) -> config_class:
        """Create and return the ConfigMeta class instance."""
        return config_class.from_dict(self._kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Return the raw kwargs as a dictionary."""
        return self._kwargs.copy()

    def __repr__(self) -> str:
        return f"{class_name}({self._kwargs})"

    # Create the class
    init_method = create_init_method()

    TypedClass = type(
        class_name,
        (object,),
        {
            "__init__": init_method,
            "create_config": create_config,
            "to_dict": to_dict,
            "__repr__": __repr__,
            "__module__": __name__,
            "__qualname__": class_name,
        },
    )

    return TypedClass


# Auto-generate and write typed classes to a file
def generate_typed_classes_file(output_file: str = None):
    """
    Generate typed classes and write them to a file for IDE support.

    Args:
        output_file: Path to write the generated classes. If None, prints to stdout.
    """
    from .unified_config import CoreConfig

    config_classes = [CoreConfig]

    module_code = generate_typed_classes_module(config_classes)

    if output_file:
        with open(output_file, "w") as f:
            f.write(module_code)
        print(f"Generated typed classes written to {output_file}")
    else:
        print(module_code)


# Example usage and testing
if __name__ == "__main__":
    # Generate typed classes file
    generate_typed_classes_file(os.path.join(current_dir, "typed_configs.py"))
