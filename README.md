# 3D Shooter Game Project

This project contains both a Python 3D shooter game using Ursina engine and a Node.js multiplayer server for Render.com deployment.

## Project Structure

```
game/
├── python_game/          # Python 3D shooter with Ursina
│   ├── main.py           # Main game entry point
│   ├── config.py         # Game configuration
│   ├── player.py         # Player character class
│   ├── enemy.py          # AI enemy class
│   ├── weapon.py         # Weapon system
│   ├── map.py            # 3D map generation
│   ├── ui.py             # User interface
│   ├── audio.py          # Sound system
│   └── requirements.txt  # Python dependencies
├── server/               # Node.js multiplayer server
│   ├── src/
│   │   ├── app.js        # Main server application
│   │   ├── game.js       # Game logic and state management
│   │   ├── player.js     # Player management
│   │   ├── room.js       # Room/lobby system
│   │   └── anti-cheat.js # Anti-cheat measures
│   ├── package.json      # Node.js dependencies
│   ├── Dockerfile        # Docker configuration
│   └── .env.example      # Environment variables template
└── README.md             # This file
```

## Quick Start

### Python Game
1. Install dependencies: `pip install -r python_game/requirements.txt`
2. Run the game: `python python_game/main.py`

### Node.js Server
1. Install dependencies: `cd server && npm install`
2. Copy `.env.example` to `.env` and configure
3. Run server: `npm start`

## Features

### Python Game
- First-person 3D shooter with Ursina engine
- Smooth camera controls and WASD movement
- AI enemies with pathfinding
- Health system and UI
- Modular weapon system
- Sound effects and particle systems

### Node.js Server
- Real-time multiplayer with Socket.io
- Player authentication and session management
- Room/lobby system
- Anti-cheat validation
- Optimized for Render.com deployment
