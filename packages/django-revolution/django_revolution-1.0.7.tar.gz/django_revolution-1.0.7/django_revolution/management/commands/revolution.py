"""
Django Revolution Management Command

Main command for generating OpenAPI clients.
"""

from django.core.management.base import BaseCommand, CommandError

from ...config import get_settings
from ...openapi.generator import OpenAPIGenerator
from ...utils import Logger


class Command(BaseCommand):
    """Django management command for OpenAPI client generation."""
    
    help = 'Generate OpenAPI clients for API zones using Django Revolution'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = Logger("revolution_command")
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--zones',
            nargs='*',
            help='Specific zones to generate (default: all zones)',
        )
        
        parser.add_argument(
            '--typescript',
            action='store_true',
            default=None,
            help='Generate TypeScript clients only',
        )
        
        parser.add_argument(
            '--python',
            action='store_true',
            default=None,
            help='Generate Python clients only',
        )
        
        parser.add_argument(
            '--no-typescript',
            action='store_true',
            help='Skip TypeScript client generation',
        )
        
        parser.add_argument(
            '--no-python',
            action='store_true',
            help='Skip Python client generation',
        )
        
        parser.add_argument(
            '--no-archive',
            action='store_true',
            help='Skip archiving generated clients',
        )
        
        parser.add_argument(
            '--no-monorepo',
            action='store_true',
            help='Skip monorepo sync',
        )
        
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean output directories before generation',
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current status and configuration',
        )
        
        parser.add_argument(
            '--list-zones',
            action='store_true',
            help='List all available zones',
        )
        
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate environment and configuration',
        )
        
        parser.add_argument(
            '--install-deps',
            action='store_true',
            help='Install required dependencies',
        )
        
        parser.add_argument(
            '--output-dir',
            help='Override output directory',
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging',
        )
    
    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Setup debug logging if requested
            if options['debug']:
                import logging
                logging.getLogger().setLevel(logging.DEBUG)
                self.logger.logger.setLevel(logging.DEBUG)
            
            # Get configuration
            config = get_settings()
            
            # Override output directory if provided
            if options['output_dir']:
                from pathlib import Path
                config.output.base_directory = str(Path(options['output_dir']).resolve())
            
            # Initialize generator
            generator = OpenAPIGenerator(config)
            
            # Handle status command
            if options['status']:
                self._show_status(generator)
                return
            
            # Handle list zones command
            if options['list_zones']:
                self._list_zones(generator)
                return
            
            # Handle validate command
            if options['validate']:
                self._validate_environment(generator)
                return
            
            # Handle install dependencies command
            if options['install_deps']:
                self._install_dependencies()
                return
            
            # Handle clean command
            if options['clean']:
                self._clean_output(generator)
                if not any([options['typescript'], options['python'], 
                           not options['no_typescript'], not options['no_python']]):
                    return
            
            # Determine what to generate
            generate_typescript = self._should_generate_typescript(config, options)
            generate_python = self._should_generate_python(config, options)
            
            if not generate_typescript and not generate_python:
                raise CommandError("Nothing to generate. Both TypeScript and Python generation are disabled.")
            
            # Override generator settings based on options
            if not generate_typescript:
                config.generators.typescript.enabled = False
            if not generate_python:
                config.generators.python.enabled = False
            
            # Override monorepo setting
            if options['no_monorepo']:
                config.monorepo.enabled = False
            
            # Get zones to process
            zones = options.get('zones')
            if zones:
                self.logger.info(f"Generating clients for specific zones: {zones}")
            else:
                self.logger.info("Generating clients for all zones")
            
            # Generate clients
            archive = not options['no_archive']
            summary = generator.generate_all(zones=zones, archive=archive)
            
            # Display results
            self._display_results(summary)
            
        except Exception as e:
            self.logger.error(f"Command failed: {str(e)}")
            if options['debug']:
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise CommandError(f"Generation failed: {str(e)}")
    
    def _should_generate_typescript(self, config, options):
        """Determine if TypeScript generation should be enabled."""
        if options['no_typescript']:
            return False
        if options['typescript']:
            return True
        if options['python'] and not options['typescript']:
            return False
        return config.generators.typescript.enabled
    
    def _should_generate_python(self, config, options):
        """Determine if Python generation should be enabled."""
        if options['no_python']:
            return False
        if options['python']:
            return True
        if options['typescript'] and not options['python']:
            return False
        return config.generators.python.enabled
    
    def _show_status(self, generator):
        """Show current status and configuration."""
        self.stdout.write(self.style.SUCCESS("Django Revolution Status"))
        self.stdout.write("=" * 50)
        
        status = generator.get_status()
        
        # Basic info
        self.stdout.write(f"Zones detected: {status['zones_detected']}")
        self.stdout.write(f"Output directory: {status['output_dir']}")
        self.stdout.write(f"TypeScript available: {status['typescript_available']}")
        self.stdout.write(f"Python available: {status['python_available']}")
        self.stdout.write(f"Monorepo enabled: {status['monorepo_enabled']}")
        
        # Zone details
        if status['zones']:
            self.stdout.write("\nConfigured Zones:")
            for zone_name, zone_data in status['zones'].items():
                self.stdout.write(f"  • {zone_name}: {len(zone_data['apps'])} apps")
                if zone_data.get('description'):
                    self.stdout.write(f"    {zone_data['description']}")
        
        # Monorepo status
        if status['monorepo_enabled'] and status.get('monorepo_status'):
            monorepo_status = status['monorepo_status']
            self.stdout.write("\nMonorepo Status:")
            self.stdout.write("  Path: {}".format(monorepo_status['monorepo_path']))
            self.stdout.write("  Exists: {}".format(monorepo_status['monorepo_exists']))
    
    def _list_zones(self, generator):
        """List all available zones."""
        zones = generator.zone_manager.zones
        
        if not zones:
            self.stdout.write(self.style.WARNING("No zones configured"))
            return
        
        self.stdout.write(self.style.SUCCESS("Available Zones"))
        self.stdout.write("=" * 50)
        
        for zone_name, zone in zones.items():
            self.stdout.write(f"\n{zone_name}:")
            self.stdout.write(f"  Title: {zone.title}")
            self.stdout.write(f"  Apps: {', '.join(zone.apps)}")
            self.stdout.write(f"  Public: {zone.public}")
            self.stdout.write(f"  Auth Required: {zone.auth_required}")
            if zone.description:
                self.stdout.write(f"  Description: {zone.description}")
    
    def _validate_environment(self, generator):
        """Validate environment and dependencies."""
        self.stdout.write(self.style.SUCCESS("Validating Environment"))
        self.stdout.write("=" * 50)
        
        # Basic validation
        is_valid = generator.validate_environment()
        
        if is_valid:
            self.stdout.write(self.style.SUCCESS("✓ Environment validation passed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Environment validation failed"))
        
        # Check dependencies
        from ...utils import check_dependency
        
        deps = [
            ('TypeScript Generator', ['npx', '@hey-api/openapi-ts', '--version']),
            ('Python Generator', ['datamodel-codegen', '--version']),
            ('Django', ['python', '-c', 'import django; print(django.VERSION)']),
        ]
        
        self.stdout.write("\nDependency Check:")
        for name, cmd in deps:
            available = check_dependency(cmd)
            status = "✓" if available else "✗"
            style = self.style.SUCCESS if available else self.style.ERROR
            self.stdout.write(style(f"  {status} {name}"))
    
    def _install_dependencies(self):
        """Install required dependencies."""
        self.stdout.write(self.style.SUCCESS("Installing Dependencies"))
        self.stdout.write("=" * 50)
        
        from ...utils import auto_install_dependencies
        
        success = auto_install_dependencies()
        
        if success:
            self.stdout.write(self.style.SUCCESS("✓ All dependencies installed"))
        else:
            self.stdout.write(self.style.ERROR("✗ Some dependencies failed to install"))
    
    def _clean_output(self, generator):
        """Clean output directories."""
        self.stdout.write(self.style.SUCCESS("Cleaning Output Directories"))
        self.stdout.write("=" * 50)
        
        success = generator.clean_output()
        
        if success:
            self.stdout.write(self.style.SUCCESS("✓ Output directories cleaned"))
        else:
            self.stdout.write(self.style.ERROR("✗ Failed to clean output directories"))
    
    def _display_results(self, summary):
        """Display generation results."""
        self.stdout.write(self.style.SUCCESS("\nGeneration Results"))
        self.stdout.write("=" * 50)
        
        # Summary
        self.stdout.write(f"Total zones processed: {summary.total_zones}")
        self.stdout.write(f"Duration: {summary.duration_seconds:.1f} seconds")
        self.stdout.write(f"Total files generated: {summary.total_files_generated}")
        
        # TypeScript results
        if summary.typescript_results:
            self.stdout.write(f"\nTypeScript: {summary.successful_typescript} successful, {summary.failed_typescript} failed")
            for zone_name, result in summary.typescript_results.items():
                status = "✓" if result.success else "✗"
                style = self.style.SUCCESS if result.success else self.style.ERROR
                self.stdout.write(style(f"  {status} {zone_name}: {result.files_generated} files"))
                if not result.success and result.error_message:
                    self.stdout.write(f"    Error: {result.error_message}")
        
        # Python results
        if summary.python_results:
            self.stdout.write(f"\nPython: {summary.successful_python} successful, {summary.failed_python} failed")
            for zone_name, result in summary.python_results.items():
                status = "✓" if result.success else "✗"
                style = self.style.SUCCESS if result.success else self.style.ERROR
                self.stdout.write(style(f"  {status} {zone_name}: {result.files_generated} files"))
                if not result.success and result.error_message:
                    self.stdout.write(f"    Error: {result.error_message}")
        
        # Final status
        total_successful = summary.successful_typescript + summary.successful_python
        total_failed = summary.failed_typescript + summary.failed_python
        
        if total_failed == 0:
            self.stdout.write(self.style.SUCCESS(f"\n🎉 All {total_successful} generations completed successfully!"))
        else:
            self.stdout.write(self.style.WARNING(f"\n⚠️  {total_successful} successful, {total_failed} failed")) 