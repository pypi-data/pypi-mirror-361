# Django Revolution

> **Zero-config TypeScript & Python client generator for Django REST Framework** 🚀

[![PyPI version](https://badge.fury.io/py/django-revolution.svg)](https://badge.fury.io/py/django-revolution)
[![Python Support](https://img.shields.io/pypi/pyversions/django-revolution.svg)](https://pypi.org/project/django-revolution/)
[![Django Support](https://img.shields.io/pypi/djversions/django-revolution.svg)](https://pypi.org/project/django-revolution/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## ✨ What is Django Revolution?

**The fastest way to generate fully-authenticated TypeScript + Python clients from Django REST Framework.**

- 🧩 Organize your API into **zones** (`public`, `admin`, `mobile`, etc.)
- ⚙️ Generate strongly typed clients with **one command**
- 🔐 Built-in support for **Bearer tokens**, refresh logic, and API keys
- 🔄 Zero config for **Swagger/OpenAPI URLs**, **frontend integration**, and **monorepos**

> No boilerplate. No manual sync. Just clean clients in seconds.

## 🧪 Example: Instantly Get a Typed API Client

```typescript
import API from '@carapis/api-client';

const api = new API('https://api.example.com');
api.setToken('your-access-token');

const profile = await api.client.getProfile();
const cars = await api.encar_public.listCars();
```

> 🔐 Auth, ⚙️ Headers, 🔄 Refresh – handled automatically.

## ⛔ Without Django Revolution

Manually update OpenAPI spec → Run generator → Fix broken types → Sync clients → Write token logic → Repeat on every change.

## ✅ With Django Revolution

One command. Done.

## 🚀 5-Minute Setup

### 1. Install

```bash
pip install django-revolution
```

### 2. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    'drf_spectacular',
    'django_revolution',  # Add this line
]

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your API',
    'VERSION': '1.0.0',
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### 3. Configure Zones

```python
# settings.py
DJANGO_REVOLUTION = {
    'zones': {
        'public': {
            'apps': ['products', 'categories'],
            'title': 'Public API',
            'public': True,
        },
        'admin': {
            'apps': ['admin_panel', 'analytics'],
            'title': 'Admin API',
            'auth_required': True,
        }
    },
    'monorepo': {
        'enabled': True,
        'path': '../monorepo',
        'api_package_path': 'packages/api'
    }
}
```

### 4. Generate Clients

```bash
# Generate everything
python manage.py revolution

# Generate specific zones
python manage.py revolution --zones public admin

# TypeScript only
python manage.py revolution --typescript
```

## 🧬 What Does It Generate?

| Language       | Location                            | Structure                                                 |
| -------------- | ----------------------------------- | --------------------------------------------------------- |
| **TypeScript** | `monorepo/packages/api/typescript/` | `public/`, `admin/` → `index.ts`, `types.ts`, `services/` |
| **Python**     | `monorepo/packages/api/python/`     | `public/`, `admin/` → `client.py`, `models/`, `setup.py`  |

💡 Each zone gets its own NPM/PyPI-style package. Ready to publish or import.

## ⚡️ TypeScript Client Auth & Usage

Django Revolution automatically generates a smart TypeScript API client with built-in authentication and token management:

- **Zone-based organization** - All endpoints grouped by zones (client, admin, internal, etc.)
- **Authentication ready** - Bearer tokens, refresh tokens, custom headers out of the box
- **Simple integration** - Works with React, Next.js, Vue, or any frontend framework
- **Type-safe** - Full TypeScript support with autocomplete

**Example Usage:**

```typescript
import API from '@carapis/api-client';

const api = new API('https://api.example.com');

// Authentication
api.setToken('your-access-token', 'your-refresh-token');

// Call any endpoint
const user = await api.client.getCurrentUser();
const products = await api.client.listProducts();

// Check authentication status
if (api.isAuthenticated()) {
  // User is logged in
}

// Change API URL
api.setApiUrl('https://api.newhost.com');
```

**Features included:**

- ✅ Automatic token management (localStorage)
- ✅ Custom headers support
- ✅ API key authentication
- ✅ Zone-based endpoint organization
- ✅ TypeScript types for all endpoints
- ✅ Error handling and validation

> **No need to write authentication logic - everything is handled automatically!**

## 🌐 Auto-Generated URLs

Django Revolution **automatically generates** all necessary URLs for your API zones:

```python
# urls.py
from django_revolution import add_revolution_urls

urlpatterns = [
    # Your existing URLs
    path('admin/', admin.site.urls),
]

# Django Revolution automatically adds:
# - /api/public/schema/ (Swagger UI)
# - /api/public/schema.yaml (OpenAPI spec)
# - /api/admin/schema/ (Swagger UI)
# - /api/admin/schema.yaml (OpenAPI spec)
# - /openapi/archive/ (Generated clients)
urlpatterns = add_revolution_urls(urlpatterns)
```

**Generated URLs:**

- `/api/{zone}/schema/` - Interactive Swagger UI
- `/api/{zone}/schema.yaml` - OpenAPI specification
- `/openapi/archive/` - Download generated clients

## 🧪 CLI Toolbox

```bash
# Generate all clients
python manage.py revolution

# Specific zones
python manage.py revolution --zones public admin

# Generator options
python manage.py revolution --typescript
python manage.py revolution --python
python manage.py revolution --no-archive

# Utility commands
python manage.py revolution --status
python manage.py revolution --list-zones
python manage.py revolution --validate
python manage.py revolution --clean
```

## 🪆 Monorepo-Friendly

Django Revolution **automatically configures** your monorepo:

```yaml
# pnpm-workspace.yaml (auto-generated)
packages:
  - 'packages/**'
  - 'packages/api/**' # Added automatically
```

**Package.json dependencies:**

```json
{
  "dependencies": {
    "@unrealos/public-api-client": "workspace:*",
    "@unrealos/admin-api-client": "workspace:*"
  }
}
```

## 🔧 Configuration

### Environment Variables

```bash
export DJANGO_REVOLUTION_DEBUG=true
export DJANGO_REVOLUTION_API_PREFIX=apix
export DJANGO_REVOLUTION_AUTO_INSTALL_DEPS=true
```

### Zone Configuration

```python
'zones': {
    'zone_name': {
        'apps': ['app1', 'app2'],           # Required
        'title': 'Human Readable Title',    # Optional
        'description': 'Zone description',  # Optional
        'public': True,                     # Optional
        'auth_required': False,             # Optional
        'rate_limit': '1000/hour',          # Optional
        'permissions': ['perm1', 'perm2'],  # Optional
        'version': 'v1',                    # Optional
        'prefix': 'custom_prefix',          # Optional
        'cors_enabled': False,              # Optional
    }
}
```

## ✅ When to Use

### ✅ Perfect For

- **Large Django projects** with multiple API audiences
- **Monorepo architectures** with frontend/backend separation
- **Teams** needing consistent API client generation
- **Projects** requiring zone-based API organization
- **Automated CI/CD** pipelines

### ❌ Not For

- **Simple single-zone APIs** (overkill)
- **Non-Django projects** (use Fern.dev instead)
- **Manual control freaks** (use drf-spectacular + generators)

## 🧠 Power Features

### Archive Management

```bash
# Automatic versioning
openapi/archive/
├── typescript/
│   ├── 2024-01-15_14-30-00/
│   └── 2024-01-15_15-45-00/
└── python/
    ├── 2024-01-15_14-30-00/
    └── 2024-01-15_15-45-00/
```

### Custom Templates

```python
'generators': {
    'typescript': {
        'custom_templates': './templates/typescript'
    },
    'python': {
        'custom_templates': './templates/python'
    }
}
```

### Programmatic Usage

```python
from django_revolution import OpenAPIGenerator, get_settings

config = get_settings()
generator = OpenAPIGenerator(config)
summary = generator.generate_all(zones=['public', 'admin'])
```

## 📊 Comparison Table

| Feature                         | Django Revolution  | drf-spectacular + generators | openapi-generator-cli | Fern.dev | Manual Setup |
| ------------------------------- | ------------------ | ---------------------------- | --------------------- | -------- | ------------ |
| **Zone-based architecture**     | ✅ **UNIQUE**      | ❌                           | ❌                    | ✅       | ❌           |
| **Automatic URL generation**    | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Monorepo integration**        | ✅ **UNIQUE**      | ❌                           | ❌                    | ✅       | ❌           |
| **Django management commands**  | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Archive management**          | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **TypeScript + Python clients** | ✅                 | ✅                           | ✅                    | ✅       | ✅           |
| **DRF native integration**      | ✅ **SEAMLESS**    | ✅                           | ⚠️ (via schema)       | ❌       | ✅           |
| **Zero configuration**          | ✅ **UNIQUE**      | ❌                           | ❌                    | ❌       | ❌           |
| **Environment variables**       | ✅ **Pydantic**    | ❌                           | ❌                    | ❌       | ❌           |
| **CLI interface**               | ✅ **Rich output** | ❌                           | ✅                    | ✅       | ❌           |

## 🙋 FAQ

**Q: Is this production-ready?**  
✅ Yes. Used in monorepos and multi-tenant production apps.

**Q: What if I use DRF with custom auth?**  
Use `setHeaders()` or `setApiKey()` to inject custom logic.

**Q: Can I use this in non-monorepo setups?**  
Absolutely. Monorepo is optional.

**Q: What if I need only TypeScript clients?**  
Use `--typescript` flag to generate only TS clients.

**Q: Does it support custom OpenAPI decorators?**  
Yes, built on `drf-spectacular` so all extensions apply.

## 🤝 Contributing

```bash
# Development setup
git clone https://github.com/unrealos/django-revolution.git
cd django-revolution
pip install -e ".[dev]"

# Run tests
pytest
black django_revolution/
isort django_revolution/
```

## 📞 Support

- **Documentation**: [https://django-revolution.readthedocs.io/](https://django-revolution.readthedocs.io/)
- **Issues**: [https://github.com/markolofsen/django-revolution/issues](https://github.com/markolofsen/django-revolution/issues)
- **Discussions**: [https://github.com/markolofsen/django-revolution/discussions](https://github.com/markolofsen/django-revolution/discussions)

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the [Unrealos Team](https://unrealos.com)**

**Django Revolution** - The **ONLY** tool that makes Django API client generation **truly automated** and **zone-aware**.
