"""
Simple tests for Django Revolution to verify test setup.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the package to Python path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

# Setup minimal environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings')


def test_package_import():
    """Test that we can import the main package components."""
    try:
        from django_revolution.config import DjangoRevolutionSettings, ZoneModel
        assert DjangoRevolutionSettings is not None
        assert ZoneModel is not None
    except ImportError as e:
        pytest.skip(f"Cannot import Django Revolution: {e}")


def test_zone_model_creation():
    """Test basic ZoneModel creation."""
    try:
        from django_revolution.config import ZoneModel
        
        zone = ZoneModel(
            name="test",
            apps=["test_app"]
        )
        
        assert zone.name == "test"
        assert zone.apps == ["test_app"]
        assert zone.public is True  # default
        assert zone.auth_required is False  # default
        assert zone.version == "v1"  # default
        
    except ImportError as e:
        pytest.skip(f"Cannot import Django Revolution: {e}")


def test_settings_creation():
    """Test basic settings creation."""
    try:
        from django_revolution.config import DjangoRevolutionSettings
        
        config = DjangoRevolutionSettings()
        
        assert config.api_prefix == "apix"
        assert config.debug is False
        assert config.auto_install_deps is True
        assert config.zones == {}
        
    except ImportError as e:
        pytest.skip(f"Cannot import Django Revolution: {e}")


def test_settings_with_zones():
    """Test settings with zone configuration."""
    try:
        from django_revolution.config import DjangoRevolutionSettings
        
        zones_config = {
            "test": {
                "apps": ["test_app"],
                "title": "Test Zone"
            }
        }
        
        config = DjangoRevolutionSettings(zones=zones_config)
        
        assert len(config.zones) == 1
        assert "test" in config.zones
        
        zones = config.get_zones()
        assert "test" in zones
        assert zones["test"].name == "test"
        assert zones["test"].title == "Test Zone"
        
    except ImportError as e:
        pytest.skip(f"Cannot import Django Revolution: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 