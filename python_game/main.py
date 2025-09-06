"""
Main game file - 3D Shooter Game with Ursina Engine
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time

# Game configuration constants (inline since config.py might not exist)
GAME_TITLE = "3D Shooter Game"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FULLSCREEN = False
VSYNC = True
SHOW_FPS = True

# Simple Player class (inline replacement)
class Player:
    def __init__(self, position=(0, 1, 0)):
        self.controller = FirstPersonController(position=position)
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        self.current_weapon = "rifle"
        self.weapons = {"pistol": True, "rifle": True, "shotgun": True}
        self.ammo = {"pistol": 50, "rifle": 30, "shotgun": 20}
        self.max_ammo = {"pistol": 50, "rifle": 30, "shotgun": 20}
        
    def update(self):
        if not self.is_alive:
            return
            
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            
    def fire_weapon(self):
        if not self.is_alive or self.ammo[self.current_weapon] <= 0:
            return None
            
        self.ammo[self.current_weapon] -= 1
        
        # Create bullet
        bullet = Entity(model='cube', color=color.yellow, scale=0.1,
                       position=self.controller.position + self.controller.forward)
        bullet.velocity = self.controller.forward * 30
        bullet.lifetime = 5.0
        return bullet
        
    def reload_weapon(self):
        self.ammo[self.current_weapon] = self.max_ammo[self.current_weapon]
        
    def switch_weapon(self, weapon_index):
        weapons = ["pistol", "rifle", "shotgun"]
        if 0 <= weapon_index < len(weapons):
            self.current_weapon = weapons[weapon_index]
            
    def add_weapon(self, weapon):
        pass  # Simplified
        
    def respawn(self, position):
        self.health = self.max_health
        self.is_alive = True
        self.controller.position = position
        for weapon in self.ammo:
            self.ammo[weapon] = self.max_ammo[weapon]

# Simple Enemy class (inline replacement)
class Enemy:
    def __init__(self, position=(0, 1, 0)):
        self.entity = Entity(model='cube', color=color.red, scale=1.5, position=position)
        self.position = position
        self.health = 50
        self.is_alive = True
        self.speed = 2
        
    def update(self):
        if not self.is_alive:
            return
            
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            if hasattr(self.entity, 'disable'):
                self.entity.disable()
            
    def destroy(self):
        if hasattr(self.entity, 'destroy'):
            self.entity.destroy()

# Simple GameMap class (inline replacement)
class GameMap:
    def __init__(self):
        # Create simple ground
        self.ground = Entity(model='plane', color=color.green, scale=50)
        
        # Create some walls
        for i in range(10):
            Entity(model='cube', color=color.gray, 
                  position=(random.uniform(-20, 20), 1.5, random.uniform(-20, 20)),
                  scale=(2, 3, 2))
                  
    def get_random_player_spawn(self):
        return Vec3(0, 1, 0)
        
    def get_random_enemy_spawn(self):
        return Vec3(random.uniform(-15, 15), 1, random.uniform(-15, 15))

# Simple GameUI class (inline replacement)
class GameUI:
    def __init__(self, player):
        self.player = player
        self.health_text = Text(f'Health: {player.health}', position=(-0.85, 0.45), scale=2)
        self.ammo_text = Text(f'Ammo: {player.ammo[player.current_weapon]}', position=(-0.85, 0.4), scale=2)
        self.weapon_text = Text(f'Weapon: {player.current_weapon}', position=(-0.85, 0.35), scale=2)
        self.score_text = Text('Score: 0', position=(-0.85, -0.45), scale=2)
        self.death_screen = None
        self.pause_menu = None
        self.debug_info = None
        self.debug_visible = False
        
    def update(self):
        if self.player:
            self.health_text.text = f'Health: {self.player.health}'
            self.ammo_text.text = f'Ammo: {self.player.ammo[self.player.current_weapon]}'
            self.weapon_text.text = f'Weapon: {self.player.current_weapon}'
            
    def show_death_screen(self):
        if not self.death_screen:
            self.death_screen = Text('YOU DIED! Press R to respawn', position=(0, 0), scale=3, color=color.red)
            
    def hide_death_screen(self):
        if self.death_screen:
            self.death_screen.disable()
            self.death_screen = None
            
    def show_pause_menu(self):
        if not self.pause_menu:
            self.pause_menu = Text('PAUSED\nPress ESC to resume\nPress Q to quit', 
                                 position=(0, 0), scale=2, color=color.white)
                                 
    def hide_pause_menu(self):
        if self.pause_menu:
            self.pause_menu.disable()
            self.pause_menu = None
            
    def toggle_debug_info(self):
        self.debug_visible = not self.debug_visible
        if self.debug_visible and not self.debug_info:
            self.debug_info = Text('DEBUG MODE ON', position=(0.5, 0.45), scale=1.5, color=color.yellow)
        elif not self.debug_visible and self.debug_info:
            self.debug_info.disable()
            self.debug_info = None

# Simple AudioManager class (inline replacement that doesn't use audio)
class AudioManager:
    def __init__(self):
        print("AudioManager initialized (no audio files loaded)")
        
    def start_ambient_sounds(self):
        pass  # Skip audio for now
        
    def play_impact_sound(self, sound_type):
        pass  # Skip audio for now

class Game:
    def __init__(self):
        # Initialize Ursina
        self.app = Ursina(
            title=GAME_TITLE,
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            fullscreen=FULLSCREEN,
            vsync=VSYNC,
            fps_counter=SHOW_FPS
        )
        
        # Game state
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.score = 0
        self.enemies_killed = 0
        self.player_deaths = 0
        
        # Game objects
        self.player = None
        self.enemies = []
        self.bullets = []
        self.game_map = None
        self.ui = None
        self.audio_manager = None
        
        # Game settings
        self.max_enemies = 5
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 10.0
        
        # Initialize game
        self.setup_game()
        
    def setup_game(self):
        """Initialize game components"""
        # Setup audio
        self.audio_manager = AudioManager()
        
        # Setup game map
        self.game_map = GameMap()
        
        # Setup player
        self.setup_player()
        
        # Setup UI
        self.ui = GameUI(self.player)
        
        # Setup enemies
        self.spawn_initial_enemies()
        
        # Setup input handlers
        self.setup_input_handlers()
        
        # Start game
        self.start_game()
        
    def setup_player(self):
        """Setup the player character"""
        spawn_point = self.game_map.get_random_player_spawn()
        self.player = Player(position=spawn_point)
        
    def setup_input_handlers(self):
        """Setup input event handlers"""
        # Store reference to self for closures
        game_instance = self
        
        # Mouse input
        def input_handler(key):
            if key == 'escape':
                game_instance.toggle_pause()
            elif key == 'r' and game_instance.game_state == "game_over":
                game_instance.restart_game()
            elif key == 'q' and game_instance.game_state == "paused":
                game_instance.quit_game()
            elif key == 'f1':
                game_instance.ui.toggle_debug_info()
            elif key == '1':
                game_instance.player.switch_weapon(0)
            elif key == '2':
                game_instance.player.switch_weapon(1)
            elif key == '3':
                game_instance.player.switch_weapon(2)
            elif key == 'r' and game_instance.game_state == "playing":
                game_instance.player.reload_weapon()
                
        # Mouse click for shooting
        def mouse_click_handler():
            if game_instance.game_state == "playing" and game_instance.player and game_instance.player.is_alive:
                bullet = game_instance.player.fire_weapon()
                if bullet:
                    game_instance.bullets.append(bullet)
                
        # Register input handlers
        self.input_handler = input_handler
        self.mouse_click_handler = mouse_click_handler
        
    def start_game(self):
        """Start the game"""
        self.game_state = "playing"
        self.audio_manager.start_ambient_sounds()
        print("Game started!")
        
    def update(self):
        """Main game update loop"""
        if self.game_state != "playing":
            return
            
        # Update player
        if self.player and self.player.is_alive:
            self.player.update()
            
        # Update enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                enemy.update()
                
        # Update bullets
        self.update_bullets()
        
        # Update UI
        if self.ui:
            self.ui.update()
            self.ui.score_text.text = f'Score: {self.score}'
            
        # Spawn new enemies
        self.update_enemy_spawning()
        
        # Check game over conditions
        self.check_game_over()
        
    def update_bullets(self):
        """Update bullet physics and collisions"""
        bullets_to_remove = []
        
        for bullet in self.bullets[:]:  # Create a copy to iterate
            if not bullet:
                bullets_to_remove.append(bullet)
                continue
                
            # Move bullet
            if hasattr(bullet, 'velocity'):
                bullet.position += bullet.velocity * time.dt
                
            # Check bullet lifetime
            if hasattr(bullet, 'lifetime'):
                bullet.lifetime -= time.dt
                if bullet.lifetime <= 0:
                    bullets_to_remove.append(bullet)
                    continue
                    
            # Check collisions with enemies
            for enemy in self.enemies:
                if enemy.is_alive and distance(bullet.position, enemy.entity.position) < 2.0:
                    # Hit enemy
                    enemy.take_damage(25)  # Fixed damage value
                    self.audio_manager.play_impact_sound('enemy_hit')
                    
                    if not enemy.is_alive:
                        self.enemies_killed += 1
                        self.score += 100
                        
                    bullets_to_remove.append(bullet)
                    break
                    
        # Remove expired bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
            if hasattr(bullet, 'destroy'):
                bullet.destroy()
                
    def update_enemy_spawning(self):
        """Update enemy spawning system"""
        alive_enemies = [e for e in self.enemies if e.is_alive]
        if len(alive_enemies) < self.max_enemies:
            self.enemy_spawn_timer += time.dt
            if self.enemy_spawn_timer >= self.enemy_spawn_interval:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
                
    def spawn_enemy(self):
        """Spawn a new enemy"""
        spawn_point = self.game_map.get_random_enemy_spawn()
        enemy = Enemy(position=spawn_point)
        self.enemies.append(enemy)
        print(f"Spawned enemy at {spawn_point}")
        
    def spawn_initial_enemies(self):
        """Spawn initial enemies"""
        for i in range(3):
            self.spawn_enemy()
            
    def check_game_over(self):
        """Check game over conditions"""
        if self.player and not self.player.is_alive and self.game_state == "playing":
            self.game_over()
            
    def game_over(self):
        """Handle game over"""
        self.game_state = "game_over"
        self.player_deaths += 1
        
        if self.ui:
            self.ui.show_death_screen()
            
        print("Game Over!")
        print(f"Score: {self.score}")
        print(f"Enemies Killed: {self.enemies_killed}")
        print(f"Deaths: {self.player_deaths}")
        
    def restart_game(self):
        """Restart the game"""
        # Reset player
        if self.player:
            spawn_point = self.game_map.get_random_player_spawn()
            self.player.respawn(spawn_point)
            
        # Clear enemies
        for enemy in self.enemies:
            enemy.destroy()
        self.enemies.clear()
        
        # Clear bullets
        for bullet in self.bullets:
            if hasattr(bullet, 'destroy'):
                bullet.destroy()
        self.bullets.clear()
        
        # Spawn new enemies
        self.spawn_initial_enemies()
        
        # Reset UI
        if self.ui:
            self.ui.hide_death_screen()
            
        # Reset game state
        self.game_state = "playing"
        self.score = 0
        self.enemies_killed = 0
        
        print("Game restarted!")
        
    def toggle_pause(self):
        """Toggle pause state"""
        if self.game_state == "playing":
            self.game_state = "paused"
            if self.ui:
                self.ui.show_pause_menu()
            print("Game paused")
        elif self.game_state == "paused":
            self.game_state = "playing"
            if self.ui:
                self.ui.hide_pause_menu()
            print("Game resumed")
            
    def quit_game(self):
        """Quit the game"""
        print("Quitting game...")
        self.app.quit()
        
    def get_game_stats(self):
        """Get current game statistics"""
        return {
            'score': self.score,
            'enemies_killed': self.enemies_killed,
            'player_deaths': self.player_deaths,
            'player_health': self.player.health if self.player else 0,
            'enemies_alive': len([e for e in self.enemies if e.is_alive]),
            'game_state': self.game_state
        }

# Global game instance
game = None

def update():
    """Global update function called by Ursina"""
    global game
    if game:
        game.update()

def input(key):
    """Global input function called by Ursina"""
    global game
    if game and hasattr(game, 'input_handler'):
        game.input_handler(key)

def mouse_click():
    """Global mouse click function called by Ursina"""
    global game
    if game and hasattr(game, 'mouse_click_handler'):
        game.mouse_click_handler()

def main():
    """Main function to start the game"""
    global game
    print("Starting 3D Shooter Game...")
    print("Controls:")
    print("  WASD - Move")
    print("  Mouse - Look around")
    print("  Left Click - Shoot")
    print("  R - Reload")
    print("  1, 2, 3 - Switch weapons")
    print("  ESC - Pause")
    print("  F1 - Toggle debug info")
    print("  R (when dead) - Respawn")
    print("  Q (when paused) - Quit")
    
    # Create game instance
    game = Game()
    
    # Start the Ursina application
    game.app.run()

if __name__ == "__main__":
    main()