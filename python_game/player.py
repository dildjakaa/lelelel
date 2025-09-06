"""
Player character class with first-person controls and physics
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
from config import *

class Player(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(
            speed=PLAYER_SPEED,
            jump_height=JUMP_FORCE,
            gravity=GRAVITY,
            mouse_sensitivity=Vec2(MOUSE_SENSITIVITY, MOUSE_SENSITIVITY),
            **kwargs
        )
        
        # Health system
        self.max_health = PLAYER_HEALTH
        self.health = self.max_health
        self.is_alive = True
        
        # Weapon system
        self.current_weapon = None
        self.weapons = []
        
        # Movement state
        self.is_moving = False
        self.is_running = False
        self.is_crouching = False
        
        # Collision detection
        self.collision_enabled = True
        self.collision_radius = 0.5
        
        # Audio
        self.footstep_sounds = []
        self.last_footstep_time = 0
        self.footstep_interval = 0.5
        
        # Initialize player appearance
        self.setup_appearance()
        
    def setup_appearance(self):
        """Set up player visual appearance"""
        # Make the player invisible (first-person view)
        self.model = None
        self.color = color.clear
        
        # Add a simple capsule for collision
        self.collider = CapsuleCollider(
            self,
            radius=self.collision_radius,
            height=2,
            center=(0, 1, 0)
        )
        
    def update(self):
        """Update player state each frame"""
        super().update()
        
        # Handle movement audio
        self.handle_footsteps()
        
        # Update movement state
        self.update_movement_state()
        
        # Check if player is alive
        if self.health <= 0 and self.is_alive:
            self.die()
            
    def handle_footsteps(self):
        """Play footstep sounds when moving"""
        if self.is_moving and time.time() - self.last_footstep_time > self.footstep_interval:
            self.play_footstep_sound()
            self.last_footstep_time = time.time()
            
    def play_footstep_sound(self):
        """Play a random footstep sound"""
        if self.footstep_sounds:
            sound = random.choice(self.footstep_sounds)
            if hasattr(sound, 'play'):
                sound.play()
                
    def update_movement_state(self):
        """Update movement state flags"""
        # Check if player is moving
        velocity = self.velocity
        self.is_moving = velocity.length() > 0.1
        
        # Check if running (holding shift)
        self.is_running = held_keys['left shift'] and self.is_moving
        
        # Check if crouching (holding ctrl)
        self.is_crouching = held_keys['left ctrl']
        
    def take_damage(self, damage):
        """Take damage and update health"""
        if not self.is_alive:
            return
            
        self.health -= damage
        self.health = max(0, self.health)
        
        # Visual feedback for damage
        self.show_damage_effect()
        
        print(f"Player took {damage} damage. Health: {self.health}")
        
    def show_damage_effect(self):
        """Show visual effect when taking damage"""
        # Red flash effect
        if hasattr(self, 'damage_overlay'):
            self.damage_overlay.color = color.red
            self.damage_overlay.alpha = 0.5
            invoke(setattr, self.damage_overlay, 'alpha', 0, delay=0.1)
            
    def heal(self, amount):
        """Heal the player"""
        if not self.is_alive:
            return
            
        self.health += amount
        self.health = min(self.max_health, self.health)
        print(f"Player healed {amount}. Health: {self.health}")
        
    def die(self):
        """Handle player death"""
        self.is_alive = False
        self.health = 0
        print("Player died!")
        
        # Disable movement
        self.speed = 0
        self.jump_height = 0
        
        # Show death effect
        self.show_death_effect()
        
    def show_death_effect(self):
        """Show death visual effect"""
        # Screen fade to black
        if hasattr(self, 'death_overlay'):
            self.death_overlay.color = color.black
            self.death_overlay.alpha = 0
            self.death_overlay.animate('alpha', 1, duration=2)
            
    def respawn(self, spawn_point=None):
        """Respawn the player"""
        self.is_alive = True
        self.health = self.max_health
        self.speed = PLAYER_SPEED
        self.jump_height = JUMP_FORCE
        
        if spawn_point:
            self.position = spawn_point
        else:
            self.position = (0, 1, 0)
            
        print("Player respawned!")
        
    def add_weapon(self, weapon):
        """Add a weapon to the player's arsenal"""
        self.weapons.append(weapon)
        if not self.current_weapon:
            self.current_weapon = weapon
            
    def switch_weapon(self, weapon_index):
        """Switch to a different weapon"""
        if 0 <= weapon_index < len(self.weapons):
            self.current_weapon = self.weapons[weapon_index]
            
    def fire_weapon(self):
        """Fire the current weapon"""
        if self.current_weapon and self.is_alive:
            return self.current_weapon.fire(self.position, self.forward)
        return None
        
    def reload_weapon(self):
        """Reload the current weapon"""
        if self.current_weapon and self.is_alive:
            self.current_weapon.reload()
            
    def get_health_percentage(self):
        """Get health as a percentage"""
        return self.health / self.max_health if self.max_health > 0 else 0
        
    def get_ammo_info(self):
        """Get current weapon ammo information"""
        if self.current_weapon:
            return {
                'current': self.current_weapon.current_ammo,
                'max': self.current_weapon.max_ammo,
                'total': self.current_weapon.total_ammo
            }
        return {'current': 0, 'max': 0, 'total': 0}
