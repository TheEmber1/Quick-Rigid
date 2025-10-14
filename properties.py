import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty, EnumProperty

class QuickRigidSettings(bpy.types.PropertyGroup):
    """Properties to store UI state for QuickRigid addon"""
    show_add_section: BoolProperty(
        name="Show Add Rigid Body Section",
        default=True
    )
    show_main_settings: BoolProperty(
        name="Show Main Settings",
        default=True
    )
    show_mass: BoolProperty(
        name="Show Mass Settings",
        default=True
    )
    show_surface: BoolProperty(
        name="Show Surface Response",
        default=True
    )
    show_simulation: BoolProperty(
        name="Show Simulation Settings",
        default=True
    )
    show_presets: BoolProperty(
        name="Show Presets",
        default=False
    )
    show_bake: BoolProperty(
        name="Show Bake Settings",
        default=False
    )
    show_timeline: BoolProperty(
        name="Show Timeline Settings",
        default=True
    )
    show_sim_settings: BoolProperty(
        name="Show Advanced Simulation Settings",
        default=True
    )
    show_cache_status: BoolProperty(
        name="Show Cache Status",
        default=True
    )
    show_settings: BoolProperty(
        name="Show Addon Settings",
        default=False
    )
    
    enable_floating_menu: BoolProperty(
        name="Enable Floating Menu",
        description="Enable or disable the floating menu and its shortcut key",
        default=True,
        update=lambda self, context: self.update_floating_menu_state()
    )
    
    shortcut_key: EnumProperty(
        name="Key",
        description="Keyboard key for the shortcut",
        items=[
            ('A', "A", "Use the A key"),
            ('B', "B", "Use the B key"),
            ('C', "C", "Use the C key"),
            ('D', "D", "Use the D key"),
            ('E', "E", "Use the E key"),
            ('F', "F", "Use the F key"),
            ('G', "G", "Use the G key"),
            ('H', "H", "Use the H key"),
            ('I', "I", "Use the I key"),
            ('J', "J", "Use the J key"),
            ('K', "K", "Use the K key"),
            ('L', "L", "Use the L key"),
            ('M', "M", "Use the M key"),
            ('N', "N", "Use the N key"),
            ('O', "O", "Use the O key"),
            ('P', "P", "Use the P key"),
            ('Q', "Q", "Use the Q key"),
            ('R', "R", "Use the R key"),
            ('S', "S", "Use the S key"),
            ('T', "T", "Use the T key"),
            ('U', "U", "Use the U key"),
            ('V', "V", "Use the V key"),
            ('W', "W", "Use the W key"),
            ('X', "X", "Use the X key"),
            ('Y', "Y", "Use the Y key"),
            ('Z', "Z", "Use the Z key"),
        ],
        default='U'
    )
    
    use_ctrl: BoolProperty(
        name="Ctrl",
        description="Use Ctrl as part of the key combination",
        default=False
    )
    
    use_alt: BoolProperty(
        name="Alt",
        description="Use Alt as part of the key combination",
        default=False
    )
    
    use_shift: BoolProperty(
        name="Shift",
        description="Use Shift as part of the key combination",
        default=False
    )
    
    def update_floating_menu_state(self):
        """Update keyboard shortcuts when the floating menu is enabled/disabled"""
        from .menus import unregister_keymaps, register_keymaps
        # First unregister any existing keymaps
        unregister_keymaps()
        
        # Register new keymaps only if floating menu is enabled
        if self.enable_floating_menu:
            register_keymaps()
            print("Quick Rigid floating menu enabled, shortcuts registered")
        else:
            print("Quick Rigid floating menu disabled, shortcuts removed")

class RigidBodyPresetItem(bpy.types.PropertyGroup):
    """Property group to store rigid body presets in scene data"""
    name: StringProperty(
        name="Preset Name",
        description="Name of the rigid body preset",
        default="New Preset"
    )
    # Store settings as a JSON string
    settings_json: StringProperty(
        name="Preset Settings",
        description="JSON representation of the rigid body settings",
        default="{}"
    )
    
    def get_settings(self):
        """Convert JSON string to Python dict"""
        try:
            import json
            return json.loads(self.settings_json)
        except:
            return {}
    
    def set_settings(self, settings_dict):
        """Convert Python dict to JSON string"""
        import json
        self.settings_json = json.dumps(settings_dict)

# List of classes to register
classes = [
    QuickRigidSettings,
    RigidBodyPresetItem
]

def register():
    """Register property classes"""
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    # Add properties to scene
    bpy.types.Scene.quick_rigid_settings = bpy.props.PointerProperty(type=QuickRigidSettings)
    bpy.types.Scene.rigid_body_presets = bpy.props.CollectionProperty(type=RigidBodyPresetItem)

def unregister():
    """Unregister property classes"""
    # Remove properties from scene
    del bpy.types.Scene.rigid_body_presets
    del bpy.types.Scene.quick_rigid_settings
    
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)