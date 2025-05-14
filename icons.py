import os
import bpy
import bpy.utils.previews

# Global variable to store icons
icons_collection = None

def load_icons():
    """Load custom icons for the addon."""
    global icons_collection
    
    # If preview collection exists, remove it and create a new one
    if icons_collection is not None:
        unload_icons()
    
    # Create new preview collection
    icons_collection = bpy.utils.previews.new()
    
    # Get addon directory path and assets folder path
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    assets_dir = os.path.join(addon_dir, "assets")
    
    # Load the icon from assets folder
    icons_collection.load("quick_rigid_icon", os.path.join(assets_dir, "QuickRigidLogo.png"), 'IMAGE')
    
def unload_icons():
    """Unload custom icons when addon is disabled."""
    global icons_collection
    
    # Remove the preview collection if it exists
    if icons_collection is not None:
        bpy.utils.previews.remove(icons_collection)
        icons_collection = None

def get_icon_id(icon_name):
    """Get the icon ID for use in UI code."""
    global icons_collection
    
    # If the icon collection doesn't exist, load it
    if icons_collection is None:
        load_icons()
    
    # Return the icon ID or a default icon if not found
    if icon_name in icons_collection:
        return icons_collection[icon_name].icon_id
    else:
        # Return a default icon ID as fallback
        return 0  # 0 is the default blank icon