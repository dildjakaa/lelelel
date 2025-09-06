/**
 * Anti-cheat system for server-side validation
 */

class AntiCheat {
    constructor() {
        this.maxMovementSpeed = parseFloat(process.env.MAX_MOVEMENT_SPEED) || 10.0;
        this.maxShootingRate = parseFloat(process.env.MAX_SHOOTING_RATE) || 10.0;
        this.validationInterval = parseInt(process.env.VALIDATION_INTERVAL) || 100;
        
        // Player tracking
        this.playerData = new Map();
        this.suspiciousActivities = new Map();
        
        // Rate limiting
        this.rateLimits = new Map();
        
        // Violation thresholds
        this.violationThresholds = {
            movement: 5,      // Max movement violations before kick
            shooting: 10,     // Max shooting violations before kick
            general: 15       // Max general violations before kick
        };
    }
    
    validateMovement(movementData) {
        const { playerId, position, timestamp } = movementData;
        
        if (!playerId || !position) {
            return false;
        }
        
        const currentTime = Date.now();
        const player = this.getPlayerData(playerId);
        
        // Check if this is the first movement
        if (!player.lastPosition) {
            player.lastPosition = position;
            player.lastPositionTime = currentTime;
            return true;
        }
        
        // Calculate movement distance and time
        const distance = this.calculateDistance(player.lastPosition, position);
        const timeDelta = currentTime - player.lastPositionTime;
        
        // Check for valid time delta
        if (timeDelta <= 0 || timeDelta > 1000) { // Max 1 second between updates
            this.recordViolation(playerId, 'movement', 'Invalid time delta');
            return false;
        }
        
        // Calculate speed
        const speed = distance / (timeDelta / 1000); // meters per second
        
        // Check speed limit
        if (speed > this.maxMovementSpeed) {
            this.recordViolation(playerId, 'movement', `Speed too high: ${speed.toFixed(2)} m/s`);
            return false;
        }
        
        // Check for teleportation (instant movement over large distance)
        if (distance > this.maxMovementSpeed * 2 && timeDelta < 100) {
            this.recordViolation(playerId, 'movement', 'Possible teleportation');
            return false;
        }
        
        // Check for impossible movement patterns
        if (this.isImpossibleMovement(player, position, timeDelta)) {
            this.recordViolation(playerId, 'movement', 'Impossible movement pattern');
            return false;
        }
        
        // Update player data
        player.lastPosition = position;
        player.lastPositionTime = currentTime;
        player.movementHistory.push({
            position: { ...position },
            timestamp: currentTime,
            speed: speed
        });
        
        // Keep only last 20 movements
        if (player.movementHistory.length > 20) {
            player.movementHistory.shift();
        }
        
        return true;
    }
    
    validateShooting(playerId, shotData) {
        const currentTime = Date.now();
        const player = this.getPlayerData(playerId);
        
        // Check rate limiting
        if (!this.checkRateLimit(playerId, 'shooting', this.maxShootingRate)) {
            this.recordViolation(playerId, 'shooting', 'Rate limit exceeded');
            return false;
        }
        
        // Check shot data validity
        if (!shotData.origin || !shotData.direction) {
            this.recordViolation(playerId, 'shooting', 'Invalid shot data');
            return false;
        }
        
        // Check if player is alive (if this info is available)
        if (shotData.playerHealth !== undefined && shotData.playerHealth <= 0) {
            this.recordViolation(playerId, 'shooting', 'Shooting while dead');
            return false;
        }
        
        // Check weapon cooldown
        const lastShotTime = player.lastShotTime || 0;
        const timeSinceLastShot = currentTime - lastShotTime;
        const minCooldown = 1000 / this.maxShootingRate; // Minimum time between shots
        
        if (timeSinceLastShot < minCooldown) {
            this.recordViolation(playerId, 'shooting', 'Shot cooldown violation');
            return false;
        }
        
        // Update player data
        player.lastShotTime = currentTime;
        player.shotHistory.push({
            timestamp: currentTime,
            shotData: { ...shotData }
        });
        
        // Keep only last 50 shots
        if (player.shotHistory.length > 50) {
            player.shotHistory.shift();
        }
        
        return true;
    }
    
    validatePosition(position) {
        if (!position || typeof position !== 'object') {
            return false;
        }
        
        const { x, y, z } = position;
        
        // Check for valid numbers
        if (typeof x !== 'number' || typeof y !== 'number' || typeof z !== 'number') {
            return false;
        }
        
        // Check for NaN or Infinity
        if (!isFinite(x) || !isFinite(y) || !isFinite(z)) {
            return false;
        }
        
        // Check reasonable bounds (adjust based on your map size)
        const mapSize = parseInt(process.env.MAP_SIZE) || 50;
        const maxHeight = 20;
        
        if (Math.abs(x) > mapSize || Math.abs(z) > mapSize || y < -10 || y > maxHeight) {
            return false;
        }
        
        return true;
    }
    
    validateRotation(rotation) {
        if (!rotation || typeof rotation !== 'object') {
            return false;
        }
        
        const { x, y, z } = rotation;
        
        // Check for valid numbers
        if (typeof x !== 'number' || typeof y !== 'number' || typeof z !== 'number') {
            return false;
        }
        
        // Check for NaN or Infinity
        if (!isFinite(x) || !isFinite(y) || !isFinite(z)) {
            return false;
        }
        
        // Check reasonable bounds (rotation should be between -180 and 180 degrees)
        if (Math.abs(x) > 180 || Math.abs(y) > 180 || Math.abs(z) > 180) {
            return false;
        }
        
        return true;
    }
    
    isImpossibleMovement(player, newPosition, timeDelta) {
        if (player.movementHistory.length < 2) {
            return false;
        }
        
        const history = player.movementHistory;
        const lastMovement = history[history.length - 1];
        
        // Check for sudden direction changes that are physically impossible
        const lastDirection = this.calculateDirection(player.lastPosition, lastMovement.position);
        const newDirection = this.calculateDirection(lastMovement.position, newPosition);
        
        // Calculate angle between directions
        const angleChange = this.calculateAngleBetweenVectors(lastDirection, newDirection);
        
        // If angle change is too sharp in too short time, it's suspicious
        if (angleChange > 90 && timeDelta < 50) { // 90 degrees in less than 50ms
            return true;
        }
        
        // Check for movement through walls (simplified check)
        if (this.isMovementThroughWall(player.lastPosition, newPosition)) {
            return true;
        }
        
        return false;
    }
    
    isMovementThroughWall(from, to) {
        // This is a simplified check - in a real game, you'd use proper collision detection
        // For now, we'll just check if the movement is too straight through the map center
        const distance = this.calculateDistance(from, to);
        const centerDistance = this.calculateDistance({ x: 0, y: 0, z: 0 }, to);
        
        // If moving a long distance and ending up near center, might be wall-hacking
        if (distance > 10 && centerDistance < 5) {
            return true;
        }
        
        return false;
    }
    
    checkRateLimit(playerId, action, maxRate) {
        const currentTime = Date.now();
        const key = `${playerId}_${action}`;
        
        if (!this.rateLimits.has(key)) {
            this.rateLimits.set(key, []);
        }
        
        const actions = this.rateLimits.get(key);
        const windowStart = currentTime - 1000; // 1 second window
        
        // Remove old actions
        while (actions.length > 0 && actions[0] < windowStart) {
            actions.shift();
        }
        
        // Check if adding this action would exceed the rate limit
        if (actions.length >= maxRate) {
            return false;
        }
        
        // Add this action
        actions.push(currentTime);
        return true;
    }
    
    recordViolation(playerId, type, reason) {
        if (!this.suspiciousActivities.has(playerId)) {
            this.suspiciousActivities.set(playerId, {
                movement: 0,
                shooting: 0,
                general: 0,
                violations: []
            });
        }
        
        const violations = this.suspiciousActivities.get(playerId);
        violations[type]++;
        violations.violations.push({
            type,
            reason,
            timestamp: Date.now()
        });
        
        // Keep only last 100 violations
        if (violations.violations.length > 100) {
            violations.violations.shift();
        }
        
        // Check if player should be kicked
        this.checkViolationThresholds(playerId);
        
        console.warn(`Anti-cheat violation: ${playerId} - ${type}: ${reason}`);
    }
    
    checkViolationThresholds(playerId) {
        const violations = this.suspiciousActivities.get(playerId);
        if (!violations) return;
        
        const { movement, shooting, general } = violations;
        
        if (movement >= this.violationThresholds.movement ||
            shooting >= this.violationThresholds.shooting ||
            general >= this.violationThresholds.general) {
            
            this.kickPlayer(playerId, 'Too many violations');
        }
    }
    
    kickPlayer(playerId, reason) {
        // This would be implemented to actually kick the player
        console.log(`Kicking player ${playerId}: ${reason}`);
        
        // Reset violation count
        this.suspiciousActivities.delete(playerId);
    }
    
    getPlayerData(playerId) {
        if (!this.playerData.has(playerId)) {
            this.playerData.set(playerId, {
                lastPosition: null,
                lastPositionTime: 0,
                lastShotTime: 0,
                movementHistory: [],
                shotHistory: []
            });
        }
        return this.playerData.get(playerId);
    }
    
    calculateDistance(pos1, pos2) {
        const dx = pos1.x - pos2.x;
        const dy = pos1.y - pos2.y;
        const dz = pos1.z - pos2.z;
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
    
    calculateDirection(from, to) {
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const dz = to.z - from.z;
        const length = Math.sqrt(dx * dx + dy * dy + dz * dz);
        
        if (length === 0) return { x: 0, y: 0, z: 0 };
        
        return {
            x: dx / length,
            y: dy / length,
            z: dz / length
        };
    }
    
    calculateAngleBetweenVectors(v1, v2) {
        const dot = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z;
        const mag1 = Math.sqrt(v1.x * v1.x + v1.y * v1.y + v1.z * v1.z);
        const mag2 = Math.sqrt(v2.x * v2.x + v2.y * v2.y + v2.z * v2.z);
        
        if (mag1 === 0 || mag2 === 0) return 0;
        
        const cosAngle = dot / (mag1 * mag2);
        const angle = Math.acos(Math.max(-1, Math.min(1, cosAngle)));
        
        return angle * (180 / Math.PI); // Convert to degrees
    }
    
    getPlayerViolations(playerId) {
        return this.suspiciousActivities.get(playerId) || {
            movement: 0,
            shooting: 0,
            general: 0,
            violations: []
        };
    }
    
    resetPlayerViolations(playerId) {
        this.suspiciousActivities.delete(playerId);
        this.playerData.delete(playerId);
    }
    
    cleanup() {
        const currentTime = Date.now();
        const cleanupTime = 5 * 60 * 1000; // 5 minutes
        
        // Clean up old rate limit data
        for (const [key, actions] of this.rateLimits) {
            const recentActions = actions.filter(time => currentTime - time < cleanupTime);
            if (recentActions.length === 0) {
                this.rateLimits.delete(key);
            } else {
                this.rateLimits.set(key, recentActions);
            }
        }
        
        // Clean up old player data
        for (const [playerId, data] of this.playerData) {
            if (currentTime - data.lastPositionTime > cleanupTime) {
                this.playerData.delete(playerId);
            }
        }
    }
    
    getStats() {
        return {
            trackedPlayers: this.playerData.size,
            suspiciousPlayers: this.suspiciousActivities.size,
            totalViolations: Array.from(this.suspiciousActivities.values())
                .reduce((sum, v) => sum + v.violations.length, 0)
        };
    }
}

module.exports = AntiCheat;
