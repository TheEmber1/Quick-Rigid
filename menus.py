import bpy

class VIEW3D_MT_quick_rigid_collision_submenu(bpy.types.Menu):
    """Collision shape settings submenu"""
    bl_label = "Collision Shape"
    bl_idname = "VIEW3D_MT_quick_rigid_collision_submenu"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if obj and obj.rigid_body:
            layout.prop_enum(obj.rigid_body, "collision_shape", 'BOX', icon='MESH_CUBE')
            layout.prop_enum(obj.rigid_body, "collision_shape", 'SPHERE', icon='MESH_UVSPHERE')
            layout.prop_enum(obj.rigid_body, "collision_shape", 'CAPSULE', icon='MESH_CAPSULE')
            layout.prop_enum(obj.rigid_body, "collision_shape", 'CYLINDER', icon='MESH_CYLINDER')
            layout.prop_enum(obj.rigid_body, "collision_shape", 'CONE', icon='MESH_CONE')
            layout.prop_enum(obj.rigid_body, "collision_shape", 'CONVEX_HULL', icon='MOD_MESHDEFORM')
            layout.prop_enum(obj.rigid_body, "collision_shape", 'MESH', icon='MESH_MONKEY')
            
            layout.separator()
            layout.prop(obj.rigid_body, "use_margin", text="Use Collision Margin")
            if obj.rigid_body.use_margin:
                layout.prop(obj.rigid_body, "collision_margin", text="Margin")

class VIEW3D_MT_quick_rigid_main_submenu(bpy.types.Menu):
    """Main rigid body settings submenu"""
    bl_label = "Main Settings"
    bl_idname = "VIEW3D_MT_quick_rigid_main_submenu"
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if obj and obj.rigid_body:
            # Type indicator
            layout.label(text=f"Type: {obj.rigid_body.type.title()}", icon='PHYSICS')
            
            # Animation settings
            layout.separator()
            layout.prop(obj.rigid_body, "kinematic", text="Animated", icon='RENDER_ANIMATION', toggle=True)
            layout.operator("rigid_body.toggle_animated", text="Toggle Animated State", icon='ACTION')

class VIEW3D_MT_quick_rigid_physics_submenu(bpy.types.Menu):
    """Physical properties submenu"""
    bl_label = "Physical Properties"
    bl_idname = "VIEW3D_MT_quick_rigid_physics_submenu"
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if obj and obj.rigid_body:
            # Mass settings section
            layout.label(text="Mass Settings:", icon='PHYSICS')
            layout.operator("rigidbody.mass_calculate", text="Calculate Mass", icon='FILE_REFRESH')
            layout.prop(obj.rigid_body, "mass", text="Mass", slider=True)
            
            layout.separator()
            
            # Surface properties
            layout.label(text="Surface Properties:", icon='MOD_PHYSICS')
            layout.prop(obj.rigid_body, "friction", text="Friction", slider=True)
            layout.prop(obj.rigid_body, "restitution", text="Bounciness", slider=True)

class VIEW3D_MT_quick_rigid_sim_submenu(bpy.types.Menu):
    """Simulation settings submenu"""
    bl_label = "Simulation Settings"
    bl_idname = "VIEW3D_MT_quick_rigid_sim_submenu"
    
    def draw(self, context):
        layout = self.layout
        
        # Gravity settings
        layout.label(text="Gravity:", icon='FORCE_FORCE')
        layout.prop(context.scene, "use_gravity", text="Use Gravity")
        
        if context.scene.use_gravity:
            col = layout.column(align=True)
            col.prop(context.scene, "gravity", text="X", index=0)
            col.prop(context.scene, "gravity", text="Y", index=1)
            col.prop(context.scene, "gravity", text="Z", index=2)
        
        layout.separator()
        
        # Simulation settings
        if context.scene.rigidbody_world:
            layout.label(text="Simulation:", icon='PLAY')
            layout.prop(context.scene.rigidbody_world, "time_scale", text="Sim Speed", slider=True)
            layout.prop(context.scene.rigidbody_world, "solver_iterations", text="Solver Iterations")
            layout.prop(context.scene.rigidbody_world, "use_split_impulse", text="Split Impulse")

class VIEW3D_MT_quick_rigid_presets_submenu(bpy.types.Menu):
    """Presets submenu"""
    bl_label = "Presets"
    bl_idname = "VIEW3D_MT_quick_rigid_presets_submenu"
    
    def draw(self, context):
        layout = self.layout
        
        # Check if we have any presets
        has_presets = False
        if hasattr(context.scene, "rigid_body_presets") and len(context.scene.rigid_body_presets) > 0:
            has_presets = True
        
        # If no presets exist, show info message
        if not has_presets:
            layout.label(text="No presets available", icon='INFO')
            layout.label(text="Click Add New Preset below")
            layout.separator()
        else:
            # User presets
            if hasattr(context.scene, "rigid_body_presets"):
                has_user_presets = False
                
                for preset in context.scene.rigid_body_presets:
                    if not has_user_presets:
                        layout.separator()
                        layout.label(text="User Presets:")
                        has_user_presets = True
                    
                    preset_op = layout.operator("object.apply_rigid_body_preset", text=preset.name, icon='FILE_NEW')
                    preset_op.preset_name = preset.name
        
        layout.separator()
        layout.operator("object.add_rigid_body_preset", text="Add New Preset", icon='ADD')

class VIEW3D_MT_quick_rigid_bake_submenu(bpy.types.Menu):
    """Baking submenu"""
    bl_label = "Bake Options"
    bl_idname = "VIEW3D_MT_quick_rigid_bake_submenu"
    
    def draw(self, context):
        layout = self.layout
        
        if context.scene.rigidbody_world:
            # Bake options
            layout.operator("rigidbody.bake_to_keyframes", text="Bake to Keyframes", icon='KEY_HLT')
            layout.operator("ptcache.bake_all", text="Bake All Dynamics", icon='PHYSICS').bake=True
            layout.operator("ptcache.bake", text="Calculate to Frame", icon='PREVIEW_RANGE')
            
            cache_op = layout.operator("ptcache.bake", text="Current Cache to Bake", icon='FILE_TICK')
            cache_op.bake = True
            
            layout.separator()
            layout.operator("ptcache.free_bake_all", text="Delete All Bakes", icon='TRASH')

class VIEW3D_MT_quick_rigid(bpy.types.Menu):
    """Quick access to rigid body tools"""
    bl_label = "Quick Rigid"
    bl_idname = "VIEW3D_MT_quick_rigid"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        
        obj = context.active_object
        has_rigidbody = obj and obj.rigid_body

        # Info message directing to N panel
        layout.label(text="Open N panel for advanced settings", icon='INFO')
        layout.separator()

        # Add/Remove section - keep original layout
        layout.operator("object.add_active_rigid_body", text="Add Active Rigid Body", icon='MESH_MONKEY')
        layout.operator("object.add_passive_rigid_body", text="Add Passive Rigid Body", icon='MESH_CUBE')
        
        if has_rigidbody:
            layout.separator()
            layout.operator("rigidbody.object_remove", text="Remove Rigid Body", icon='X')
            
            layout.separator()
            
            # Type indicator
            layout.label(text=f"Type: {obj.rigid_body.type.title()}", icon='PHYSICS')
            
            # Animation
            layout.prop(obj.rigid_body, "kinematic", text="Animated", icon='RENDER_ANIMATION', toggle=True)
            
            layout.separator()
            
            # Collision Shape submenu
            layout.menu("VIEW3D_MT_quick_rigid_collision_submenu", text="Collision Shape", icon='MESH_ICOSPHERE')
            
            # Physics properties - Keep these but remove Calculate Mass
            layout.prop(obj.rigid_body, "mass", text="Mass", slider=True)
            layout.prop(obj.rigid_body, "friction", text="Friction", slider=True)
            layout.prop(obj.rigid_body, "restitution", text="Bounciness", slider=True)
            
            layout.separator()
            
            # Copy/Paste
            layout.operator("rigidbody.object_settings_copy", text="Copy Settings", icon='COPYDOWN')

# List of classes to register
classes = [
    VIEW3D_MT_quick_rigid_collision_submenu,
    VIEW3D_MT_quick_rigid_main_submenu,
    VIEW3D_MT_quick_rigid_physics_submenu,
    VIEW3D_MT_quick_rigid_sim_submenu,
    VIEW3D_MT_quick_rigid_presets_submenu,
    VIEW3D_MT_quick_rigid_bake_submenu,
    VIEW3D_MT_quick_rigid
]

def register():
    """Register menu classes"""
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    """Unregister menu classes"""
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

# Registration of keymaps 
addon_keymaps = []

def register_keymaps():
    """Register keyboard shortcuts"""
    # First make sure to clear any existing keymaps
    unregister_keymaps()
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # Check if floating menu is enabled in settings
        try:
            if hasattr(bpy.context.scene, "quick_rigid_settings"):
                settings = bpy.context.scene.quick_rigid_settings
                
                # Only register keymaps if floating menu is enabled
                if settings.enable_floating_menu:
                    key = settings.shortcut_key
                    use_ctrl = settings.use_ctrl
                    use_alt = settings.use_alt
                    use_shift = settings.use_shift
                    
                    # Register the keymap
                    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
                    kmi = km.keymap_items.new("wm.call_menu", key, 'PRESS',
                                              ctrl=use_ctrl, alt=use_alt, shift=use_shift)
                    kmi.properties.name = "VIEW3D_MT_quick_rigid"
                    addon_keymaps.append((km, kmi))
                    print(f"Registered Quick Rigid shortcut: {key} (ctrl={use_ctrl}, alt={use_alt}, shift={use_shift})")
                else:
                    print("Quick Rigid floating menu is disabled - no shortcuts registered")
        except (AttributeError, RuntimeError):
            # If context isn't available, skip registration
            pass

def unregister_keymaps():
    """Unregister keyboard shortcuts"""
    # Remove our stored keymaps - this is the safe way to do it
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    
    # Clear the list
    addon_keymaps.clear()
    print("Unregistered all Quick Rigid shortcuts")