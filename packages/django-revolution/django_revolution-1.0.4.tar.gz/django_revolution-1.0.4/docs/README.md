%%README.LLM id=django-revolution-overview%%

# Django Revolution Overview

**Zone-based API client generator for Django projects**

## 🎯 Purpose

Django Revolution organizes APIs into logical zones and generates type-safe clients for multiple languages. Zero configuration, automatic OpenAPI schema generation, monorepo integration.

## ✅ Rules

- Define zones in `api/config.py` or Django settings
- Use `python manage.py revolution` for generation
- Auto-installs dependencies (HeyAPI, openapi-python-client)
- Supports monorepo integration
- Archives clients with versioning

## 🚀 Key Features

### Zone-Based API Organization

```python
# Define zones in Django settings
DJANGO_REVOLUTION = {
    'zones': {
        'client': {
            'apps': ['src.accounts', 'src.billing'],
            'title': 'Client API',
            'public': True,
        },
        'admin': {
            'apps': ['src.services'],
            'title': 'Admin API',
            'auth_required': True,
        }
    }
}
```

### Multi-Language Client Generation

- **TypeScript clients** - Full-featured TypeScript SDKs with type safety
- **Python clients** - Native Python clients for backend-to-backend communication
- **OpenAPI schemas** - Automatic OpenAPI 3.0 schema generation
- **Consolidated exports** - Single entry point for all API zones

### Seamless Django Integration

- **Zero configuration** - Works out of the box with existing Django projects
- **Automatic URL integration** - No manual URL configuration needed
- **Management commands** - Simple `python manage.py revolution` command
- **Django settings integration** - Native integration with Django settings

### Monorepo Support

- **Smart file sync** - Intelligent synchronization with monorepo structures
- **Workspace integration** - Full support for pnpm/yarn workspaces
- **Build automation** - Automatic build and dependency management

## 🏗️ Architecture Benefits

### Zone-Based Design

```python
# Each zone has clear boundaries
'client': {
    'apps': ['src.accounts', 'src.billing'],
    'title': 'Client API',
    'public': True,
    'auth_required': False,
}
```

### Automatic URL Integration

Django Revolution automatically creates URL patterns:

- **Zone-specific prefixes** - `/apix/client/`, `/apix/admin/`
- **Automatic app discovery** - Finds all apps in each zone
- **URL pattern generation** - Creates proper URL routing

### Type-Safe Configuration

Built with Pydantic 2 for modern, type-safe configuration:

- **Runtime validation** - All configuration is validated at startup
- **IDE support** - Full autocomplete and type hints
- **Error prevention** - Catch configuration errors early

## 🎯 Use Cases

### Microservices Architecture

- **Service boundaries** - Clear API boundaries between services
- **Independent scaling** - Scale different API zones independently
- **Team ownership** - Different teams can own different zones

### Multi-Client Applications

- **Web applications** - TypeScript clients for frontend
- **Mobile apps** - Generated clients for mobile development
- **Third-party integrations** - Python clients for backend integrations

### Enterprise Applications

- **Role-based access** - Different zones for different user roles
- **Compliance** - Separate zones for sensitive data
- **Security** - Granular security controls

## 🔧 Technical Advantages

### Developer Experience

- **Simple setup** - One command to generate all clients
- **Hot reload** - Automatic regeneration on changes
- **Error handling** - Graceful error handling with clear messages

### Performance

- **Lazy loading** - Only load what you need
- **Tree shaking** - Remove unused code in production
- **Caching** - Smart caching of generated content

### Maintainability

- **Single source of truth** - All API definitions in one place
- **Consistent patterns** - Standardized API patterns across zones
- **Easy updates** - Update all clients with one command

## 📊 Comparison with Alternatives

| Feature                   | Django Revolution | DRF | FastAPI |
| ------------------------- | ----------------- | --- | ------- |
| Zone-based organization   | ✅                | ❌  | ❌      |
| Multi-language clients    | ✅                | ❌  | ❌      |
| Monorepo integration      | ✅                | ❌  | ❌      |
| Automatic URL integration | ✅                | ❌  | ❌      |
| Type-safe configuration   | ✅                | ❌  | ✅      |
| Django integration        | ✅                | ✅  | ❌      |

## 🚀 Getting Started

### Installation

```bash
pip install django-revolution
```

### Configuration

```python
# settings.py
DJANGO_REVOLUTION = {
    'api_prefix': 'apix',
    'zones': {
        'client': {
            'apps': ['src.accounts', 'src.billing'],
            'title': 'Client API',
            'public': True,
        }
    }
}
```

### Generate Clients

```bash
python manage.py revolution --typescript --python
```

### Use Generated Clients

```typescript
// TypeScript
import { ClientAPI } from '@unrealos/client-api-client';

const client = new ClientAPI({
  baseURL: 'http://localhost:8000/apix/client',
});

const user = await client.accounts.getUser(1);
```

```python
# Python
from client_api_client import ClientAPI

client = ClientAPI(base_url="http://localhost:8000/apix/client")
user = client.accounts.get_user(1)
```

## 🎉 Why Django Revolution?

### Revolutionary Approach

Django Revolution introduces a completely new way of thinking about API organization in Django projects. Instead of monolithic APIs, it promotes a zone-based approach that scales with your application.

### Developer Productivity

- **90% less boilerplate** - Automatic generation eliminates repetitive code
- **Type safety** - Catch errors at compile time, not runtime
- **Hot reload** - See changes immediately during development
- **One command** - Generate all clients with a single command

### Enterprise Ready

- **Scalable architecture** - Grows with your application
- **Security focused** - Built-in security controls per zone
- **Compliance ready** - Audit trails and access controls
- **Team friendly** - Clear ownership and boundaries

%%END%%
