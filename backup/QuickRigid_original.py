import bpy
import os
import json
from bpy.props import StringProperty, CollectionProperty, IntProperty, PointerProperty, BoolProperty

# Add these properties to store the expanded state of each section
class QuickRigidSettings(bpy.types.PropertyGroup):
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
        default=True
    )
    show_bake: BoolProperty(
        name="Show Bake Settings",
        default=True
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
            
            # Removed Gravity, Simulation Speed, and Solver Iterations
            
            layout.separator()
            
            # Copy/Paste
            layout.operator("rigidbody.object_settings_copy", text="Copy Settings", icon='COPYDOWN')
            
            # Removed Bake to Keyframes

class VIEW3D_PT_QuickRigid(bpy.types.Panel):
    """Panel for Quick Rigid tools"""
    bl_label = "Quick Rigid"
    bl_idname = "VIEW3D_PT_quick_rigid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick Rigid"
   
    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        
        if not context.selected_objects:
            layout.label(text="Select a mesh to add a rigid body", icon='INFO')
            return
            
        # Check if there are selected mesh objects
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            layout.label(text="Select a mesh to add a rigid body", icon='INFO')
            return

        # Get quick rigid settings
        settings = context.scene.quick_rigid_settings
        
        # Show info about selection count if multiple objects - moved to the top
        if len(selected_meshes) > 1:
            rb_count = len([obj for obj in selected_meshes if obj.rigid_body])
            layout.label(text=f"{len(selected_meshes)} objects selected ({rb_count} with rigid bodies)", icon='INFO')
            
        # Add rigid body box - collapsible
        box = layout.box()
        row = box.row()
        row.prop(settings, "show_add_section", icon="TRIA_DOWN" if settings.show_add_section else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Add Rigid Body:", icon='PHYSICS')
        
        # Only show contents if expanded
        if settings.show_add_section:
            row = box.row(align=True)
            row.operator("object.add_active_rigid_body", text="Add Active", icon='MESH_MONKEY')
            row.operator("object.add_passive_rigid_body", text="Add Passive", icon='MESH_CUBE')
            
            # Remove button with red color
            remove_row = box.row()
            remove_row.alert = True  # This makes the button red
            remove_row.operator("rigidbody.object_remove", text="Remove Rigid Body", icon='X')

            # Show rigid body type inside the box if active object has rigid body
            obj = context.active_object
            if obj and obj.rigid_body:
                type_row = box.row()
                icon = 'PINNED' if obj.rigid_body.type == 'PASSIVE' else 'UNPINNED'
                type_row.label(text=f"Type: {obj.rigid_body.type.title()}", icon=icon)

        # Only show the rest of the UI if active object has rigid body
        obj = context.active_object
        if not obj or not obj.rigid_body:
            return
        
        # Copy/Paste - moved directly above main settings with no extra spacing
        row = layout.row(align=True)
        row.operator("rigidbody.object_settings_copy", text="Copy Settings", icon='COPYDOWN')
        
        # Main settings - collapsible
        box = layout.box()
        row = box.row()
        row.prop(settings, "show_main_settings", icon="TRIA_DOWN" if settings.show_main_settings else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Main Settings:", icon='SETTINGS')
        
        if settings.show_main_settings:
            col = box.column(align=True)
            col.prop(obj.rigid_body, "collision_shape", text="Shape", icon='MESH_ICOSPHERE')
            col.prop(obj.rigid_body, "kinematic", text="Animated", icon='RENDER_ANIMATION', toggle=True)
        
        # Mass settings - collapsible
        box = layout.box()
        row = box.row()
        row.prop(settings, "show_mass", icon="TRIA_DOWN" if settings.show_mass else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Mass:", icon='PHYSICS')
        
        if settings.show_mass:
            col = box.column(align=True)
            col.prop(obj.rigid_body, "mass", slider=True)
            col.operator("rigidbody.mass_calculate", text="Calculate Mass", icon='FILE_REFRESH')

        # Surface Response - collapsible
        box = layout.box()
        row = box.row()
        row.prop(settings, "show_surface", icon="TRIA_DOWN" if settings.show_surface else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Surface Response:", icon='MOD_PHYSICS')
        
        if settings.show_surface:
            col = box.column(align=True)
            col.prop(obj.rigid_body, "friction", slider=True)
            col.prop(obj.rigid_body, "restitution", text="Bounciness", slider=True)

        # Gravity and Simulation - collapsible
        box = layout.box()
        row = box.row()
        row.prop(settings, "show_simulation", icon="TRIA_DOWN" if settings.show_simulation else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Simulation:", icon='WORLD')
        
        if settings.show_simulation:
            col = box.column(align=True)
            col.prop(context.scene, "use_gravity", text="Gravity")
            if context.scene.use_gravity:
                col.prop(context.scene, "gravity", text="")
            
            col.separator()
            if context.scene.rigidbody_world:
                col.prop(context.scene.rigidbody_world, "time_scale", text="Sim Speed", slider=True)

        # Presets section - collapsible
        box = layout.box()
        row = box.row()
        row.prop(settings, "show_presets", icon="TRIA_DOWN" if settings.show_presets else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Presets:", icon='PRESET')
        
        if settings.show_presets:
            # Create a grid layout for presets - 1 column
            grid = box.column()
            
            # Check if any presets exist
            has_presets = False
            if hasattr(context.scene, "rigid_body_presets") and len(context.scene.rigid_body_presets) > 0:
                has_presets = True
            
            # If no presets exist, show info message
            if not has_presets:
                info_row = grid.row(align=True)
                info_row.alignment = 'CENTER'
                info_row.label(text="No presets available", icon='INFO')
                
                info_row = grid.row(align=True)
                info_row.alignment = 'CENTER'
                info_row.label(text="Click Add New Preset below")
                
                grid.separator()
            else:
                # User presets from the scene - each with delete button
                for preset in context.scene.rigid_body_presets:
                    # Create a row for this preset with the delete button
                    user_row = grid.row(align=True)
                    
                    # Preset button (takes most of the row)
                    preset_op = user_row.operator("object.apply_rigid_body_preset", text=preset.name)
                    preset_op.preset_name = preset.name
                    
                    # Delete button - explicit X button
                    delete_op = user_row.operator("object.delete_rigid_body_preset", text="", icon='X')
                    delete_op.preset_name = preset.name
            
            # Add new preset button
            box.separator()
            row = box.row(align=True)
            row.operator("object.add_rigid_body_preset", text="Add New Preset", icon='ADD')
        
        # Improved Bake section - collapsible
        if context.scene.rigidbody_world:
            bake_box = layout.box()
            row = bake_box.row()
            row.prop(settings, "show_bake", icon="TRIA_DOWN" if settings.show_bake else "TRIA_RIGHT", 
                    icon_only=True, emboss=False)
            row.label(text="Bake:", icon='KEY_HLT')
            
            if settings.show_bake:
                # Nice visual separation
                bake_box.separator()
                
                # Point Cache settings reference
                rb_world = context.scene.rigidbody_world
                point_cache = rb_world.point_cache
                
                # Main bake options section
                bake_col = bake_box.column(align=True)
                
                # All bake options vertically stacked like in default Blender
                bake_col.scale_y = 1.2
                bake_col.operator("rigidbody.bake_to_keyframes", text="Bake to Keyframes", icon='ACTION')
                bake_col.operator("ptcache.bake_all", text="Bake All Dynamics", icon='PHYSICS').bake=True
                bake_col.operator("ptcache.bake", text="Calculate to Frame", icon='PREVIEW_RANGE')
                
                cache_op = bake_col.operator("ptcache.bake", text="Current Cache to Bake", icon='FILE_TICK')
                cache_op.bake = True
                
                # Delete button with red color at the bottom
                bake_col.separator()
                delete_row = bake_col.row(align=True)
                delete_row.alert = True  # This makes the button red
                delete_row.operator("ptcache.free_bake_all", text="Delete All Bakes", icon='TRASH')
                
                bake_box.separator()
                
                # Frame range settings - collapsible
                timeline_box = bake_box.box()
                row = timeline_box.row()
                row.prop(settings, "show_timeline", icon="TRIA_DOWN" if settings.show_timeline else "TRIA_RIGHT", 
                         icon_only=True, emboss=False)
                row.label(text="Timeline Settings:", icon='TIME')
                
                if settings.show_timeline:
                    # Frame range in a clean row with better visual arrangement
                    frame_row = timeline_box.row(align=True)
                    frame_row.label(text="Frame Range:")
                    
                    range_row = timeline_box.row(align=True)
                    range_row.prop(point_cache, "frame_start", text="Start")
                    range_row.prop(point_cache, "frame_end", text="End")
                    
                    # Add step as part of timeline settings
                    step_row = timeline_box.row()
                    step_row.prop(point_cache, "step", text="Cache Step")
                
                # Advanced simulation settings - collapsible
                sim_box = bake_box.box()
                row = sim_box.row()
                row.prop(settings, "show_sim_settings", icon="TRIA_DOWN" if settings.show_sim_settings else "TRIA_RIGHT", 
                         icon_only=True, emboss=False)
                row.label(text="Simulation Settings:", icon='SETTINGS')
                
                if settings.show_sim_settings:
                    # Solver settings with better organization
                    col = sim_box.column(align=True)
                    col.prop(context.scene.rigidbody_world, "solver_iterations", text="Solver Iterations")
                    col.prop(context.scene.rigidbody_world, "use_split_impulse", text="Split Impulse")
                
                # Cache information - collapsible
                cache_box = bake_box.box()
                row = cache_box.row()
                row.prop(settings, "show_cache_status", icon="TRIA_DOWN" if settings.show_cache_status else "TRIA_RIGHT", 
                         icon_only=True, emboss=False)
                row.label(text="Cache Status:", icon='INFO')
                
                if settings.show_cache_status:
                    # Status indicator with appropriate icons
                    status_row = cache_box.row()
                    if point_cache.is_baked:
                        status_row.label(text="Baked", icon='CHECKMARK')
                    elif point_cache.is_baking:
                        status_row.label(text="Baking in Progress...", icon='TEMP')
                    else:
                        status_row.label(text="Not Baked", icon='X')
                    
                    # Disk cache options with better organization
                    cache_box.separator()
                    disk_row = cache_box.row()
                    disk_row.prop(point_cache, "use_disk_cache", text="Disk Cache", icon='DISK_DRIVE')
                    
                    # Only show additional disk options when enabled
                    if point_cache.use_disk_cache:
                        disk_col = cache_box.column(align=True)
                        disk_col.prop(point_cache, "use_library_path", text="Use Lib Path")
                        disk_col.prop(point_cache, "compression", text="Compression")
                        disk_col.separator()
                        disk_col.prop(point_cache, "filepath", text="File Path")

class RIGID_BODY_OT_toggle_animated(bpy.types.Operator):
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
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.rigid_body
    
    def invoke(self, context, event):
        # Show dialog to get preset name
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.rigid_body:
            self.report({'ERROR'}, "No active object with rigid body")
            return {'CANCELLED'}
            
        # Create preset from current settings
        preset = RigidBodyPreset.from_object(obj, self.preset_name)
        
        # Save preset to scene
        success = RigidBodyPresetManager.save_preset_to_scene(
            self.preset_name, 
            preset.settings
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

class RigidBodyPreset:
    """Class representing a rigid body preset"""
    def __init__(self, name="New Preset", settings=None):
        self.name = name
        # Default settings if none provided
        if settings is None:
            self.settings = {
                'type': 'ACTIVE',
                'collision_shape': 'CONVEX_HULL',
                'mass': 1.0,
                'friction': 0.5,
                'restitution': 0.0,
                'kinematic': False
            }
        else:
            self.settings = settings
    
    @staticmethod
    def from_object(obj, name="New Preset"):
        """Create a preset from an object's rigid body settings"""
        if obj and obj.rigid_body:
            settings = {
                'type': obj.rigid_body.type,
                'collision_shape': obj.rigid_body.collision_shape,
                'mass': obj.rigid_body.mass,
                'friction': obj.rigid_body.friction,
                'restitution': obj.rigid_body.restitution,
                'kinematic': obj.rigid_body.kinematic
            }
            return RigidBodyPreset(name, settings)
        return RigidBodyPreset(name)  # Default preset if no rigid body
    
    def apply_to_object(self, obj):
        """Apply preset settings to an object"""
        if not obj or not obj.rigid_body:
            return False
            
        rb = obj.rigid_body
        rb.type = self.settings['type']
        rb.collision_shape = self.settings['collision_shape']
        rb.mass = self.settings['mass']
        rb.friction = self.settings['friction']
        rb.restitution = self.settings['restitution']
        rb.kinematic = self.settings['kinematic']
        return True

# Default presets that will be available
DEFAULT_PRESETS = []  # Removed all default presets

# This class will store preset data in Blender's PropertyGroup system
class RigidBodyPresetItem(bpy.types.PropertyGroup):
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
        try:
            return json.loads(self.settings_json)
        except:
            return {}
    
    def set_settings(self, settings_dict):
        self.settings_json = json.dumps(settings_dict)

# Preset management 
class RigidBodyPresetManager:
    @staticmethod
    def get_user_presets_path():
        # User preset file will be stored in the addon directory
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(addon_dir, "rigid_body_presets.json")
    
    @staticmethod
    def save_preset_to_scene(name, settings):
        """Save preset to the current scene's collection"""
        # Use the passed context instead of accessing bpy.context directly
        scene = bpy.context.scene
        if not hasattr(scene, "rigid_body_presets"):
            return False
            
        # Check if preset with this name already exists
        for preset in scene.rigid_body_presets:
            if preset.name == name:
                # Update existing preset
                preset.set_settings(settings)
                return True
                
        # Create new preset
        preset = scene.rigid_body_presets.add()
        preset.name = name
        preset.set_settings(settings)
        return True

    @staticmethod
    def apply_preset_by_name(name, obj):
        """Apply a preset by name to an object"""
        # Get scene from the object's ID data to avoid context issues
        scene = obj.id_data.scene if hasattr(obj, "id_data") and hasattr(obj.id_data, "scene") else bpy.context.scene
        
        if not hasattr(scene, "rigid_body_presets") or not obj or not obj.rigid_body:
            return False
            
        # Find preset with matching name
        for preset_item in scene.rigid_body_presets:
            if preset_item.name == name:
                settings = preset_item.get_settings()
                
                # Apply settings to object
                rb = obj.rigid_body
                for key, value in settings.items():
                    if hasattr(rb, key):
                        setattr(rb, key, value)
                return True
                
        return False

# Registration
addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu", 'U', 'PRESS')
        kmi.properties.name = "VIEW3D_MT_quick_rigid"
        addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    bpy.utils.register_class(QuickRigidSettings)
    bpy.utils.register_class(RigidBodyPresetItem)
    bpy.types.Scene.quick_rigid_settings = bpy.props.PointerProperty(type=QuickRigidSettings)
    bpy.types.Scene.rigid_body_presets = bpy.props.CollectionProperty(type=RigidBodyPresetItem)

    bpy.utils.register_class(AddPassiveRigidBody)
    bpy.utils.register_class(AddActiveRigidBody)
    bpy.utils.register_class(RIGID_BODY_OT_toggle_animated)
    bpy.utils.register_class(AddRigidBodyPreset)
    bpy.utils.register_class(ApplyRigidBodyPreset)
    bpy.utils.register_class(DeleteRigidBodyPreset)
    
    # Register menus - add all submenus first, then the main menu
    bpy.utils.register_class(VIEW3D_MT_quick_rigid_collision_submenu)
    bpy.utils.register_class(VIEW3D_MT_quick_rigid_main_submenu)
    bpy.utils.register_class(VIEW3D_MT_quick_rigid_physics_submenu)
    bpy.utils.register_class(VIEW3D_MT_quick_rigid_sim_submenu)
    bpy.utils.register_class(VIEW3D_MT_quick_rigid_presets_submenu)
    bpy.utils.register_class(VIEW3D_MT_quick_rigid_bake_submenu)
    bpy.utils.register_class(VIEW3D_MT_quick_rigid)
    
    bpy.utils.register_class(VIEW3D_PT_QuickRigid)
    
    # We no longer initialize presets since DEFAULT_PRESETS is empty
    # for preset in DEFAULT_PRESETS:
    #     RigidBodyPresetManager.save_preset_to_scene(preset.name, preset.settings)
    
    register_keymaps()

def unregister():
    unregister_keymaps()
    
    bpy.utils.unregister_class(VIEW3D_PT_QuickRigid)
    
    # Unregister menus
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid)
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid_bake_submenu)
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid_presets_submenu)
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid_sim_submenu)
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid_physics_submenu)
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid_main_submenu)
    bpy.utils.unregister_class(VIEW3D_MT_quick_rigid_collision_submenu)
    
    bpy.utils.unregister_class(DeleteRigidBodyPreset)
    bpy.utils.unregister_class(ApplyRigidBodyPreset)
    bpy.utils.unregister_class(AddRigidBodyPreset)
    bpy.utils.unregister_class(RIGID_BODY_OT_toggle_animated)
    bpy.utils.unregister_class(AddActiveRigidBody)
    bpy.utils.unregister_class(AddPassiveRigidBody)
    
    del bpy.types.Scene.rigid_body_presets
    del bpy.types.Scene.quick_rigid_settings
    bpy.utils.unregister_class(RigidBodyPresetItem)
    bpy.utils.unregister_class(QuickRigidSettings)