%%README.LLM id=django-revolution-usage%%

# Usage Guide

**How to use Django Revolution. Real examples.**

## 🎯 Purpose

Show how to configure zones, generate clients, and use them in real projects.

## ✅ Rules

- Define zones in `api/config.py`
- Django Revolution auto-detects your configuration
- Use `python manage.py revolution` commands
- Import generated clients
- Keep it simple

## 📦 Basic Zone Setup

### 1. Auto-Detection (Recommended)

If you already have `api/config.py`, Django Revolution detects it automatically:

```python
# api/config.py (your existing file)
from django_revolution import ZoneConfig

class APIConfig(ZoneConfig):
    zones = {
        'public': {'apps': ['public_api']},
        'private': {'apps': ['private_api']}
    }
```

### 2. Generate Everything

```bash
# Auto-detects zones and generates all clients
python manage.py revolution
```

### 3. Use Generated Clients

```typescript
// TypeScript
import { client } from './tests/openapi/clients/typescript/public';
const users = await client.sdk.users.list();
```

```python
# Python
from tests.openapi.clients.python.public import PublicAPI
api = PublicAPI(base_url="https://api.example.com")
users = api.users.list()
```

## 🔧 Zone Configuration Options

### Public Zone

```python
'public': {
    'apps': ['public_api'],
    'title': 'Public API',
    'description': 'Public API for users and posts',
    'public': True,              # No auth required
    'version': 'v1'
}
```

### Private Zone

```python
'private': {
    'apps': ['private_api'],
    'title': 'Private API',
    'description': 'Private API for categories and products',
    'auth_required': True,       # Auth required
    'permissions': ['private.access'],
    'version': 'v1'
}
```

### Advanced Zone

```python
'mobile': {
    'apps': ['mobile', 'push'],
    'title': 'Mobile API',
    'description': 'Mobile application API',
    'version': 'v3',
    'prefix': 'mobile-api',      # Custom prefix
    'cors_enabled': True,
    'rate_limit': '1000/hour',
    'middleware': ['mobile.middleware.RateLimitMiddleware']
}
```

## 🚀 Using Generated Clients

### TypeScript Client (HeyAPI)

```typescript
// Import generated client
import { client } from './tests/openapi/clients/typescript/public';

// Configure base settings
client.setConfig({
  baseUrl: 'https://api.example.com',
  headers: {
    Authorization: 'Bearer your-token-here',
    'Content-Type': 'application/json',
  },
});

// Use generated SDK methods
const products = await client.sdk.products.list();
const user = await client.sdk.users.get({ id: 123 });

// Handle responses
try {
  const newProduct = await client.sdk.products.create({
    name: 'New Product',
    price: 99.99,
  });
  console.log('Created:', newProduct);
} catch (error) {
  console.error('Error:', error);
}
```

### Python Client (openapi-python-client)

```python
# Import generated client
from tests.openapi.clients.python.public import PublicAPI

# Configure client
api = PublicAPI(base_url="https://api.example.com")

# Set authentication
api.set_token("your-token-here")

# Use generated methods
products = api.products.list()
user = api.users.get(123)

# Handle responses
try:
    new_product = api.products.create(
        name="New Product",
        price=99.99
    )
    print(f"Created: {new_product}")
except Exception as error:
    print(f"Error: {error}")
```

## 🏗️ Real World Examples

### E-commerce Platform

```python
# api/config.py
from django_revolution import ZoneConfig

class EcommerceConfig(ZoneConfig):
    zones = {
        'customer': {
            'apps': ['products', 'orders', 'reviews', 'cart'],
            'title': 'Customer API',
            'description': 'Public customer-facing API',
            'public': True,
            'version': 'v1'
        },
        'seller': {
            'apps': ['inventory', 'analytics', 'payments'],
            'title': 'Seller API',
            'description': 'Seller dashboard API',
            'auth_required': True,
            'permissions': ['seller.access'],
            'version': 'v1'
        },
        'admin': {
            'apps': ['admin', 'reports', 'moderation'],
            'title': 'Admin API',
            'description': 'Administrative interface',
            'auth_required': True,
            'permissions': ['admin.full_access'],
            'version': 'v2'
        }
    }
```

### SaaS Application

```python
# api/config.py
from django_revolution import ZoneConfig

class SaaSConfig(ZoneConfig):
    zones = {
        'public': {
            'apps': ['accounts', 'pricing', 'marketing'],
            'title': 'Public API',
            'description': 'Public marketing and signup API',
            'public': True,
            'version': 'v1'
        },
        'app': {
            'apps': ['dashboard', 'projects', 'teams', 'billing'],
            'title': 'Application API',
            'description': 'Main application interface',
            'auth_required': True,
            'version': 'v2'
        },
        'webhooks': {
            'apps': ['webhooks', 'integrations'],
            'title': 'Webhooks API',
            'description': 'External integrations and webhooks',
            'auth_required': True,
            'rate_limit': '100/minute',
            'version': 'v1'
        }
    }
```

## 🎛️ Command Reference

### List Available Zones

```bash
python manage.py revolution --list-zones
```

### Check System Status

```bash
python manage.py revolution --status
```

### Generate All Clients

```bash
python manage.py revolution
```

### Generate Specific Zones

```bash
python manage.py revolution --zones public private
```

### Generate TypeScript Only

```bash
python manage.py revolution --typescript
```

### Generate Python Only

```bash
python manage.py revolution --python
```

### Clean and Regenerate

```bash
python manage.py revolution --clean
```

### Skip Archiving

```bash
python manage.py revolution --no-archive
```

### Install Dependencies

```bash
python manage.py revolution --install-deps
```

### Quiet Mode

```bash
python manage.py revolution --quiet
```

## 📁 Generated File Structure

After running `python manage.py revolution`, you'll get:

```
project/
├── tests/
│   ├── openapi/
│   │   ├── clients/
│   │   │   ├── typescript/
│   │   │   │   ├── public/          # TypeScript client for public zone
│   │   │   │   │   ├── index.ts       # Main export file
│   │   │   │   │   ├── package.json   # NPM package config
│   │   │   │   │   ├── client.gen.ts  # Generated client
│   │   │   │   │   ├── types.gen.ts   # Generated types
│   │   │   │   │   └── sdk.gen.ts     # Generated SDK
│   │   │   │   └── private/           # TypeScript client for private zone
│   │   │   └── python/
│   │   │       ├── public/          # Python client for public zone
│   │   │       │   ├── __init__.py    # Package init
│   │   │       │   └── django_revolution_public/
│   │   │       └── private/           # Python client for private zone
│   │   ├── schemas/
│   │   │   ├── public.yaml          # OpenAPI schema for public zone
│   │   │   └── private.yaml          # OpenAPI schema for private zone
│   │   └── archive/
│   │       ├── typescript/
│   │       │   ├── public.zip       # Archived TypeScript client
│   │       │   └── private.zip
│   │       └── python/
│   │           ├── public.zip       # Archived Python client
│   │           └── private.zip
```

## 🔧 Advanced Usage

### Custom Templates

Django Revolution uses Jinja2 templates that you can customize:

```python
# Custom template context
context = {
    'zone_name': 'customer',
    'title': 'Customer API Client',
    'description': 'Generated client for customer zone',
    'apps': ['products', 'orders'],
    'version': 'v1'
}
```

### Monorepo Integration

Generated clients can be automatically synced to your monorepo:

```python
# In your configuration
REVOLUTION_CONFIG = {
    'monorepo': {
        'enabled': True,
        'path': '/path/to/monorepo',
        'api_package_path': 'packages/api'
    }
}
```

### CI/CD Integration

```yaml
# .github/workflows/generate-clients.yml
name: Generate API Clients
on:
  push:
    paths: ['**/api/**', '**/models.py']

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: pip install -r requirements.txt
      - run: python manage.py revolution
      - run: git add openapi/
      - run: git commit -m "Update generated API clients" || exit 0
      - run: git push
```

%%END%%
