"""
Integration tests for Django Revolution.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from io import StringIO

from django_revolution.config import DjangoRevolutionSettings
from django_revolution.zones import ZoneManager, ZoneDetector
from django_revolution.openapi.generator import OpenAPIGenerator


class TestFullWorkflow(TestCase):
    """Test complete Django Revolution workflow."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_zones = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public API",
                "description": "Public API for testing",
                "public": True,
                "auth_required": False
            },
            "private": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Private API",
                "description": "Private API for testing",
                "public": False,
                "auth_required": True
            }
        }
        
        self.config = DjangoRevolutionSettings(zones=self.test_zones)
    
    def test_config_to_zones_workflow(self):
        """Test configuration to zones workflow."""
        # Test config creation
        self.assertEqual(len(self.config.zones), 2)
        
        # Test zone models creation
        zones = self.config.get_zones()
        self.assertEqual(len(zones), 2)
        self.assertIn("public", zones)
        self.assertIn("private", zones)
        
        # Test zone validation
        public_zone = zones["public"]
        self.assertEqual(public_zone.name, "public")
        self.assertEqual(public_zone.apps, ["tests.django_sample.apps.public_api"])
        self.assertTrue(public_zone.public)
        self.assertFalse(public_zone.auth_required)
        self.assertEqual(public_zone.description, "Public API for testing")
    
    def test_zone_manager_integration(self):
        """Test ZoneManager integration with config."""
        manager = ZoneManager(self.config)
        
        # Test zone loading
        self.assertEqual(len(manager.zones), 2)
        self.assertIn("public", manager.zones)
        self.assertIn("private", manager.zones)
        
        # Test zone properties
        public_zone = manager.zones["public"]
        self.assertEqual(public_zone.title, "Public API")
        self.assertTrue(public_zone.public)
        
        private_zone = manager.zones["private"]
        self.assertEqual(private_zone.title, "Private API")
        self.assertFalse(private_zone.public)
        self.assertTrue(private_zone.auth_required)
    
    def test_zone_detector_integration(self):
        """Test ZoneDetector integration."""
        detector = ZoneDetector(self.config)
        
        # Test zone detection
        self.assertEqual(len(detector.zones), 2)
        
        # Test zone validation
        with patch('django.apps.apps.is_installed', return_value=True):
            validation_results = detector.validate_all_zones()
            
            self.assertIsInstance(validation_results, dict)
            self.assertTrue(validation_results["public"])
            self.assertTrue(validation_results["private"])
        
        # Test getting zone apps
        public_apps = detector.get_zone_apps("public")
        self.assertEqual(public_apps, ["tests.django_sample.apps.public_api"])
        
        private_apps = detector.get_zone_apps("private")
        self.assertEqual(private_apps, ["tests.django_sample.apps.private_api"])
    
    def test_openapi_generator_integration(self):
        """Test OpenAPIGenerator integration."""
        generator = OpenAPIGenerator(self.config)
        
        # Test generator initialization
        self.assertEqual(len(generator.zone_manager.zones), 2)
        
        # Test schema generation (mocked)
        with patch('django_revolution.utils.run_command') as mock_command:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', create=True) as mock_open:
                    mock_command.return_value = (True, "")
                    
                    mock_file = MagicMock()
                    mock_file.read.return_value = '{"openapi": "3.0.0", "info": {"title": "Test API"}}'
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    schemas = generator.generate_schemas()
                    
                    self.assertIsInstance(schemas, dict)
                    self.assertIn("public", schemas)
                    self.assertIn("private", schemas)
    
    def test_management_command_integration(self):
        """Test management command integration."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = self.config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_all.return_value = {
                    "total_zones": 2,
                    "successful_typescript": 2,
                    "successful_python": 2,
                    "duration_seconds": 1.5
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--status', stdout=out)
                
                output = out.getvalue()
                self.assertIn("Django Revolution Status", output)
                self.assertIn("2 zones", output)
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test invalid zone configuration
        invalid_zones = {
            "test": {
                "apps": [],  # Empty apps list should fail validation
                "title": "Test"
            }
        }
        
        with self.assertRaises(Exception):
            DjangoRevolutionSettings(zones=invalid_zones)
    
    def test_end_to_end_workflow_mock(self):
        """Test end-to-end workflow with mocks."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                with patch('django_revolution.utils.run_command') as mock_command:
                    with patch('subprocess.run') as mock_subprocess:
                        # Setup configuration
                        mock_get_settings.return_value = self.config
                        
                        # Setup generator mock
                        mock_gen_instance = MagicMock()
                        mock_gen_instance.generate_all.return_value = {
                            "total_zones": 2,
                            "successful_typescript": 2,
                            "successful_python": 2,
                            "failed_typescript": 0,
                            "failed_python": 0,
                            "total_files_generated": 16,
                            "duration_seconds": 2.3
                        }
                        mock_generator.return_value = mock_gen_instance
                        
                        # Setup command mocks
                        mock_command.return_value = (True, "")
                        mock_subprocess.return_value.returncode = 0
                        
                        # Run full generation
                        out = StringIO()
                        call_command('revolution', stdout=out)
                        
                        output = out.getvalue()
                        
                        # Verify successful execution
                        self.assertIn("Generated", output)
                        self.assertIn("2 zones", output)
                        mock_gen_instance.generate_all.assert_called_once()


class TestRealWorldScenarios(TestCase):
    """Test real-world usage scenarios."""
    
    def test_ecommerce_api_scenario(self):
        """Test e-commerce API scenario."""
        ecommerce_zones = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public Catalog API",
                "description": "Public product catalog and search",
                "public": True,
                "auth_required": False,
                "version": "v1"
            },
            "customer": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Customer API",
                "description": "Customer account and order management",
                "public": False,
                "auth_required": True,
                "version": "v1",
                "permissions": ["customer"]
            },
            "admin": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Admin API",
                "description": "Administrative interface",
                "public": False,
                "auth_required": True,
                "version": "v1",
                "permissions": ["admin", "staff"]
            }
        }
        
        config = DjangoRevolutionSettings(zones=ecommerce_zones)
        zones = config.get_zones()
        
        # Test zone structure
        self.assertEqual(len(zones), 3)
        self.assertIn("public", zones)
        self.assertIn("customer", zones)
        self.assertIn("admin", zones)
        
        # Test zone properties
        public_zone = zones["public"]
        self.assertTrue(public_zone.public)
        self.assertFalse(public_zone.auth_required)
        self.assertEqual(public_zone.version, "v1")
        
        customer_zone = zones["customer"]
        self.assertFalse(customer_zone.public)
        self.assertTrue(customer_zone.auth_required)
        self.assertEqual(customer_zone.permissions, ["customer"])
        
        admin_zone = zones["admin"]
        self.assertFalse(admin_zone.public)
        self.assertTrue(admin_zone.auth_required)
        self.assertEqual(admin_zone.permissions, ["admin", "staff"])
    
    def test_saas_api_scenario(self):
        """Test SaaS API scenario with versioning."""
        saas_zones = {
            "v1": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "API v1",
                "description": "Legacy API version 1",
                "version": "v1",
                "public": True,
                "path_prefix": "v1"
            },
            "v2": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "API v2",
                "description": "Current API version 2",
                "version": "v2",
                "public": True,
                "path_prefix": "v2"
            },
            "beta": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Beta API",
                "description": "Beta features for testing",
                "version": "beta",
                "public": False,
                "auth_required": True,
                "path_prefix": "beta"
            }
        }
        
        config = DjangoRevolutionSettings(zones=saas_zones)
        zones = config.get_zones()
        
        # Test versioning
        self.assertEqual(zones["v1"].version, "v1")
        self.assertEqual(zones["v2"].version, "v2")
        self.assertEqual(zones["beta"].version, "beta")
        
        # Test path prefixes
        self.assertEqual(zones["v1"].path_prefix, "v1")
        self.assertEqual(zones["v2"].path_prefix, "v2")
        self.assertEqual(zones["beta"].path_prefix, "beta")
        
        # Test access control
        self.assertTrue(zones["v1"].public)
        self.assertTrue(zones["v2"].public)
        self.assertFalse(zones["beta"].public)
        self.assertTrue(zones["beta"].auth_required)
    
    def test_microservices_scenario(self):
        """Test microservices API scenario."""
        microservices_zones = {
            "users": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "User Service API",
                "description": "User management microservice",
                "public": False,
                "auth_required": True,
                "version": "v1"
            },
            "orders": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Order Service API",
                "description": "Order processing microservice",
                "public": False,
                "auth_required": True,
                "version": "v1"
            },
            "gateway": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "API Gateway",
                "description": "Public API gateway",
                "public": True,
                "auth_required": False,
                "version": "v1"
            }
        }
        
        config = DjangoRevolutionSettings(zones=microservices_zones)
        
        # Test zone manager with microservices
        manager = ZoneManager(config)
        detector = ZoneDetector(config)
        
        self.assertEqual(len(manager.zones), 3)
        self.assertEqual(len(detector.zones), 3)
        
        # Test service isolation
        for zone_name, zone in manager.zones.items():
            self.assertIsNotNone(zone.title)
            self.assertIsNotNone(zone.description)
            self.assertIn("Service" in zone.title or "Gateway" in zone.title, [True])


class TestPerformance(TestCase):
    """Test performance characteristics."""
    
    def test_large_zone_configuration(self):
        """Test performance with large zone configuration."""
        large_zones = {}
        
        # Create 50 zones
        for i in range(50):
            large_zones[f"zone_{i}"] = {
                "apps": [f"tests.django_sample.apps.public_api"],
                "title": f"Zone {i}",
                "description": f"Test zone {i}",
                "public": i % 2 == 0,
                "auth_required": i % 3 == 0,
                "version": f"v{i // 10 + 1}"
            }
        
        # Test configuration creation
        config = DjangoRevolutionSettings(zones=large_zones)
        zones = config.get_zones()
        
        # Should handle large configurations
        self.assertEqual(len(zones), 50)
        
        # Test zone manager performance
        manager = ZoneManager(config)
        self.assertEqual(len(manager.zones), 50)
        
        # Test detector performance
        detector = ZoneDetector(config)
        self.assertEqual(len(detector.zones), 50)
    
    def test_memory_usage(self):
        """Test memory usage with complex configurations."""
        complex_zones = {}
        
        # Create complex zone configurations
        for i in range(20):
            complex_zones[f"zone_{i}"] = {
                "apps": ["tests.django_sample.apps.public_api", "tests.django_sample.apps.private_api"],
                "title": f"Complex Zone {i}",
                "description": f"Complex zone description {i}" * 10,  # Long description
                "public": i % 2 == 0,
                "auth_required": i % 3 == 0,
                "permissions": [f"perm_{j}" for j in range(5)],
                "middleware": [f"middleware_{j}" for j in range(3)],
                "version": f"v{i // 5 + 1}",
                "cors_enabled": i % 4 == 0
            }
        
        # Test memory-efficient processing
        config = DjangoRevolutionSettings(zones=complex_zones)
        zones = config.get_zones()
        
        # Should process without memory issues
        self.assertEqual(len(zones), 20)
        
        # Test zone access performance
        for i in range(20):
            zone = config.get_zone(f"zone_{i}")
            self.assertIsNotNone(zone)
            self.assertEqual(zone.name, f"zone_{i}")
            self.assertEqual(len(zone.permissions), 5)
            self.assertEqual(len(zone.middleware), 3)


class TestEdgeCases(TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_configuration(self):
        """Test behavior with empty configuration."""
        config = DjangoRevolutionSettings(zones={})
        
        zones = config.get_zones()
        self.assertEqual(len(zones), 0)
        
        manager = ZoneManager(config)
        self.assertEqual(len(manager.zones), 0)
        
        detector = ZoneDetector(config)
        self.assertEqual(len(detector.zones), 0)
    
    def test_single_zone_configuration(self):
        """Test behavior with single zone."""
        single_zone = {
            "only": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Only Zone",
                "public": True
            }
        }
        
        config = DjangoRevolutionSettings(zones=single_zone)
        zones = config.get_zones()
        
        self.assertEqual(len(zones), 1)
        self.assertIn("only", zones)
        
        zone = zones["only"]
        self.assertEqual(zone.name, "only")
        self.assertEqual(zone.title, "Only Zone")
        self.assertTrue(zone.public)
    
    def test_zone_with_special_characters(self):
        """Test zones with special characters in names."""
        special_zones = {
            "zone-with-dashes": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Zone with Dashes"
            },
            "zone_with_underscores": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Zone with Underscores"
            }
        }
        
        config = DjangoRevolutionSettings(zones=special_zones)
        zones = config.get_zones()
        
        self.assertEqual(len(zones), 2)
        self.assertIn("zone-with-dashes", zones)
        self.assertIn("zone_with_underscores", zones)


if __name__ == "__main__":
    pytest.main([__file__]) 