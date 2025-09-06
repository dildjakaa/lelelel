/**
 * Player management and authentication
 */

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');

class PlayerManager {
    constructor() {
        this.players = new Map();
        this.sessions = new Map();
        this.jwtSecret = process.env.JWT_SECRET || 'default-secret-key';
        this.bcryptRounds = parseInt(process.env.BCRYPT_ROUNDS) || 12;
        
        // Player statistics
        this.stats = {
            totalConnections: 0,
            activePlayers: 0,
            totalKills: 0,
            totalDeaths: 0
        };
    }
    
    createPlayer(playerData) {
        const playerId = playerData.playerId || uuidv4();
        const currentTime = Date.now();
        
        const player = {
            playerId,
            username: playerData.username || `Player_${playerId.substring(0, 8)}`,
            email: playerData.email || null,
            password: playerData.password ? this.hashPassword(playerData.password) : null,
            isOnline: false,
            lastSeen: currentTime,
            createdAt: currentTime,
            
            // Game stats
            stats: {
                kills: 0,
                deaths: 0,
                wins: 0,
                losses: 0,
                totalPlayTime: 0,
                level: 1,
                experience: 0
            },
            
            // Current session data
            currentRoom: null,
            socketId: null,
            lastActivity: currentTime,
            
            // Game state
            position: { x: 0, y: 1, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            health: 100,
            maxHealth: 100,
            isAlive: true,
            currentWeapon: 'rifle',
            ammo: 30,
            lastShotTime: 0,
            canShoot: true,
            team: null,
            
            // Anti-cheat data
            lastPosition: { x: 0, y: 1, z: 0 },
            lastPositionTime: currentTime,
            movementHistory: [],
            shotHistory: []
        };
        
        this.players.set(playerId, player);
        this.stats.totalConnections++;
        
        return player;
    }
    
    getPlayer(playerId) {
        return this.players.get(playerId);
    }
    
    updatePlayer(playerId, updates) {
        const player = this.players.get(playerId);
        if (!player) return false;
        
        Object.assign(player, updates);
        player.lastActivity = Date.now();
        
        return true;
    }
    
    authenticatePlayer(credentials) {
        const { username, password, playerId } = credentials;
        
        // Find player by username or playerId
        let player = null;
        for (const [id, p] of this.players) {
            if (p.username === username || id === playerId) {
                player = p;
                break;
            }
        }
        
        if (!player) {
            // Create new player if not found
            player = this.createPlayer({ username, password });
        }
        
        // Verify password if provided
        if (password && player.password) {
            if (!this.verifyPassword(password, player.password)) {
                return { success: false, message: 'Invalid password' };
            }
        }
        
        // Generate session token
        const token = this.generatePlayerToken(player.playerId);
        
        return {
            success: true,
            player,
            token
        };
    }
    
    generatePlayerToken(playerId) {
        const payload = {
            playerId,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
        };
        
        return jwt.sign(payload, this.jwtSecret);
    }
    
    verifyToken(token) {
        try {
            const decoded = jwt.verify(token, this.jwtSecret);
            return { valid: true, playerId: decoded.playerId };
        } catch (error) {
            return { valid: false, error: error.message };
        }
    }
    
    startPlayerSession(playerId, socketId) {
        const player = this.players.get(playerId);
        if (!player) return false;
        
        player.isOnline = true;
        player.socketId = socketId;
        player.lastActivity = Date.now();
        
        this.sessions.set(socketId, playerId);
        this.stats.activePlayers++;
        
        return true;
    }
    
    endPlayerSession(socketId) {
        const playerId = this.sessions.get(socketId);
        if (!playerId) return false;
        
        const player = this.players.get(playerId);
        if (player) {
            player.isOnline = false;
            player.socketId = null;
            player.lastSeen = Date.now();
            
            // Update total play time
            if (player.sessionStartTime) {
                const sessionTime = Date.now() - player.sessionStartTime;
                player.stats.totalPlayTime += sessionTime;
            }
        }
        
        this.sessions.delete(socketId);
        this.stats.activePlayers = Math.max(0, this.stats.activePlayers - 1);
        
        return true;
    }
    
    updatePlayerPosition(playerId, position) {
        const player = this.players.get(playerId);
        if (!player) return false;
        
        // Store previous position for anti-cheat
        player.lastPosition = { ...player.position };
        player.lastPositionTime = Date.now();
        
        // Update current position
        player.position = position;
        player.lastActivity = Date.now();
        
        // Add to movement history for anti-cheat
        player.movementHistory.push({
            position: { ...position },
            timestamp: Date.now()
        });
        
        // Keep only last 10 movements
        if (player.movementHistory.length > 10) {
            player.movementHistory.shift();
        }
        
        return true;
    }
    
    updatePlayerRotation(playerId, rotation) {
        const player = this.players.get(playerId);
        if (!player) return false;
        
        player.rotation = rotation;
        player.lastActivity = Date.now();
        
        return true;
    }
    
    updatePlayerHealth(playerId, health) {
        const player = this.players.get(playerId);
        if (!player) return false;
        
        player.health = Math.max(0, Math.min(player.maxHealth, health));
        player.isAlive = player.health > 0;
        player.lastActivity = Date.now();
        
        return true;
    }
    
    updatePlayerWeapon(playerId, weaponType, ammo) {
        const player = this.players.get(playerId);
        if (!player) return false;
        
        player.currentWeapon = weaponType;
        player.ammo = ammo;
        player.lastActivity = Date.now();
        
        return true;
    }
    
    recordKill(killerId, victimId) {
        const killer = this.players.get(killerId);
        const victim = this.players.get(victimId);
        
        if (killer) {
            killer.stats.kills++;
            killer.stats.experience += 10;
            this.checkLevelUp(killer);
        }
        
        if (victim) {
            victim.stats.deaths++;
        }
        
        this.stats.totalKills++;
        this.stats.totalDeaths++;
    }
    
    recordWin(playerId) {
        const player = this.players.get(playerId);
        if (player) {
            player.stats.wins++;
            player.stats.experience += 50;
            this.checkLevelUp(player);
        }
    }
    
    recordLoss(playerId) {
        const player = this.players.get(playerId);
        if (player) {
            player.stats.losses++;
        }
    }
    
    checkLevelUp(player) {
        const requiredExp = player.stats.level * 100;
        if (player.stats.experience >= requiredExp) {
            player.stats.level++;
            player.stats.experience -= requiredExp;
            return true;
        }
        return false;
    }
    
    getPlayerStats(playerId) {
        const player = this.players.get(playerId);
        if (!player) return null;
        
        return {
            playerId: player.playerId,
            username: player.username,
            level: player.stats.level,
            experience: player.stats.experience,
            kills: player.stats.kills,
            deaths: player.stats.deaths,
            wins: player.stats.wins,
            losses: player.stats.losses,
            totalPlayTime: player.stats.totalPlayTime,
            kdRatio: player.stats.deaths > 0 ? (player.stats.kills / player.stats.deaths).toFixed(2) : player.stats.kills,
            winRate: (player.stats.wins + player.stats.losses) > 0 ? 
                ((player.stats.wins / (player.stats.wins + player.stats.losses)) * 100).toFixed(1) : 0
        };
    }
    
    getLeaderboard(limit = 10) {
        const players = Array.from(this.players.values())
            .filter(p => p.stats.kills > 0 || p.stats.wins > 0)
            .sort((a, b) => {
                // Sort by level, then by experience, then by kills
                if (a.stats.level !== b.stats.level) {
                    return b.stats.level - a.stats.level;
                }
                if (a.stats.experience !== b.stats.experience) {
                    return b.stats.experience - a.stats.experience;
                }
                return b.stats.kills - a.stats.kills;
            })
            .slice(0, limit)
            .map(p => ({
                username: p.username,
                level: p.stats.level,
                kills: p.stats.kills,
                deaths: p.stats.deaths,
                wins: p.stats.wins,
                kdRatio: p.stats.deaths > 0 ? (p.stats.kills / p.stats.deaths).toFixed(2) : p.stats.kills
            }));
            
        return players;
    }
    
    getOnlinePlayers() {
        return Array.from(this.players.values())
            .filter(p => p.isOnline)
            .map(p => ({
                playerId: p.playerId,
                username: p.username,
                level: p.stats.level,
                currentRoom: p.currentRoom,
                lastActivity: p.lastActivity
            }));
    }
    
    getPlayerCount() {
        return this.stats.activePlayers;
    }
    
    getTotalConnections() {
        return this.stats.totalConnections;
    }
    
    // Password utilities
    hashPassword(password) {
        return bcrypt.hashSync(password, this.bcryptRounds);
    }
    
    verifyPassword(password, hash) {
        return bcrypt.compareSync(password, hash);
    }
    
    // Cleanup inactive players
    cleanupInactivePlayers() {
        const currentTime = Date.now();
        const inactiveThreshold = 30 * 60 * 1000; // 30 minutes
        
        for (const [playerId, player] of this.players) {
            if (!player.isOnline && (currentTime - player.lastSeen) > inactiveThreshold) {
                // Remove very old inactive players to prevent memory leaks
                if ((currentTime - player.lastSeen) > (24 * 60 * 60 * 1000)) { // 24 hours
                    this.players.delete(playerId);
                }
            }
        }
    }
    
    // Get server statistics
    getServerStats() {
        return {
            ...this.stats,
            totalPlayers: this.players.size,
            onlinePlayers: this.stats.activePlayers,
            averageKills: this.stats.totalKills / Math.max(1, this.stats.totalConnections),
            averageDeaths: this.stats.totalDeaths / Math.max(1, this.stats.totalConnections)
        };
    }
}

module.exports = PlayerManager;
