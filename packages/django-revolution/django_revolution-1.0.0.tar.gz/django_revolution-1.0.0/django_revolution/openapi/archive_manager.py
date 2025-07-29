"""
Archive Manager for Django Revolution

Manages archiving of generated clients with versioning and compression.
"""

import shutil
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from ..config import DjangoRevolutionSettings, GenerationResult
from ..utils import Logger, ensure_directories


class ArchiveManager:
    """Manages archiving of generated client libraries."""
    
    def __init__(self, config: DjangoRevolutionSettings, logger: Logger, output_dir: Path):
        """
        Initialize archive manager.
        
        Args:
            config: Django Revolution settings
            logger: Logger instance
            output_dir: Base output directory
        """
        self.config = config
        self.logger = logger
        self.output_dir = output_dir
        
        # Setup archive directories
        self.ts_archive_dir = output_dir / config.output.archive_directory_ts
        self.py_archive_dir = output_dir / config.output.archive_directory_py
        
        ensure_directories(self.ts_archive_dir, self.py_archive_dir)
    
    def archive_typescript_client(self, zone_name: str, client_path: Path) -> Dict[str, Any]:
        """
        Archive a TypeScript client.
        
        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client
            
        Returns:
            Archive operation result
        """
        return self._archive_client(
            zone_name=zone_name,
            client_path=client_path,
            archive_dir=self.ts_archive_dir,
            client_type="typescript"
        )
    
    def archive_python_client(self, zone_name: str, client_path: Path) -> Dict[str, Any]:
        """
        Archive a Python client.
        
        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client
            
        Returns:
            Archive operation result
        """
        return self._archive_client(
            zone_name=zone_name,
            client_path=client_path,
            archive_dir=self.py_archive_dir,
            client_type="python"
        )
    
    def _archive_client(self, zone_name: str, client_path: Path, archive_dir: Path, client_type: str) -> Dict[str, Any]:
        """
        Archive a client with compression and metadata.
        
        Args:
            zone_name: Name of the zone
            client_path: Path to the generated client
            archive_dir: Directory for archives
            client_type: Type of client (typescript/python)
            
        Returns:
            Archive operation result
        """
        if not client_path.exists():
            error_msg = f"Client path does not exist: {client_path}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'zone_name': zone_name,
                'client_type': client_type
            }
        
        try:
            # Generate timestamp for versioning
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create archive filename
            archive_filename = f"{zone_name}_{client_type}_{timestamp}"
            
            # Create both tar.gz and zip archives
            tar_path = archive_dir / f"{archive_filename}.tar.gz"
            zip_path = archive_dir / f"{archive_filename}.zip"
            
            # Create tar.gz archive
            self._create_tar_archive(client_path, tar_path)
            
            # Create zip archive
            self._create_zip_archive(client_path, zip_path)
            
            # Generate metadata
            metadata = self._generate_metadata(zone_name, client_type, client_path, timestamp)
            metadata_path = archive_dir / f"{archive_filename}_metadata.json"
            
            self._write_metadata(metadata, metadata_path)
            
            # Create latest symlinks
            self._create_latest_symlinks(archive_dir, zone_name, client_type, tar_path, zip_path)
            
            self.logger.success(f"Archived {client_type} client for {zone_name}")
            
            return {
                'success': True,
                'zone_name': zone_name,
                'client_type': client_type,
                'tar_archive': str(tar_path),
                'zip_archive': str(zip_path),
                'metadata': str(metadata_path),
                'timestamp': timestamp
            }
            
        except Exception as e:
            error_msg = f"Failed to archive {client_type} client for {zone_name}: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'zone_name': zone_name,
                'client_type': client_type
            }
    
    def _create_tar_archive(self, source_path: Path, archive_path: Path):
        """Create a tar.gz archive."""
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_path, arcname=source_path.name)
    
    def _create_zip_archive(self, source_path: Path, archive_path: Path):
        """Create a zip archive."""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    # Create relative path for archive
                    relative_path = file_path.relative_to(source_path.parent)
                    zipf.write(file_path, relative_path)
    
    def _generate_metadata(self, zone_name: str, client_type: str, client_path: Path, timestamp: str) -> Dict[str, Any]:
        """Generate metadata for the archived client."""
        # Count files and calculate size
        file_count = 0
        total_size = 0
        
        for file_path in client_path.rglob('*'):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size
        
        return {
            'zone_name': zone_name,
            'client_type': client_type,
            'timestamp': timestamp,
            'archive_date': datetime.now().isoformat(),
            'client_path': str(client_path),
            'file_count': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'generator_version': '2.0.0',
            'config': {
                'typescript': self.config.generators.typescript.model_dump() if client_type == 'typescript' else None,
                'python': self.config.generators.python.model_dump() if client_type == 'python' else None
            }
        }
    
    def _write_metadata(self, metadata: Dict[str, Any], metadata_path: Path):
        """Write metadata to JSON file."""
        import json
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _create_latest_symlinks(self, archive_dir: Path, zone_name: str, client_type: str, tar_path: Path, zip_path: Path):
        """Create symlinks to the latest archives."""
        latest_tar = archive_dir / f"{zone_name}_{client_type}_latest.tar.gz"
        latest_zip = archive_dir / f"{zone_name}_{client_type}_latest.zip"
        
        # Remove existing symlinks
        for symlink in [latest_tar, latest_zip]:
            if symlink.is_symlink():
                symlink.unlink()
        
        # Create new symlinks
        try:
            latest_tar.symlink_to(tar_path.name)
            latest_zip.symlink_to(zip_path.name)
        except OSError:
            # Symlinks might not be supported on all systems
            # Copy files instead
            shutil.copy2(tar_path, latest_tar)
            shutil.copy2(zip_path, latest_zip)
    
    def archive_all_clients(self, clients_dir: Path, typescript_results: Dict[str, GenerationResult], python_results: Dict[str, GenerationResult]) -> Dict[str, Any]:
        """
        Archive all generated clients.
        
        Args:
            clients_dir: Base clients directory
            typescript_results: TypeScript generation results
            python_results: Python generation results
            
        Returns:
            Overall archive operation results
        """
        archive_results = {
            'typescript': {},
            'python': {},
            'summary': {
                'total_archived': 0,
                'successful': 0,
                'failed': 0
            }
        }
        
        # Archive TypeScript clients
        for zone_name, result in typescript_results.items():
            if result.success:
                archive_result = self.archive_typescript_client(zone_name, result.output_path)
                archive_results['typescript'][zone_name] = archive_result
                
                if archive_result['success']:
                    archive_results['summary']['successful'] += 1
                else:
                    archive_results['summary']['failed'] += 1
                
                archive_results['summary']['total_archived'] += 1
        
        # Archive Python clients
        for zone_name, result in python_results.items():
            if result.success:
                archive_result = self.archive_python_client(zone_name, result.output_path)
                archive_results['python'][zone_name] = archive_result
                
                if archive_result['success']:
                    archive_results['summary']['successful'] += 1
                else:
                    archive_results['summary']['failed'] += 1
                
                archive_results['summary']['total_archived'] += 1
        
        # Generate archive index
        self._generate_archive_index(archive_results)
        
        self.logger.info(
            f"Archive completed: {archive_results['summary']['successful']} successful, "
            f"{archive_results['summary']['failed']} failed"
        )
        
        return archive_results
    
    def _generate_archive_index(self, archive_results: Dict[str, Any]):
        """Generate an index of all archives."""
        index_data = {
            'generated_at': datetime.now().isoformat(),
            'generator_version': '2.0.0',
            'summary': archive_results['summary'],
            'archives': {
                'typescript': {},
                'python': {}
            }
        }
        
        # Process TypeScript archives
        for zone_name, result in archive_results['typescript'].items():
            if result.get('success'):
                index_data['archives']['typescript'][zone_name] = {
                    'tar_archive': result['tar_archive'],
                    'zip_archive': result['zip_archive'],
                    'metadata': result['metadata'],
                    'timestamp': result['timestamp']
                }
        
        # Process Python archives
        for zone_name, result in archive_results['python'].items():
            if result.get('success'):
                index_data['archives']['python'][zone_name] = {
                    'tar_archive': result['tar_archive'],
                    'zip_archive': result['zip_archive'],
                    'metadata': result['metadata'],
                    'timestamp': result['timestamp']
                }
        
        # Write index files
        self._write_index_file(index_data, self.ts_archive_dir / 'index.json')
        self._write_index_file(index_data, self.py_archive_dir / 'index.json')
        self._write_index_file(index_data, self.output_dir / 'archive_index.json')
    
    def _write_index_file(self, index_data: Dict[str, Any], index_path: Path):
        """Write archive index to file."""
        import json
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Failed to write index file {index_path}: {e}")
    
    def list_archives(self, client_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List available archives.
        
        Args:
            client_type: Optional filter by client type (typescript/python)
            
        Returns:
            Dictionary of available archives
        """
        archives = {
            'typescript': [],
            'python': []
        }
        
        if client_type is None or client_type == 'typescript':
            archives['typescript'] = self._list_archives_in_dir(self.ts_archive_dir, 'typescript')
        
        if client_type is None or client_type == 'python':
            archives['python'] = self._list_archives_in_dir(self.py_archive_dir, 'python')
        
        return archives
    
    def _list_archives_in_dir(self, archive_dir: Path, client_type: str) -> list:
        """List archives in a specific directory."""
        if not archive_dir.exists():
            return []
        
        archives = []
        
        for archive_file in archive_dir.glob(f"*_{client_type}_*.tar.gz"):
            if '_latest' not in archive_file.name:
                metadata_file = archive_dir / f"{archive_file.stem}_metadata.json"
                
                archive_info = {
                    'filename': archive_file.name,
                    'path': str(archive_file),
                    'size_mb': round(archive_file.stat().st_size / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(archive_file.stat().st_ctime).isoformat(),
                    'metadata_available': metadata_file.exists()
                }
                
                archives.append(archive_info)
        
        # Sort by creation time (newest first)
        archives.sort(key=lambda x: x['created'], reverse=True)
        
        return archives
    
    def clean_old_archives(self, keep_count: int = 5) -> Dict[str, Any]:
        """
        Clean old archives, keeping only the most recent ones.
        
        Args:
            keep_count: Number of archives to keep per zone/type
            
        Returns:
            Cleanup operation results
        """
        results = {
            'typescript': self._clean_archives_in_dir(self.ts_archive_dir, 'typescript', keep_count),
            'python': self._clean_archives_in_dir(self.py_archive_dir, 'python', keep_count)
        }
        
        total_removed = results['typescript']['removed'] + results['python']['removed']
        self.logger.info(f"Archive cleanup completed: {total_removed} files removed")
        
        return results
    
    def _clean_archives_in_dir(self, archive_dir: Path, client_type: str, keep_count: int) -> Dict[str, int]:
        """Clean archives in a specific directory."""
        if not archive_dir.exists():
            return {'removed': 0, 'kept': 0}
        
        # Group archives by zone
        zone_archives = {}
        
        for archive_file in archive_dir.glob(f"*_{client_type}_*.tar.gz"):
            if '_latest' in archive_file.name:
                continue
            
            zone_name = archive_file.name.split(f'_{client_type}_')[0]
            
            if zone_name not in zone_archives:
                zone_archives[zone_name] = []
            
            zone_archives[zone_name].append(archive_file)
        
        removed_count = 0
        kept_count = 0
        
        # Clean each zone's archives
        for zone_name, archives in zone_archives.items():
            # Sort by modification time (newest first)
            archives.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep the most recent archives
            to_keep = archives[:keep_count]
            to_remove = archives[keep_count:]
            
            kept_count += len(to_keep)
            
            # Remove old archives and their metadata
            for archive_file in to_remove:
                try:
                    # Remove tar.gz file
                    archive_file.unlink()
                    
                    # Remove corresponding zip file
                    zip_file = archive_file.with_suffix('.zip')
                    if zip_file.exists():
                        zip_file.unlink()
                    
                    # Remove metadata file
                    metadata_file = archive_dir / f"{archive_file.stem}_metadata.json"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    removed_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to remove archive {archive_file}: {e}")
        
        return {'removed': removed_count, 'kept': kept_count} 