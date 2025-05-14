import bpy
from .icons import get_icon_id  # Import the function to get icon ID

class VIEW3D_PT_QuickRigid(bpy.types.Panel):
    """Panel for Quick Rigid tools"""
    bl_label = "Quick Rigid"
    bl_idname = "VIEW3D_PT_quick_rigid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Quick Rigid"
   
    def draw_header(self, context):
        # Add custom icon to the header
        self.layout.label(text="", icon_value=get_icon_id("quick_rigid_icon"))
   
    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.2
        
        # Get quick rigid settings - moved to the top so we can use it everywhere
        settings = context.scene.quick_rigid_settings
        
        if not context.selected_objects:
            layout.label(text="Select a mesh to add a rigid body", icon='INFO')
            # Still show addon settings even when nothing is selected
            self.draw_settings_box(context, layout, settings)
            return
            
        # Check if there are selected mesh objects
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            layout.label(text="Select a mesh to add a rigid body", icon='INFO')
            # Still show addon settings even when no mesh is selected
            self.draw_settings_box(context, layout, settings)
            return
            
        # Show info about selection count if multiple objects - moved to the top
        if len(selected_meshes) > 1:
            rb_count = len([obj for obj in selected_meshes if obj.rigid_body])
            layout.label(text=f"{len(selected_meshes)} objects selected ({rb_count} with rigid bodies)", icon='INFO')
            
        # Add rigid body box - always show this
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

        # Get the active object and check for rigid body
        obj = context.active_object
        has_rigid_body = obj and hasattr(obj, "rigid_body") and obj.rigid_body is not None
        
        # Only show the rigid body specific settings if active object has rigid body
        if has_rigid_body:
            # Main settings - collapsible
            box = layout.box()
            row = box.row()
            row.prop(settings, "show_main_settings", icon="TRIA_DOWN" if settings.show_main_settings else "TRIA_RIGHT", 
                    icon_only=True, emboss=False)
            row.label(text="Main Settings:", icon='SETTINGS')
            
            if settings.show_main_settings:
                # Collision shape property
                col = box.column(align=True)
                col.prop(obj.rigid_body, "collision_shape", text="Shape", icon='MESH_ICOSPHERE')
                
                # Add a small space between shape and animated properties
                box.separator(factor=0.5)
                
                # Animated property 
                anim_row = box.row()
                anim_row.prop(obj.rigid_body, "kinematic", text="Animated", icon='RENDER_ANIMATION', toggle=True)
                
                # Copy settings button
                box.separator(factor=0.7)
                copy_row = box.row(align=True)
                copy_row.operator("rigidbody.object_settings_copy", text="Copy Settings", icon='COPYDOWN')
            
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
            
            # Presets section - only show when we have a rigid body
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
        
        # Only show Bake section if there's a rigid body and a rigidbody_world
        if has_rigid_body and context.scene.rigidbody_world:
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
                    
                    # Check if blend file is saved before enabling disk cache
                    is_saved = bool(bpy.data.filepath)
                    disk_row = cache_box.row()
                    disk_row.enabled = is_saved  # Gray out if file is not saved
                    disk_row.prop(point_cache, "use_disk_cache", text="Disk Cache", icon='DISK_DRIVE')
                    
                    if not is_saved:
                        # Show message explaining why it's disabled
                        info_row = cache_box.row()
                        info_row.alignment = 'CENTER'
                        info_row.label(text="Save file to enable disk cache", icon='ERROR')
                    
                    # Only show additional disk options when enabled and file is saved
                    if point_cache.use_disk_cache and is_saved:
                        disk_col = cache_box.column(align=True)
                        disk_col.prop(point_cache, "use_library_path", text="Use Lib Path")
                        disk_col.prop(point_cache, "compression", text="Compression")
                        disk_col.separator()
                        disk_col.prop(point_cache, "filepath", text="File Path")
        
        # Always show settings box at the bottom
        self.draw_settings_box(context, layout, settings)
    
    def draw_settings_box(self, context, layout, settings):
        """Draw the addon settings box"""
        # Addon Settings - collapsible
        settings_box = layout.box()
        row = settings_box.row()
        row.prop(settings, "show_settings", icon="TRIA_DOWN" if settings.show_settings else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text="Addon Settings:", icon='PREFERENCES')
        
        if settings.show_settings:
            # Enable/disable floating menu
            col = settings_box.column()
            col.prop(settings, "enable_floating_menu", text="Enable Floating Menu")
            
            # Only show shortcut settings if floating menu is enabled
            if settings.enable_floating_menu:
                # Show current shortcut with shortcut text
                combo_text = ""
                if settings.use_ctrl:
                    combo_text += "Ctrl+"
                if settings.use_alt:
                    combo_text += "Alt+"
                if settings.use_shift:
                    combo_text += "Shift+"
                combo_text += settings.shortcut_key
                
                # Shortcut key setting with current shortcut
                col.label(text=f"Menu Shortcut: {combo_text}")
                
                # Modifier checkboxes in a row
                mod_row = col.row(align=True)
                mod_row.prop(settings, "use_ctrl", toggle=True)
                mod_row.prop(settings, "use_alt", toggle=True)
                mod_row.prop(settings, "use_shift", toggle=True)
                
                # Key selection dropdown
                key_row = col.row()
                key_row.prop(settings, "shortcut_key", text="Key")
                
                # Apply button
                apply_row = col.row()
                apply_row.operator("quick_rigid.apply_shortcut_key", text="Apply Shortcut", icon='CHECKMARK')
            
            col.separator()
            
            # Documentation link
            doc_row = col.row()
            doc_op = doc_row.operator("wm.url_open", text="Documentation", icon='HELP')
            doc_op.url = "https://github.com/TheEmber1/Quick-Rigid"
            
            # Report bug link
            bug_row = col.row()
            bug_op = bug_row.operator("wm.url_open", text="Report Bug", icon='ERROR')
            bug_op.url = "https://github.com/TheEmber1/Quick-Rigid/issues"
            
            # YouTube link
            youtube_row = col.row()
            youtube_op = youtube_row.operator("wm.url_open", text="YouTube Channel", icon='URL')
            youtube_op.url = "https://www.youtube.com/@The_Ember"
            
            # Credits section with version info moved above
            col.separator()
            
            # Version info
            version_row = col.row()
            version_row.alignment = 'CENTER'
            version_row.label(text="Quick Rigid v1.2.0")
            
            # Creator credit
            credit_row = col.row()
            credit_row.alignment = 'CENTER'
            credit_row.label(text="Created by THE EMBER")

# List of classes to register
classes = [
    VIEW3D_PT_QuickRigid
]

def register():
    """Register panel classes"""
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    """Unregister panel classes"""
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)