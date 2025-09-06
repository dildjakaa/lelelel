/**
 * Room and lobby management system
 */

const { v4: uuidv4 } = require('uuid');

class RoomManager {
    constructor() {
        this.rooms = new Map();
        this.maxRooms = parseInt(process.env.MAX_ROOMS) || 10;
        this.maxPlayersPerRoom = parseInt(process.env.MAX_PLAYERS_PER_ROOM) || 8;
    }
    
    createRoom(roomData) {
        if (this.rooms.size >= this.maxRooms) {
            return null; // Server at capacity
        }
        
        const roomId = uuidv4();
        const currentTime = Date.now();
        
        const room = {
            id: roomId,
            name: roomData.name || `Room ${Date.now()}`,
            gameMode: roomData.gameMode || 'deathmatch',
            maxPlayers: Math.min(roomData.maxPlayers || 8, this.maxPlayersPerRoom),
            isPrivate: roomData.isPrivate || false,
            password: roomData.password || null,
            createdBy: roomData.createdBy,
            createdAt: currentTime,
            lastActivity: currentTime,
            
            // Player management
            players: new Map(),
            spectators: new Set(),
            
            // Game state
            gameState: {
                isActive: false,
                isGameOver: false,
                winner: null,
                startTime: null,
                endTime: null,
                lastUpdate: currentTime
            },
            
            // Game configuration
            gameConfig: {
                respawnEnabled: true,
                respawnTime: 5000,
                maxHealth: 100,
                timeLimit: 600000, // 10 minutes
                killLimit: 50
            },
            
            // Map and spawn points
            mapSize: parseInt(process.env.MAP_SIZE) || 50,
            spawnPoints: [],
            
            // Statistics
            stats: {
                totalKills: 0,
                totalDeaths: 0,
                roundsPlayed: 0
            }
        };
        
        // Generate spawn points
        this.generateSpawnPoints(room);
        
        this.rooms.set(roomId, room);
        return roomId;
    }
    
    getRoom(roomId) {
        return this.rooms.get(roomId);
    }
    
    getAllRooms() {
        return Array.from(this.rooms.values());
    }
    
    getPublicRooms() {
        return Array.from(this.rooms.values())
            .filter(room => !room.isPrivate && room.players.size < room.maxPlayers);
    }
    
    addPlayerToRoom(roomId, playerId, socket) {
        const room = this.rooms.get(roomId);
        if (!room) return false;
        
        if (room.players.size >= room.maxPlayers) {
            return false; // Room is full
        }
        
        // Create player data for the room
        const playerData = {
            playerId,
            socket,
            username: `Player_${playerId.substring(0, 8)}`,
            team: this.assignTeam(room),
            position: this.getRandomSpawnPoint(room),
            rotation: { x: 0, y: 0, z: 0 },
            health: room.gameConfig.maxHealth,
            maxHealth: room.gameConfig.maxHealth,
            isAlive: true,
            currentWeapon: 'rifle',
            ammo: 30,
            lastShotTime: 0,
            canShoot: true,
            lastActivity: Date.now(),
            kills: 0,
            deaths: 0,
            score: 0
        };
        
        room.players.set(playerId, playerData);
        room.lastActivity = Date.now();
        
        // Start game if enough players
        if (room.players.size >= 2 && !room.gameState.isActive) {
            this.startGame(room);
        }
        
        return true;
    }
    
    removePlayerFromRoom(roomId, playerId) {
        const room = this.rooms.get(roomId);
        if (!room) return false;
        
        const player = room.players.get(playerId);
        if (player) {
            room.players.delete(playerId);
            room.lastActivity = Date.now();
            
            // End game if not enough players
            if (room.players.size < 2 && room.gameState.isActive) {
                this.endGame(room, 'Not enough players');
            }
        }
        
        return true;
    }
    
    assignTeam(room) {
        if (room.gameMode === 'teamDeathmatch' || room.gameMode === 'elimination') {
            const teamA = Array.from(room.players.values()).filter(p => p.team === 'A').length;
            const teamB = Array.from(room.players.values()).filter(p => p.team === 'B').length;
            return teamA <= teamB ? 'A' : 'B';
        }
        return null; // No teams for deathmatch
    }
    
    startGame(room) {
        room.gameState.isActive = true;
        room.gameState.startTime = Date.now();
        room.gameState.isGameOver = false;
        room.gameState.winner = null;
        
        // Reset all players
        for (const [playerId, player] of room.players) {
            player.health = room.gameConfig.maxHealth;
            player.isAlive = true;
            player.position = this.getRandomSpawnPoint(room);
            player.rotation = { x: 0, y: 0, z: 0 };
            player.currentWeapon = 'rifle';
            player.ammo = 30;
            player.kills = 0;
            player.deaths = 0;
            player.score = 0;
        }
        
        // Broadcast game start
        this.broadcastToRoom(room, 'game_started', {
            gameMode: room.gameMode,
            playerCount: room.players.size,
            timestamp: Date.now()
        });
        
        console.log(`Game started in room ${room.id} (${room.gameMode})`);
    }
    
    endGame(room, reason) {
        room.gameState.isActive = false;
        room.gameState.isGameOver = true;
        room.gameState.endTime = Date.now();
        
        // Determine winner
        if (reason !== 'Not enough players') {
            room.gameState.winner = this.determineWinner(room);
        }
        
        // Broadcast game end
        this.broadcastToRoom(room, 'game_ended', {
            winner: room.gameState.winner,
            reason,
            duration: room.gameState.endTime - room.gameState.startTime,
            timestamp: Date.now()
        });
        
        room.stats.roundsPlayed++;
        
        console.log(`Game ended in room ${room.id}: ${reason}`);
        
        // Reset room after delay
        setTimeout(() => {
            this.resetRoom(room);
        }, 10000); // 10 seconds
    }
    
    determineWinner(room) {
        if (room.gameMode === 'teamDeathmatch' || room.gameMode === 'elimination') {
            const teamA = Array.from(room.players.values()).filter(p => p.team === 'A' && p.isAlive);
            const teamB = Array.from(room.players.values()).filter(p => p.team === 'B' && p.isAlive);
            
            if (teamA.length === 0) return 'Team B';
            if (teamB.length === 0) return 'Team A';
        } else {
            // Deathmatch - player with most kills
            const players = Array.from(room.players.values());
            const winner = players.reduce((prev, current) => 
                (prev.kills > current.kills) ? prev : current
            );
            return winner.username;
        }
        
        return null;
    }
    
    resetRoom(room) {
        room.gameState = {
            isActive: false,
            isGameOver: false,
            winner: null,
            startTime: null,
            endTime: null,
            lastUpdate: Date.now()
        };
        
        // Reset all players
        for (const [playerId, player] of room.players) {
            player.health = room.gameConfig.maxHealth;
            player.isAlive = true;
            player.position = this.getRandomSpawnPoint(room);
            player.rotation = { x: 0, y: 0, z: 0 };
            player.currentWeapon = 'rifle';
            player.ammo = 30;
        }
        
        this.broadcastToRoom(room, 'room_reset', {
            timestamp: Date.now()
        });
    }
    
    updatePlayerPosition(roomId, playerId, position) {
        const room = this.rooms.get(roomId);
        if (!room) return false;
        
        const player = room.players.get(playerId);
        if (player) {
            player.position = position;
            player.lastActivity = Date.now();
            return true;
        }
        
        return false;
    }
    
    updatePlayerRotation(roomId, playerId, rotation) {
        const room = this.rooms.get(roomId);
        if (!room) return false;
        
        const player = room.players.get(playerId);
        if (player) {
            player.rotation = rotation;
            player.lastActivity = Date.now();
            return true;
        }
        
        return false;
    }
    
    processShot(roomId, shooterId, shotData) {
        const room = this.rooms.get(roomId);
        if (!room) return null;
        
        const shooter = room.players.get(shooterId);
        if (!shooter || !shooter.isAlive) return null;
        
        // Check if shooter can shoot
        const currentTime = Date.now();
        const fireRate = this.getWeaponFireRate(shooter.currentWeapon);
        const cooldownTime = 1000 / fireRate;
        
        if (currentTime - shooter.lastShotTime < cooldownTime) {
            return { hit: false, reason: 'Rate limited' };
        }
        
        if (shooter.ammo <= 0) {
            return { hit: false, reason: 'No ammo' };
        }
        
        // Consume ammo
        shooter.ammo--;
        shooter.lastShotTime = currentTime;
        
        // Calculate hit
        const hitResult = this.calculateHit(room, shooter, shotData);
        
        if (hitResult.hit) {
            // Apply damage
            const target = room.players.get(hitResult.targetId);
            if (target) {
                const damage = this.getWeaponDamage(shooter.currentWeapon);
                target.health -= damage;
                target.health = Math.max(0, target.health);
                
                if (target.health <= 0) {
                    target.isAlive = false;
                    target.deaths++;
                    shooter.kills++;
                    shooter.score += 100;
                    room.stats.totalKills++;
                    room.stats.totalDeaths++;
                }
            }
        }
        
        return hitResult;
    }
    
    processDamage(roomId, attackerId, damageData) {
        const room = this.rooms.get(roomId);
        if (!room) return null;
        
        const target = room.players.get(damageData.targetId);
        if (!target || !target.isAlive) return null;
        
        const damage = damageData.damage || 25;
        target.health -= damage;
        target.health = Math.max(0, target.health);
        
        const isDead = target.health <= 0;
        if (isDead) {
            target.isAlive = false;
            target.deaths++;
            
            // Award kill to attacker
            const attacker = room.players.get(attackerId);
            if (attacker) {
                attacker.kills++;
                attacker.score += 100;
            }
            
            room.stats.totalKills++;
            room.stats.totalDeaths++;
        }
        
        return {
            damage,
            newHealth: target.health,
            isDead
        };
    }
    
    reloadPlayerWeapon(roomId, playerId) {
        const room = this.rooms.get(roomId);
        if (!room) return false;
        
        const player = room.players.get(playerId);
        if (!player) return false;
        
        const maxAmmo = this.getWeaponMaxAmmo(player.currentWeapon);
        player.ammo = maxAmmo;
        player.lastActivity = Date.now();
        
        return true;
    }
    
    calculateHit(room, shooter, shotData) {
        const weaponRange = this.getWeaponRange(shooter.currentWeapon);
        const rayOrigin = shotData.origin || shooter.position;
        const rayDirection = shotData.direction;
        
        let closestHit = null;
        let closestDistance = Infinity;
        
        // Check against all other players
        for (const [playerId, player] of room.players) {
            if (playerId === shooter.playerId || !player.isAlive) continue;
            
            const hitPoint = this.raycastToPlayer(rayOrigin, rayDirection, player, weaponRange);
            if (hitPoint) {
                const distance = this.calculateDistance(rayOrigin, hitPoint);
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestHit = {
                        playerId,
                        player,
                        hitPoint,
                        distance
                    };
                }
            }
        }
        
        if (closestHit) {
            return {
                hit: true,
                targetId: closestHit.playerId,
                hitPoint: closestHit.hitPoint,
                distance: closestHit.distance
            };
        }
        
        return { hit: false, reason: 'No target hit' };
    }
    
    raycastToPlayer(origin, direction, player, maxDistance) {
        const playerRadius = 0.5;
        const playerCenter = player.position;
        
        // Simple sphere intersection test
        const toPlayer = this.subtractVectors(playerCenter, origin);
        const projectionLength = this.dotProduct(toPlayer, direction);
        
        if (projectionLength < 0) return null;
        
        const closestPoint = this.addVectors(origin, this.multiplyVector(direction, projectionLength));
        const distanceToPlayer = this.calculateDistance(closestPoint, playerCenter);
        
        if (distanceToPlayer <= playerRadius && projectionLength <= maxDistance) {
            return closestPoint;
        }
        
        return null;
    }
    
    generateSpawnPoints(room) {
        const mapSize = room.mapSize;
        const numSpawnPoints = Math.min(room.maxPlayers * 2, 16);
        
        for (let i = 0; i < numSpawnPoints; i++) {
            const angle = (i / numSpawnPoints) * 2 * Math.PI;
            const distance = (mapSize * 0.3) + (Math.random() * mapSize * 0.2);
            
            const spawnPoint = {
                x: Math.cos(angle) * distance,
                y: 1,
                z: Math.sin(angle) * distance
            };
            
            room.spawnPoints.push(spawnPoint);
        }
    }
    
    getRandomSpawnPoint(room) {
        if (room.spawnPoints.length === 0) {
            return { x: 0, y: 1, z: 0 };
        }
        
        return room.spawnPoints[Math.floor(Math.random() * room.spawnPoints.length)];
    }
    
    broadcastToRoom(room, event, data) {
        for (const [playerId, player] of room.players) {
            if (player.socket) {
                player.socket.emit(event, data);
            }
        }
    }
    
    updateAllRooms() {
        const currentTime = Date.now();
        
        for (const [roomId, room] of this.rooms) {
            // Update room activity
            room.lastActivity = currentTime;
            
            // Clean up empty rooms
            if (room.players.size === 0) {
                this.rooms.delete(roomId);
                continue;
            }
            
            // Check for inactive players
            this.cleanupInactivePlayers(room);
        }
    }
    
    cleanupInactivePlayers(room) {
        const currentTime = Date.now();
        const timeout = 30000; // 30 seconds
        
        for (const [playerId, player] of room.players) {
            if (currentTime - player.lastActivity > timeout) {
                room.players.delete(playerId);
                this.broadcastToRoom(room, 'player_disconnected', {
                    playerId,
                    timestamp: currentTime
                });
            }
        }
    }
    
    getRoomCount() {
        return this.rooms.size;
    }
    
    // Weapon configuration
    getWeaponDamage(weaponType) {
        const damages = {
            pistol: 25,
            rifle: 35,
            shotgun: 60
        };
        return damages[weaponType] || 25;
    }
    
    getWeaponRange(weaponType) {
        const ranges = {
            pistol: 30,
            rifle: 60,
            shotgun: 15
        };
        return ranges[weaponType] || 30;
    }
    
    getWeaponFireRate(weaponType) {
        const fireRates = {
            pistol: 2,
            rifle: 8,
            shotgun: 1
        };
        return fireRates[weaponType] || 2;
    }
    
    getWeaponMaxAmmo(weaponType) {
        const ammoCounts = {
            pistol: 12,
            rifle: 30,
            shotgun: 8
        };
        return ammoCounts[weaponType] || 30;
    }
    
    // Utility functions
    calculateDistance(pos1, pos2) {
        const dx = pos1.x - pos2.x;
        const dy = pos1.y - pos2.y;
        const dz = pos1.z - pos2.z;
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
    
    subtractVectors(a, b) {
        return { x: a.x - b.x, y: a.y - b.y, z: a.z - b.z };
    }
    
    addVectors(a, b) {
        return { x: a.x + b.x, y: a.y + b.y, z: a.z + b.z };
    }
    
    multiplyVector(v, scalar) {
        return { x: v.x * scalar, y: v.y * scalar, z: v.z * scalar };
    }
    
    dotProduct(a, b) {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }
}

module.exports = RoomManager;
