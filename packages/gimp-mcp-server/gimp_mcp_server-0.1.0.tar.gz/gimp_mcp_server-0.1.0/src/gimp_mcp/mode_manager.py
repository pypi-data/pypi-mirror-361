"""
GIMP Mode Manager - Handles GUI and headless mode detection and management

This module provides mode-aware GIMP connection management, automatically
detecting whether GIMP GUI is available and providing appropriate interfaces.
"""

import logging
import os
from typing import Optional, Any

from .utils.errors import GimpError, GimpModeError
from .utils.gi_helpers import safe_gi_import

logger = logging.getLogger(__name__)


class GimpModeManager:
    """Manages GIMP connection modes and provides appropriate interfaces."""
    
    def __init__(self, force_mode: Optional[str] = None):
        """
        Initialize the mode manager.
        
        Args:
            force_mode: Force specific mode ("gui", "headless", or None for auto-detect)
        """
        self.force_mode = force_mode
        self.gui_mode = self._detect_gui_mode()
        self.gimp_app = None
        self._connection_verified = False
        self._gi_modules = None
        
        logger.info(f"Mode manager initialized - GUI mode: {self.gui_mode}")
    
    def _detect_gui_mode(self) -> bool:
        """Detect if GIMP GUI is available and accessible."""
        # If mode is forced, use that
        if self.force_mode:
            if self.force_mode.lower() == "gui":
                return True
            elif self.force_mode.lower() == "headless":
                return False
            else:
                logger.warning(f"Unknown force_mode: {self.force_mode}, falling back to auto-detect")
        
        try:
            # Import GObject Introspection modules
            gi_modules = safe_gi_import()
            if not gi_modules:
                logger.info("GObject Introspection not available, using headless mode")
                return False
            
            Gtk = gi_modules.get("Gtk")
            if not Gtk:
                logger.info("GTK not available, using headless mode")
                return False
            
            # Check if display is available
            try:
                # Try to initialize GTK
                if hasattr(Gtk, 'init_check'):
                    if not Gtk.init_check():
                        logger.info("GTK init_check failed, using headless mode")
                        return False
                
                # Check for display environment
                display = os.environ.get('DISPLAY')
                if not display and os.name != 'nt':  # Not Windows
                    logger.info("No DISPLAY environment variable, using headless mode")
                    return False
                
                # Try to get default display
                if hasattr(Gtk, 'get_default_display'):
                    display = Gtk.get_default_display()
                    if display is None:
                        logger.info("No default display available, using headless mode")
                        return False
                
                logger.info("GUI mode detected and available")
                return True
                
            except Exception as e:
                logger.info(f"GUI detection failed: {e}, using headless mode")
                return False
                
        except Exception as e:
            logger.info(f"Mode detection failed: {e}, defaulting to headless mode")
            return False
    
    def get_gimp_instance(self) -> Any:
        """Return appropriate GIMP interface based on mode."""
        if self.gui_mode:
            return self._get_gui_instance()
        else:
            return self._get_headless_instance()
    
    def _get_gui_instance(self) -> Any:
        """Get GIMP instance for GUI mode."""
        try:
            # Import required modules
            gi_modules = safe_gi_import()
            if not gi_modules:
                raise GimpModeError("GObject Introspection not available for GUI mode")
            
            Gimp = gi_modules.get("Gimp")
            Gtk = gi_modules.get("Gtk")
            if not Gimp or not Gtk:
                raise GimpModeError("GIMP or GTK module not available for GUI mode")
            
            # Initialize GTK for GUI mode
            if hasattr(Gtk, 'init'):
                try:
                    Gtk.init()
                    logger.debug("GTK initialized successfully for GUI mode")
                except Exception as e:
                    logger.warning(f"GTK initialization failed: {e}")
            
            # Initialize GIMP for GUI mode
            if hasattr(Gimp, 'main'):
                # For GIMP 3.0+ with proper GI bindings
                logger.debug("Using GIMP 3.0+ GUI interface")
                
                # Try to initialize GIMP main context
                try:
                    # This would be the proper way to initialize GIMP in GUI mode
                    # Note: Actual initialization depends on GIMP 3.0 API
                    if hasattr(Gimp, 'init'):
                        Gimp.init()
                    logger.debug("GIMP GUI context initialized")
                except Exception as e:
                    logger.warning(f"GIMP GUI initialization warning: {e}")
                
                return Gimp
            else:
                # Fallback for older versions
                logger.debug("Using fallback GUI interface")
                return Gimp
                
        except Exception as e:
            logger.error(f"Failed to initialize GUI mode: {e}")
            raise GimpModeError(f"GUI mode initialization failed: {e}")
    
    def _get_headless_instance(self) -> Any:
        """Get GIMP instance for headless mode."""
        try:
            # Import required modules
            gi_modules = safe_gi_import()
            if not gi_modules:
                raise GimpModeError("GObject Introspection not available for headless mode")
            
            Gimp = gi_modules.get("Gimp")
            if not Gimp:
                raise GimpModeError("GIMP module not available for headless mode")
            
            # Initialize GIMP for headless mode
            logger.debug("Using GIMP headless interface")
            
            # For headless mode, we need to avoid GUI initialization
            try:
                # Initialize GIMP without GUI
                if hasattr(Gimp, 'init'):
                    # Pass appropriate arguments for headless mode
                    # This might require specific initialization parameters
                    Gimp.init()
                    logger.debug("GIMP headless context initialized")
                
                # Set headless-specific configurations
                if hasattr(Gimp, 'context_set_defaults'):
                    Gimp.context_set_defaults()
                    logger.debug("GIMP headless defaults set")
                
            except Exception as e:
                logger.warning(f"GIMP headless initialization warning: {e}")
            
            return Gimp
            
        except Exception as e:
            logger.error(f"Failed to initialize headless mode: {e}")
            raise GimpModeError(f"Headless mode initialization failed: {e}")
    
    def switch_mode(self, new_mode: str) -> bool:
        """
        Switch to a different mode.
        
        Args:
            new_mode: "gui" or "headless"
            
        Returns:
            True if mode switch was successful
        """
        try:
            old_mode = "GUI" if self.gui_mode else "headless"
            
            if new_mode.lower() == "gui":
                self.gui_mode = True
            elif new_mode.lower() == "headless":
                self.gui_mode = False
            else:
                raise GimpModeError(f"Invalid mode: {new_mode}")
            
            # Reset connection
            self.gimp_app = None
            self._connection_verified = False
            
            # Try to get new instance
            self.gimp_app = self.get_gimp_instance()
            
            new_mode_str = "GUI" if self.gui_mode else "headless"
            logger.info(f"Mode switched from {old_mode} to {new_mode_str}")
            
            return True
            
        except Exception as e:
            logger.error(f"Mode switch failed: {e}")
            return False
    
    def get_mode_info(self) -> dict:
        """Get information about current mode and capabilities."""
        return {
            "current_mode": "GUI" if self.gui_mode else "headless",
            "forced_mode": self.force_mode,
            "connection_verified": self._connection_verified,
            "capabilities": {
                "gui_available": self._check_gui_availability(),
                "headless_available": self._check_headless_availability(),
                "can_switch_modes": True,
            },
            "environment": {
                "display": os.environ.get('DISPLAY'),
                "platform": os.name,
                "gi_available": safe_gi_import() is not None,
            }
        }
    
    def _check_gui_availability(self) -> bool:
        """Check if GUI mode is available."""
        try:
            # Temporarily check GUI availability
            original_mode = self.gui_mode
            self.gui_mode = True
            
            try:
                self._get_gui_instance()
                return True
            except Exception:
                return False
            finally:
                self.gui_mode = original_mode
                
        except Exception:
            return False
    
    def _check_headless_availability(self) -> bool:
        """Check if headless mode is available."""
        try:
            # Temporarily check headless availability
            original_mode = self.gui_mode
            self.gui_mode = False
            
            try:
                self._get_headless_instance()
                return True
            except Exception:
                return False
            finally:
                self.gui_mode = original_mode
                
        except Exception:
            return False
    
    def validate_mode_requirements(self) -> bool:
        """Validate that current mode requirements are met."""
        try:
            if self.gui_mode:
                # Check GUI mode requirements
                gi_modules = safe_gi_import()
                if not gi_modules:
                    return False
                
                Gtk = gi_modules.get("Gtk")
                Gimp = gi_modules.get("Gimp")
                
                if not Gtk or not Gimp:
                    return False
                
                # Check display availability
                if not os.environ.get('DISPLAY') and os.name != 'nt':
                    return False
                
            else:
                # Check headless mode requirements
                gi_modules = safe_gi_import()
                if not gi_modules:
                    return False
                
                Gimp = gi_modules.get("Gimp")
                if not Gimp:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Mode validation failed: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of mode manager."""
        return f"GimpModeManager(mode={'GUI' if self.gui_mode else 'headless'}, forced={self.force_mode})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"GimpModeManager("
            f"gui_mode={self.gui_mode}, "
            f"force_mode={self.force_mode}, "
            f"connection_verified={self._connection_verified}"
            f")"
        )
    
    def initialize_gimp_context(self) -> bool:
        """Initialize GIMP context for current mode."""
        try:
            if self.gimp_app is None:
                self.gimp_app = self.get_gimp_instance()
            
            # Verify the instance is working
            if self.gimp_app:
                # Perform basic initialization tests
                if self.gui_mode:
                    logger.debug("Initializing GIMP GUI context")
                    # GUI-specific initialization
                    if hasattr(self.gimp_app, 'context_push'):
                        self.gimp_app.context_push()
                else:
                    logger.debug("Initializing GIMP headless context")
                    # Headless-specific initialization
                    if hasattr(self.gimp_app, 'context_set_defaults'):
                        self.gimp_app.context_set_defaults()
                
                self._connection_verified = True
                return True
            else:
                self._connection_verified = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize GIMP context: {e}")
            self._connection_verified = False
            return False
    
    def cleanup_gimp_context(self) -> bool:
        """Clean up GIMP context."""
        try:
            if self.gimp_app:
                # Perform cleanup based on mode
                if self.gui_mode:
                    logger.debug("Cleaning up GIMP GUI context")
                    if hasattr(self.gimp_app, 'context_pop'):
                        self.gimp_app.context_pop()
                else:
                    logger.debug("Cleaning up GIMP headless context")
                    # Headless cleanup
                    pass
                
                self.gimp_app = None
            
            self._connection_verified = False
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup GIMP context: {e}")
            return False
    
    def get_runtime_info(self) -> dict:
        """Get runtime information about the current GIMP mode."""
        info = self.get_mode_info()
        
        # Add runtime-specific information
        try:
            if self.gimp_app:
                # Try to get GIMP version info
                if hasattr(self.gimp_app, 'version'):
                    info['gimp_version'] = self.gimp_app.version()
                
                # Try to get available procedures
                if hasattr(self.gimp_app, 'get_procedures'):
                    procedures = self.gimp_app.get_procedures()
                    info['procedures_count'] = len(procedures) if procedures else 0
                    info['sample_procedures'] = list(procedures)[:10] if procedures else []
                
                # Check for common capabilities
                capabilities = {}
                common_methods = [
                    'list_images', 'image_new', 'file_load', 'file_save',
                    'layer_new', 'paintbrush_default', 'context_set_foreground'
                ]
                
                for method in common_methods:
                    capabilities[method] = hasattr(self.gimp_app, method)
                
                info['runtime_capabilities'] = capabilities
            
        except Exception as e:
            info['runtime_error'] = str(e)
        
        return info
    
    def test_basic_operations(self) -> dict:
        """Test basic GIMP operations to verify functionality."""
        test_results = {
            'initialization': False,
            'context_management': False,
            'image_operations': False,
            'layer_operations': False,
            'drawing_operations': False,
            'errors': []
        }
        
        try:
            # Test initialization
            if self.initialize_gimp_context():
                test_results['initialization'] = True
            
            # Test context management
            if self.gimp_app:
                if hasattr(self.gimp_app, 'context_push') and hasattr(self.gimp_app, 'context_pop'):
                    test_results['context_management'] = True
                elif not self.gui_mode:
                    # Headless mode might not have context push/pop
                    test_results['context_management'] = True
            
            # Test image operations
            if self.gimp_app and hasattr(self.gimp_app, 'list_images'):
                try:
                    images = self.gimp_app.list_images()
                    test_results['image_operations'] = True
                except Exception as e:
                    test_results['errors'].append(f"Image operations test failed: {e}")
            
            # Test layer operations
            if hasattr(self.gimp_app, 'Layer') if self.gimp_app else False:
                test_results['layer_operations'] = True
            
            # Test drawing operations
            if hasattr(self.gimp_app, 'paintbrush_default') if self.gimp_app else False:
                test_results['drawing_operations'] = True
            
        except Exception as e:
            test_results['errors'].append(f"Basic operations test failed: {e}")
        
        return test_results