"""
Python Client Generator for Django Revolution

Generates Python clients using openapi-python-client.
"""

from pathlib import Path
from typing import Dict, Optional, Any

from ..config import DjangoRevolutionSettings, GenerationResult
from ..utils import Logger, run_command, check_dependency, ensure_directories


class PythonClientGenerator:
    """Python client generator using openapi-python-client."""
    
    def __init__(self, config: DjangoRevolutionSettings, logger: Optional[Logger] = None):
        """
        Initialize Python generator.
        
        Args:
            config: Django Revolution settings
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or Logger("python_client_generator")
        self.output_dir = Path(config.generators.python.output_directory)
        
    def is_available(self) -> bool:
        """
        Check if openapi-python-client is available.
        
        Returns:
            bool: True if available
        """
        return check_dependency(['openapi-python-client', '--version'])
    
    def generate_client(self, zone_name: str, schema_path: Path) -> GenerationResult:
        """
        Generate Python client for a single zone.
        
        Args:
            zone_name: Name of the zone
            schema_path: Path to OpenAPI schema file
            
        Returns:
            GenerationResult with operation details
        """
        self.logger.info(f"Generating Python client for zone: {zone_name}")
        
        # Validate schema file
        if not schema_path.exists():
            error_msg = f"Schema file not found: {schema_path}"
            self.logger.error(error_msg)
            return GenerationResult(
                success=False,
                zone_name=zone_name,
                output_path=Path(),
                files_generated=0,
                error_message=error_msg
            )
        
        # Setup output directory
        zone_output_dir = self.output_dir / zone_name
        ensure_directories(zone_output_dir)
        
        # Generate project and package names
        project_name = self.config.generators.python.project_name_template.format(zone=zone_name)
        
        try:
            # Build command for openapi-python-client
            cmd = [
                'openapi-python-client',
                'generate',
                '--path', str(schema_path),
                '--output-path', str(zone_output_dir)
            ]
            
            # Add overwrite flag if enabled
            if self.config.generators.python.overwrite:
                cmd.append('--overwrite')
            
            # Add fail-on-warning flag if enabled
            if self.config.generators.python.fail_on_warning:
                cmd.append('--fail-on-warning')
            
            # Add custom templates if specified
            if self.config.generators.python.custom_templates:
                cmd.extend(['--custom-template-path', self.config.generators.python.custom_templates])
            
            success, output = run_command(' '.join(cmd), timeout=120)
            
            if success:
                # Count generated files
                generated_dir = zone_output_dir / project_name
                files_generated = self._count_generated_files(generated_dir)
                
                # Enhance the generated client
                self._enhance_client(zone_name, generated_dir)
                
                # Generate files using templates (after enhancement to override generated files)
                self._generate_from_templates(zone_name, generated_dir)
                
                self.logger.success(f"Python client generated for {zone_name}: {files_generated} files")
                
                return GenerationResult(
                    success=True,
                    zone_name=zone_name,
                    output_path=generated_dir,
                    files_generated=files_generated,
                    error_message=""
                )
            else:
                error_msg = f"Python generation failed: {output}"
                self.logger.error(error_msg)
                
                return GenerationResult(
                    success=False,
                    zone_name=zone_name,
                    output_path=zone_output_dir,
                    files_generated=0,
                    error_message=error_msg
                )
                
        except Exception as e:
            error_msg = f"Python generation exception: {str(e)}"
            self.logger.error(error_msg)
            
            return GenerationResult(
                success=False,
                zone_name=zone_name,
                output_path=zone_output_dir,
                files_generated=0,
                error_message=error_msg
            )
    
    def generate_all(self, schemas: Dict[str, Path]) -> Dict[str, GenerationResult]:
        """
        Generate Python clients for all provided schemas.
        
        Args:
            schemas: Dictionary mapping zone names to schema paths
            
        Returns:
            Dictionary mapping zone names to generation results
        """
        if not schemas:
            self.logger.warning("No schemas provided for Python generation")
            return {}
        
        self.logger.info(f"Generating Python clients for {len(schemas)} zones")
        
        results = {}
        
        for zone_name, schema_path in schemas.items():
            result = self.generate_client(zone_name, schema_path)
            results[zone_name] = result
        
        successful = sum(1 for r in results.values() if r.success)
        self.logger.info(f"Python generation completed: {successful}/{len(results)} successful")
        
        return results
    
    def _count_generated_files(self, directory: Path) -> int:
        """
        Count the number of generated files in a directory.
        
        Args:
            directory: Directory to count files in
            
        Returns:
            Number of files generated
        """
        if not directory.exists():
            return 0
        
        count = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                count += 1
        
        return count
    
    def _generate_from_templates(self, zone_name: str, output_dir: Path):
        """
        Generate files using Jinja2 templates.
        
        Args:
            zone_name: Name of the zone
            output_dir: Output directory for the client (zone root)
        """
        try:
            import jinja2
            from datetime import datetime
            
            # Setup Jinja2 environment
            templates_dir = Path(__file__).parent / 'templates'
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Get zone info from config
            zones = self.config.zones
            zone_info = zones.get(zone_name, {})
            
            # Prepare context for templates
            context = {
                'zone_name': zone_name,
                'title': zone_info.get('title', f'{zone_name.title()} API'),
                'description': zone_info.get('description', f'Python client for {zone_name} zone'),
                'apps': zone_info.get('apps', []),
                'generation_time': datetime.now().isoformat(),
            }
            
            # Найти реальную папку Python-пакета (где лежит __init__.py)
            package_dir = None
            for sub in output_dir.iterdir():
                if sub.is_dir() and (sub / '__init__.py').exists():
                    package_dir = sub
                    break
            if not package_dir:
                self.logger.warning(f"Не удалось найти пакет для шаблона в {output_dir}")
                return
            
            # Сгенерировать __init__.py по шаблону
            init_template = env.get_template('__init__.py.j2')
            init_content = init_template.render(**context)
            with open(package_dir / '__init__.py', 'w', encoding='utf-8') as f:
                f.write(init_content)
            
            self.logger.debug(f"Generated template __init__.py for {zone_name} in {package_dir}")
            
        except ImportError:
            self.logger.warning("Jinja2 not available, skipping template generation")
        except Exception as e:
            self.logger.warning(f"Failed to generate template files for {zone_name}: {e}")
    
    def _enhance_client(self, zone_name: str, client_dir: Path):
        """
        Enhance the generated Python client with additional features.
        
        Args:
            zone_name: Name of the zone
            client_dir: Directory containing the generated client
        """
        try:
            # Add convenience imports to __init__.py
            self._add_convenience_imports(client_dir)
            
            # Generate usage example
            self._generate_usage_example(zone_name, client_dir)
            
            # Enhance setup.py if it exists
            self._enhance_setup_py(zone_name, client_dir)
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance client for {zone_name}: {e}")
    
    def _add_convenience_imports(self, client_dir: Path):
        """Add convenience imports to the package __init__.py."""
        init_file = None
        
        # Find the main package __init__.py
        for python_file in client_dir.rglob('__init__.py'):
            if 'client' in str(python_file) or 'api' in str(python_file):
                init_file = python_file
                break
        
        if not init_file or not init_file.exists():
            return
        
        # Read existing content
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add convenience imports if not already present
            convenience_imports = '''
# Convenience imports for easier usage
try:
    from .client import Client
    from .models import *
    from .api import *
    __all__ = ['Client']
except ImportError:
    pass
'''
            
            if 'Convenience imports' not in content:
                content = content + convenience_imports
                
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
        except Exception as e:
            self.logger.debug(f"Could not enhance __init__.py: {e}")
    
    def _generate_usage_example(self, zone_name: str, client_dir: Path):
        """Generate a usage example file."""
        example_content = f'''"""
Usage example for {zone_name} API client.

This file demonstrates how to use the generated client.
"""

from {self.config.generators.python.package_name_template.format(zone=zone_name)} import Client

# Initialize the client
client = Client(base_url="https://api.example.com")

# Example usage:
# response = client.some_endpoint.get_data()
# print(response)

if __name__ == "__main__":
    print(f"{{zone_name}} API client is ready to use!")
'''
        
        example_file = client_dir / "example.py"
        
        try:
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(example_content)
        except Exception as e:
            self.logger.debug(f"Could not generate example file: {e}")
    
    def _enhance_setup_py(self, zone_name: str, client_dir: Path):
        """Enhance setup.py with better metadata."""
        setup_file = client_dir / "setup.py"
        
        if not setup_file.exists():
            return
        
        try:
            with open(setup_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add additional metadata
            enhancements = f'''
# Enhanced by Django Revolution
setup_kwargs.update({{
    "keywords": ["api", "client", "openapi", "{zone_name}", "django-revolution"],
    "project_urls": {{
        "Source": "https://github.com/markolofsen/django-revolution",
        "Documentation": "https://github.com/markolofsen/django-revolution",
    }},
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
}})
'''
            
            if 'Enhanced by Django Revolution' not in content:
                # Insert before the final setup() call
                setup_call_pos = content.rfind('setup(')
                if setup_call_pos > 0:
                    content = content[:setup_call_pos] + enhancements + '\n' + content[setup_call_pos:]
                    
                    with open(setup_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
        except Exception as e:
            self.logger.debug(f"Could not enhance setup.py: {e}")
    
    def clean_output(self) -> bool:
        """
        Clean Python output directory.
        
        Returns:
            bool: True if cleaning successful
        """
        try:
            if self.output_dir.exists():
                import shutil
                shutil.rmtree(self.output_dir)
            
            ensure_directories(self.output_dir)
            self.logger.success("Python output directory cleaned")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clean Python output directory: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get Python generator status.
        
        Returns:
            Status information dictionary
        """
        return {
            'available': self.is_available(),
            'output_directory': str(self.output_dir),
            'enabled': self.config.generators.python.enabled,
            'project_name_template': self.config.generators.python.project_name_template,
            'package_name_template': self.config.generators.python.package_name_template,
            'overwrite': self.config.generators.python.overwrite,
            'fail_on_warning': self.config.generators.python.fail_on_warning,
            'custom_templates': self.config.generators.python.custom_templates
        } 