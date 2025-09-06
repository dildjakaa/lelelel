"""
Modular weapon system for easy expansion
"""
from ursina import *
import time
import random
from config import *

class Weapon(Entity):
    def __init__(self, name="Weapon", damage=25, range=50.0, fire_rate=0.5, 
                 max_ammo=30, total_ammo=120, **kwargs):
        super().__init__(**kwargs)
        
        self.name = name
        self.damage = damage
        self.range = range
        self.fire_rate = fire_rate  # shots per second
        self.max_ammo = max_ammo
        self.total_ammo = total_ammo
        self.current_ammo = max_ammo
        
        # Timing
        self.last_shot_time = 0
        self.reload_time = 2.0
        self.is_reloading = False
        
        # Visual and audio
        self.muzzle_flash = None
        self.shell_eject = None
        self.fire_sound = None
        self.reload_sound = None
        
        # Setup weapon appearance
        self.setup_weapon()
        
    def setup_weapon(self):
        """Set up weapon visual and audio components"""
        # Create muzzle flash effect
        self.muzzle_flash = Entity(
            parent=self,
            model='cube',
            scale=(0.1, 0.1, 0.3),
            color=color.yellow,
            position=(0, 0, 0.5),
            alpha=0
        )
        
        # Create shell ejection effect
        self.shell_eject = Entity(
            parent=self,
            model='cube',
            scale=(0.05, 0.05, 0.1),
            color=color.orange,
            position=(0.2, 0, 0),
            alpha=0
        )
        
    def can_fire(self):
        """Check if weapon can fire"""
        current_time = time.time()
        time_since_last_shot = current_time - self.last_shot_time
        min_time_between_shots = 1.0 / self.fire_rate
        
        return (not self.is_reloading and 
                self.current_ammo > 0 and 
                time_since_last_shots >= min_time_between_shots)
                
    def fire(self, position, direction):
        """Fire the weapon"""
        if not self.can_fire():
            return None
            
        # Update ammo and timing
        self.current_ammo -= 1
        self.last_shot_time = time.time()
        
        # Create bullet/projectile
        bullet = self.create_bullet(position, direction)
        
        # Visual effects
        self.show_muzzle_flash()
        self.eject_shell()
        
        # Audio
        self.play_fire_sound()
        
        return bullet
        
    def create_bullet(self, position, direction):
        """Create a bullet entity"""
        bullet = Entity(
            model='sphere',
            scale=0.1,
            color=color.yellow,
            position=position,
            collider='sphere'
        )
        
        # Add bullet physics
        bullet.velocity = direction * 100  # Bullet speed
        bullet.lifetime = self.range / 100  # Time until bullet disappears
        
        return bullet
        
    def show_muzzle_flash(self):
        """Show muzzle flash effect"""
        if self.muzzle_flash:
            self.muzzle_flash.alpha = 1
            self.muzzle_flash.animate('alpha', 0, duration=0.1)
            
    def eject_shell(self):
        """Show shell ejection effect"""
        if self.shell_eject:
            self.shell_eject.alpha = 1
            self.shell_eject.animate('alpha', 0, duration=0.5)
            
    def play_fire_sound(self):
        """Play weapon fire sound"""
        if self.fire_sound:
            if hasattr(self.fire_sound, 'play'):
                self.fire_sound.play()
                
    def play_reload_sound(self):
        """Play weapon reload sound"""
        if self.reload_sound:
            if hasattr(self.reload_sound, 'play'):
                self.reload_sound.play()
                
    def reload(self):
        """Reload the weapon"""
        if self.is_reloading or self.current_ammo >= self.max_ammo:
            return False
            
        if self.total_ammo <= 0:
            print("No ammo left!")
            return False
            
        self.is_reloading = True
        self.play_reload_sound()
        
        # Reload after delay
        invoke(self.finish_reload, delay=self.reload_time)
        
        return True
        
    def finish_reload(self):
        """Finish the reload process"""
        ammo_needed = self.max_ammo - self.current_ammo
        ammo_to_add = min(ammo_needed, self.total_ammo)
        
        self.current_ammo += ammo_to_add
        self.total_ammo -= ammo_to_add
        self.is_reloading = False
        
        print(f"Reloaded! Ammo: {self.current_ammo}/{self.max_ammo}, Total: {self.total_ammo}")
        
    def get_ammo_info(self):
        """Get current ammo information"""
        return {
            'current': self.current_ammo,
            'max': self.max_ammo,
            'total': self.total_ammo,
            'is_reloading': self.is_reloading
        }
        
    def add_ammo(self, amount):
        """Add ammo to total reserve"""
        self.total_ammo += amount
        print(f"Added {amount} ammo. Total: {self.total_ammo}")

class Pistol(Weapon):
    def __init__(self, **kwargs):
        super().__init__(
            name="Pistol",
            damage=25,
            range=30.0,
            fire_rate=2.0,
            max_ammo=12,
            total_ammo=60,
            **kwargs
        )
        
class Rifle(Weapon):
    def __init__(self, **kwargs):
        super().__init__(
            name="Rifle",
            damage=35,
            range=60.0,
            fire_rate=8.0,
            max_ammo=30,
            total_ammo=120,
            **kwargs
        )
        
class Shotgun(Weapon):
    def __init__(self, **kwargs):
        super().__init__(
            name="Shotgun",
            damage=60,
            range=15.0,
            fire_rate=1.0,
            max_ammo=8,
            total_ammo=32,
            **kwargs
        )
        
    def fire(self, position, direction):
        """Shotgun fires multiple pellets"""
        if not self.can_fire():
            return None
            
        # Update ammo and timing
        self.current_ammo -= 1
        self.last_shot_time = time.time()
        
        # Create multiple pellets
        pellets = []
        for i in range(8):  # 8 pellets per shot
            # Add spread to direction
            spread = random.uniform(-0.2, 0.2)
            pellet_direction = direction + Vec3(spread, spread, 0)
            pellet_direction = pellet_direction.normalized()
            
            pellet = self.create_bullet(position, pellet_direction)
            pellets.append(pellet)
            
        # Visual effects
        self.show_muzzle_flash()
        self.eject_shell()
        self.play_fire_sound()
        
        return pellets
