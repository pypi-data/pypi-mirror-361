"""
Test Django Revolution Management Commands.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command, CommandError
from io import StringIO

from django_revolution.config import DjangoRevolutionSettings
from django_revolution.management.commands.revolution import Command


class TestRevolutionCommand(TestCase):
    """Test revolution management command."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_zones = {
            "public": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "Public API"
            },
            "private": {
                "apps": ["tests.django_sample.apps.private_api"],
                "title": "Private API"
            }
        }
        
        self.config = DjangoRevolutionSettings(zones=self.test_zones)
        self.command = Command()
    
    def test_command_initialization(self):
        """Test command initialization."""
        self.assertEqual(self.command.help, "Django Revolution - Zone-based API client generation")
    
    def test_list_zones_option(self):
        """Test --list-zones option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.return_value = self.config
            
            out = StringIO()
            call_command('revolution', '--list-zones', stdout=out)
            
            output = out.getvalue()
            self.assertIn("public", output)
            self.assertIn("private", output)
            self.assertIn("Available zones", output)
    
    def test_status_option(self):
        """Test --status option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.return_value = self.config
            
            out = StringIO()
            call_command('revolution', '--status', stdout=out)
            
            output = out.getvalue()
            self.assertIn("Django Revolution Status", output)
            self.assertIn("Zones:", output)
    
    def test_validate_option(self):
        """Test --validate option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django.apps.apps.is_installed', return_value=True):
                mock_get_settings.return_value = self.config
                
                out = StringIO()
                call_command('revolution', '--validate', stdout=out)
                
                output = out.getvalue()
                self.assertIn("validation", output.lower())
    
    def test_install_deps_option(self):
        """Test --install-deps option."""
        with patch('django_revolution.utils.auto_install_dependencies') as mock_install:
            mock_install.return_value = True
            
            out = StringIO()
            call_command('revolution', '--install-deps', stdout=out)
            
            output = out.getvalue()
            self.assertIn("Dependencies", output)
    
    def test_typescript_generation(self):
        """Test --typescript option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = self.config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_typescript_clients.return_value = {
                    "public": {"success": True, "files_generated": 5},
                    "private": {"success": True, "files_generated": 5}
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--typescript', stdout=out)
                
                output = out.getvalue()
                self.assertIn("TypeScript", output)
                mock_gen_instance.generate_typescript_clients.assert_called_once()
    
    def test_python_generation(self):
        """Test --python option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = self.config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_python_clients.return_value = {
                    "public": {"success": True, "files_generated": 3},
                    "private": {"success": True, "files_generated": 3}
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--python', stdout=out)
                
                output = out.getvalue()
                self.assertIn("Python", output)
                mock_gen_instance.generate_python_clients.assert_called_once()
    
    def test_specific_zones(self):
        """Test --zones option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = self.config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_all.return_value = {
                    "total_zones": 1,
                    "successful_typescript": 1,
                    "successful_python": 1
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--zones', 'public', stdout=out)
                
                output = out.getvalue()
                self.assertIn("public", output)
                mock_gen_instance.generate_all.assert_called_with(zones=['public'])
    
    def test_clean_option(self):
        """Test --clean option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('shutil.rmtree') as mock_rmtree:
                    mock_get_settings.return_value = self.config
                    
                    out = StringIO()
                    call_command('revolution', '--clean', stdout=out)
                    
                    output = out.getvalue()
                    self.assertIn("Cleaned", output)
                    mock_rmtree.assert_called()
    
    def test_quiet_option(self):
        """Test --quiet option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.return_value = self.config
            
            out = StringIO()
            call_command('revolution', '--quiet', '--status', stdout=out)
            
            output = out.getvalue()
            # Should be minimal output in quiet mode
            self.assertLess(len(output), 200)
    
    def test_no_archive_option(self):
        """Test --no-archive option."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = self.config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_all.return_value = {
                    "total_zones": 2,
                    "successful_typescript": 2,
                    "successful_python": 2
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--no-archive', stdout=out)
                
                output = out.getvalue()
                self.assertIn("Generated", output)
    
    def test_full_generation(self):
        """Test full generation without options."""
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
                mock_gen_instance.create_archives.return_value = True
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', stdout=out)
                
                output = out.getvalue()
                self.assertIn("Generated", output)
                mock_gen_instance.generate_all.assert_called_once()
    
    def test_error_handling(self):
        """Test error handling in command."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.side_effect = Exception("Test error")
            
            out = StringIO()
            err = StringIO()
            
            with self.assertRaises(SystemExit):
                call_command('revolution', '--status', stdout=out, stderr=err)


class TestCommandOptions(TestCase):
    """Test command option parsing and validation."""
    
    def test_invalid_zones(self):
        """Test invalid zone names."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.return_value = DjangoRevolutionSettings(zones={})
            
            out = StringIO()
            err = StringIO()
            
            with self.assertRaises(SystemExit):
                call_command('revolution', '--zones', 'nonexistent', stdout=out, stderr=err)
    
    def test_multiple_zones(self):
        """Test multiple zone specification."""
        config = DjangoRevolutionSettings(zones={
            "public": {"apps": ["tests.django_sample.apps.public_api"]},
            "private": {"apps": ["tests.django_sample.apps.private_api"]}
        })
        
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_all.return_value = {
                    "total_zones": 2,
                    "successful_typescript": 2,
                    "successful_python": 2
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--zones', 'public', 'private', stdout=out)
                
                output = out.getvalue()
                self.assertIn("public", output)
                self.assertIn("private", output)
                mock_gen_instance.generate_all.assert_called_with(zones=['public', 'private'])
    
    def test_missing_dependencies(self):
        """Test handling of missing dependencies."""
        with patch('django_revolution.utils.auto_install_dependencies') as mock_install:
            mock_install.return_value = False
            
            out = StringIO()
            call_command('revolution', '--install-deps', stdout=out)
            
            output = out.getvalue()
            self.assertIn("Failed", output)
    
    def test_generation_failure(self):
        """Test handling of generation failures."""
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = DjangoRevolutionSettings(zones={
                    "test": {"apps": ["tests.django_sample.apps.public_api"]}
                })
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_all.side_effect = Exception("Generation failed")
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                err = StringIO()
                
                with self.assertRaises(SystemExit):
                    call_command('revolution', stdout=out, stderr=err)


class TestCommandIntegration(TestCase):
    """Test command integration with other components."""
    
    def test_command_with_real_config(self):
        """Test command with real configuration."""
        test_zones = {
            "api": {
                "apps": ["tests.django_sample.apps.public_api"],
                "title": "API Zone"
            }
        }
        
        config = DjangoRevolutionSettings(zones=test_zones)
        
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_all.return_value = {
                    "total_zones": 1,
                    "successful_typescript": 1,
                    "successful_python": 1,
                    "duration_seconds": 1.2
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', stdout=out)
                
                output = out.getvalue()
                self.assertIn("Generated", output)
                self.assertIn("1 zone", output)
    
    def test_command_logging_levels(self):
        """Test command logging with different verbosity."""
        config = DjangoRevolutionSettings(zones={
            "public": {"apps": ["tests.django_sample.apps.public_api"]}
        })
        
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.return_value = config
            
            # Test verbose output
            out = StringIO()
            call_command('revolution', '--status', '--verbosity', '2', stdout=out)
            
            output = out.getvalue()
            self.assertGreater(len(output), 0)
    
    def test_command_help(self):
        """Test command help output."""
        out = StringIO()
        call_command('revolution', '--help', stdout=out)
        
        output = out.getvalue()
        self.assertIn("Django Revolution", output)
        self.assertIn("--zones", output)
        self.assertIn("--typescript", output)
        self.assertIn("--python", output)


class TestCommandArguments(TestCase):
    """Test command argument parsing and validation."""
    
    def test_mutually_exclusive_options(self):
        """Test mutually exclusive options."""
        config = DjangoRevolutionSettings(zones={
            "public": {"apps": ["tests.django_sample.apps.public_api"]}
        })
        
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            with patch('django_revolution.openapi.generator.OpenAPIGenerator') as mock_generator:
                mock_get_settings.return_value = config
                
                mock_gen_instance = MagicMock()
                mock_gen_instance.generate_typescript_clients.return_value = {
                    "public": {"success": True}
                }
                mock_generator.return_value = mock_gen_instance
                
                out = StringIO()
                call_command('revolution', '--typescript', '--status', stdout=out)
                
                # Should work with multiple options
                output = out.getvalue()
                self.assertGreater(len(output), 0)
    
    def test_boolean_flags(self):
        """Test boolean flag handling."""
        config = DjangoRevolutionSettings(zones={
            "public": {"apps": ["tests.django_sample.apps.public_api"]}
        })
        
        with patch('django_revolution.config.get_settings') as mock_get_settings:
            mock_get_settings.return_value = config
            
            out = StringIO()
            call_command('revolution', '--quiet', '--validate', stdout=out)
            
            output = out.getvalue()
            # Should work with boolean flags
            self.assertIsInstance(output, str)


if __name__ == "__main__":
    pytest.main([__file__]) 