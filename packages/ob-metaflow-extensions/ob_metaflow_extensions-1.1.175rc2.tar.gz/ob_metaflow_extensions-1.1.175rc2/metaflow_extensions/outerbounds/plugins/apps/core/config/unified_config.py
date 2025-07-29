"""
Unified Configuration System for Outerbounds Apps

This module provides a type-safe, declarative configuration system that serves as the
single source of truth for app configuration. It automatically generates CLI options,
handles config file parsing, and manages field merging behavior.

No external dependencies required - uses only Python standard library.
"""


import os
import json
from typing import Any, Dict, List, Optional, Union, Type


from .config_utils import (
    ConfigField,
    ConfigMeta,
    JsonFriendlyKeyValuePairType,
    PureStringKVPairType,
    CommaSeparatedListType,
    FieldBehavior,
    CLIOption,
    config_meta_to_dict,
    merge_field_values,
    apply_defaults,
    populate_config_recursive,
    validate_config_meta,
    validate_required_fields,
    ConfigValidationFailedException,
)


class AuthType:
    BROWSER = "Browser"
    API = "API"

    @classmethod
    def choices(cls):
        return [cls.BROWSER, cls.API]


class ResourceConfig(metaclass=ConfigMeta):
    """Resource configuration for the app."""

    cpu = ConfigField(
        default="1",
        cli_meta=CLIOption(
            name="cpu",
            cli_option_str="--cpu",
            help="CPU resource request and limit.",
        ),
        field_type=str,
        example="500m",
    )
    memory = ConfigField(
        default="4Gi",
        cli_meta=CLIOption(
            name="memory",
            cli_option_str="--memory",
            help="Memory resource request and limit.",
        ),
        field_type=str,
        example="512Mi",
    )
    gpu = ConfigField(
        cli_meta=CLIOption(
            name="gpu",
            cli_option_str="--gpu",
            help="GPU resource request and limit.",
        ),
        field_type=str,
        example="1",
    )
    disk = ConfigField(
        default="20Gi",
        cli_meta=CLIOption(
            name="disk",
            cli_option_str="--disk",
            help="Storage resource request and limit.",
        ),
        field_type=str,
        example="1Gi",
    )


class HealthCheckConfig(metaclass=ConfigMeta):
    """Health check configuration."""

    enabled = ConfigField(
        default=False,
        cli_meta=CLIOption(
            name="health_check_enabled",
            cli_option_str="--health-check-enabled",
            help="Whether to enable health checks.",
            is_flag=True,
        ),
        field_type=bool,
        example=True,
    )
    path = ConfigField(
        cli_meta=CLIOption(
            name="health_check_path",
            cli_option_str="--health-check-path",
            help="The path for health checks.",
        ),
        field_type=str,
        example="/health",
    )
    initial_delay_seconds = ConfigField(
        cli_meta=CLIOption(
            name="health_check_initial_delay",
            cli_option_str="--health-check-initial-delay",
            help="Number of seconds to wait before performing the first health check.",
        ),
        field_type=int,
        example=10,
    )
    period_seconds = ConfigField(
        cli_meta=CLIOption(
            name="health_check_period",
            cli_option_str="--health-check-period",
            help="How often to perform the health check.",
        ),
        field_type=int,
        example=30,
    )


class AuthConfig(metaclass=ConfigMeta):
    """Authentication configuration."""

    type = ConfigField(
        default=AuthType.BROWSER,
        cli_meta=CLIOption(
            name="auth_type",
            cli_option_str="--auth-type",
            help="The type of authentication to use for the app.",
            choices=AuthType.choices(),
        ),
        field_type=str,
        example="Browser",
    )
    public = ConfigField(
        default=True,
        cli_meta=CLIOption(
            name="auth_public",
            cli_option_str="--public-access/--private-access",
            help="Whether the app is public or not.",
            is_flag=True,
        ),
        field_type=bool,
        example=True,
    )

    @staticmethod
    def validate(auth_config: "AuthConfig"):
        if auth_config.type is not None and auth_config.type not in AuthType.choices():
            raise ConfigValidationFailedException(
                field_name="type",
                field_info=auth_config._get_field("type"),
                current_value=auth_config.type,
                message=f"Invalid auth type: {auth_config.type}. Must be one of {AuthType.choices()}",
            )
        return True


class ReplicaConfig(metaclass=ConfigMeta):
    """Replica configuration."""

    fixed = ConfigField(
        cli_meta=CLIOption(
            name="fixed_replicas",
            cli_option_str="--fixed-replicas",
            help="The fixed number of replicas to deploy the app with. If min and max are set, this will raise an error.",
        ),
        field_type=int,
        example=1,
    )

    min = ConfigField(
        cli_meta=CLIOption(
            name="min_replicas",
            cli_option_str="--min-replicas",
            help="The minimum number of replicas to deploy the app with.",
        ),
        field_type=int,
        example=1,
    )
    max = ConfigField(
        cli_meta=CLIOption(
            name="max_replicas",
            cli_option_str="--max-replicas",
            help="The maximum number of replicas to deploy the app with.",
        ),
        field_type=int,
        example=10,
    )

    @staticmethod
    def defaults(replica_config: "ReplicaConfig"):
        if all(
            [
                replica_config.min is None,
                replica_config.max is None,
                replica_config.fixed is None,
            ]
        ):
            replica_config.fixed = 1
        return

    @staticmethod
    def validate(replica_config: "ReplicaConfig"):
        # TODO: Have a better validation story.
        both_min_max_set = (
            replica_config.min is not None and replica_config.max is not None
        )
        fixed_set = replica_config.fixed is not None
        max_is_set = replica_config.max is not None
        min_is_set = replica_config.min is not None
        any_min_max_set = (
            replica_config.min is not None or replica_config.max is not None
        )

        def _greater_than_equals_zero(x):
            return x is not None and x >= 0

        if both_min_max_set and replica_config.min > replica_config.max:
            raise ConfigValidationFailedException(
                field_name="min",
                field_info=replica_config._get_field("min"),
                current_value=replica_config.min,
                message="Min replicas cannot be greater than max replicas",
            )
        if fixed_set and any_min_max_set:
            raise ConfigValidationFailedException(
                field_name="fixed",
                field_info=replica_config._get_field("fixed"),
                current_value=replica_config.fixed,
                message="Fixed replicas cannot be set when min or max replicas are set",
            )

        if max_is_set and not min_is_set:
            raise ConfigValidationFailedException(
                field_name="min",
                field_info=replica_config._get_field("min"),
                current_value=replica_config.min,
                message="If max replicas is set then min replicas must be set too.",
            )

        if fixed_set and replica_config.fixed < 0:
            raise ConfigValidationFailedException(
                field_name="fixed",
                field_info=replica_config._get_field("fixed"),
                current_value=replica_config.fixed,
                message="Fixed replicas cannot be less than 0",
            )

        if min_is_set and not _greater_than_equals_zero(replica_config.min):
            raise ConfigValidationFailedException(
                field_name="min",
                field_info=replica_config._get_field("min"),
                current_value=replica_config.min,
                message="Min replicas cannot be less than 0",
            )

        if max_is_set and not _greater_than_equals_zero(replica_config.max):
            raise ConfigValidationFailedException(
                field_name="max",
                field_info=replica_config._get_field("max"),
                current_value=replica_config.max,
                message="Max replicas cannot be less than 0",
            )
        return True


def more_than_n_not_none(n, *args):
    return sum(1 for arg in args if arg is not None) > n


class DependencyConfig(metaclass=ConfigMeta):
    """Dependency configuration."""

    from_requirements_file = ConfigField(
        cli_meta=CLIOption(
            name="dep_from_requirements",
            cli_option_str="--dep-from-requirements",
            help="The path to the requirements.txt file to attach to the app.",
        ),
        field_type=str,
        behavior=FieldBehavior.NOT_ALLOWED,
        example="requirements.txt",
    )
    from_pyproject_toml = ConfigField(
        cli_meta=CLIOption(
            name="dep_from_pyproject",
            cli_option_str="--dep-from-pyproject",
            help="The path to the pyproject.toml file to attach to the app.",
        ),
        field_type=str,
        behavior=FieldBehavior.NOT_ALLOWED,
        example="pyproject.toml",
    )
    python = ConfigField(
        cli_meta=CLIOption(
            name="python",
            cli_option_str="--python",
            help="The Python version to use for the app.",
        ),
        field_type=str,
        behavior=FieldBehavior.NOT_ALLOWED,
        example="3.10",
    )
    pypi = ConfigField(
        cli_meta=CLIOption(
            name="pypi",  # TODO: Can set CLI meta to None
            cli_option_str="--pypi",
            help="A dictionary of pypi dependencies to attach to the app. The key is the package name and the value is the version.",
            hidden=True,  # Complex structure, better handled in config file
        ),
        field_type=dict,
        behavior=FieldBehavior.NOT_ALLOWED,
        example={"numpy": "1.23.0", "pandas": ""},
    )
    conda = ConfigField(
        cli_meta=CLIOption(  # TODO: Can set CLI meta to None
            name="conda",
            cli_option_str="--conda",
            help="A dictionary of conda dependencies to attach to the app. The key is the package name and the value is the version.",
            hidden=True,  # Complex structure, better handled in config file
        ),
        field_type=dict,
        behavior=FieldBehavior.NOT_ALLOWED,
        example={"numpy": "1.23.0", "pandas": ""},
    )

    @staticmethod
    def validate(dependency_config: "DependencyConfig"):
        # You can either have from_requirements_file or from_pyproject_toml or python with pypi or conda
        # but not more than one of them.
        if more_than_n_not_none(
            1,
            dependency_config.from_requirements_file,
            dependency_config.from_pyproject_toml,
        ):
            raise ConfigValidationFailedException(
                field_name="from_requirements_file",
                field_info=dependency_config._get_field("from_requirements_file"),
                current_value=dependency_config.from_requirements_file,
                message="Cannot set from_requirements_file and from_pyproject_toml at the same time",
            )
        if any([dependency_config.pypi, dependency_config.conda]) and any(
            [
                dependency_config.from_requirements_file,
                dependency_config.from_pyproject_toml,
            ]
        ):
            raise ConfigValidationFailedException(
                field_name="pypi" if dependency_config.pypi else "conda",
                field_info=dependency_config._get_field(
                    "pypi" if dependency_config.pypi else "conda"
                ),
                current_value=dependency_config.pypi or dependency_config.conda,
                message="Cannot set pypi or conda when from_requirements_file or from_pyproject_toml is set",
            )
        return True


class PackageConfig(metaclass=ConfigMeta):
    """Package configuration."""

    src_path = ConfigField(
        cli_meta=CLIOption(
            name="package_src_path",
            cli_option_str="--package-src-path",
            help="The path to the source code to deploy with the App.",
        ),
        field_type=str,
        example="./",
    )
    suffixes = ConfigField(
        cli_meta=CLIOption(
            name="package_suffixes",
            cli_option_str="--package-suffixes",
            help="A list of suffixes to add to the source code to deploy with the App.",
        ),
        field_type=list,
        example=[".py", ".ipynb"],
    )


class BasicAppValidations:
    @staticmethod
    def name(name):
        if name is None:
            return True
        if len(name) > 128:
            raise ConfigValidationFailedException(
                field_name="name",
                field_info=CoreConfig._get_field(CoreConfig, "name"),
                current_value=name,
                message="Name cannot be longer than 128 characters",
            )
        return True

    @staticmethod
    def port(port):
        if port is None:
            return True
        if port < 1 or port > 65535:
            raise ConfigValidationFailedException(
                field_name="port",
                field_info=CoreConfig._get_field(CoreConfig, "port"),
                current_value=port,
                message="Port must be between 1 and 65535",
            )
        return True

    @staticmethod
    def tags(tags):
        if tags is None:
            return True
        if not all(isinstance(tag, dict) and len(tag) == 1 for tag in tags):
            raise ConfigValidationFailedException(
                field_name="tags",
                field_info=CoreConfig._get_field(CoreConfig, "tags"),
                current_value=tags,
                message="Tags must be a list of dictionaries with one key. Currently they are set to %s "
                % (str(tags)),
            )
        return True

    @staticmethod
    def secrets(secrets):
        if secrets is None:  # If nothing is set we dont care.
            return True

        if not isinstance(secrets, list):
            raise ConfigValidationFailedException(
                field_name="secrets",
                field_info=CoreConfig._get_field(CoreConfig, "secrets"),
                current_value=secrets,
                message="Secrets must be a list of strings",
            )
        from ..validations import secrets_validator

        try:
            secrets_validator(secrets)
        except Exception as e:
            raise ConfigValidationFailedException(
                field_name="secrets",
                field_info=CoreConfig._get_field(CoreConfig, "secrets"),
                current_value=secrets,
                message=f"Secrets validation failed, {e}",
            )
        return True

    @staticmethod
    def persistence(persistence):
        if persistence is None:
            return True
        if persistence not in ["none", "postgres"]:
            raise ConfigValidationFailedException(
                field_name="persistence",
                field_info=CoreConfig._get_field(CoreConfig, "persistence"),
                current_value=persistence,
                message=f"Persistence must be one of: {['none', 'postgres']}",
            )
        return True


class CoreConfig(metaclass=ConfigMeta):
    """Unified App Configuration - The single source of truth for application configuration.

    CoreConfig is the central configuration class that defines all application settings using the
    ConfigMeta metaclass and ConfigField descriptors. It provides a declarative, type-safe way
    to manage configuration from multiple sources (CLI, config files, environment) with automatic
    validation, merging, and CLI generation.

    Core Features:
    - **Declarative Configuration**: All fields are defined using ConfigField descriptors
    - **Multi-Source Configuration**: Supports CLI options, config files (JSON/YAML), and programmatic setting
    - **Automatic CLI Generation**: CLI options are automatically generated from field metadata
    - **Type Safety**: Built-in type checking and validation for all fields
    - **Hierarchical Structure**: Supports nested configuration objects (resources, auth, dependencies)
    - **Intelligent Merging**: Configurable merging behavior for different field types
    - **Validation Framework**: Comprehensive validation with custom validation functions

    Configuration Lifecycle:
    1. **Definition**: Fields are defined declaratively using ConfigField descriptors
    2. **Instantiation**: Objects are created with all fields initialized to None or nested objects
    3. **Population**: Values are populated from CLI options, config files, or direct assignment
    4. **Merging**: Multiple config sources are merged according to field behavior settings
    5. **Validation**: Field validation functions and required field checks are performed
    6. **Default Application**: Default values are applied to any remaining None fields
    7. **Commit**: Final validation and preparation for use


    Usage Examples:
        Create from CLI options:
        ```python
        config = CoreConfig.from_cli({
            'name': 'myapp',
            'port': 8080,
            'commands': ['python app.py']
        })
        ```

        Create from config file:
        ```python
        config = CoreConfig.from_file('config.yaml')
        ```

        Create from dictionary:
        ```python
        config = CoreConfig.from_dict({
            'name': 'myapp',
            'port': 8080,
            'resources': {
                'cpu': '500m',
                'memory': '1Gi'
            }
        })
        ```

        Merge configurations:
        ```python
        file_config = CoreConfig.from_file('config.yaml')
        cli_config = CoreConfig.from_cli(cli_options)
        final_config = CoreConfig.merge_configs(file_config, cli_config)
        final_config.commit()  # Validate and apply defaults
        ```
    """

    # TODO: We can add Force Upgrade / No Deps flags here too if we need to.
    # Since those can be exposed on the CLI side and the APP state will anyways
    # be expored before being worked upon.

    SCHEMA_DOC = """Schema for defining Outerbounds Apps configuration. This schema is what we will end up using on the CLI/programmatic interface.
How to read this schema:
1. If the a property has `mutation_behavior` set to `union` then it will allow overrides of values at runtime from the CLI.
2. If the property has `mutation_behavior`set to `not_allowed` then either the CLI or the config file value will be used (which ever is not None). If the user supplies something in both then an error will be raised.
3. If a property has `experimental` set to true then a lot its validations may-be skipped and parsing handled somewhere else.
"""

    # Required fields
    name = ConfigField(
        cli_meta=CLIOption(
            name="name",
            cli_option_str="--name",
        ),
        validation_fn=BasicAppValidations.name,
        field_type=str,
        required=True,
        help="The name of the app to deploy.",
        example="myapp",
    )
    port = ConfigField(
        cli_meta=CLIOption(
            name="port",
            cli_option_str="--port",
        ),
        validation_fn=BasicAppValidations.port,
        field_type=int,
        required=True,
        help="Port where the app is hosted. When deployed this will be port on which we will deploy the app.",
        example=8000,
    )

    # Optional basic fields
    description = ConfigField(
        cli_meta=CLIOption(
            name="description",
            cli_option_str="--description",
            help="The description of the app to deploy.",
        ),
        field_type=str,
        example="This is a description of my app.",
    )
    app_type = ConfigField(
        cli_meta=CLIOption(
            name="app_type",
            cli_option_str="--app-type",
            help="The User defined type of app to deploy. Its only used for bookkeeping purposes.",
        ),
        field_type=str,
        example="MyCustomAgent",
    )
    image = ConfigField(
        cli_meta=CLIOption(
            name="image",
            cli_option_str="--image",
            help="The Docker image to deploy with the App.",
        ),
        field_type=str,
        example="python:3.10-slim",
    )

    # List fields
    tags = ConfigField(
        cli_meta=CLIOption(
            name="tags",
            cli_option_str="--tag",
            multiple=True,
            click_type=PureStringKVPairType,
        ),
        field_type=list,
        validation_fn=BasicAppValidations.tags,
        help="The tags of the app to deploy.",
        example=[{"foo": "bar"}, {"x": "y"}],
    )
    secrets = ConfigField(
        cli_meta=CLIOption(
            name="secrets", cli_option_str="--secret", multiple=True, click_type=str
        ),
        field_type=list,
        help="Outerbounds integrations to attach to the app. You can use the value you set in the `@secrets` decorator in your code.",
        example=["hf-token"],
        validation_fn=BasicAppValidations.secrets,
    )
    compute_pools = ConfigField(
        cli_meta=CLIOption(
            name="compute_pools",
            cli_option_str="--compute-pools",
            help="A list of compute pools to deploy the app to.",
            multiple=True,
            click_type=str,
        ),
        field_type=list,
        example=["default", "large"],
    )
    environment = ConfigField(
        cli_meta=CLIOption(
            name="environment",
            cli_option_str="--env",
            multiple=True,
            click_type=JsonFriendlyKeyValuePairType,  # TODO: Fix me.
        ),
        field_type=dict,
        help="Environment variables to deploy with the App.",
        example={
            "DEBUG": True,
            "DATABASE_CONFIG": {"host": "localhost", "port": 5432},
            "ALLOWED_ORIGINS": ["http://localhost:3000", "https://myapp.com"],
        },
    )
    commands = ConfigField(
        cli_meta=None,  # We dont expose commands as an options. We rather expose it like `--` with click.
        field_type=list,
        required=True,  # Either from CLI or from config file.
        help="A list of commands to run the app with.",  # TODO: Fix me: make me configurable via the -- stuff in click.
        example=["python app.py", "python app.py --foo bar"],
        behavior=FieldBehavior.NOT_ALLOWED,
    )

    # Complex nested fields
    resources = ConfigField(
        cli_meta=None,  # No top-level CLI option, only nested fields have CLI options
        field_type=ResourceConfig,
        # TODO : see if we can add a validation func for resources.
        help="Resource configuration for the app.",
    )
    auth = ConfigField(
        cli_meta=None,  # No top-level CLI option, only nested fields have CLI options
        field_type=AuthConfig,
        help="Auth related configurations.",
        validation_fn=AuthConfig.validate,
    )
    replicas = ConfigField(
        cli_meta=None,  # No top-level CLI option, only nested fields have CLI options
        validation_fn=ReplicaConfig.validate,
        field_type=ReplicaConfig,
        default=ReplicaConfig.defaults,
        help="The number of replicas to deploy the app with.",
    )
    dependencies = ConfigField(
        cli_meta=None,  # No top-level CLI option, only nested fields have CLI options
        validation_fn=DependencyConfig.validate,
        field_type=DependencyConfig,
        help="The dependencies to attach to the app. ",
    )
    package = ConfigField(
        cli_meta=None,  # No top-level CLI option, only nested fields have CLI options
        field_type=PackageConfig,
        help="Configurations associated with packaging the app.",
    )

    no_deps = ConfigField(
        cli_meta=CLIOption(
            name="no_deps",
            cli_option_str="--no-deps",
            help="Do not any dependencies. Directly used the image provided",
            is_flag=True,
        ),
        field_type=bool,
        default=False,
        help="Do not bake any dependencies. Directly used the image provided",
    )

    force_upgrade = ConfigField(
        cli_meta=CLIOption(
            name="force_upgrade",
            cli_option_str="--force-upgrade",
            help="Force upgrade the app even if it is currently being upgraded.",
            is_flag=True,
        ),
        field_type=bool,
        default=False,
        help="Force upgrade the app even if it is currently being upgraded.",
    )

    # ------- Experimental -------------
    # These options get treated in the `..experimental` module.
    # If we move any option as a first class citizen then we need to move
    # its capsule parsing from the `..experimental` module to the `..capsule.CapsuleInput` module.

    persistence = ConfigField(
        cli_meta=CLIOption(
            name="persistence",
            cli_option_str="--persistence",
            help="The persistence mode to deploy the app with.",
            choices=["none", "postgres"],
        ),
        validation_fn=BasicAppValidations.persistence,
        field_type=str,
        default="none",
        example="postgres",
        is_experimental=True,
    )

    project = ConfigField(
        cli_meta=CLIOption(
            name="project",
            cli_option_str="--project",
            help="The project name to deploy the app to.",
        ),
        field_type=str,
        is_experimental=True,
        example="my-project",
    )
    branch = ConfigField(
        cli_meta=CLIOption(
            name="branch",
            cli_option_str="--branch",
            help="The branch name to deploy the app to.",
        ),
        field_type=str,
        is_experimental=True,
        example="main",
    )
    models = ConfigField(
        cli_meta=None,
        field_type=list,
        is_experimental=True,
        example=[{"asset_id": "model-123", "asset_instance_id": "instance-456"}],
    )
    data = ConfigField(
        cli_meta=None,
        field_type=list,
        is_experimental=True,
        example=[{"asset_id": "data-789", "asset_instance_id": "instance-101"}],
    )
    # ------- /Experimental -------------

    def to_dict(self):
        return config_meta_to_dict(self)

    @staticmethod
    def merge_configs(
        base_config: "CoreConfig", override_config: "CoreConfig"
    ) -> "CoreConfig":
        """
        Merge two configurations with override taking precedence.

        Handles FieldBehavior for proper merging:
        - UNION: Merge values (for lists, dicts)
        - NOT_ALLOWED: Base config value takes precedence (override is ignored)

        Args:
            base_config: Base configuration (lower precedence)
            override_config: Override configuration (higher precedence)

        Returns:
            Merged CoreConfig instance
        """
        merged_config = CoreConfig()

        # Process each field according to its behavior
        for field_name, field_info in CoreConfig._fields.items():
            base_value = getattr(base_config, field_name, None)
            override_value = getattr(override_config, field_name, None)

            # Get the behavior for this field
            behavior = getattr(field_info, "behavior", FieldBehavior.UNION)

            merged_value = merge_field_values(
                base_value, override_value, field_info, behavior
            )

            setattr(merged_config, field_name, merged_value)

        return merged_config

    def set_defaults(self):
        apply_defaults(self)

    def validate(self):
        validate_config_meta(self)

    def commit(self):
        self.validate()
        validate_required_fields(self)
        self.set_defaults()

    @classmethod
    def from_dict(cls, config_data: Dict[str, Any]) -> "CoreConfig":
        config = cls()
        # Define functions for dict source
        def get_dict_key(field_name, field_info):
            return field_name

        def get_dict_value(source_data, key):
            return source_data.get(key)

        populate_config_recursive(
            config, cls, config_data, get_dict_key, get_dict_value
        )
        return config

    @classmethod
    def from_cli(cls, cli_options: Dict[str, Any]) -> "CoreConfig":
        config = cls()
        # Define functions for CLI source
        def get_cli_key(field_name, field_info):
            # Need to have a special Exception for commands since the Commands
            # are passed down via unprocessed args after `--` in click
            if field_name == cls.commands.name:
                return field_name
            # Return the CLI parameter name if CLI metadata exists
            if field_info.cli_meta and not field_info.cli_meta.hidden:
                return field_info.cli_meta.name
            return None

        def get_cli_value(source_data, key):
            value = source_data.get(key)
            # Only return non-None values since None means not set in CLI
            if value is None:
                return None
            if key == cls.environment.name:
                _env_dict = {}
                for v in value:
                    _env_dict.update(v)
                return _env_dict
            if type(value) == tuple:
                obj = list(x for x in source_data[key])
                if len(obj) == 0:
                    return None  # Dont return Empty Lists so that we can set Nones
                return obj
            return value

        # Use common recursive population function with nested value checking
        populate_config_recursive(
            config,
            cls,
            cli_options,
            get_cli_key,
            get_cli_value,
        )
        return config
