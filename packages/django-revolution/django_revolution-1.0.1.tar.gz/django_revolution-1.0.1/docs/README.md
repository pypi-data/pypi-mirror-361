# Django Revolution

**Zone-based API client generator for Django projects**

Django Revolution is a powerful, modern solution for organizing and generating API clients in Django projects. It introduces a revolutionary zone-based approach to API management, making it easier to maintain, scale, and generate type-safe clients for multiple languages.

## 🚀 Key Features

### **Zone-Based API Organization**

- **Logical API separation** - Organize your API into logical zones (client, admin, internal, etc.)
- **Granular control** - Each zone can have different authentication, permissions, and access levels
- **Scalable architecture** - Easily add new zones without affecting existing ones
- **Clear boundaries** - Well-defined API boundaries for different user types and use cases

### **Multi-Language Client Generation**

- **TypeScript clients** - Full-featured TypeScript SDKs with type safety
- **Python clients** - Native Python clients for backend-to-backend communication
- **OpenAPI schemas** - Automatic OpenAPI 3.0 schema generation
- **Consolidated exports** - Single entry point for all API zones

### **Seamless Django Integration**

- **Zero configuration** - Works out of the box with existing Django projects
- **Automatic URL integration** - No manual URL configuration needed
- **Management commands** - Simple `python manage.py revolution` command
- **Django settings integration** - Native integration with Django settings

### **Monorepo Support**

- **Smart file sync** - Intelligent synchronization with monorepo structures
- **Workspace integration** - Full support for pnpm/yarn workspaces
- **Build automation** - Automatic build and dependency management
- **File exclusion** - Smart exclusion of unnecessary files (package.json, node_modules)

## 🏗️ Architecture Benefits

### **1. Zone-Based Design**

```python
# Define zones in your Django settings
DJANGO_REVOLUTION = {
    'zones': {
        'client': {
            'apps': ['src.accounts', 'src.billing'],
            'title': 'Client API',
            'public': True,
            'auth_required': False,
        },
        'admin': {
            'apps': ['src.services'],
            'title': 'Admin API',
            'public': False,
            'auth_required': True,
        }
    }
}
```

### **2. Automatic URL Integration**

Django Revolution automatically creates and integrates URL patterns for each zone:

- **Zone-specific URL prefixes** - `/apix/client/`, `/apix/admin/`
- **Automatic app discovery** - Finds all apps in each zone
- **URL pattern generation** - Creates proper URL routing
- **Zero manual configuration** - Everything works automatically

### **3. Type-Safe Configuration**

Built with Pydantic 2 for modern, type-safe configuration:

- **Runtime validation** - All configuration is validated at startup
- **IDE support** - Full autocomplete and type hints
- **Error prevention** - Catch configuration errors early
- **Documentation** - Self-documenting configuration

## 🎯 Use Cases

### **Microservices Architecture**

- **Service boundaries** - Clear API boundaries between services
- **Independent scaling** - Scale different API zones independently
- **Team ownership** - Different teams can own different zones
- **Version management** - Version zones independently

### **Multi-Client Applications**

- **Web applications** - TypeScript clients for frontend
- **Mobile apps** - Generated clients for mobile development
- **Third-party integrations** - Python clients for backend integrations
- **Internal tools** - Admin and internal API zones

### **Enterprise Applications**

- **Role-based access** - Different zones for different user roles
- **Compliance** - Separate zones for sensitive data
- **Audit trails** - Clear API usage tracking per zone
- **Security** - Granular security controls

## 🔧 Technical Advantages

### **1. Developer Experience**

- **Simple setup** - One command to generate all clients
- **Hot reload** - Automatic regeneration on changes
- **Error handling** - Graceful error handling with clear messages
- **Logging** - Comprehensive logging for debugging

### **2. Performance**

- **Lazy loading** - Only load what you need
- **Tree shaking** - Remove unused code in production
- **Caching** - Smart caching of generated content
- **Optimized builds** - Production-ready client builds

### **3. Maintainability**

- **Single source of truth** - All API definitions in one place
- **Consistent patterns** - Standardized API patterns across zones
- **Easy updates** - Update all clients with one command
- **Version control** - Track API changes in version control

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

### **1. Installation**

```bash
pip install django-revolution
```

### **2. Configuration**

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

### **3. Generate Clients**

```bash
python manage.py revolution --typescript --python
```

### **4. Use Generated Clients**

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

### **1. Revolutionary Approach**

Django Revolution introduces a completely new way of thinking about API organization in Django projects. Instead of monolithic APIs, it promotes a zone-based approach that scales with your application.

### **2. Developer Productivity**

- **90% less boilerplate** - Automatic generation eliminates repetitive code
- **Type safety** - Catch errors at compile time, not runtime
- **Hot reload** - See changes immediately during development
- **One command** - Generate all clients with a single command

### **3. Enterprise Ready**

- **Scalable architecture** - Grows with your application
- **Security focused** - Built-in security controls per zone
- **Compliance ready** - Audit trails and access controls
- **Team friendly** - Clear ownership and boundaries

### **4. Future Proof**

- **Modern stack** - Built with the latest technologies (Pydantic 2, OpenAPI 3.0)
- **Extensible** - Easy to add new features and languages
- **Community driven** - Open source with active development
- **Standards compliant** - Follows industry best practices

## 🔮 Roadmap

### **Phase 1 (Current)**

- ✅ Zone-based API organization
- ✅ TypeScript and Python client generation
- ✅ Monorepo integration
- ✅ Django integration

### **Phase 2 (Planned)**

- 🔄 GraphQL schema generation
- 🔄 Go and Rust client generation
- 🔄 Testing integration
- 🔄 Documentation generation

### **Phase 3 (Future)**

- 📋 CI/CD integration
- 📋 Cloud deployment support
- 📋 Advanced caching strategies
- 📋 Performance monitoring

## 🤝 Contributing

Django Revolution is open source and welcomes contributions! Whether you're fixing bugs, adding features, or improving documentation, your contributions are valuable.

## 📄 License

MIT License - see LICENSE file for details.

---

**Django Revolution** - Revolutionizing API development in Django projects since 2024 🚀
