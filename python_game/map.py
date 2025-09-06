"""
3D Map generation and management
"""
from ursina import *
import random
import math
from config import *

class GameMap:
    def __init__(self):
        self.entities = []
        self.spawn_points = []
        self.enemy_spawn_points = []
        self.walls = []
        self.cover_objects = []
        
        # Generate the map
        self.generate_map()
        
    def generate_map(self):
        """Generate the 3D game map"""
        # Clear existing entities
        self.clear_map()
        
        # Generate terrain
        self.generate_terrain()
        
        # Generate walls and structures
        self.generate_walls()
        
        # Generate cover objects
        self.generate_cover_objects()
        
        # Generate spawn points
        self.generate_spawn_points()
        
        # Add lighting
        self.setup_lighting()
        
    def clear_map(self):
        """Clear all map entities"""
        for entity in self.entities:
            if hasattr(entity, 'destroy'):
                entity.destroy()
        self.entities.clear()
        self.walls.clear()
        self.cover_objects.clear()
        self.spawn_points.clear()
        self.enemy_spawn_points.clear()
        
    def generate_terrain(self):
        """Generate the base terrain"""
        # Create ground plane
        ground = Entity(
            model='cube',
            scale=(MAP_SIZE, 1, MAP_SIZE),
            position=(0, -0.5, 0),
            color=color.gray,
            texture='white_cube',
            collider='box'
        )
        self.entities.append(ground)
        
        # Add some height variation
        for i in range(20):
            x = random.uniform(-MAP_SIZE/2, MAP_SIZE/2)
            z = random.uniform(-MAP_SIZE/2, MAP_SIZE/2)
            height = random.uniform(0.5, 2.0)
            
            hill = Entity(
                model='cube',
                scale=(random.uniform(2, 5), height, random.uniform(2, 5)),
                position=(x, height/2, z),
                color=color.brown,
                collider='box'
            )
            self.entities.append(hill)
            
    def generate_walls(self):
        """Generate walls and barriers"""
        # Outer boundary walls
        wall_height = WALL_HEIGHT
        wall_thickness = 1.0
        
        # North wall
        north_wall = Entity(
            model='cube',
            scale=(MAP_SIZE, wall_height, wall_thickness),
            position=(0, wall_height/2, MAP_SIZE/2),
            color=color.dark_gray,
            collider='box'
        )
        self.walls.append(north_wall)
        self.entities.append(north_wall)
        
        # South wall
        south_wall = Entity(
            model='cube',
            scale=(MAP_SIZE, wall_height, wall_thickness),
            position=(0, wall_height/2, -MAP_SIZE/2),
            color=color.dark_gray,
            collider='box'
        )
        self.walls.append(south_wall)
        self.entities.append(south_wall)
        
        # East wall
        east_wall = Entity(
            model='cube',
            scale=(wall_thickness, wall_height, MAP_SIZE),
            position=(MAP_SIZE/2, wall_height/2, 0),
            color=color.dark_gray,
            collider='box'
        )
        self.walls.append(east_wall)
        self.entities.append(east_wall)
        
        # West wall
        west_wall = Entity(
            model='cube',
            scale=(wall_thickness, wall_height, MAP_SIZE),
            position=(-MAP_SIZE/2, wall_height/2, 0),
            color=color.dark_gray,
            collider='box'
        )
        self.walls.append(west_wall)
        self.entities.append(west_wall)
        
        # Internal walls and structures
        self.generate_internal_structures()
        
    def generate_internal_structures(self):
        """Generate internal walls and structures"""
        # Create a maze-like structure
        num_rooms = random.randint(3, 6)
        
        for i in range(num_rooms):
            room_size = random.uniform(8, 15)
            x = random.uniform(-MAP_SIZE/3, MAP_SIZE/3)
            z = random.uniform(-MAP_SIZE/3, MAP_SIZE/3)
            
            # Create room walls
            self.create_room(x, z, room_size)
            
        # Add some random walls
        for i in range(random.randint(5, 10)):
            self.create_random_wall()
            
    def create_room(self, center_x, center_z, size):
        """Create a room with walls"""
        wall_height = WALL_HEIGHT
        wall_thickness = 0.5
        
        # Room walls (not all sides, create openings)
        walls_to_create = random.sample(['north', 'south', 'east', 'west'], random.randint(2, 4))
        
        if 'north' in walls_to_create:
            wall = Entity(
                model='cube',
                scale=(size, wall_height, wall_thickness),
                position=(center_x, wall_height/2, center_z + size/2),
                color=color.gray,
                collider='box'
            )
            self.walls.append(wall)
            self.entities.append(wall)
            
        if 'south' in walls_to_create:
            wall = Entity(
                model='cube',
                scale=(size, wall_height, wall_thickness),
                position=(center_x, wall_height/2, center_z - size/2),
                color=color.gray,
                collider='box'
            )
            self.walls.append(wall)
            self.entities.append(wall)
            
        if 'east' in walls_to_create:
            wall = Entity(
                model='cube',
                scale=(wall_thickness, wall_height, size),
                position=(center_x + size/2, wall_height/2, center_z),
                color=color.gray,
                collider='box'
            )
            self.walls.append(wall)
            self.entities.append(wall)
            
        if 'west' in walls_to_create:
            wall = Entity(
                model='cube',
                scale=(wall_thickness, wall_height, size),
                position=(center_x - size/2, wall_height/2, center_z),
                color=color.gray,
                collider='box'
            )
            self.walls.append(wall)
            self.entities.append(wall)
            
    def create_random_wall(self):
        """Create a random wall segment"""
        wall_height = WALL_HEIGHT
        wall_length = random.uniform(3, 8)
        wall_thickness = 0.5
        
        # Random position
        x = random.uniform(-MAP_SIZE/2 + 5, MAP_SIZE/2 - 5)
        z = random.uniform(-MAP_SIZE/2 + 5, MAP_SIZE/2 - 5)
        
        # Random rotation
        rotation_y = random.choice([0, 90, 180, 270])
        
        wall = Entity(
            model='cube',
            scale=(wall_length, wall_height, wall_thickness),
            position=(x, wall_height/2, z),
            rotation_y=rotation_y,
            color=color.gray,
            collider='box'
        )
        self.walls.append(wall)
        self.entities.append(wall)
        
    def generate_cover_objects(self):
        """Generate cover objects like crates, barrels, etc."""
        num_objects = random.randint(15, 25)
        
        for i in range(num_objects):
            object_type = random.choice(['crate', 'barrel', 'box', 'pillar'])
            self.create_cover_object(object_type)
            
    def create_cover_object(self, object_type):
        """Create a specific type of cover object"""
        x = random.uniform(-MAP_SIZE/2 + 3, MAP_SIZE/2 - 3)
        z = random.uniform(-MAP_SIZE/2 + 3, MAP_SIZE/2 - 3)
        
        if object_type == 'crate':
            obj = Entity(
                model='cube',
                scale=(1.5, 1.5, 1.5),
                position=(x, 0.75, z),
                color=color.brown,
                collider='box'
            )
        elif object_type == 'barrel':
            obj = Entity(
                model='cylinder',
                scale=(1, 2, 1),
                position=(x, 1, z),
                color=color.dark_gray,
                collider='cylinder'
            )
        elif object_type == 'box':
            obj = Entity(
                model='cube',
                scale=(1, 1, 1),
                position=(x, 0.5, z),
                color=color.orange,
                collider='box'
            )
        else:  # pillar
            obj = Entity(
                model='cylinder',
                scale=(0.8, 3, 0.8),
                position=(x, 1.5, z),
                color=color.light_gray,
                collider='cylinder'
            )
            
        self.cover_objects.append(obj)
        self.entities.append(obj)
        
    def generate_spawn_points(self):
        """Generate player and enemy spawn points"""
        # Player spawn points
        num_player_spawns = 4
        for i in range(num_player_spawns):
            x = random.uniform(-MAP_SIZE/3, MAP_SIZE/3)
            z = random.uniform(-MAP_SIZE/3, MAP_SIZE/3)
            spawn_point = Vec3(x, 1, z)
            self.spawn_points.append(spawn_point)
            
            # Visual marker for spawn point
            marker = Entity(
                model='sphere',
                scale=0.5,
                position=spawn_point,
                color=color.green,
                alpha=0.5
            )
            self.entities.append(marker)
            
        # Enemy spawn points
        num_enemy_spawns = 6
        for i in range(num_enemy_spawns):
            x = random.uniform(-MAP_SIZE/2 + 5, MAP_SIZE/2 - 5)
            z = random.uniform(-MAP_SIZE/2 + 5, MAP_SIZE/2 - 5)
            spawn_point = Vec3(x, 1, z)
            self.enemy_spawn_points.append(spawn_point)
            
            # Visual marker for enemy spawn point
            marker = Entity(
                model='sphere',
                scale=0.3,
                position=spawn_point,
                color=color.red,
                alpha=0.5
            )
            self.entities.append(marker)
            
    def setup_lighting(self):
        """Set up lighting for the map"""
        # Ambient light
        ambient_light = AmbientLight(color=color.rgb(100, 100, 100))
        self.entities.append(ambient_light)
        
        # Directional light (sun)
        sun = DirectionalLight(
            color=color.rgb(255, 255, 200),
            direction=Vec3(-1, -1, -1).normalized()
        )
        self.entities.append(sun)
        
        # Add some point lights for atmosphere
        for i in range(random.randint(3, 6)):
            x = random.uniform(-MAP_SIZE/2, MAP_SIZE/2)
            z = random.uniform(-MAP_SIZE/2, MAP_SIZE/2)
            
            light = PointLight(
                color=color.rgb(255, 200, 100),
                position=Vec3(x, 3, z),
                attenuation=(1, 0.1, 0.01)
            )
            self.entities.append(light)
            
    def get_random_player_spawn(self):
        """Get a random player spawn point"""
        if self.spawn_points:
            return random.choice(self.spawn_points)
        return Vec3(0, 1, 0)
        
    def get_random_enemy_spawn(self):
        """Get a random enemy spawn point"""
        if self.enemy_spawn_points:
            return random.choice(self.enemy_spawn_points)
        return Vec3(0, 1, 0)
        
    def is_position_valid(self, position, radius=1.0):
        """Check if a position is valid for spawning"""
        # Check if position is within map bounds
        if (abs(position.x) > MAP_SIZE/2 - radius or 
            abs(position.z) > MAP_SIZE/2 - radius):
            return False
            
        # Check for collisions with walls and cover objects
        for wall in self.walls:
            if distance(position, wall.position) < radius + 1.0:
                return False
                
        for cover in self.cover_objects:
            if distance(position, cover.position) < radius + 1.0:
                return False
                
        return True
        
    def get_map_bounds(self):
        """Get the map boundaries"""
        return {
            'min_x': -MAP_SIZE/2,
            'max_x': MAP_SIZE/2,
            'min_z': -MAP_SIZE/2,
            'max_z': MAP_SIZE/2,
            'min_y': 0,
            'max_y': MAP_HEIGHT
        }
