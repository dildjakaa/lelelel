/**
 * Game state management and core game logic
 */

class GameManager {
    constructor() {
        this.rooms = new Map();
        this.gameConfig = {
            tickRate: parseInt(process.env.GAME_TICK_RATE) || 60,
            maxPlayersPerRoom: parseInt(process.env.MAX_PLAYERS_PER_ROOM) || 8,
            maxRooms: parseInt(process.env.MAX_ROOMS) || 10,
            mapSize: parseInt(process.env.MAP_SIZE) || 50,
            respawnTime: 5000, // 5 seconds
            maxHealth: 100,
            weaponDamage: {
                pistol: 25,
                rifle: 35,
                shotgun: 60
            },
            weaponRange: {
                pistol: 30,
                rifle: 60,
                shotgun: 15
            },
            weaponFireRate: {
                pistol: 2, // shots per second
                rifle: 8,
                shotgun: 1
            }
        };
        
        this.gameModes = {
            deathmatch: {
                name: 'Deathmatch',
                maxPlayers: 8,
                respawnEnabled: true,
                teamBased: false
            },
            teamDeathmatch: {
                name: 'Team Deathmatch',
                maxPlayers: 8,
                respawnEnabled: true,
                teamBased: true
            },
            elimination: {
                name: 'Elimination',
                maxPlayers: 8,
                respawnEnabled: false,
                teamBased: true
            }
        };
    }
    
    update() {
        // Update all active rooms
        for (const [roomId, room] of this.rooms) {
            if (room.isActive) {
                this.updateRoom(room);
            }
        }
    }
    
    updateRoom(room) {
        const currentTime = Date.now();
        
        // Update game state
        room.gameState.lastUpdate = currentTime;
        
        // Process respawns
        this.processRespawns(room, currentTime);
        
        // Update player states
        this.updatePlayerStates(room);
        
        // Check win conditions
        this.checkWinConditions(room);
        
        // Clean up disconnected players
        this.cleanupDisconnectedPlayers(room);
    }
    
    processRespawns(room, currentTime) {
        if (!room.gameConfig.respawnEnabled) return;
        
        for (const [playerId, player] of room.players) {
            if (!player.isAlive && player.respawnTime && currentTime >= player.respawnTime) {
                this.respawnPlayer(room, playerId);
            }
        }
    }
    
    respawnPlayer(room, playerId) {
        const player = room.players.get(playerId);
        if (!player) return;
        
        // Reset player state
        player.health = this.gameConfig.maxHealth;
        player.isAlive = true;
        player.respawnTime = null;
        player.position = this.getRandomSpawnPoint(room);
        player.rotation = { x: 0, y: 0, z: 0 };
        
        // Reset weapon
        player.currentWeapon = 'rifle';
        player.ammo = this.getWeaponAmmo('rifle');
        player.lastShotTime = 0;
        
        // Notify room
        room.broadcast('player_respawned', {
            playerId,
            position: player.position,
            timestamp: Date.now()
        });
    }
    
    updatePlayerStates(room) {
        const currentTime = Date.now();
        
        for (const [playerId, player] of room.players) {
            // Update last activity
            player.lastActivity = currentTime;
            
            // Update weapon cooldown
            if (player.lastShotTime > 0) {
                const timeSinceLastShot = currentTime - player.lastShotTime;
                const fireRate = this.gameConfig.weaponFireRate[player.currentWeapon];
                const cooldownTime = 1000 / fireRate;
                
                if (timeSinceLastShot >= cooldownTime) {
                    player.canShoot = true;
                }
            }
        }
    }
    
    checkWinConditions(room) {
        const gameMode = this.gameModes[room.gameMode];
        if (!gameMode) return;
        
        const alivePlayers = Array.from(room.players.values()).filter(p => p.isAlive);
        
        if (gameMode.teamBased) {
            this.checkTeamWinCondition(room, alivePlayers);
        } else {
            this.checkDeathmatchWinCondition(room, alivePlayers);
        }
    }
    
    checkTeamWinCondition(room, alivePlayers) {
        const teamA = alivePlayers.filter(p => p.team === 'A');
        const teamB = alivePlayers.filter(p => p.team === 'B');
        
        if (teamA.length === 0) {
            this.endGame(room, 'B', 'Team B wins!');
        } else if (teamB.length === 0) {
            this.endGame(room, 'A', 'Team A wins!');
        }
    }
    
    checkDeathmatchWinCondition(room, alivePlayers) {
        if (alivePlayers.length <= 1) {
            const winner = alivePlayers[0];
            this.endGame(room, winner.playerId, `${winner.username} wins!`);
        }
    }
    
    endGame(room, winner, message) {
        room.gameState.isGameOver = true;
        room.gameState.winner = winner;
        room.gameState.endTime = Date.now();
        
        room.broadcast('game_ended', {
            winner,
            message,
            timestamp: Date.now()
        });
        
        // Reset room after delay
        setTimeout(() => {
            this.resetRoom(room);
        }, 10000); // 10 seconds
    }
    
    resetRoom(room) {
        room.gameState = this.createInitialGameState();
        
        // Reset all players
        for (const [playerId, player] of room.players) {
            this.respawnPlayer(room, playerId);
        }
        
        room.broadcast('game_reset', {
            timestamp: Date.now()
        });
    }
    
    createInitialGameState() {
        return {
            isGameOver: false,
            winner: null,
            startTime: Date.now(),
            lastUpdate: Date.now(),
            endTime: null
        };
    }
    
    getRandomSpawnPoint(room) {
        const mapSize = this.gameConfig.mapSize;
        const spawnPoints = room.spawnPoints || [];
        
        if (spawnPoints.length > 0) {
            return spawnPoints[Math.floor(Math.random() * spawnPoints.length)];
        }
        
        // Generate random spawn point
        return {
            x: (Math.random() - 0.5) * mapSize,
            y: 1,
            z: (Math.random() - 0.5) * mapSize
        };
    }
    
    getWeaponAmmo(weaponType) {
        const ammoCounts = {
            pistol: 12,
            rifle: 30,
            shotgun: 8
        };
        return ammoCounts[weaponType] || 30;
    }
    
    processShot(room, shooterId, shotData) {
        const shooter = room.players.get(shooterId);
        if (!shooter || !shooter.isAlive || !shooter.canShoot) {
            return { hit: false, reason: 'Invalid shooter' };
        }
        
        const weaponType = shooter.currentWeapon;
        const fireRate = this.gameConfig.weaponFireRate[weaponType];
        const currentTime = Date.now();
        
        // Check fire rate
        if (currentTime - shooter.lastShotTime < 1000 / fireRate) {
            return { hit: false, reason: 'Rate limited' };
        }
        
        // Check ammo
        if (shooter.ammo <= 0) {
            return { hit: false, reason: 'No ammo' };
        }
        
        // Consume ammo
        shooter.ammo--;
        shooter.lastShotTime = currentTime;
        shooter.canShoot = false;
        
        // Calculate hit
        const hitResult = this.calculateHit(room, shooter, shotData);
        
        return hitResult;
    }
    
    calculateHit(room, shooter, shotData) {
        const weaponType = shooter.currentWeapon;
        const weaponRange = this.gameConfig.weaponRange[weaponType];
        const weaponDamage = this.gameConfig.weaponDamage[weaponType];
        
        // Simple raycast hit detection
        const rayOrigin = shotData.origin || shooter.position;
        const rayDirection = shotData.direction;
        const maxDistance = weaponRange;
        
        let closestHit = null;
        let closestDistance = Infinity;
        
        // Check against all other players
        for (const [playerId, player] of room.players) {
            if (playerId === shooter.playerId || !player.isAlive) continue;
            
            const hitPoint = this.raycastToPlayer(rayOrigin, rayDirection, player, maxDistance);
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
            // Apply damage
            const damageResult = this.applyDamage(room, closestHit.playerId, weaponDamage);
            
            return {
                hit: true,
                targetId: closestHit.playerId,
                hitPoint: closestHit.hitPoint,
                damage: weaponDamage,
                damageResult
            };
        }
        
        return { hit: false, reason: 'No target hit' };
    }
    
    raycastToPlayer(origin, direction, player, maxDistance) {
        // Simple sphere intersection test
        const playerRadius = 0.5;
        const playerCenter = player.position;
        
        // Calculate distance from ray to player center
        const toPlayer = this.subtractVectors(playerCenter, origin);
        const projectionLength = this.dotProduct(toPlayer, direction);
        
        if (projectionLength < 0) return null; // Behind origin
        
        const closestPoint = this.addVectors(origin, this.multiplyVector(direction, projectionLength));
        const distanceToPlayer = this.calculateDistance(closestPoint, playerCenter);
        
        if (distanceToPlayer <= playerRadius && projectionLength <= maxDistance) {
            return closestPoint;
        }
        
        return null;
    }
    
    applyDamage(room, targetId, damage) {
        const target = room.players.get(targetId);
        if (!target || !target.isAlive) return null;
        
        target.health -= damage;
        target.health = Math.max(0, target.health);
        
        const isDead = target.health <= 0;
        
        if (isDead) {
            target.isAlive = false;
            target.respawnTime = Date.now() + this.gameConfig.respawnTime;
        }
        
        return {
            damage,
            newHealth: target.health,
            isDead
        };
    }
    
    cleanupDisconnectedPlayers(room) {
        const currentTime = Date.now();
        const timeout = 30000; // 30 seconds
        
        for (const [playerId, player] of room.players) {
            if (currentTime - player.lastActivity > timeout) {
                room.players.delete(playerId);
                room.broadcast('player_disconnected', {
                    playerId,
                    timestamp: Date.now()
                });
            }
        }
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

module.exports = GameManager;
