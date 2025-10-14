import bpy
from bpy.props import StringProperty

from .presets import RigidBodyPreset, RigidBodyPresetManager

class AddPassiveRigidBody(bpy.types.Operator):
    """Add passive rigid bodies to all selected mesh objects"""
    bl_idname = "object.add_passive_rigid_body"
    bl_label = "Add Passive Rigid Body"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if at least one selected object is a mesh
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # Store originally selected objects
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        original_active_object = context.active_object
        
        if not selected_objects:
            self.report({'ERROR'}, "Rigid bodies can only be added to mesh objects")
            return {'CANCELLED'}
        
        # Add passive rigid body to each selected mesh object
        for obj in selected_objects:
            # Set the object as active
            context.view_layer.objects.active = obj
            # Add rigid body as passive
            bpy.ops.rigidbody.objects_add(type='PASSIVE')
        
        # Restore the original active object if it was in the selected objects
        # or set the active object to the last processed object with a rigid body
        if original_active_object in selected_objects:
            context.view_layer.objects.active = original_active_object
        else:
            # Set the last processed object as active so UI will show settings
            context.view_layer.objects.active = selected_objects[-1]
        
        # Report how many objects were affected
        self.report({'INFO'}, f"Added passive rigid bodies to {len(selected_objects)} objects")
        return {'FINISHED'}

class AddActiveRigidBody(bpy.types.Operator):
    """Add active rigid bodies to all selected mesh objects"""
    bl_idname = "object.add_active_rigid_body"
    bl_label = "Add Active Rigid Body"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if at least one selected object is a mesh
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # Store originally selected objects
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        original_active_object = context.active_object
        
        if not selected_objects:
            self.report({'ERROR'}, "Rigid bodies can only be added to mesh objects")
            return {'CANCELLED'}
        
        # Add active rigid body to each selected mesh object
        for obj in selected_objects:
            # Set the object as active
            context.view_layer.objects.active = obj
            # Add rigid body as active
            bpy.ops.rigidbody.objects_add(type='ACTIVE')
        
        # Restore the original active object if it was in the selected objects
        # or set the active object to the last processed object with a rigid body
        if original_active_object in selected_objects:
            context.view_layer.objects.active = original_active_object
        else:
            # Set the last processed object as active so UI will show settings
            context.view_layer.objects.active = selected_objects[-1]
        
        # Report how many objects were affected
        self.report({'INFO'}, f"Added active rigid bodies to {len(selected_objects)} objects")
        return {'FINISHED'}

class RIGID_BODY_OT_toggle_animated(bpy.types.Operator):
    """Toggle the animated state of the rigid body"""
    bl_idname = "rigid_body.toggle_animated"
    bl_label = "Toggle Animated State"
    bl_description = "Toggle the animated state of the rigid body"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.rigid_body:
            obj.rigid_body.kinematic = not obj.rigid_body.kinematic
        return {'FINISHED'}

class AddRigidBodyPreset(bpy.types.Operator):
    """Add a new preset based on current rigid body settings"""
    bl_idname = "object.add_rigid_body_preset"
    bl_label = "Add Rigid Body Preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: StringProperty(
        name="Preset Name",
        description="Name of the preset to save",
        default="New Preset"
    )
    
    overwrite: bpy.props.BoolProperty(
        name="Overwrite Existing",
        description="Overwrite existing preset with the same name",
        default=False
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.rigid_body
    
    def invoke(self, context, event):
        # Show dialog to get preset name
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset_name")
        
        # Check if a preset with this name already exists
        preset_exists = False
        if hasattr(context.scene, "rigid_body_presets"):
            for preset in context.scene.rigid_body_presets:
                if preset.name == self.preset_name:
                    preset_exists = True
                    break
        
        # Show warning and checkbox if preset already exists
        if preset_exists:
            warning_row = layout.row()
            warning_row.alert = True
            warning_row.label(text=f"Warning: Preset '{self.preset_name}' already exists!")
            layout.prop(self, "overwrite", text="Overwrite existing preset")
    
    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.rigid_body:
            self.report({'ERROR'}, "No active object with rigid body")
            return {'CANCELLED'}
            
        # Check if preset with this name already exists
        preset_exists = False
        if hasattr(context.scene, "rigid_body_presets"):
            for preset in context.scene.rigid_body_presets:
                if preset.name == self.preset_name:
                    preset_exists = True
                    break
        
        # If preset exists and user didn't choose to overwrite, cancel
        if preset_exists and not self.overwrite:
            self.report({'WARNING'}, f"Preset '{self.preset_name}' already exists. Choose a different name or enable overwrite.")
            return {'CANCELLED'}
            
        # Create preset from current settings
        preset = RigidBodyPreset.from_object(obj, self.preset_name)
        
        # Save preset to scene with both rigid body and simulation settings
        success = RigidBodyPresetManager.save_preset_to_scene(
            self.preset_name, 
            preset.settings,
            preset.simulation_settings
        )
        
        if success:
            self.report({'INFO'}, f"Saved preset '{self.preset_name}'")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Failed to save preset")
            return {'CANCELLED'}

class ApplyRigidBodyPreset(bpy.types.Operator):
    """Apply a rigid body preset to the selected objects"""
    bl_idname = "object.apply_rigid_body_preset"
    bl_label = "Apply Rigid Body Preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: StringProperty(
        name="Preset Name",
        description="Name of the preset to apply",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects and any(obj.rigid_body for obj in context.selected_objects)
    
    def execute(self, context):
        if not self.preset_name:
            self.report({'ERROR'}, "No preset name specified")
            return {'CANCELLED'}
            
        # Get selected objects with rigid bodies
        selected_rb_objects = [obj for obj in context.selected_objects if obj.rigid_body]
        if not selected_rb_objects:
            self.report({'ERROR'}, "No selected objects with rigid bodies")
            return {'CANCELLED'}
            
        # Apply preset to all selected objects with rigid bodies
        count = 0
        for obj in selected_rb_objects:
            if RigidBodyPresetManager.apply_preset_by_name(self.preset_name, obj):
                count += 1
                
        if count > 0:
            self.report({'INFO'}, f"Applied preset '{self.preset_name}' to {count} objects")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Failed to apply preset '{self.preset_name}'")
            return {'CANCELLED'}

class DeleteRigidBodyPreset(bpy.types.Operator):
    """Delete a saved rigid body preset"""
    bl_idname = "object.delete_rigid_body_preset"
    bl_label = "Delete Rigid Body Preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    preset_name: StringProperty(
        name="Preset Name",
        description="Name of the preset to delete",
        default=""
    )
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.scene, "rigid_body_presets")
    
    def execute(self, context):
        if not self.preset_name:
            self.report({'ERROR'}, "No preset name specified")
            return {'CANCELLED'}
            
        scene = context.scene
        if not hasattr(scene, "rigid_body_presets"):
            self.report({'ERROR'}, "No presets available")
            return {'CANCELLED'}
            
        # Find and remove the preset
        for i, preset in enumerate(scene.rigid_body_presets):
            if preset.name == self.preset_name:
                scene.rigid_body_presets.remove(i)
                self.report({'INFO'}, f"Deleted preset '{self.preset_name}'")
                return {'FINISHED'}
                
        self.report({'ERROR'}, f"Preset '{self.preset_name}' not found")
        return {'CANCELLED'}

class ApplyShortcutKey(bpy.types.Operator):
    """Apply the selected shortcut key for the Quick Rigid menu"""
    bl_idname = "quick_rigid.apply_shortcut_key"
    bl_label = "Apply Shortcut Key"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from .menus import addon_keymaps, unregister_keymaps, register_keymaps
        
        # Get the settings
        settings = context.scene.quick_rigid_settings
        new_key = settings.shortcut_key
        use_ctrl = settings.use_ctrl
        use_alt = settings.use_alt
        use_shift = settings.use_shift
        enable_menu = settings.enable_floating_menu
        
        # Build a user-friendly description of the shortcut
        combo_text = ""
        if use_ctrl:
            combo_text += "Ctrl+"
        if use_alt:
            combo_text += "Alt+"
        if use_shift:
            combo_text += "Shift+"
        combo_text += new_key
        
        # First ensure we've removed any existing keymaps
        unregister_keymaps()
        
        # Only register a new keymap if floating menu is enabled
        if enable_menu:
            # Now create a new keymap with the selected combination
            wm = context.window_manager
            kc = wm.keyconfigs.addon
            if kc:
                try:
                    # Create new keymap
                    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
                    kmi = km.keymap_items.new("wm.call_menu", new_key, 'PRESS', 
                                             ctrl=use_ctrl, alt=use_alt, shift=use_shift)
                    kmi.properties.name = "VIEW3D_MT_quick_rigid"
                    addon_keymaps.append((km, kmi))
                    
                    self.report({'INFO'}, f"Shortcut changed to '{combo_text}'")
                except Exception as e:
                    print(f"Failed to set keymap: {e}")
                    self.report({'ERROR'}, f"Could not create shortcut: {e}")
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, "Could not access keyconfigs")
                return {'CANCELLED'}
        else:
            self.report({'INFO'}, "Floating menu disabled - no shortcut assigned")
        
        return {'FINISHED'}

# List of classes to register
classes = [
    AddPassiveRigidBody,
    AddActiveRigidBody,
    RIGID_BODY_OT_toggle_animated,
    AddRigidBodyPreset,
    ApplyRigidBodyPreset,
    DeleteRigidBodyPreset,
    ApplyShortcutKey
]

def register():
    """Register operator classes"""
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    """Unregister operator classes"""
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)