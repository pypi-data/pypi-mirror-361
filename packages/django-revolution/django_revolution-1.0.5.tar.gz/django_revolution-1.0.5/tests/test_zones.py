"""
Test Django Revolution Zones functionality.
"""

import pytest
from unittest.mock import patch
from django.test import TestCase

from django_revolution.config import DjangoRevolutionSettings, ZoneModel
from django_revolution.zones import ZoneManager, ZoneDetector


class TestZoneManager(TestCase):
    """Test ZoneManager functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_zones = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public API",
                "public": True,
                "auth_required": False
            },
            "private": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Private API", 
                "public": False,
                "auth_required": True
            }
        }
        
        self.config = DjangoRevolutionSettings(zones=self.test_zones)
        self.manager = ZoneManager(self.config)
    
    def test_zone_manager_initialization(self):
        """Test ZoneManager initialization."""
        self.assertEqual(len(self.manager.zones), 2)
        self.assertIn("public", self.manager.zones)
        self.assertIn("private", self.manager.zones)
        
        # Test zone model types
        self.assertIsInstance(self.manager.zones["public"], ZoneModel)
        self.assertIsInstance(self.manager.zones["private"], ZoneModel)
    
    def test_zone_manager_with_mock_apps(self):
        """Test ZoneManager with mocked Django apps."""
        with patch('django.apps.apps.is_installed', return_value=True):
            manager = ZoneManager(self.config)
            self.assertEqual(len(manager.zones), 2)
    
    def test_get_app_urls(self):
        """Test app URL generation."""
        apps_list = ["tests.django_sample.apps.public_api"]
        
        with patch('django.apps.apps.is_installed', return_value=True), \
             patch('django.urls.path') as mock_path, \
             patch('django.urls.include') as mock_include:
            
            mock_path.return_value = "mocked_path"
            mock_include.return_value = "mocked_include"
            
            urls = self.manager.get_app_urls(apps_list)
            
            # Should return URL patterns
            self.assertIsInstance(urls, list)
    
    def test_get_app_urls_with_missing_apps(self):
        """Test app URL generation with missing apps."""
        apps_list = ["tests.django_sample.apps.public_api", "nonexistent_app"]
        
        with patch('django.apps.apps.is_installed', side_effect=lambda x: x == "tests.django_sample.apps.public_api"), \
             patch('django.urls.path') as mock_path, \
             patch('django.urls.include') as mock_include:
            
            mock_path.return_value = "mocked_path"
            mock_include.return_value = "mocked_include"
            
            urls = self.manager.get_app_urls(apps_list)
            
            # Should still work with existing apps
            self.assertIsInstance(urls, list)
    
    def test_get_zone_urls(self):
        """Test zone-specific URL generation."""
        with patch('django.apps.apps.is_installed', return_value=True), \
             patch('django.urls.path') as mock_path, \
             patch('drf_spectacular.views.SpectacularAPIView') as mock_view:
            
            mock_path.return_value = "mocked_path"
            mock_view.as_view.return_value = "mocked_view"
            
            zone_urls = self.manager.get_zone_urls()
            
            # Should return URL patterns for each zone
            self.assertIsInstance(zone_urls, list)
    
    def test_get_zone_schema_urls(self):
        """Test zone schema URL generation."""
        with patch('django.apps.apps.is_installed', return_value=True), \
             patch('django.urls.path') as mock_path, \
             patch('drf_spectacular.views.SpectacularAPIView') as mock_view, \
             patch('drf_spectacular.views.SpectacularSwaggerView') as mock_swagger:
            
            mock_path.return_value = "mocked_path"
            mock_view.as_view.return_value = "mocked_view"
            mock_swagger.as_view.return_value = "mocked_swagger"
            
            schema_urls = self.manager.get_zone_schema_urls()
            
            # Should return schema URL patterns
            self.assertIsInstance(schema_urls, list)


class TestZoneDetector(TestCase):
    """Test ZoneDetector functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_zones = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public API"
            }
        }
        
        self.config = DjangoRevolutionSettings(zones=self.test_zones)
        self.detector = ZoneDetector(self.config)
    
    def test_zone_detector_initialization(self):
        """Test ZoneDetector initialization."""
        self.assertEqual(len(self.detector.zones), 1)
        self.assertIn("public", self.detector.zones)
        self.assertIsInstance(self.detector.zones["public"], ZoneModel)
    
    def test_get_zone_names(self):
        """Test getting zone names."""
        zone_names = self.detector.get_zone_names()
        
        self.assertIsInstance(zone_names, list)
        self.assertIn("public", zone_names)
        self.assertEqual(len(zone_names), 1)
    
    def test_get_zone(self):
        """Test getting a specific zone."""
        zone = self.detector.get_zone("public")
        
        self.assertIsInstance(zone, ZoneModel)
        self.assertEqual(zone.name, "public")
        self.assertEqual(zone.apps, ["tests.django_sample.apps.public_api"])
        
        # Test non-existent zone
        non_existent = self.detector.get_zone("non_existent")
        self.assertIsNone(non_existent)
    
    def test_get_zone_apps(self):
        """Test getting apps for a specific zone."""
        zone_apps = self.detector.get_zone_apps("public")
        
        self.assertEqual(zone_apps, ["tests.django_sample.apps.public_api"])
    
    def test_get_zone_apps_nonexistent(self):
        """Test getting apps for non-existent zone."""
        zone_apps = self.detector.get_zone_apps("nonexistent")
        
        self.assertEqual(zone_apps, [])
    
    def test_get_all_apps(self):
        """Test getting all apps across zones."""
        all_apps = self.detector.get_all_apps()
        
        self.assertIn("tests.django_sample.apps.public_api", all_apps)
        self.assertIsInstance(all_apps, list)
    
    def test_validate_zone_apps(self):
        """Test zone apps validation."""
        # Valid apps
        with patch('django.apps.apps.is_installed', return_value=True):
            is_valid = self.detector.validate_zone_apps("public")
            self.assertTrue(is_valid)
        
        # Invalid apps
        with patch('django.apps.apps.is_installed', return_value=False):
            is_valid = self.detector.validate_zone_apps("public")
            self.assertFalse(is_valid)
    
    def test_validate_all_zones(self):
        """Test validation of all zones."""
        # All valid
        with patch('django.apps.apps.is_installed', return_value=True):
            validation_results = self.detector.validate_all_zones()
            
            self.assertIsInstance(validation_results, dict)
            self.assertIn("public", validation_results)
            self.assertTrue(validation_results["public"])
        
        # Some invalid
        with patch('django.apps.apps.is_installed', return_value=False):
            validation_results = self.detector.validate_all_zones()
            
            self.assertIn("public", validation_results)
            self.assertFalse(validation_results["public"])


class TestZoneIntegration(TestCase):
    """Test integration between zones and configuration."""
    
    def test_zone_manager_with_detector(self):
        """Test ZoneManager working with ZoneDetector."""
        test_zones = {
            "test_zone": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Test Zone"
            }
        }
        
        config = DjangoRevolutionSettings(zones=test_zones)
        manager = ZoneManager(config)
        detector = ZoneDetector(config)
        
        # Both should have the same zones
        self.assertEqual(len(manager.zones), len(detector.zones))
        self.assertIn("test_zone", manager.zones)
        self.assertIn("test_zone", detector.zones)
        
        # Zone models should be equivalent
        manager_zone = manager.zones["test_zone"]
        detector_zone = detector.zones["test_zone"]
        
        self.assertEqual(manager_zone.name, detector_zone.name)
        self.assertEqual(manager_zone.apps, detector_zone.apps)
        self.assertEqual(manager_zone.title, detector_zone.title)
    
    def test_zone_model_creation_from_config(self):
        """Test creating ZoneModel from configuration."""
        zone_config = {
            "apps": ["tests.django_sample.apps.public_api"],
            "title": "Test Zone",
            "public": True,
            "auth_required": False
        }
        
        zone = ZoneModel(name="test_zone", **zone_config)
        
        self.assertEqual(zone.name, "test_zone")
        self.assertEqual(zone.apps, ["tests.django_sample.apps.public_api"])
        self.assertEqual(zone.title, "Test Zone")
        self.assertTrue(zone.public)
        self.assertFalse(zone.auth_required)
    
    def test_multiple_zones_different_configs(self):
        """Test multiple zones with different configurations."""
        test_zones = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public API",
                "public": True,
                "auth_required": False,
                "version": "v1"
            },
            "private": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Private API",
                "public": False,
                "auth_required": True,
                "version": "v2",
                "permissions": ["admin", "staff"]
            }
        }
        
        config = DjangoRevolutionSettings(zones=test_zones)
        zones = config.get_zones()
        
        # Test public zone
        public_zone = zones["public"]
        self.assertTrue(public_zone.public)
        self.assertFalse(public_zone.auth_required)
        self.assertEqual(public_zone.version, "v1")
        self.assertIsNone(public_zone.permissions)
        
        # Test private zone
        private_zone = zones["private"]
        self.assertFalse(private_zone.public)
        self.assertTrue(private_zone.auth_required)
        self.assertEqual(private_zone.version, "v2")
        self.assertEqual(private_zone.permissions, ["admin", "staff"])


class TestZoneURLGeneration(TestCase):
    """Test URL pattern generation for zones."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_zones = {
            "api": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "API Zone",
                "prefix": "api"
            }
        }
        
        self.config = DjangoRevolutionSettings(zones=self.test_zones)
        self.manager = ZoneManager(self.config)
    
    def test_zone_url_patterns_generation(self):
        """Test zone URL pattern generation."""
        with patch('django.apps.apps.is_installed', return_value=True), \
             patch('django.urls.path') as mock_path, \
             patch('django.urls.include') as mock_include:
            
            mock_path.return_value = "mocked_path"
            mock_include.return_value = "mocked_include"
            
            patterns = self.manager.get_zone_urls()
            
            # Should generate URL patterns
            self.assertIsInstance(patterns, list)
    
    def test_zone_schema_urls_generation(self):
        """Test zone schema URL generation."""
        with patch('django.apps.apps.is_installed', return_value=True), \
             patch('django.urls.path') as mock_path, \
             patch('drf_spectacular.views.SpectacularAPIView') as mock_view, \
             patch('drf_spectacular.views.SpectacularSwaggerView') as mock_swagger:
            
            mock_path.return_value = "mocked_path"
            mock_view.as_view.return_value = "mocked_view"
            mock_swagger.as_view.return_value = "mocked_swagger"
            
            schema_urls = self.manager.get_zone_schema_urls()
            
            # Should generate schema URLs
            self.assertIsInstance(schema_urls, list)


if __name__ == "__main__":
    pytest.main([__file__])