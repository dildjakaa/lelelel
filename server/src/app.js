/**
 * Main server application for 3D Shooter Multiplayer Game
 * Optimized for Render.com deployment
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const morgan = require('morgan');
const path = require('path');
require('dotenv').config();

// Import game modules
const GameManager = require('./game');
const PlayerManager = require('./player');
const RoomManager = require('./room');
const AntiCheat = require('./anti-cheat');
const Logger = require('./logger');

class GameServer {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: {
                origin: process.env.CORS_ORIGIN || "*",
                methods: ["GET", "POST"],
                credentials: process.env.CORS_CREDENTIALS === 'true'
            },
            transports: ['websocket', 'polling']
        });
        
        // Configuration
        this.port = process.env.PORT || process.env.RENDER_PORT || 3000;
        this.host = process.env.HOST || '0.0.0.0';
        this.nodeEnv = process.env.NODE_ENV || 'development';
        
        // Game managers
        this.gameManager = new GameManager();
        this.playerManager = new PlayerManager();
        this.roomManager = new RoomManager();
        this.antiCheat = new AntiCheat();
        this.logger = new Logger();
        
        // Server state
        this.isShuttingDown = false;
        this.connectedClients = new Map();
        
        // Initialize server
        this.setupMiddleware();
        this.setupRoutes();
        this.setupSocketHandlers();
        this.setupGameLoop();
        this.setupGracefulShutdown();
        
        this.logger.info('Server initialized successfully');
    }
    
    setupMiddleware() {
        // Security middleware
        this.app.use(helmet({
            contentSecurityPolicy: false, // Disable for WebSocket compatibility
            crossOriginEmbedderPolicy: false
        }));
        
        // CORS
        this.app.use(cors({
            origin: process.env.CORS_ORIGIN || "*",
            credentials: process.env.CORS_CREDENTIALS === 'true'
        }));
        
        // Compression
        this.app.use(compression());
        
        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
        
        // Logging
        if (this.nodeEnv === 'development') {
            this.app.use(morgan('dev'));
        } else {
            this.app.use(morgan('combined'));
        }
        
        // Rate limiting
        const limiter = rateLimit({
            windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15 minutes
            max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
            message: 'Too many requests from this IP, please try again later.',
            standardHeaders: true,
            legacyHeaders: false
        });
        this.app.use('/api/', limiter);
    }
    
    setupRoutes() {
        // Health check endpoint
        this.app.get('/health', (req, res) => {
            res.status(200).json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                players: this.playerManager.getPlayerCount(),
                rooms: this.roomManager.getRoomCount()
            });
        });
        
        // Server info endpoint
        this.app.get('/api/info', (req, res) => {
            res.json({
                name: '3D Shooter Multiplayer Server',
                version: '1.0.0',
                maxPlayersPerRoom: parseInt(process.env.MAX_PLAYERS_PER_ROOM) || 8,
                maxRooms: parseInt(process.env.MAX_ROOMS) || 10,
                gameTickRate: parseInt(process.env.GAME_TICK_RATE) || 60
            });
        });
        
        // Player statistics
        this.app.get('/api/stats', (req, res) => {
            res.json({
                totalPlayers: this.playerManager.getPlayerCount(),
                activeRooms: this.roomManager.getRoomCount(),
                serverUptime: process.uptime(),
                memoryUsage: process.memoryUsage()
            });
        });
        
        // Room list
        this.app.get('/api/rooms', (req, res) => {
            const rooms = this.roomManager.getAllRooms().map(room => ({
                id: room.id,
                name: room.name,
                playerCount: room.players.size,
                maxPlayers: room.maxPlayers,
                gameMode: room.gameMode,
                isPrivate: room.isPrivate
            }));
            res.json(rooms);
        });
        
        // Player authentication (placeholder)
        this.app.post('/api/auth/login', (req, res) => {
            const { username, password } = req.body;
            
            // Simple authentication (implement proper auth in production)
            if (username && password) {
                const token = this.playerManager.generatePlayerToken(username);
                res.json({
                    success: true,
                    token,
                    playerId: username
                });
            } else {
                res.status(400).json({
                    success: false,
                    message: 'Invalid credentials'
                });
            }
        });
        
        // Serve static files (for web client)
        this.app.use(express.static(path.join(__dirname, '../public')));
        
        // 404 handler
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Not found',
                message: 'The requested resource was not found'
            });
        });
        
        // Error handler
        this.app.use((err, req, res, next) => {
            this.logger.error('Express error:', err);
            res.status(500).json({
                error: 'Internal server error',
                message: this.nodeEnv === 'development' ? err.message : 'Something went wrong'
            });
        });
    }
    
    setupSocketHandlers() {
        this.io.on('connection', (socket) => {
            this.logger.info(`Client connected: ${socket.id}`);
            
            // Store client connection
            this.connectedClients.set(socket.id, {
                socket,
                playerId: null,
                roomId: null,
                lastActivity: Date.now()
            });
            
            // Player authentication
            socket.on('authenticate', (data) => {
                this.handleAuthentication(socket, data);
            });
            
            // Room management
            socket.on('join_room', (data) => {
                this.handleJoinRoom(socket, data);
            });
            
            socket.on('leave_room', () => {
                this.handleLeaveRoom(socket);
            });
            
            socket.on('create_room', (data) => {
                this.handleCreateRoom(socket, data);
            });
            
            // Game events
            socket.on('player_move', (data) => {
                this.handlePlayerMove(socket, data);
            });
            
            socket.on('player_rotate', (data) => {
                this.handlePlayerRotate(socket, data);
            });
            
            socket.on('player_shoot', (data) => {
                this.handlePlayerShoot(socket, data);
            });
            
            socket.on('player_reload', () => {
                this.handlePlayerReload(socket);
            });
            
            socket.on('player_damage', (data) => {
                this.handlePlayerDamage(socket, data);
            });
            
            // Disconnection
            socket.on('disconnect', () => {
                this.handleDisconnect(socket);
            });
            
            // Ping/Pong for connection health
            socket.on('ping', () => {
                socket.emit('pong');
            });
        });
    }
    
    handleAuthentication(socket, data) {
        const { playerId, token } = data;
        
        if (!playerId) {
            socket.emit('auth_error', { message: 'Player ID required' });
            return;
        }
        
        // Simple token validation (implement proper JWT validation in production)
        const client = this.connectedClients.get(socket.id);
        if (client) {
            client.playerId = playerId;
            client.lastActivity = Date.now();
            
            socket.emit('authenticated', { playerId });
            this.logger.info(`Player authenticated: ${playerId}`);
        }
    }
    
    handleJoinRoom(socket, data) {
        const { roomId } = data;
        const client = this.connectedClients.get(socket.id);
        
        if (!client || !client.playerId) {
            socket.emit('error', { message: 'Not authenticated' });
            return;
        }
        
        const room = this.roomManager.getRoom(roomId);
        if (!room) {
            socket.emit('error', { message: 'Room not found' });
            return;
        }
        
        if (room.players.size >= room.maxPlayers) {
            socket.emit('error', { message: 'Room is full' });
            return;
        }
        
        // Leave current room if any
        if (client.roomId) {
            this.handleLeaveRoom(socket);
        }
        
        // Join new room
        const success = this.roomManager.addPlayerToRoom(roomId, client.playerId, socket);
        if (success) {
            client.roomId = roomId;
            socket.join(roomId);
            
            // Notify room about new player
            socket.to(roomId).emit('player_joined', {
                playerId: client.playerId,
                playerCount: room.players.size
            });
            
            // Send room state to new player
            socket.emit('room_joined', {
                roomId,
                players: Array.from(room.players.keys()),
                gameState: room.gameState
            });
            
            this.logger.info(`Player ${client.playerId} joined room ${roomId}`);
        } else {
            socket.emit('error', { message: 'Failed to join room' });
        }
    }
    
    handleLeaveRoom(socket) {
        const client = this.connectedClients.get(socket.id);
        if (!client || !client.roomId) return;
        
        const roomId = client.roomId;
        const room = this.roomManager.getRoom(roomId);
        
        if (room) {
            this.roomManager.removePlayerFromRoom(roomId, client.playerId);
            socket.leave(roomId);
            
            // Notify room about player leaving
            socket.to(roomId).emit('player_left', {
                playerId: client.playerId,
                playerCount: room.players.size
            });
            
            this.logger.info(`Player ${client.playerId} left room ${roomId}`);
        }
        
        client.roomId = null;
    }
    
    handleCreateRoom(socket, data) {
        const { roomName, maxPlayers, gameMode, isPrivate } = data;
        const client = this.connectedClients.get(socket.id);
        
        if (!client || !client.playerId) {
            socket.emit('error', { message: 'Not authenticated' });
            return;
        }
        
        const roomId = this.roomManager.createRoom({
            name: roomName || `Room ${Date.now()}`,
            maxPlayers: maxPlayers || 8,
            gameMode: gameMode || 'deathmatch',
            isPrivate: isPrivate || false,
            createdBy: client.playerId
        });
        
        if (roomId) {
            // Auto-join the created room
            this.handleJoinRoom(socket, { roomId });
            socket.emit('room_created', { roomId, roomName: roomName || `Room ${Date.now()}` });
        } else {
            socket.emit('error', { message: 'Failed to create room' });
        }
    }
    
    handlePlayerMove(socket, data) {
        const client = this.connectedClients.get(socket.id);
        if (!client || !client.roomId) return;
        
        // Anti-cheat validation
        if (!this.antiCheat.validateMovement(data)) {
            this.logger.warn(`Invalid movement from player ${client.playerId}`);
            return;
        }
        
        // Update player position in room
        const room = this.roomManager.getRoom(client.roomId);
        if (room) {
            room.updatePlayerPosition(client.playerId, data);
            
            // Broadcast to other players in room
            socket.to(client.roomId).emit('player_moved', {
                playerId: client.playerId,
                position: data.position,
                timestamp: Date.now()
            });
        }
    }
    
    handlePlayerRotate(socket, data) {
        const client = this.connectedClients.get(socket.id);
        if (!client || !client.roomId) return;
        
        const room = this.roomManager.getRoom(client.roomId);
        if (room) {
            room.updatePlayerRotation(client.playerId, data);
            
            // Broadcast to other players in room
            socket.to(client.roomId).emit('player_rotated', {
                playerId: client.playerId,
                rotation: data.rotation,
                timestamp: Date.now()
            });
        }
    }
    
    handlePlayerShoot(socket, data) {
        const client = this.connectedClients.get(socket.id);
        if (!client || !client.roomId) return;
        
        // Anti-cheat validation
        if (!this.antiCheat.validateShooting(client.playerId, data)) {
            this.logger.warn(`Invalid shooting from player ${client.playerId}`);
            return;
        }
        
        const room = this.roomManager.getRoom(client.roomId);
        if (room) {
            // Process shot and check for hits
            const hitResult = room.processShot(client.playerId, data);
            
            // Broadcast shot to all players in room
            socket.to(client.roomId).emit('player_shot', {
                playerId: client.playerId,
                shotData: data,
                hitResult,
                timestamp: Date.now()
            });
            
            // Send hit confirmation to shooter
            if (hitResult.hit) {
                socket.emit('shot_hit', hitResult);
            }
        }
    }
    
    handlePlayerReload(socket) {
        const client = this.connectedClients.get(socket.id);
        if (!client || !client.roomId) return;
        
        const room = this.roomManager.getRoom(client.roomId);
        if (room) {
            room.reloadPlayerWeapon(client.playerId);
            
            // Broadcast reload to other players
            socket.to(client.roomId).emit('player_reloaded', {
                playerId: client.playerId,
                timestamp: Date.now()
            });
        }
    }
    
    handlePlayerDamage(socket, data) {
        const client = this.connectedClients.get(socket.id);
        if (!client || !client.roomId) return;
        
        const room = this.roomManager.getRoom(client.roomId);
        if (room) {
            const damageResult = room.processDamage(client.playerId, data);
            
            if (damageResult) {
                // Broadcast damage to all players
                this.io.to(client.roomId).emit('player_damaged', {
                    targetId: data.targetId,
                    damage: damageResult.damage,
                    newHealth: damageResult.newHealth,
                    isDead: damageResult.isDead,
                    timestamp: Date.now()
                });
            }
        }
    }
    
    handleDisconnect(socket) {
        const client = this.connectedClients.get(socket.id);
        if (client) {
            this.logger.info(`Client disconnected: ${socket.id}`);
            
            // Leave room if in one
            if (client.roomId) {
                this.handleLeaveRoom(socket);
            }
            
            // Remove from connected clients
            this.connectedClients.delete(socket.id);
        }
    }
    
    setupGameLoop() {
        const tickRate = parseInt(process.env.GAME_TICK_RATE) || 60;
        const tickInterval = 1000 / tickRate;
        
        setInterval(() => {
            if (!this.isShuttingDown) {
                this.gameManager.update();
                this.roomManager.updateAllRooms();
            }
        }, tickInterval);
        
        this.logger.info(`Game loop started at ${tickRate} FPS`);
    }
    
    setupGracefulShutdown() {
        const shutdown = (signal) => {
            this.logger.info(`Received ${signal}, shutting down gracefully...`);
            this.isShuttingDown = true;
            
            // Notify all clients
            this.io.emit('server_shutdown', {
                message: 'Server is shutting down',
                timestamp: Date.now()
            });
            
            // Close server after delay
            setTimeout(() => {
                this.server.close(() => {
                    this.logger.info('Server closed');
                    process.exit(0);
                });
            }, 5000);
        };
        
        process.on('SIGTERM', () => shutdown('SIGTERM'));
        process.on('SIGINT', () => shutdown('SIGINT'));
    }
    
    start() {
        this.server.listen(this.port, this.host, () => {
            this.logger.info(`Server running on ${this.host}:${this.port}`);
            this.logger.info(`Environment: ${this.nodeEnv}`);
            this.logger.info(`Max players per room: ${process.env.MAX_PLAYERS_PER_ROOM || 8}`);
            this.logger.info(`Max rooms: ${process.env.MAX_ROOMS || 10}`);
        });
    }
}

// Start server
const server = new GameServer();
server.start();

module.exports = GameServer;
