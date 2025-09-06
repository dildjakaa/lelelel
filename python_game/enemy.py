"""
AI Enemy class with pathfinding and combat behavior
"""
from ursina import *
import random
import math
from config import *

class Enemy(Entity):
    def __init__(self, position=(0, 0, 0), **kwargs):
        super().__init__(
            model='cube',
            color=color.red,
            position=position,
            scale=(1, 2, 1),
            **kwargs
        )
        
        # Health system
        self.max_health = ENEMY_HEALTH
        self.health = self.max_health
        self.is_alive = True
        
        # AI state
        self.state = "patrol"  # patrol, chase, attack, dead
        self.target = None
        self.last_attack_time = 0
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
        
        # Movement
        self.speed = ENEMY_SPEED
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 10.0
        self.friction = 0.8
        
        # Detection
        self.detection_range = ENEMY_DETECTION_RANGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.last_player_position = None
        
        # Patrol behavior
        self.patrol_points = []
        self.current_patrol_target = 0
        self.patrol_wait_time = 0
        self.patrol_wait_duration = 2.0
        
        # Collision
        self.collider = BoxCollider(self, center=(0, 1, 0), size=(1, 2, 1))
        
        # Visual effects
        self.health_bar = None
        self.damage_effect = None
        
        # Setup enemy
        self.setup_enemy()
        
    def setup_enemy(self):
        """Set up enemy visual components"""
        # Create health bar
        self.health_bar = Entity(
            parent=self,
            model='cube',
            color=color.green,
            scale=(1, 0.1, 0.1),
            position=(0, 2.5, 0),
            billboard=True
        )
        
        # Create damage effect
        self.damage_effect = Entity(
            parent=self,
            model='cube',
            color=color.red,
            scale=(1.2, 2.2, 1.2),
            alpha=0
        )
        
    def update(self):
        """Update enemy AI and behavior"""
        if not self.is_alive:
            return
            
        # Update health bar
        self.update_health_bar()
        
        # AI state machine
        if self.state == "patrol":
            self.patrol_behavior()
        elif self.state == "chase":
            self.chase_behavior()
        elif self.state == "attack":
            self.attack_behavior()
            
        # Apply movement
        self.apply_movement()
        
        # Check if dead
        if self.health <= 0 and self.is_alive:
            self.die()
            
    def patrol_behavior(self):
        """Patrol between waypoints"""
        if not self.patrol_points:
            self.generate_patrol_points()
            
        if not self.patrol_points:
            return
            
        target_point = self.patrol_points[self.current_patrol_target]
        distance_to_target = distance(self.position, target_point)
        
        if distance_to_target < 1.0:
            # Reached patrol point, wait then move to next
            if self.patrol_wait_time <= 0:
                self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_points)
                self.patrol_wait_time = self.patrol_wait_duration
            else:
                self.patrol_wait_time -= time.dt
        else:
            # Move towards patrol point
            direction = (target_point - self.position).normalized()
            self.move_towards(direction)
            
        # Check for player detection
        self.check_player_detection()
        
    def chase_behavior(self):
        """Chase the player"""
        if not self.target:
            self.state = "patrol"
            return
            
        distance_to_player = distance(self.position, self.target.position)
        
        # Check if player is still in range
        if distance_to_player > self.detection_range * 1.5:
            self.state = "patrol"
            self.target = None
            return
            
        # Check if close enough to attack
        if distance_to_player <= self.attack_range:
            self.state = "attack"
            return
            
        # Move towards player
        direction = (self.target.position - self.position).normalized()
        self.move_towards(direction)
        
    def attack_behavior(self):
        """Attack the player"""
        if not self.target:
            self.state = "patrol"
            return
            
        distance_to_player = distance(self.position, self.target.position)
        
        # Check if player is still in attack range
        if distance_to_player > self.attack_range * 1.2:
            self.state = "chase"
            return
            
        # Attack if cooldown is ready
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.attack_player()
            self.last_attack_time = current_time
            
    def check_player_detection(self):
        """Check if player is detected"""
        # Find player (assuming player is the first person controller)
        player = None
        for entity in scene.entities:
            if hasattr(entity, 'is_alive') and hasattr(entity, 'health') and entity != self:
                if hasattr(entity, 'max_health') and entity.max_health == PLAYER_HEALTH:
                    player = entity
                    break
                    
        if not player or not player.is_alive:
            return
            
        distance_to_player = distance(self.position, player.position)
        
        # Check if player is in detection range
        if distance_to_player <= self.detection_range:
            # Check line of sight (simple version)
            if self.has_line_of_sight(player):
                self.target = player
                self.state = "chase"
                self.last_player_position = player.position
                
    def has_line_of_sight(self, target):
        """Check if there's a clear line of sight to target"""
        # Simple line of sight check (can be improved with raycasting)
        direction = (target.position - self.position).normalized()
        distance_to_target = distance(self.position, target.position)
        
        # Cast a ray to check for obstacles
        hit_info = raycast(self.position, direction, distance_to_target, ignore=[self])
        
        return hit_info.hit == False or hit_info.entity == target
        
    def move_towards(self, direction):
        """Move towards a direction"""
        # Apply acceleration
        self.velocity += direction * self.acceleration * time.dt
        
        # Limit speed
        if self.velocity.length() > self.speed:
            self.velocity = self.velocity.normalized() * self.speed
            
        # Apply friction
        self.velocity *= self.friction
        
    def apply_movement(self):
        """Apply movement to position"""
        if self.velocity.length() > 0.1:
            # Move the enemy
            self.position += self.velocity * time.dt
            
            # Rotate to face movement direction
            if self.velocity.length() > 0.1:
                self.rotation_y = math.degrees(math.atan2(self.velocity.x, self.velocity.z))
                
    def attack_player(self):
        """Attack the player"""
        if not self.target or not self.target.is_alive:
            return
            
        # Deal damage to player
        self.target.take_damage(ENEMY_DAMAGE)
        
        # Visual feedback
        self.show_attack_effect()
        
        print(f"Enemy attacked player for {ENEMY_DAMAGE} damage!")
        
    def show_attack_effect(self):
        """Show attack visual effect"""
        if self.damage_effect:
            self.damage_effect.alpha = 0.5
            self.damage_effect.animate('alpha', 0, duration=0.2)
            
    def take_damage(self, damage):
        """Take damage"""
        if not self.is_alive:
            return
            
        self.health -= damage
        self.health = max(0, self.health)
        
        # Show damage effect
        self.show_damage_effect()
        
        print(f"Enemy took {damage} damage. Health: {self.health}")
        
    def show_damage_effect(self):
        """Show damage visual effect"""
        if self.damage_effect:
            self.damage_effect.alpha = 0.3
            self.damage_effect.animate('alpha', 0, duration=0.3)
            
    def die(self):
        """Handle enemy death"""
        self.is_alive = False
        self.health = 0
        self.state = "dead"
        
        # Disable collision
        self.collider.enabled = False
        
        # Visual effect
        self.show_death_effect()
        
        print("Enemy died!")
        
    def show_death_effect(self):
        """Show death visual effect"""
        # Fade out
        self.animate('alpha', 0, duration=1.0)
        
        # Disable health bar
        if self.health_bar:
            self.health_bar.enabled = False
            
    def update_health_bar(self):
        """Update health bar display"""
        if not self.health_bar or not self.is_alive:
            return
            
        health_percentage = self.health / self.max_health
        self.health_bar.scale_x = health_percentage
        
        # Change color based on health
        if health_percentage > 0.6:
            self.health_bar.color = color.green
        elif health_percentage > 0.3:
            self.health_bar.color = color.yellow
        else:
            self.health_bar.color = color.red
            
    def generate_patrol_points(self):
        """Generate random patrol points around the enemy"""
        num_points = random.randint(3, 6)
        self.patrol_points = []
        
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            distance = random.uniform(5, 15)
            
            x = self.position.x + math.cos(angle) * distance
            z = self.position.z + math.sin(angle) * distance
            
            # Keep within map bounds
            x = max(-MAP_SIZE/2, min(MAP_SIZE/2, x))
            z = max(-MAP_SIZE/2, min(MAP_SIZE/2, z))
            
            self.patrol_points.append(Vec3(x, self.position.y, z))
            
    def respawn(self, position=None):
        """Respawn the enemy"""
        if position:
            self.position = position
        else:
            self.position = (0, 0, 0)
            
        self.is_alive = True
        self.health = self.max_health
        self.state = "patrol"
        self.target = None
        self.velocity = Vec3(0, 0, 0)
        self.alpha = 1
        self.collider.enabled = True
        
        if self.health_bar:
            self.health_bar.enabled = True
            
        print("Enemy respawned!")
