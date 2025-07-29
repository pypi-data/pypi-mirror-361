%%README.LLM id=django-revolution-architecture%%

# Architecture

**How Django Revolution works under the hood.**

## 🎯 Purpose

Understand Django Revolution's modular architecture. Clean components, clear separation of concerns.

## ✅ Rules

- Zone-based organization
- Auto-discovery from Django configuration
- Industry-standard tools (HeyAPI, openapi-python-client)
- KISS principle throughout

## 🏗️ Core Components

### 1. Zone Detection (`zones.py`)

- **ZoneDetector** - Auto-finds zones from Django `api.config.APIConfig`
- **Zone** - Dataclass representing individual zone configuration
- **ZoneConfig** - Base configuration for defining zones
- **ZoneManager** - Generates URL patterns and manages zone routing

### 2. URL Management (`urls/`)

- **get_urls()** - Main entry point for URL generation
- **URLLogger** - Rich console logging with emojis and progress
- **URLAnalyzer** - Analyzes URL patterns and provides insights
- **ZoneManager** - Creates zone-specific URL patterns

### 3. OpenAPI Generation (`openapi/`)

- **OpenAPIGenerator** - Orchestrates the entire generation process
- **HeyAPITypeScriptGenerator** - TypeScript client generation using HeyAPI
- **PythonClientGenerator** - Python client generation using openapi-python-client
- **Template System** - Jinja2 templates for custom client generation
- **Auto-installer** - Automatically installs npm dependencies

### 4. Management Commands (`management/`)

- **revolution** - Django management command with rich CLI interface
- **Auto-dependency installation** - Installs HeyAPI and openapi-python-client
- **Status checking** - Validates system state and dependencies

## 📊 System Flow

```mermaid
graph TD
    A[Django APIConfig] --> B[ZoneDetector]
    B --> C[Zone Objects]
    C --> D[Schema Generator]
    C --> E[URL Manager]
    D --> F[OpenAPI Schemas]
    F --> G[HeyAPI TypeScript]
    F --> H[openapi-python-client]
    G --> I[TypeScript Clients]
    H --> J[Python Clients]
    I --> K[ZIP Archives]
    J --> K
    E --> L[URL Patterns]
```

## 🔧 How It Works

### 1. Zone Detection Process

```python
# 1. ZoneDetector scans for api.config.APIConfig
detector = ZoneDetector(logger)
zones = detector.detect_zones()

# 2. Converts to Zone objects with validation
for zone_name, zone_data in zones.items():
    zone = Zone(
        name=zone_name,  # 'public' or 'private'
        apps=zone_data['apps'],  # ['public_api'] or ['private_api']
        title=zone_data.get('title', zone_name.title()),
        description=zone_data.get('description'),
        # ... other attributes
    )
```

### 2. URL Generation

```python
# 1. Creates dynamic URL modules for each zone
def create_zone_urlconf_module(zone_name, zone_config):
    # Generates Python module with URL patterns

# 2. Creates schema endpoints
urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(urlconf=zone_urlconf)),
    path('schema/swagger/', SpectacularSwaggerView.as_view()),
]
```

### 3. Schema Generation

```python
# 1. Uses Django's spectacular to generate schemas
cmd = [
    "python", "manage.py", "spectacular",
    "--file", schema_file,
    "--urlconf", zone_urlconf_module
]

# 2. Creates isolated schemas per zone
schemas/
├── public.yaml
├── private.yaml
└── partner.yaml
```

### 4. Client Generation Pipeline

```python
# 1. TypeScript generation (HeyAPI)
cmd = [
    'npx', '@hey-api/openapi-ts',
    '--input', schema_path,
    '--output', output_dir,
    '--client', 'legacy/fetch'
]

# 2. Python generation (openapi-python-client)
cmd = [
    'openapi-python-client',
    'generate',
    '--url', f'file://{schema_path}',
    '--output-path', output_dir
]

# 3. Template rendering (Jinja2)
template.render(zone_name=zone.name, apps=zone.apps)

# 4. Archiving to ZIP
zipfile.ZipFile(archive_path, 'w')
```

## 📁 Module Structure

```
django_revolution/
├── __init__.py                    # Main exports
├── apps.py                       # Django app configuration
├── zones.py                      # Zone management
├── urls/
│   ├── __init__.py               # URL generation entry point
│   ├── utils.py                  # URLLogger, URLAnalyzer
│   └── zones.py                  # ZoneManager re-export
├── openapi/
│   ├── __init__.py               # OpenAPI exports
│   ├── generator.py              # Main OpenAPI orchestrator
│   ├── heyapi_ts.py             # TypeScript generator
│   ├── python_client.py         # Python generator
│   ├── utils.py                 # Logger, ErrorHandler, auto-install
│   ├── zones.py                 # Zone detection re-export
│   └── templates/               # Jinja2 templates
│       ├── __init__.py.j2       # Python package template
│       ├── index.ts.j2          # TypeScript index template
│       ├── package.json.j2      # NPM package template
│       └── index_consolidated.ts.j2  # Consolidated exports
└── management/
    └── commands/
        └── revolution.py         # Django management command
```

## 🔄 Process Flow Detail

### 1. Initialization Phase

```python
# When Django starts:
1. DjangoRevolutionConfig.ready() called
2. ensure_directories() creates output folders
3. ZoneDetector.setup_django() validates Django environment
4. URLLogger initialized for rich console output
```

### 2. Zone Discovery Phase

```python
# When command runs:
1. ZoneDetector.detect_zones() scans for api.config.APIConfig
2. Validates zone configuration (apps exist, no duplicates)
3. Creates Zone objects with full metadata
4. Logs discovered zones with rich formatting
```

### 3. Schema Generation Phase

```python
# For each zone:
1. create_zone_urlconf_module() generates dynamic URL module
2. Django spectacular extracts OpenAPI schema
3. Schema saved to openapi/schemas/{zone_name}.yaml
4. Progress logged with success/failure indicators
```

### 4. Client Generation Phase

```python
# For each zone:
1. HeyAPITypeScriptGenerator.generate() creates TS client
2. PythonClientGenerator.generate() creates Python client
3. Template files rendered with Jinja2
4. Files counted and logged
5. Clients archived to ZIP files
```

## 🛠️ Configuration System

### Auto-Detection Configuration

```python
# Django Revolution auto-detects this pattern:
# api/config.py
from django_revolution import ZoneConfig

class APIConfig(ZoneConfig):
    zones = {
        'public': {
            'apps': ['public_api'],          # Required
            'title': 'Public API',           # Auto-generated if missing
            'description': 'Public API for users and posts', # Auto-generated if missing
            'public': True,                  # Default: True
            'auth_required': False,          # Default: False
            'version': 'v1',                 # Default: 'v1'
            'path_prefix': 'public'          # Default: zone_name
        },
        'private': {
            'apps': ['private_api'],         # Required
            'title': 'Private API',          # Auto-generated if missing
            'description': 'Private API for categories and products', # Auto-generated if missing
            'public': False,                 # Default: True
            'auth_required': True,           # Default: False
            'version': 'v1',                 # Default: 'v1'
            'path_prefix': 'private'         # Default: zone_name
        }
    }
```

### Generated Configuration

```python
# Automatic configuration from get_config():
{
    'output': {
        'base_directory': 'openapi',
        'schemas_directory': 'schemas',
        'clients_directory': 'clients',
        'archive_directory_ts': 'archive/typescript',
        'archive_directory_py': 'archive/python'
    },
    'generators': {
        'typescript': {
            'enabled': True,
            'output_directory': 'openapi/clients/typescript',
            'settings': {'output_format': 'prettier'}
        },
        'python': {
            'enabled': True,
            'output_directory': 'openapi/clients/python',
            'settings': {
                'project_name_template': 'django_revolution_{zone}',
                'overwrite': True
            }
        }
    }
}
```

## 🧩 Extension Points

### Custom Zone Types

```python
# Extend Zone dataclass for custom functionality
@dataclass
class CustomZone(Zone):
    """Custom zone with additional features."""
    rate_limit: Optional[str] = None
    custom_middleware: List[str] = field(default_factory=list)

    def get_rate_limit_config(self):
        # Custom rate limiting logic
        pass
```

### Custom Templates

```python
# Override default templates
class CustomHeyAPIGenerator(HeyAPITypeScriptGenerator):
    def _generate_template_files(self, zone, output_dir):
        # Use custom templates
        custom_templates_dir = Path('custom/templates')
        # ... custom template rendering
```

### Custom Generators

```python
# Add new client generators
class SwiftClientGenerator:
    def generate(self, zone: Zone, schema_path: str):
        # Generate Swift client
        pass

# Register in OpenAPIGenerator
generator.swift_generator = SwiftClientGenerator(config, logger)
```

## 🔍 Error Handling

### Graceful Degradation

```python
# ErrorHandler provides consistent error management
try:
    result = operation()
except Exception as e:
    return error_handler.handle_exception(e, "Operation context")
    # Logs error, continues with other operations
```

### Dependency Validation

```python
# Auto-installer checks and installs dependencies
dependencies = [
    {'name': '@hey-api/openapi-ts', 'check_cmd': ['npx', '@hey-api/openapi-ts', '--version']},
    {'name': 'openapi-python-client', 'check_cmd': ['openapi-python-client', '--version']}
]

# Automatically installs missing dependencies
auto_install_dependencies()
```

### Rich Logging

```python
# Logger provides beautiful console output
logger.info("🔍 Detecting zones...")
logger.success("✅ Generated TypeScript client for customer zone")
logger.error("❌ Failed to generate schema for admin zone")
logger.warning("⚠️ Node.js not found, skipping TypeScript generation")
```

## 🚀 Performance Optimizations

### Parallel Processing

```python
# Generate multiple clients simultaneously (future enhancement)
with ThreadPoolExecutor() as executor:
    typescript_futures = [executor.submit(ts_gen.generate, zone) for zone in zones]
    python_futures = [executor.submit(py_gen.generate, zone) for zone in zones]
```

### Caching

```python
# Cache zone detection results
@lru_cache(maxsize=1)
def detect_zones():
    # Expensive zone detection only runs once
    return zone_detector.detect_zones()
```

### Incremental Generation

```python
# Only regenerate if schema changed (future enhancement)
if schema_file.stat().st_mtime > client_dir_mtime:
    generate_client(zone, schema_file)
```

%%END%%
