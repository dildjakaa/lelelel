"""
Main game file - 3D Shooter Game with Ursina Engine
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import time

# Import game modules
from config import *
from player import Player
from enemy import Enemy
from weapon import Pistol, Rifle, Shotgun
from map import GameMap
from ui import GameUI
from audio import AudioManager

class Game:
    def __init__(self):
        # Initialize Ursina
        app = Ursina(
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
        
        # Add weapons
        pistol = Pistol()
        rifle = Rifle()
        shotgun = Shotgun()
        
        self.player.add_weapon(pistol)
        self.player.add_weapon(rifle)
        self.player.add_weapon(shotgun)
        
        # Set default weapon
        self.player.current_weapon = rifle
        
    def setup_input_handlers(self):
        """Setup input event handlers"""
        # Mouse input
        def input(key):
            if key == 'escape':
                self.toggle_pause()
            elif key == 'r' and self.game_state == "game_over":
                self.restart_game()
            elif key == 'q' and self.game_state == "paused":
                self.quit_game()
            elif key == 'f1':
                self.ui.toggle_debug_info()
            elif key == '1':
                self.player.switch_weapon(0)
            elif key == '2':
                self.player.switch_weapon(1)
            elif key == '3':
                self.player.switch_weapon(2)
            elif key == 'reload':
                self.player.reload_weapon()
                
        # Mouse click for shooting
        def mouse_click():
            if self.game_state == "playing" and self.player and self.player.is_alive:
                self.player.fire_weapon()
                
        # Register input handlers
        self.input_handler = input
        self.mouse_click_handler = mouse_click
        
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
            
        # Spawn new enemies
        self.update_enemy_spawning()
        
        # Check game over conditions
        self.check_game_over()
        
    def update_bullets(self):
        """Update bullet physics and collisions"""
        bullets_to_remove = []
        
        for bullet in self.bullets:
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
                if enemy.is_alive and distance(bullet.position, enemy.position) < 1.0:
                    # Hit enemy
                    enemy.take_damage(self.player.current_weapon.damage)
                    self.audio_manager.play_impact_sound('enemy_hit')
                    
                    if not enemy.is_alive:
                        self.enemies_killed += 1
                        self.score += 100
                        
                    bullets_to_remove.append(bullet)
                    break
                    
            # Check collisions with walls
            hit_info = raycast(bullet.position, bullet.velocity.normalized(), 
                             bullet.velocity.length() * time.dt, ignore=[self.player])
            if hit_info.hit:
                bullets_to_remove.append(bullet)
                self.audio_manager.play_impact_sound('bullet')
                
        # Remove expired bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
            if hasattr(bullet, 'destroy'):
                bullet.destroy()
                
    def update_enemy_spawning(self):
        """Update enemy spawning system"""
        if len(self.enemies) < self.max_enemies:
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
            if hasattr(enemy, 'destroy'):
                enemy.destroy()
        self.enemies.clear()
        
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
        application.quit()
        
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
    if game and game.input_handler:
        game.input_handler(key)

def mouse_click():
    """Global mouse click function called by Ursina"""
    global game
    if game and game.mouse_click_handler:
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
    app.run()

if __name__ == "__main__":
    main()
