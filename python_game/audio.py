"""
Audio system for the game
"""
from ursina import *
import os
from config import *

class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.music = {}
        self.master_volume = MASTER_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.music_volume = MUSIC_VOLUME
        
        # Load audio files
        self.load_audio_files()
        
    def load_audio_files(self):
        """Load all audio files"""
        # Create placeholder sounds if files don't exist
        self.create_placeholder_sounds()
        
    def create_placeholder_sounds(self):
        """Create placeholder sounds for testing"""
        # Footstep sounds
        self.sounds['footstep_1'] = Audio('', loop=False, autoplay=False)
        self.sounds['footstep_2'] = Audio('', loop=False, autoplay=False)
        self.sounds['footstep_3'] = Audio('', loop=False, autoplay=False)
        
        # Weapon sounds
        self.sounds['pistol_fire'] = Audio('', loop=False, autoplay=False)
        self.sounds['rifle_fire'] = Audio('', loop=False, autoplay=False)
        self.sounds['shotgun_fire'] = Audio('', loop=False, autoplay=False)
        self.sounds['reload'] = Audio('', loop=False, autoplay=False)
        self.sounds['empty_gun'] = Audio('', loop=False, autoplay=False)
        
        # Impact sounds
        self.sounds['bullet_impact'] = Audio('', loop=False, autoplay=False)
        self.sounds['enemy_hit'] = Audio('', loop=False, autoplay=False)
        self.sounds['player_hit'] = Audio('', loop=False, autoplay=False)
        
        # UI sounds
        self.sounds['button_click'] = Audio('', loop=False, autoplay=False)
        self.sounds['menu_open'] = Audio('', loop=False, autoplay=False)
        self.sounds['menu_close'] = Audio('', loop=False, autoplay=False)
        
        # Ambient sounds
        self.sounds['wind'] = Audio('', loop=True, autoplay=False)
        self.sounds['ambient'] = Audio('', loop=True, autoplay=False)
        
    def play_sound(self, sound_name, volume=1.0, pitch=1.0):
        """Play a sound effect"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.volume = volume * self.sfx_volume * self.master_volume
            sound.pitch = pitch
            sound.play()
            
    def play_music(self, music_name, volume=1.0, loop=True):
        """Play background music"""
        if music_name in self.music:
            music = self.music[music_name]
            music.volume = volume * self.music_volume * self.master_volume
            music.loop = loop
            music.play()
            
    def stop_music(self, music_name):
        """Stop background music"""
        if music_name in self.music:
            self.music[music_name].stop()
            
    def stop_all_music(self):
        """Stop all background music"""
        for music in self.music.values():
            music.stop()
            
    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        
    def play_footstep(self):
        """Play random footstep sound"""
        footstep_sounds = ['footstep_1', 'footstep_2', 'footstep_3']
        sound_name = random.choice(footstep_sounds)
        self.play_sound(sound_name, volume=0.5)
        
    def play_weapon_fire(self, weapon_type):
        """Play weapon fire sound"""
        if weapon_type == 'pistol':
            self.play_sound('pistol_fire', volume=0.8)
        elif weapon_type == 'rifle':
            self.play_sound('rifle_fire', volume=0.9)
        elif weapon_type == 'shotgun':
            self.play_sound('shotgun_fire', volume=1.0)
            
    def play_reload_sound(self):
        """Play weapon reload sound"""
        self.play_sound('reload', volume=0.7)
        
    def play_empty_gun_sound(self):
        """Play empty gun sound"""
        self.play_sound('empty_gun', volume=0.6)
        
    def play_impact_sound(self, impact_type):
        """Play impact sound"""
        if impact_type == 'bullet':
            self.play_sound('bullet_impact', volume=0.6)
        elif impact_type == 'enemy_hit':
            self.play_sound('enemy_hit', volume=0.7)
        elif impact_type == 'player_hit':
            self.play_sound('player_hit', volume=0.8)
            
    def play_ui_sound(self, ui_action):
        """Play UI sound"""
        if ui_action == 'button_click':
            self.play_sound('button_click', volume=0.5)
        elif ui_action == 'menu_open':
            self.play_sound('menu_open', volume=0.6)
        elif ui_action == 'menu_close':
            self.play_sound('menu_close', volume=0.6)
            
    def start_ambient_sounds(self):
        """Start ambient background sounds"""
        self.play_music('wind', volume=0.3)
        self.play_music('ambient', volume=0.2)
        
    def stop_ambient_sounds(self):
        """Stop ambient background sounds"""
        self.stop_music('wind')
        self.stop_music('ambient')
        
    def create_3d_sound(self, sound_name, position, max_distance=10.0):
        """Create a 3D positioned sound"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            # Ursina doesn't have built-in 3D audio, but we can simulate it
            # by adjusting volume based on distance from camera
            camera_pos = camera.position
            distance = distance(camera_pos, position)
            
            if distance <= max_distance:
                volume_factor = 1.0 - (distance / max_distance)
                self.play_sound(sound_name, volume=volume_factor)
                
    def play_explosion_sound(self, position):
        """Play explosion sound at 3D position"""
        self.create_3d_sound('bullet_impact', position, max_distance=20.0)
        
    def play_weapon_fire_3d(self, weapon_type, position):
        """Play weapon fire sound at 3D position"""
        sound_name = f"{weapon_type}_fire"
        self.create_3d_sound(sound_name, position, max_distance=15.0)
        
    def update_audio_settings(self):
        """Update audio settings from config"""
        self.master_volume = MASTER_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.music_volume = MUSIC_VOLUME
        
    def get_audio_info(self):
        """Get current audio settings"""
        return {
            'master_volume': self.master_volume,
            'sfx_volume': self.sfx_volume,
            'music_volume': self.music_volume,
            'loaded_sounds': list(self.sounds.keys()),
            'loaded_music': list(self.music.keys())
        }
