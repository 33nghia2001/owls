from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.base.core.system'
    label = 'system'

    def ready(self):
        """
        SECURITY: Verify critical security dependencies on app startup.
        
        This ensures that required security libraries are installed before
        the application starts accepting requests.
        """
        self._verify_security_dependencies()
    
    def _verify_security_dependencies(self):
        """
        Check that all required security libraries are installed.
        Raises ImportError in production if critical libs are missing.
        """
        from django.conf import settings
        
        missing_libs = []
        
        # Check bleach for HTML sanitization
        try:
            import bleach
        except ImportError:
            missing_libs.append('bleach')
        
        # Check python-magic for file type validation
        try:
            import magic
        except ImportError:
            missing_libs.append('python-magic-bin')  # or python-magic on Linux
        
        if missing_libs:
            error_msg = (
                f"SECURITY ERROR: Missing required security libraries: {', '.join(missing_libs)}. "
                f"Install with: pip install {' '.join(missing_libs)}"
            )
            
            if not getattr(settings, 'DEBUG', False):
                # In production, fail hard - security libs are mandatory
                raise ImportError(error_msg)
            else:
                # In development, log warning but allow startup
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(error_msg)
