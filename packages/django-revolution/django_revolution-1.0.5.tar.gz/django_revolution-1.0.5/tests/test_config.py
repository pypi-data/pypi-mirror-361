"""
Test Django Revolution Configuration.
"""

import pytest
from django.test import TestCase, override_settings
from django_revolution.config import DjangoRevolutionSettings, ZoneModel, get_settings
from pydantic import ValidationError


class TestZoneModel(TestCase):
    """Test ZoneModel validation and functionality."""
    
    def test_valid_zone_creation(self):
        """Test creating a valid zone."""
        zone = ZoneModel(
            name="test_zone",
            apps=["tests.django_sample.apps.public_api"],
            title="Test Zone",
            description="Test zone description",
            public=True,
            auth_required=False
        )
        
        self.assertEqual(zone.name, "test_zone")
        self.assertEqual(zone.apps, ["tests.django_sample.apps.public_api"])
        self.assertEqual(zone.title, "Test Zone")
        self.assertTrue(zone.public)
        self.assertFalse(zone.auth_required)
    
    def test_zone_with_minimal_config(self):
        """Test zone with minimal required config."""
        zone = ZoneModel(
            name="minimal",
            apps=["tests.django_sample.apps.public_api"]
        )
        
        self.assertEqual(zone.name, "minimal")
        self.assertEqual(zone.apps, ["tests.django_sample.apps.public_api"])
        self.assertIsNone(zone.title)
        self.assertTrue(zone.public)  # default
        self.assertFalse(zone.auth_required)  # default
        self.assertEqual(zone.version, "v1")  # default
    
    def test_zone_validation_empty_name(self):
        """Test zone validation with empty name."""
        with self.assertRaises(ValidationError):
            ZoneModel(
                name="",
                apps=["tests.django_sample.apps.public_api"]
            )
    
    def test_zone_validation_empty_apps(self):
        """Test zone validation with empty apps list."""
        with self.assertRaises(ValidationError):
            ZoneModel(
                name="test_zone",
                apps=[]
            )
    
    def test_zone_validation_invalid_fields(self):
        """Test zone validation with invalid field types."""
        with self.assertRaises(ValidationError):
            ZoneModel(
                name="test_zone",
                apps="not_a_list",  # Should be a list
                public="not_a_bool"  # Should be a boolean
            )


class TestDjangoRevolutionSettings(TestCase):
    """Test DjangoRevolutionSettings configuration."""
    
    def test_default_settings(self):
        """Test default settings creation."""
        settings = DjangoRevolutionSettings()
        
        self.assertEqual(settings.api_prefix, "apix")
        self.assertFalse(settings.debug)
        self.assertTrue(settings.auto_install_deps)
        self.assertEqual(settings.zones, {})
    
    def test_settings_with_zones(self):
        """Test settings with zones configuration."""
        zones_config = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public API",
                "public": True
            },
            "private": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Private API",
                "public": False,
                "auth_required": True
            }
        }
        
        settings = DjangoRevolutionSettings(zones=zones_config)
        
        self.assertEqual(len(settings.zones), 2)
        self.assertIn("public", settings.zones)
        self.assertIn("private", settings.zones)
    
    def test_get_zones(self):
        """Test getting ZoneModel instances from settings."""
        zones_config = {
            "test_zone": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Test Zone"
            }
        }
        
        settings = DjangoRevolutionSettings(zones=zones_config)
        zones = settings.get_zones()
        
        self.assertIsInstance(zones, dict)
        self.assertIn("test_zone", zones)
        self.assertIsInstance(zones["test_zone"], ZoneModel)
        self.assertEqual(zones["test_zone"].name, "test_zone")
        self.assertEqual(zones["test_zone"].title, "Test Zone")
    
    def test_get_zone_single(self):
        """Test getting a single zone."""
        zones_config = {
            "test_zone": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Test Zone"
            }
        }
        
        settings = DjangoRevolutionSettings(zones=zones_config)
        zone = settings.get_zone("test_zone")
        
        self.assertIsInstance(zone, ZoneModel)
        self.assertEqual(zone.name, "test_zone")
        
        # Test non-existent zone
        self.assertIsNone(settings.get_zone("non_existent"))
    
    def test_settings_from_django_settings(self):
        """Test loading settings from Django settings."""
        django_config = {
            'api_prefix': 'test_api',
            'debug': True,
            'zones': {
                'public': {
                    'apps': ['tests.django_sample.apps.public_api'],
                    'title': 'Public API'
                }
            }
        }
        
        with override_settings(DJANGO_REVOLUTION=django_config):
            settings = DjangoRevolutionSettings.from_django_settings()
            
            self.assertEqual(settings.api_prefix, 'test_api')
            self.assertTrue(settings.debug)
            self.assertIn('public', settings.zones)


class TestGetSettings(TestCase):
    """Test get_settings() function."""
    
    def test_get_settings_default(self):
        """Test getting default settings."""
        settings = get_settings()
        
        self.assertIsInstance(settings, DjangoRevolutionSettings)
        self.assertEqual(settings.api_prefix, "apix")
    
    def test_get_settings_with_django_config(self):
        """Test getting settings with Django configuration."""
        django_config = {
            'api_prefix': 'test_api',
            'zones': {
                'public': {
                    'apps': ['tests.django_sample.apps.public_api'],
                    'title': 'Public API'
                }
            }
        }
        
        with override_settings(DJANGO_REVOLUTION=django_config):
            settings = get_settings()
            
            self.assertEqual(settings.api_prefix, 'test_api')
            self.assertIn('public', settings.zones)


class TestOutputSettings(TestCase):
    """Test output settings configuration."""
    
    def test_output_settings_defaults(self):
        """Test output settings default values."""
        settings = DjangoRevolutionSettings()
        
        self.assertEqual(settings.output.base_directory, "openapi")
        self.assertEqual(settings.output.schemas_directory, "schemas")
        self.assertEqual(settings.output.clients_directory, "clients")
    
    def test_output_settings_custom(self):
        """Test custom output settings."""
        output_config = {
            "base_directory": "custom_openapi",
            "schemas_directory": "custom_schemas",
            "clients_directory": "custom_clients"
        }
        
        settings = DjangoRevolutionSettings(output=output_config)
        
        self.assertEqual(settings.output.base_directory, "custom_openapi")
        self.assertEqual(settings.output.schemas_directory, "custom_schemas")
        self.assertEqual(settings.output.clients_directory, "custom_clients")


class TestGeneratorSettings(TestCase):
    """Test generator settings configuration."""
    
    def test_generator_settings_defaults(self):
        """Test generator settings default values."""
        settings = DjangoRevolutionSettings()
        
        self.assertTrue(settings.generators.typescript.enabled)
        self.assertTrue(settings.generators.python.enabled)
    
    def test_generator_settings_custom(self):
        """Test custom generator settings."""
        generators_config = {
            "typescript": {
                "enabled": False,
                "output_directory": "custom_ts"
            },
            "python": {
                "enabled": True,
                "output_directory": "custom_py"
            }
        }
        
        settings = DjangoRevolutionSettings(generators=generators_config)
        
        self.assertFalse(settings.generators.typescript.enabled)
        self.assertEqual(settings.generators.typescript.output_directory, "custom_ts")
        self.assertTrue(settings.generators.python.enabled)
        self.assertEqual(settings.generators.python.output_directory, "custom_py")


if __name__ == "__main__":
    pytest.main([__file__]) 