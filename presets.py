import bpy
import os
import json

# Default presets that will be available (currently empty)
DEFAULT_PRESETS = []

class RigidBodyPreset:
    """Class representing a rigid body preset"""
    def __init__(self, name="New Preset", settings=None, simulation_settings=None):
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
            
        # Add simulation settings
        self.simulation_settings = simulation_settings or {}
    
    @staticmethod
    def from_object(obj, name="New Preset"):
        """Create a preset from an object's rigid body settings"""
        # Get scene from context instead of object
        scene = bpy.context.scene
        
        if not obj or not obj.rigid_body:
            return RigidBodyPreset(name)
            
        # Object rigid body settings
        settings = {
            'type': obj.rigid_body.type,
            'collision_shape': obj.rigid_body.collision_shape,
            'mass': obj.rigid_body.mass,
            'friction': obj.rigid_body.friction,
            'restitution': obj.rigid_body.restitution,
            'kinematic': obj.rigid_body.kinematic
        }
        
        # Simulation settings from scene
        simulation_settings = {
            'use_gravity': scene.use_gravity,
            'gravity': [scene.gravity[0], scene.gravity[1], scene.gravity[2]]
        }
        
        # Add rigid body world settings if available
        if scene.rigidbody_world:
            simulation_settings.update({
                'time_scale': scene.rigidbody_world.time_scale,
                'solver_iterations': scene.rigidbody_world.solver_iterations,
                'use_split_impulse': scene.rigidbody_world.use_split_impulse
            })
            
        return RigidBodyPreset(name, settings, simulation_settings)
    
    def apply_to_object(self, obj):
        """Apply preset settings to an object and simulation settings to scene"""
        if not obj or not obj.rigid_body:
            return False
        
        # Get scene from context
        scene = bpy.context.scene
        
        # Apply rigid body settings to object
        rb = obj.rigid_body
        for key, value in self.settings.items():
            if hasattr(rb, key):
                setattr(rb, key, value)
                
        # Apply simulation settings to scene if they exist
        if self.simulation_settings:
            # Apply gravity settings
            if 'use_gravity' in self.simulation_settings:
                scene.use_gravity = self.simulation_settings['use_gravity']
            
            if 'gravity' in self.simulation_settings and isinstance(self.simulation_settings['gravity'], list):
                for i in range(min(len(self.simulation_settings['gravity']), 3)):
                    scene.gravity[i] = self.simulation_settings['gravity'][i]
            
            # Apply rigid body world settings if available
            if scene.rigidbody_world:
                if 'time_scale' in self.simulation_settings:
                    scene.rigidbody_world.time_scale = self.simulation_settings['time_scale']
                
                if 'solver_iterations' in self.simulation_settings:
                    scene.rigidbody_world.solver_iterations = self.simulation_settings['solver_iterations']
                
                if 'use_split_impulse' in self.simulation_settings:
                    scene.rigidbody_world.use_split_impulse = self.simulation_settings['use_split_impulse']
                    
        return True

class RigidBodyPresetManager:
    """Manages saving, loading and applying rigid body presets"""
    
    @staticmethod
    def get_user_presets_path():
        """Get path to user presets file"""
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(addon_dir, "rigid_body_presets.json")
    
    @staticmethod
    def save_preset_to_scene(name, settings, simulation_settings=None):
        """Save preset to the current scene's collection"""
        # Don't use bpy.context.scene directly, as it might not be available during registration
        try:
            # Try to access the active scene safely
            scene = bpy.context.scene
            if not hasattr(scene, "rigid_body_presets"):
                return False
                
            # Combine settings into one dictionary for storage
            combined_settings = settings.copy()
            if simulation_settings:
                combined_settings['simulation'] = simulation_settings
                
            # Check if preset with this name already exists
            for preset in scene.rigid_body_presets:
                if preset.name == name:
                    # Update existing preset
                    preset.set_settings(combined_settings)
                    return True
                    
            # Create new preset
            preset = scene.rigid_body_presets.add()
            preset.name = name
            preset.set_settings(combined_settings)
            return True
        except (AttributeError, RuntimeError):
            # If context.scene isn't available, we'll handle this gracefully
            return False

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
                
                # Apply rigid body settings to object
                rb = obj.rigid_body
                simulation_settings = settings.pop('simulation', None)
                
                for key, value in settings.items():
                    if hasattr(rb, key):
                        setattr(rb, key, value)
                        
                # Apply simulation settings if available
                if simulation_settings:
                    # Apply gravity settings
                    if 'use_gravity' in simulation_settings:
                        scene.use_gravity = simulation_settings['use_gravity']
                    
                    if 'gravity' in simulation_settings and isinstance(simulation_settings['gravity'], list):
                        for i in range(min(len(simulation_settings['gravity']), 3)):
                            scene.gravity[i] = simulation_settings['gravity'][i]
                    
                    # Apply rigid body world settings if available
                    if scene.rigidbody_world:
                        if 'time_scale' in simulation_settings:
                            scene.rigidbody_world.time_scale = simulation_settings['time_scale']
                        
                        if 'solver_iterations' in simulation_settings:
                            scene.rigidbody_world.solver_iterations = simulation_settings['solver_iterations']
                        
                        if 'use_split_impulse' in simulation_settings:
                            scene.rigidbody_world.use_split_impulse = simulation_settings['use_split_impulse']
                
                return True
                
        return False

    @staticmethod
    def initialize_default_presets():
        """Initialize scene with default presets"""
        for preset in DEFAULT_PRESETS:
            RigidBodyPresetManager.save_preset_to_scene(preset.name, preset.settings, preset.simulation_settings if hasattr(preset, 'simulation_settings') else None)