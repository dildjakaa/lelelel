#!/bin/bash

# 3D Shooter Game Setup Script
echo "Setting up 3D Shooter Game Project..."

# Create necessary directories
mkdir -p python_game/assets/sounds
mkdir -p python_game/assets/models
mkdir -p python_game/assets/textures
mkdir -p server/logs

# Set up Python game
echo "Setting up Python game..."
cd python_game

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip3 and try again."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

cd ..

# Set up Node.js server
echo "Setting up Node.js server..."
cd server

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is required but not installed. Please install Node.js 18+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "npm is required but not installed. Please install npm and try again."
    exit 1
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp env.example .env
    echo "Please edit .env file with your configuration before running the server."
fi

cd ..

# Make scripts executable
chmod +x setup.sh

echo ""
echo "Setup complete!"
echo ""
echo "To run the Python game:"
echo "  cd python_game"
echo "  python3 main.py"
echo ""
echo "To run the Node.js server:"
echo "  cd server"
echo "  npm start"
echo ""
echo "To run the server in development mode:"
echo "  cd server"
echo "  npm run dev"
echo ""
echo "For Render.com deployment:"
echo "  1. Push this repository to GitHub"
echo "  2. Connect your GitHub repository to Render.com"
echo "  3. Create a new Web Service using this repository"
echo "  4. Set environment variables in Render dashboard"
echo "  5. Deploy!"
echo ""
echo "Game Controls:"
echo "  WASD - Move"
echo "  Mouse - Look around"
echo "  Left Click - Shoot"
echo "  R - Reload"
echo "  1, 2, 3 - Switch weapons"
echo "  ESC - Pause"
echo "  F1 - Toggle debug info"
echo ""
echo "Enjoy your 3D Shooter Game!"
