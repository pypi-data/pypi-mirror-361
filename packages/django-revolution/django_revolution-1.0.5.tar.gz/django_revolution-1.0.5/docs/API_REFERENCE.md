%%README.LLM id=django-revolution-api%%

# API Reference

**Complete API documentation for Django Revolution.**

## 🎯 Purpose

Reference documentation for classes, methods, and configuration options.

## ✅ Rules

- Auto-detects existing Django `api.config.APIConfig`
- All dependencies auto-installed
- Minimal configuration required
- Easy to extend

## 🧾 Core Classes

### DjangoRevolutionSettings (Pydantic)

Main configuration class for Django Revolution, using Pydantic 2.

```python
from django_revolution.config import DjangoRevolutionSettings, get_settings

settings = get_settings()
print(settings.api_prefix)  # 'apix'
print(settings.zones)       # {'public': {...}, 'private': {...}}
```

**Fields:**

- `api_prefix: str` - API prefix for all routes
- `output: OutputSettings` - Output directories
- `generators: GeneratorsSettings` - Generator configs
- `monorepo: MonorepoSettings` - Monorepo integration
- `zones: Dict[str, Dict[str, Any]]` - Zone configurations

### ZoneModel (Pydantic)

Pydantic model for individual zone configuration.

```python
from django_revolution.config import ZoneModel

zone = ZoneModel(
    name='public',
    apps=['public_api'],
    title='Public API',
    description='Public API for users and posts',
    public=True,
    version='v1'
)
```

**Fields:**

- `name: str` - Zone name
- `apps: List[str]` - Django apps in zone
- `title: Optional[str]`
- `description: Optional[str]`
- `public: bool`
- `auth_required: bool`
- `rate_limit: Optional[str]`
- `permissions: Optional[List[str]]`
- `version: str`
- `prefix: Optional[str]`
- `cors_enabled: bool`
- `middleware: Optional[List[str]]`
- `path_prefix: Optional[str]`

### ZoneDetector

Auto-detects zones from Django configuration.

```python
from django_revolution.zones import ZoneDetector

detector = ZoneDetector()
zones = detector.detect_zones()  # Returns Dict[str, ZoneModel]
```

**Methods:**

- `detect_zones() -> Dict[str, ZoneModel]`
- `get_zone_names() -> List[str]`
- `get_zone(name: str) -> Optional[ZoneModel]`
- `validate_zone(zone_name: str) -> bool`
- `get_zones_summary() -> Dict[str, Any]`

### OpenAPIGenerator

Main generator for OpenAPI schemas and clients.

```python
from django_revolution.openapi import OpenAPIGenerator

generator = OpenAPIGenerator()
summary = generator.generate_all()  # Generate all clients
```

**Methods:**

- `generate_all(zones: Optional[List[str]] = None) -> GenerationSummary`
- `detect_zones() -> Dict[str, ZoneModel]`
- `generate_schemas_for_zones(zones: Dict[str, ZoneModel]) -> Dict[str, Path]`
- `generate_typescript_clients(zones, schemas) -> Dict[str, GenerationResult]`
- `generate_python_clients(zones, schemas) -> Dict[str, GenerationResult]`
- `archive_clients(zones, ts_results, py_results) -> Dict[str, Any]`
- `get_status() -> Dict[str, Any]`
- `clean_output() -> bool`

### GenerationSummary

Result summary from client generation.

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class GenerationSummary:
    total_zones: int
    successful_typescript: int
    successful_python: int
    failed_typescript: int
    failed_python: int
    total_files_generated: int
    duration_seconds: float
    typescript_results: Dict[str, GenerationResult]
    python_results: Dict[str, GenerationResult]
```

### HeyAPITypeScriptGenerator

TypeScript client generator using HeyAPI.

```python
from django_revolution.openapi import HeyAPITypeScriptGenerator

generator = HeyAPITypeScriptGenerator(config, logger)
result = generator.generate(zone, schema_path)
```

### PythonClientGenerator

Python client generator using openapi-python-client.

```python
from django_revolution.openapi import PythonClientGenerator

generator = PythonClientGenerator(config, logger)
result = generator.generate(zone, schema_path)
```

## 🎛️ Configuration

### Django Settings

```python
# settings.py
INSTALLED_APPS = [
    'django_revolution',
    # your apps
]

# Optional configuration
REVOLUTION_CONFIG = {
    'output_dir': 'openapi',           # Base output directory
    'auto_install_deps': True,         # Auto-install dependencies
    'typescript_enabled': True,        # Enable TypeScript generation
    'python_enabled': True,            # Enable Python generation
    'archive_clients': True,           # Archive generated clients
    'monorepo': {
        'enabled': False,              # Enable monorepo sync
        'path': '/path/to/monorepo',
        'api_package_path': 'packages/api'
    }
}
```

### Zone Configuration Options

```python
# Complete zone configuration
zone_options = {
    # Required
    'apps': ['app1', 'app2'],         # List of Django apps

    # Metadata
    'title': 'Zone Title',            # Human-readable title
    'description': 'Zone description', # Zone description

    # Access Control
    'public': True,                   # No auth required
    'auth_required': False,           # Auth required
    'permissions': ['perm1'],         # Required permissions

    # Versioning & URLs
    'version': 'v1',                  # API version
    'prefix': 'custom',               # Custom URL prefix
    'path_prefix': 'custom-path',     # Custom path prefix

    # Features
    'cors_enabled': True,             # Enable CORS
    'rate_limit': '1000/hour',        # Rate limit string
    'middleware': ['custom.middleware'], # Custom middleware
}
```

## 📋 Management Commands

### revolution

Main Django management command for client generation.

```bash
python manage.py revolution [options]
```

**Options:**

- `--zones ZONE [ZONE ...]` - Specific zones to generate
- `--typescript` - Generate TypeScript clients only
- `--python` - Generate Python clients only
- `--no-typescript` - Skip TypeScript generation
- `--no-python` - Skip Python generation
- `--no-archive` - Skip archiving
- `--no-monorepo` - Skip monorepo sync
- `--clean` - Clean output directories
- `--status` - Show current status
- `--list-zones` - List available zones
- `--validate` - Validate environment
- `--install-deps` - Install dependencies
- `--output-dir PATH` - Override output directory
- `--debug` - Enable debug logging

## 🔧 Utility Functions

### get_settings()

Get Django Revolution settings with validation.

```python
from django_revolution.config import get_settings

settings = get_settings()
print(settings.zones)
```

### create_generator()

Create OpenAPIGenerator instance with default settings.

```python
from django_revolution import create_generator

generator = create_generator()
summary = generator.generate_all()
```

### quick_generate()

Quick generation function for common use cases.

```python
from django_revolution import quick_generate

summary = quick_generate(
    zones=['public', 'admin'],
    typescript=True,
    python=True,
    archive=True
)
```

### add_revolution_urls()

Add Django Revolution URLs to URL patterns.

```python
from django_revolution.urls_integration import add_revolution_urls

urlpatterns = [
    # Your existing URLs
    path('admin/', admin.site.urls),
]

# Add Django Revolution URLs
urlpatterns = add_revolution_urls(urlpatterns)
```

## 🎯 CLI Interface

### Standalone CLI

Interactive CLI with rich interface.

```bash
django-revolution
```

**Features:**

- Zone selection with checkboxes
- Client type selection (TypeScript/Python)
- Archive creation options
- Real-time progress tracking
- Generation summary with results table

### Programmatic CLI

```python
from django_revolution.cli import main

# Run CLI programmatically
main()
```

## 🔍 Error Handling

### ErrorHandler

Consistent error handling across the library.

```python
from django_revolution.utils import ErrorHandler

error_handler = ErrorHandler()

try:
    result = operation()
except Exception as e:
    error_handler.handle_exception(e, "Operation context")
```

### Logger

Rich console logging with emojis and progress.

```python
from django_revolution.utils import Logger

logger = Logger("component_name")
logger.info("🔍 Starting operation...")
logger.success("✅ Operation completed")
logger.error("❌ Operation failed")
logger.warning("⚠️ Warning message")
```

## 🛠️ Extension Points

### Custom Generators

Extend the generation system with custom generators.

```python
from django_revolution.openapi import BaseGenerator

class CustomGenerator(BaseGenerator):
    def generate(self, zone: ZoneModel, schema_path: str) -> GenerationResult:
        # Custom generation logic
        pass

# Register in OpenAPIGenerator
generator.custom_generator = CustomGenerator(config, logger)
```

### Custom Templates

Override default Jinja2 templates.

```python
# In configuration
DJANGO_REVOLUTION = {
    'generators': {
        'typescript': {
            'custom_templates': './templates/typescript'
        },
        'python': {
            'custom_templates': './templates/python'
        }
    }
}
```

### Custom Zone Types

Extend zone configuration with custom fields.

```python
from django_revolution.config import ZoneModel

class CustomZoneModel(ZoneModel):
    custom_field: Optional[str] = None

    def get_custom_config(self):
        return self.custom_field
```

%%END%%
