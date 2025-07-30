"""
Monorepo Sync for Django Revolution

Synchronizes generated clients to monorepo structure.
"""

import shutil
import json
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import DjangoRevolutionSettings
from ..utils import Logger, ensure_directories, run_command


class MonorepoSync:
    """Synchronizes generated clients to monorepo."""
    
    def __init__(self, config: DjangoRevolutionSettings, logger: Logger):
        """
        Initialize monorepo sync.
        
        Args:
            config: Django Revolution settings
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.monorepo_path = Path(config.monorepo.path)
        self.api_package_path = self.monorepo_path / config.monorepo.api_package_path
        
    def sync_typescript_client(self, zone_name: str, client_path: Path) -> Dict[str, Any]:
        """
        Sync TypeScript client to monorepo.
        
        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client
            
        Returns:
            Sync operation result
        """
        if not self.config.monorepo.enabled:
            return {'success': False, 'error': 'Monorepo sync disabled'}
        
        target_path = self.api_package_path / 'typescript' / zone_name
        
        return self._sync_client(
            zone_name=zone_name,
            client_path=client_path,
            target_path=target_path,
            client_type='typescript'
        )
    
    def sync_python_client(self, zone_name: str, client_path: Path) -> Dict[str, Any]:
        """
        Sync Python client to monorepo.
        
        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client
            
        Returns:
            Sync operation result
        """
        if not self.config.monorepo.enabled:
            return {'success': False, 'error': 'Monorepo sync disabled'}
        
        target_path = self.api_package_path / 'python' / zone_name
        
        return self._sync_client(
            zone_name=zone_name,
            client_path=client_path,
            target_path=target_path,
            client_type='python'
        )
    
    def _sync_client(self, zone_name: str, client_path: Path, target_path: Path, client_type: str) -> Dict[str, Any]:
        """
        Sync a client to monorepo target path.
        
        Args:
            zone_name: Name of the zone
            client_path: Source client path
            target_path: Target path in monorepo
            client_type: Type of client (typescript/python)
            
        Returns:
            Sync operation result
        """
        try:
            # Validate source path
            if not client_path.exists():
                error_msg = f"Source client path does not exist: {client_path}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'zone_name': zone_name,
                    'client_type': client_type
                }
            
            # Validate monorepo exists
            if not self.monorepo_path.exists():
                error_msg = f"Monorepo path does not exist: {self.monorepo_path}"
                self.logger.warning(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'zone_name': zone_name,
                    'client_type': client_type
                }
            
            # Ensure target directory exists
            ensure_directories(target_path.parent)
            
            # Remove existing target if it exists
            if target_path.exists():
                shutil.rmtree(target_path)
            
            # Copy client to monorepo (excluding package.json and node_modules)
            def ignore_files(dir, files):
                ignored = []
                if 'package.json' in files:
                    ignored.append('package.json')
                if 'node_modules' in files:
                    ignored.append('node_modules')
                return ignored
            
            shutil.copytree(client_path, target_path, ignore=ignore_files)
            
            # Update monorepo-specific files
            self._update_monorepo_files(zone_name, target_path, client_type)
            
            # Run monorepo-specific commands
            sync_commands = self._run_monorepo_commands(target_path, client_type)
            
            self.logger.success(f"Synced {client_type} client for {zone_name} to monorepo")
            
            return {
                'success': True,
                'zone_name': zone_name,
                'client_type': client_type,
                'target_path': str(target_path),
                'commands_run': sync_commands
            }
            
        except Exception as e:
            error_msg = f"Failed to sync {client_type} client for {zone_name}: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'zone_name': zone_name,
                'client_type': client_type
            }
    
    def _update_monorepo_files(self, zone_name: str, target_path: Path, client_type: str):
        """Update monorepo-specific configuration files."""
        if client_type == 'typescript':
            self._update_typescript_monorepo_files(zone_name, target_path)
        elif client_type == 'python':
            self._update_python_monorepo_files(zone_name, target_path)
    
    def _update_typescript_monorepo_files(self, zone_name: str, target_path: Path):
        """Update TypeScript monorepo files."""
        # Update package.json for monorepo workspace
        package_json_path = target_path / 'package.json'
        
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                # Update for monorepo workspace
                package_data['name'] = f"@unrealos{zone_name}-api-client"
                package_data['private'] = True  # Monorepo packages are usually private
                package_data['version'] = "workspace:*"
                
                # Add monorepo-specific scripts
                if 'scripts' not in package_data:
                    package_data['scripts'] = {}
                
                package_data['scripts'].update({
                    'build': 'tsc --build',
                    'clean': 'rm -rf dist',
                    'dev': 'tsc --watch',
                    'lint': 'eslint . --ext .ts --fix',
                    'type-check': 'tsc --noEmit'
                })
                
                # Add workspace dependencies
                if 'devDependencies' not in package_data:
                    package_data['devDependencies'] = {}
                
                # Write updated package.json
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_data, f, indent=2, ensure_ascii=False)
                
                self.logger.debug(f"Updated package.json for {zone_name}")
                
            except Exception as e:
                self.logger.warning(f"Failed to update package.json for {zone_name}: {e}")
        
        # Create/update tsconfig.json for monorepo
        tsconfig_path = target_path / 'tsconfig.json'
        tsconfig_data = {
            "extends": "../../tsconfig.base.json",
            "compilerOptions": {
                "outDir": "./dist",
                "rootDir": "./src",
                "declarationDir": "./dist/types"
            },
            "include": [
                "src/**/*",
                "*.ts"
            ],
            "exclude": [
                "dist",
                "node_modules",
                "**/*.test.ts",
                "**/*.spec.ts"
            ],
            "references": []
        }
        
        try:
            with open(tsconfig_path, 'w', encoding='utf-8') as f:
                json.dump(tsconfig_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Failed to create tsconfig.json for {zone_name}: {e}")
    
    def _update_python_monorepo_files(self, zone_name: str, target_path: Path):
        """Update Python monorepo files."""
        # Update setup.py or pyproject.toml for monorepo
        setup_py_path = target_path / 'setup.py'
        
        if setup_py_path.exists():
            try:
                with open(setup_py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add monorepo-specific configuration
                monorepo_config = '''
# Monorepo configuration
import os
import sys

# Add shared modules path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

# Monorepo version management
def get_version():
    """Get version from monorepo version file or environment."""
    version_file = os.path.join(os.path.dirname(__file__), '..', '..', 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return os.environ.get('MONOREPO_VERSION', '0.1.0')

# Override version if not already set
if 'version=' not in setup_kwargs:
    setup_kwargs['version'] = get_version()
'''
                
                if 'Monorepo configuration' not in content:
                    # Insert at the beginning
                    content = monorepo_config + '\n' + content
                    
                    with open(setup_py_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
            except Exception as e:
                self.logger.warning(f"Failed to update setup.py for {zone_name}: {e}")
    
    def _run_monorepo_commands(self, target_path: Path, client_type: str) -> list:
        """Run monorepo-specific commands after sync."""
        commands_run = []
        
        if client_type == 'typescript':
            # Install dependencies using workspace
            if (self.monorepo_path / 'pnpm-workspace.yaml').exists():
                cmd = 'pnpm install'
                success, output = run_command(cmd, cwd=self.monorepo_path, timeout=60)
                commands_run.append({
                    'command': cmd,
                    'success': success,
                    'output': output[:200] if output else ''  # Truncate output
                })
            
            # НЕ билдим отдельные пакеты - билдим только основной пакет монорепо
        
        elif client_type == 'python':
            # Install in development mode
            if (target_path / 'setup.py').exists():
                cmd = 'pip install -e .'
                success, output = run_command(cmd, cwd=target_path, timeout=120)
                commands_run.append({
                    'command': cmd,
                    'success': success,
                    'output': output[:200] if output else ''
                })
        
        return commands_run
    
    def sync_all_clients(self, clients_dir: Path) -> Dict[str, Any]:
        """
        Sync all generated clients to monorepo.
        
        Args:
            clients_dir: Base clients directory
            
        Returns:
            Overall sync operation results
        """
        if not self.config.monorepo.enabled:
            self.logger.info("Monorepo sync disabled")
            return {'success': False, 'error': 'Monorepo sync disabled'}
        
        sync_results = {
            'typescript': {},
            'python': {},
            'summary': {
                'total_synced': 0,
                'successful': 0,
                'failed': 0
            }
        }
        
        # Sync TypeScript clients
        typescript_dir = clients_dir / 'typescript'
        if typescript_dir.exists():
            for zone_dir in typescript_dir.iterdir():
                if zone_dir.is_dir():
                    zone_name = zone_dir.name
                    result = self.sync_typescript_client(zone_name, zone_dir)
                    sync_results['typescript'][zone_name] = result
                    
                    if result.get('success'):
                        sync_results['summary']['successful'] += 1
                    else:
                        sync_results['summary']['failed'] += 1
                    
                    sync_results['summary']['total_synced'] += 1
        
        # Копируем consolidated index.ts
        consolidated_index = typescript_dir / 'index.ts'
        if consolidated_index.exists():
            target_index = self.api_package_path / 'typescript' / 'index.ts'
            try:
                shutil.copy2(consolidated_index, target_index)
                self.logger.success(f"Copied consolidated index.ts to monorepo: {target_index}")
            except Exception as e:
                self.logger.warning(f"Failed to copy consolidated index.ts: {e}")
        
        # Запускаем build в основном пакете api, если есть package.json
        build_dir = self.api_package_path.parent  # Переходим на уровень выше от src к api
        if (build_dir / 'package.json').exists():
            cmd = 'pnpm build'
            success, output = run_command(cmd, cwd=build_dir, timeout=120)
            self.logger.info(f"Build for main api package: {'OK' if success else 'FAIL'}")
            if not success:
                self.logger.warning(f"Build output: {output[:500] if output else 'No output'}")
        else:
            self.logger.warning(f"package.json not found in {build_dir}")
        
        # Update monorepo workspace configuration
        self._update_workspace_config(sync_results)
        
        self.logger.info(
            f"Monorepo sync completed: {sync_results['summary']['successful']} successful, "
            f"{sync_results['summary']['failed']} failed"
        )
        
        return sync_results
    
    def _find_python_client_path(self, zone_dir: Path) -> Optional[Path]:
        """Find the actual Python client path (might be nested)."""
        # Look for setup.py or pyproject.toml
        for item in zone_dir.rglob('setup.py'):
            return item.parent
        
        for item in zone_dir.rglob('pyproject.toml'):
            return item.parent
        
        # Fallback to the zone directory itself
        return zone_dir if zone_dir.exists() else None
    
    def _update_workspace_config(self, sync_results: Dict[str, Any]):
        """Update monorepo workspace configuration."""
        # Update pnpm workspace if it exists
        workspace_file = self.monorepo_path / 'pnpm-workspace.yaml'
        
        if workspace_file.exists():
            try:
                import yaml
                
                with open(workspace_file, 'r', encoding='utf-8') as f:
                    workspace_config = yaml.safe_load(f)
                
                if 'packages' not in workspace_config:
                    workspace_config['packages'] = []
                
                # Add API packages
                api_packages_pattern = f"{self.config.monorepo.api_package_path}/**"
                if api_packages_pattern not in workspace_config['packages']:
                    workspace_config['packages'].append(api_packages_pattern)
                
                with open(workspace_file, 'w', encoding='utf-8') as f:
                    yaml.dump(workspace_config, f, default_flow_style=False)
                
                self.logger.debug("Updated pnpm workspace configuration")
                
            except ImportError:
                self.logger.warning("PyYAML not available, cannot update workspace config")
            except Exception as e:
                self.logger.warning(f"Failed to update workspace config: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get monorepo sync status.
        
        Returns:
            Status information dictionary
        """
        return {
            'enabled': self.config.monorepo.enabled,
            'monorepo_path': str(self.monorepo_path),
            'monorepo_exists': self.monorepo_path.exists(),
            'api_package_path': str(self.api_package_path),
            'workspace_files': {
                'pnpm_workspace': (self.monorepo_path / 'pnpm-workspace.yaml').exists(),
                'package_json': (self.monorepo_path / 'package.json').exists(),
                'lerna_json': (self.monorepo_path / 'lerna.json').exists(),
                'turbo_json': (self.monorepo_path / 'turbo.json').exists()
            }
        }
    
    def clean_monorepo_clients(self) -> Dict[str, Any]:
        """
        Clean generated clients from monorepo.
        
        Returns:
            Cleanup operation results
        """
        if not self.config.monorepo.enabled:
            return {'success': False, 'error': 'Monorepo sync disabled'}
        
        results = {
            'typescript_cleaned': 0,
            'python_cleaned': 0,
            'errors': []
        }
        
        try:
            # Clean TypeScript clients only
            ts_dir = self.api_package_path / 'typescript'
            if ts_dir.exists():
                for zone_dir in ts_dir.iterdir():
                    if zone_dir.is_dir():
                        shutil.rmtree(zone_dir)
                        results['typescript_cleaned'] += 1
            
            # Skip Python clients for monorepo
            # py_dir = self.api_package_path / 'python'
            # if py_dir.exists():
            #     for zone_dir in py_dir.iterdir():
            #         if zone_dir.is_dir():
            #             shutil.rmtree(zone_dir)
            #             results['python_cleaned'] += 1
            
            total_cleaned = results['typescript_cleaned']  # Only TypeScript
            self.logger.success(f"Cleaned {total_cleaned} TypeScript clients from monorepo")
            
        except Exception as e:
            error_msg = f"Failed to clean monorepo clients: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results 