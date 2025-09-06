"""
Game configuration settings
"""
import os

# Game Settings
GAME_TITLE = "3D Shooter Game"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FULLSCREEN = False
VSYNC = True
FPS = 60

# Player Settings
PLAYER_SPEED = 5.0
MOUSE_SENSITIVITY = 1.0
JUMP_FORCE = 8.0
GRAVITY = -20.0
PLAYER_HEALTH = 100

# Camera Settings
CAMERA_FOV = 90
CAMERA_NEAR = 0.1
CAMERA_FAR = 1000.0

# Enemy Settings
ENEMY_SPEED = 3.0
ENEMY_HEALTH = 50
ENEMY_DAMAGE = 10
ENEMY_DETECTION_RANGE = 15.0
ENEMY_ATTACK_RANGE = 2.0
ENEMY_ATTACK_COOLDOWN = 2.0

# Weapon Settings
DEFAULT_WEAPON_DAMAGE = 25
DEFAULT_WEAPON_RANGE = 50.0
DEFAULT_WEAPON_FIRE_RATE = 0.5
DEFAULT_WEAPON_AMMO = 30

# Map Settings
MAP_SIZE = 50
MAP_HEIGHT = 10
WALL_HEIGHT = 3.0

# Audio Settings
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.5

# Debug Settings
DEBUG_MODE = False
SHOW_WIREFRAME = False
SHOW_COLLISION_BOXES = False
SHOW_FPS = True

# File Paths
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
SOUNDS_PATH = os.path.join(ASSETS_PATH, "sounds")
MODELS_PATH = os.path.join(ASSETS_PATH, "models")
TEXTURES_PATH = os.path.join(ASSETS_PATH, "textures")

# Create assets directories if they don't exist
os.makedirs(SOUNDS_PATH, exist_ok=True)
os.makedirs(MODELS_PATH, exist_ok=True)
os.makedirs(TEXTURES_PATH, exist_ok=True)
