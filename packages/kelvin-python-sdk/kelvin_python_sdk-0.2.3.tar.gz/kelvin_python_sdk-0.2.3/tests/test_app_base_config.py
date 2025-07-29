import pytest
from pydantic import ValidationError

from kelvin.config.common import AppBaseConfig, AppTypes


def test_valid_app_base_config():
    """Test that a valid AppBaseConfig object can be created."""
    valid_data = {
        "name": "my-app",
        "title": "My Application",
        "description": "A valid description for the app.",
        "type": AppTypes.importer,
        "version": "1.0.0",
    }
    config = AppBaseConfig(**valid_data)
    assert config.name == "my-app"
    assert config.title == "My Application"
    assert config.description == "A valid description for the app."
    assert config.type == AppTypes.importer
    assert config.version == "1.0.0"


def test_invalid_name():
    """Test that an invalid name raises a ValidationError."""
    invalid_names = ["MyApp", "my_app", "-myapp", "myapp-"]
    for name in invalid_names:
        with pytest.raises(ValidationError):
            AppBaseConfig(
                name=name,
                title="Invalid Name Test",
                description="Description",
                type=AppTypes.importer,
                version="1.0.0",
            )


def test_invalid_version():
    """Test that an invalid version raises a ValidationError."""
    invalid_versions = ["1.0", "1.0.0-beta@", "version1.0.0", "1..0"]
    for version in invalid_versions:
        with pytest.raises(ValidationError):
            AppBaseConfig(
                name="valid-name",
                title="Invalid Version Test",
                description="Description",
                type=AppTypes.importer,
                version=version,
            )


def test_invalid_type():
    """Test that an invalid type raises a ValidationError."""
    with pytest.raises(ValidationError):
        AppBaseConfig(
            name="valid-name",
            title="Invalid Type Test",
            description="Description",
            type="invalid-type",
            version="1.0.0",
        )


def test_valid_enum_types():
    """Test that valid enum types are accepted."""
    for app_type in AppTypes:
        config = AppBaseConfig(
            name="valid-name",
            title="Valid Enum Type Test",
            description="Description",
            type=app_type,
            version="1.0.0",
        )
        assert config.type == app_type


def test_missing_fields():
    """Test that missing required fields raise a ValidationError."""
    with pytest.raises(ValidationError):
        AppBaseConfig(
            name="valid-name",
            title="Missing Description Test",
            description=None,
            type=AppTypes.importer,
            version="1.0.0",
        )
    with pytest.raises(ValidationError):
        AppBaseConfig(
            name=None,
            title="Missing Name Test",
            description="Description",
            type=AppTypes.importer,
            version="1.0.0",
        )
    with pytest.raises(ValidationError):
        AppBaseConfig(
            name="valid-name",
            title=None,
            description="Description",
            type=AppTypes.importer,
            version="1.0.0",
        )


def test_valid_version_with_metadata():
    """Test that versions with metadata are accepted."""
    valid_versions = [
        "1.0.0-alpha",
        "1.0.0+build123",
        "1.0.0-dev1",
    ]
    for version in valid_versions:
        config = AppBaseConfig(
            name="valid-name",
            title="Valid Version Test",
            description="Description",
            type=AppTypes.importer,
            version=version,
        )
        assert config.version == version
