# syft-objects - Distributed file discovery and addressing system 

__version__ = "0.10.18"

# Internal imports (hidden from public API)
from . import models as _models
from . import data_accessor as _data_accessor
from . import config as _config
from . import prompts as _prompts
from . import mock_analyzer as _mock_analyzer
from . import factory as _factory
from . import collections as _collections
from . import utils as _utils
from . import client as _client
from . import auto_install as _auto_install
from . import permissions as _permissions
from . import file_ops as _file_ops
from . import display as _display

# Public API - only expose essential user-facing functionality
from .collections import ObjectsCollection
from .config import config

# Create global objects collection instance
objects = ObjectsCollection()

# Create clearer API endpoints
def create_object(name=None, *, move_files_to_syftbox=None, **kwargs):
    """Create a new SyftObject with explicit naming.
    
    Creates a new SyftObject with the specified parameters.
    
    Args:
        name: Optional name for the object
        **kwargs: All the same arguments as syobj:
            - private_contents: String content for private file
            - mock_contents: String content for mock file
            - private_file: Path to private file
            - mock_file: Path to mock file
            - private_folder: Path to private folder
            - mock_folder: Path to mock folder
            - discovery_read: List of who can discover
            - mock_read: List of who can read mock
            - mock_write: List of who can write mock
            - private_read: List of who can read private
            - private_write: List of who can write private
            - metadata: Additional metadata dict
            - skip_validation: Skip mock/real file validation
            - mock_note: Optional note explaining mock data differences
            - suggest_mock_notes: Whether to suggest mock notes (None uses config)
            - move_files_to_syftbox: Whether to copy/move files to SyftBox (default: False)
                - When True: User files are copied, generated files are moved
                - When False: Files stay in their original locations
    
    Returns:
        SyftObject: The newly created object
    """
    # Handle move_files_to_syftbox parameter
    if move_files_to_syftbox is not None:
        # If explicitly provided, add to metadata
        if 'metadata' not in kwargs:
            kwargs['metadata'] = {}
        kwargs['metadata']['move_files_to_syftbox'] = move_files_to_syftbox
    
    # Use the internal factory module's syobj function
    return _factory.syobj(name, **kwargs)

def delete_object(uid, user_email=None):
    """Delete a SyftObject by UID with permission checking.
    
    Args:
        uid: String UID of the object to delete
        user_email: Email of the user attempting deletion. If None, will try to get from SyftBox client.
        
    Returns:
        bool: True if deletion was successful, False otherwise
        
    Raises:
        KeyError: If UID is not found
        TypeError: If uid is not a string
        PermissionError: If user doesn't have permission to delete the object
    """
    if not isinstance(uid, str):
        raise TypeError(f"UID must be str, not {type(uid).__name__}")
    
    try:
        obj = objects[uid]  # This uses the UID lookup
        result = obj.delete_obj(user_email)  # Now includes permission checking
        if result:
            # Refresh the collection after successful deletion
            objects.refresh()
        return result
    except KeyError:
        raise KeyError(f"Object with UID '{uid}' not found")

# Export the essential public API
__all__ = [
    "create_object", # Function for creating objects
    "delete_object", # Function for deleting objects
    "objects",       # Global collection instance
    "config",        # Configuration instance
]

# Internal setup (hidden from user)
_client.check_syftbox_status()
_auto_install.ensure_syftbox_app_installed(silent=True)

# Import startup banner (hidden)
from .client import _print_startup_banner
_print_startup_banner(only_if_needed=True)

# Clean up namespace - remove any accidentally exposed internal modules
import sys
_current_module = sys.modules[__name__]
_internal_modules = ['models', 'data_accessor', 'factory', 'collections', 'utils', 
                     'client', 'auto_install', 'permissions', 'file_ops', 'display',
                     'prompts', 'mock_analyzer',
                     'ObjectsCollection', 'sys']  # Hide all internal modules (but keep syobj and config)
for _attr_name in _internal_modules:
    if hasattr(_current_module, _attr_name):
        delattr(_current_module, _attr_name)

# Already defined above - remove this duplicate
# __all__ is defined earlier in the file
