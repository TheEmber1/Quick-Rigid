import bpy

bl_info = {
    "name": "Quick Rigid",
    "author": "THE EMBER",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Press U",
    "description": "Speeds up the Rigid Body workflow with a convenient menu",
    "warning": "",
    "doc_url": "",
    "category": "Simulation",
}

# Import all modules
from . import properties
from . import presets
from . import operators
from . import menus
from . import panels
from . import icons

def register():
    # Register modules in the correct order
    properties.register()
    operators.register()
    menus.register()
    panels.register()
    
    # Load custom icons
    icons.load_icons()
    
    # Initialize keymaps (from menus module)
    menus.register_keymaps()

def unregister():
    # Unregister modules in the reverse order
    menus.unregister_keymaps()
    
    # Unload custom icons
    icons.unload_icons()
    
    panels.unregister()
    menus.unregister()
    operators.unregister()
    properties.unregister()