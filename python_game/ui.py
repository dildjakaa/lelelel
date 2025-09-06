"""
User Interface system for the game
"""
from ursina import *
from config import *

class GameUI:
    def __init__(self, player):
        self.player = player
        self.elements = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up all UI elements"""
        self.create_crosshair()
        self.create_health_bar()
        self.create_ammo_display()
        self.create_minimap()
        self.create_damage_overlay()
        self.create_death_screen()
        self.create_pause_menu()
        self.create_debug_info()
        
    def create_crosshair(self):
        """Create crosshair in center of screen"""
        # Center crosshair
        self.elements['crosshair'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.02, 0.02),
            color=color.white,
            position=(0, 0, 0)
        )
        
        # Crosshair lines
        self.elements['crosshair_h'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.04, 0.002),
            color=color.white,
            position=(0, 0, 0)
        )
        
        self.elements['crosshair_v'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.002, 0.04),
            color=color.white,
            position=(0, 0, 0)
        )
        
    def create_health_bar(self):
        """Create health bar display"""
        # Health bar background
        self.elements['health_bg'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.3, 0.05),
            color=color.dark_red,
            position=(-0.7, -0.4, 0)
        )
        
        # Health bar fill
        self.elements['health_fill'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.3, 0.05),
            color=color.red,
            position=(-0.7, -0.4, 0)
        )
        
        # Health text
        self.elements['health_text'] = Text(
            text="100/100",
            parent=camera.ui,
            position=(-0.55, -0.4, 0),
            scale=2,
            color=color.white
        )
        
    def create_ammo_display(self):
        """Create ammunition display"""
        # Ammo background
        self.elements['ammo_bg'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.2, 0.05),
            color=color.dark_gray,
            position=(0.6, -0.4, 0)
        )
        
        # Ammo text
        self.elements['ammo_text'] = Text(
            text="30/30",
            parent=camera.ui,
            position=(0.5, -0.4, 0),
            scale=2,
            color=color.white
        )
        
        # Weapon name
        self.elements['weapon_name'] = Text(
            text="Rifle",
            parent=camera.ui,
            position=(0.5, -0.35, 0),
            scale=1.5,
            color=color.yellow
        )
        
    def create_minimap(self):
        """Create minimap display"""
        # Minimap background
        self.elements['minimap_bg'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.2, 0.2),
            color=color.dark_gray,
            position=(0.7, 0.7, 0)
        )
        
        # Minimap border
        self.elements['minimap_border'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.21, 0.21),
            color=color.white,
            position=(0.7, 0.7, 0)
        )
        
        # Player dot on minimap
        self.elements['minimap_player'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.01, 0.01),
            color=color.green,
            position=(0.7, 0.7, 0)
        )
        
    def create_damage_overlay(self):
        """Create damage overlay effect"""
        self.elements['damage_overlay'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 2),
            color=color.red,
            alpha=0,
            position=(0, 0, 0)
        )
        
    def create_death_screen(self):
        """Create death screen"""
        # Death overlay
        self.elements['death_overlay'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 2),
            color=color.black,
            alpha=0,
            position=(0, 0, 0)
        )
        
        # Death text
        self.elements['death_text'] = Text(
            text="YOU DIED",
            parent=camera.ui,
            position=(0, 0.1, 0),
            scale=4,
            color=color.red,
            alpha=0
        )
        
        # Respawn instruction
        self.elements['respawn_text'] = Text(
            text="Press R to respawn",
            parent=camera.ui,
            position=(0, -0.1, 0),
            scale=2,
            color=color.white,
            alpha=0
        )
        
    def create_pause_menu(self):
        """Create pause menu"""
        # Pause overlay
        self.elements['pause_overlay'] = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 2),
            color=color.black,
            alpha=0.7,
            position=(0, 0, 0)
        )
        
        # Pause title
        self.elements['pause_title'] = Text(
            text="PAUSED",
            parent=camera.ui,
            position=(0, 0.2, 0),
            scale=4,
            color=color.white,
            alpha=0
        )
        
        # Resume button
        self.elements['resume_text'] = Text(
            text="Press ESC to resume",
            parent=camera.ui,
            position=(0, 0, 0),
            scale=2,
            color=color.white,
            alpha=0
        )
        
        # Quit button
        self.elements['quit_text'] = Text(
            text="Press Q to quit",
            parent=camera.ui,
            position=(0, -0.1, 0),
            scale=2,
            color=color.red,
            alpha=0
        )
        
    def create_debug_info(self):
        """Create debug information display"""
        if not DEBUG_MODE:
            return
            
        # FPS counter
        self.elements['fps_text'] = Text(
            text="FPS: 60",
            parent=camera.ui,
            position=(-0.9, 0.9, 0),
            scale=1.5,
            color=color.green
        )
        
        # Position info
        self.elements['pos_text'] = Text(
            text="Pos: (0, 0, 0)",
            parent=camera.ui,
            position=(-0.9, 0.8, 0),
            scale=1.5,
            color=color.green
        )
        
        # Health info
        self.elements['debug_health'] = Text(
            text="Health: 100",
            parent=camera.ui,
            position=(-0.9, 0.7, 0),
            scale=1.5,
            color=color.green
        )
        
    def update(self):
        """Update UI elements each frame"""
        self.update_health_display()
        self.update_ammo_display()
        self.update_minimap()
        self.update_debug_info()
        
    def update_health_display(self):
        """Update health bar and text"""
        if not self.player:
            return
            
        health_percentage = self.player.get_health_percentage()
        
        # Update health bar fill
        if 'health_fill' in self.elements:
            self.elements['health_fill'].scale_x = 0.3 * health_percentage
            
        # Update health text
        if 'health_text' in self.elements:
            self.elements['health_text'].text = f"{int(self.player.health)}/{self.player.max_health}"
            
        # Change color based on health
        if health_percentage > 0.6:
            color_val = color.green
        elif health_percentage > 0.3:
            color_val = color.yellow
        else:
            color_val = color.red
            
        if 'health_fill' in self.elements:
            self.elements['health_fill'].color = color_val
            
    def update_ammo_display(self):
        """Update ammunition display"""
        if not self.player or not self.player.current_weapon:
            return
            
        ammo_info = self.player.get_ammo_info()
        
        # Update ammo text
        if 'ammo_text' in self.elements:
            self.elements['ammo_text'].text = f"{ammo_info['current']}/{ammo_info['max']}"
            
        # Update weapon name
        if 'weapon_name' in self.elements:
            self.elements['weapon_name'].text = self.player.current_weapon.name
            
    def update_minimap(self):
        """Update minimap display"""
        if not self.player:
            return
            
        # Convert world position to minimap position
        map_bounds = MAP_SIZE
        world_pos = self.player.position
        
        # Normalize position to -1 to 1 range
        minimap_x = (world_pos.x / map_bounds) * 0.2
        minimap_z = (world_pos.z / map_bounds) * 0.2
        
        # Update player dot position
        if 'minimap_player' in self.elements:
            self.elements['minimap_player'].position = (0.7 + minimap_x, 0.7 + minimap_z, 0)
            
    def update_debug_info(self):
        """Update debug information"""
        if not DEBUG_MODE or not self.player:
            return
            
        # Update FPS
        if 'fps_text' in self.elements:
            fps = int(1 / time.dt) if time.dt > 0 else 0
            self.elements['fps_text'].text = f"FPS: {fps}"
            
        # Update position
        if 'pos_text' in self.elements:
            pos = self.player.position
            self.elements['pos_text'].text = f"Pos: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})"
            
        # Update health
        if 'debug_health' in self.elements:
            self.elements['debug_health'].text = f"Health: {int(self.player.health)}"
            
    def show_damage_effect(self):
        """Show damage overlay effect"""
        if 'damage_overlay' in self.elements:
            self.elements['damage_overlay'].alpha = 0.5
            self.elements['damage_overlay'].animate('alpha', 0, duration=0.3)
            
    def show_death_screen(self):
        """Show death screen"""
        if 'death_overlay' in self.elements:
            self.elements['death_overlay'].alpha = 0.8
        if 'death_text' in self.elements:
            self.elements['death_text'].alpha = 1
        if 'respawn_text' in self.elements:
            self.elements['respawn_text'].alpha = 1
            
    def hide_death_screen(self):
        """Hide death screen"""
        if 'death_overlay' in self.elements:
            self.elements['death_overlay'].alpha = 0
        if 'death_text' in self.elements:
            self.elements['death_text'].alpha = 0
        if 'respawn_text' in self.elements:
            self.elements['respawn_text'].alpha = 0
            
    def show_pause_menu(self):
        """Show pause menu"""
        if 'pause_overlay' in self.elements:
            self.elements['pause_overlay'].alpha = 0.7
        if 'pause_title' in self.elements:
            self.elements['pause_title'].alpha = 1
        if 'resume_text' in self.elements:
            self.elements['resume_text'].alpha = 1
        if 'quit_text' in self.elements:
            self.elements['quit_text'].alpha = 1
            
    def hide_pause_menu(self):
        """Hide pause menu"""
        if 'pause_overlay' in self.elements:
            self.elements['pause_overlay'].alpha = 0
        if 'pause_title' in self.elements:
            self.elements['pause_title'].alpha = 0
        if 'resume_text' in self.elements:
            self.elements['resume_text'].alpha = 0
        if 'quit_text' in self.elements:
            self.elements['quit_text'].alpha = 0
            
    def toggle_debug_info(self):
        """Toggle debug information display"""
        global DEBUG_MODE
        DEBUG_MODE = not DEBUG_MODE
        
        if DEBUG_MODE:
            self.create_debug_info()
        else:
            if 'fps_text' in self.elements:
                self.elements['fps_text'].destroy()
            if 'pos_text' in self.elements:
                self.elements['pos_text'].destroy()
            if 'debug_health' in self.elements:
                self.elements['debug_health'].destroy()
