/**
 * Logging system for the game server
 */

const winston = require('winston');
const path = require('path');
const fs = require('fs');

class Logger {
    constructor() {
        this.logLevel = process.env.LOG_LEVEL || 'info';
        this.logFile = process.env.LOG_FILE || 'logs/server.log';
        
        // Create logs directory if it doesn't exist
        const logDir = path.dirname(this.logFile);
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        // Configure winston logger
        this.logger = winston.createLogger({
            level: this.logLevel,
            format: winston.format.combine(
                winston.format.timestamp({
                    format: 'YYYY-MM-DD HH:mm:ss'
                }),
                winston.format.errors({ stack: true }),
                winston.format.json()
            ),
            defaultMeta: { service: 'game-server' },
            transports: [
                // Console transport
                new winston.transports.Console({
                    format: winston.format.combine(
                        winston.format.colorize(),
                        winston.format.simple(),
                        winston.format.printf(({ timestamp, level, message, ...meta }) => {
                            return `${timestamp} [${level}]: ${message} ${Object.keys(meta).length ? JSON.stringify(meta) : ''}`;
                        })
                    )
                }),
                
                // File transport
                new winston.transports.File({
                    filename: this.logFile,
                    maxsize: 5242880, // 5MB
                    maxFiles: 5,
                    tailable: true
                }),
                
                // Error file transport
                new winston.transports.File({
                    filename: path.join(logDir, 'error.log'),
                    level: 'error',
                    maxsize: 5242880, // 5MB
                    maxFiles: 5,
                    tailable: true
                })
            ]
        });
        
        // Add custom methods
        this.addCustomMethods();
    }
    
    addCustomMethods() {
        // Game-specific logging methods
        this.logger.playerConnect = (playerId, socketId) => {
            this.logger.info('Player connected', {
                playerId,
                socketId,
                event: 'player_connect'
            });
        };
        
        this.logger.playerDisconnect = (playerId, socketId, reason) => {
            this.logger.info('Player disconnected', {
                playerId,
                socketId,
                reason,
                event: 'player_disconnect'
            });
        };
        
        this.logger.playerJoinRoom = (playerId, roomId) => {
            this.logger.info('Player joined room', {
                playerId,
                roomId,
                event: 'player_join_room'
            });
        };
        
        this.logger.playerLeaveRoom = (playerId, roomId) => {
            this.logger.info('Player left room', {
                playerId,
                roomId,
                event: 'player_leave_room'
            });
        };
        
        this.logger.gameStart = (roomId, gameMode, playerCount) => {
            this.logger.info('Game started', {
                roomId,
                gameMode,
                playerCount,
                event: 'game_start'
            });
        };
        
        this.logger.gameEnd = (roomId, winner, duration) => {
            this.logger.info('Game ended', {
                roomId,
                winner,
                duration,
                event: 'game_end'
            });
        };
        
        this.logger.playerKill = (killerId, victimId, weapon) => {
            this.logger.info('Player kill', {
                killerId,
                victimId,
                weapon,
                event: 'player_kill'
            });
        };
        
        this.logger.antiCheatViolation = (playerId, violationType, reason) => {
            this.logger.warn('Anti-cheat violation', {
                playerId,
                violationType,
                reason,
                event: 'anti_cheat_violation'
            });
        };
        
        this.logger.serverError = (error, context) => {
            this.logger.error('Server error', {
                error: error.message,
                stack: error.stack,
                context,
                event: 'server_error'
            });
        };
        
        this.logger.performance = (operation, duration, metadata = {}) => {
            this.logger.info('Performance metric', {
                operation,
                duration,
                ...metadata,
                event: 'performance'
            });
        };
    }
    
    // Standard logging methods
    info(message, meta = {}) {
        this.logger.info(message, meta);
    }
    
    warn(message, meta = {}) {
        this.logger.warn(message, meta);
    }
    
    error(message, meta = {}) {
        this.logger.error(message, meta);
    }
    
    debug(message, meta = {}) {
        this.logger.debug(message, meta);
    }
    
    // Game-specific logging methods
    logPlayerAction(playerId, action, data = {}) {
        this.logger.info('Player action', {
            playerId,
            action,
            ...data,
            event: 'player_action'
        });
    }
    
    logRoomEvent(roomId, event, data = {}) {
        this.logger.info('Room event', {
            roomId,
            event,
            ...data,
            event: 'room_event'
        });
    }
    
    logSecurityEvent(event, data = {}) {
        this.logger.warn('Security event', {
            event,
            ...data,
            event: 'security'
        });
    }
    
    logSystemEvent(event, data = {}) {
        this.logger.info('System event', {
            event,
            ...data,
            event: 'system'
        });
    }
    
    // Performance monitoring
    startTimer(operation) {
        const start = process.hrtime.bigint();
        return {
            end: (metadata = {}) => {
                const end = process.hrtime.bigint();
                const duration = Number(end - start) / 1000000; // Convert to milliseconds
                this.logger.performance(operation, duration, metadata);
                return duration;
            }
        };
    }
    
    // Memory usage logging
    logMemoryUsage() {
        const usage = process.memoryUsage();
        this.logger.info('Memory usage', {
            rss: Math.round(usage.rss / 1024 / 1024) + ' MB',
            heapTotal: Math.round(usage.heapTotal / 1024 / 1024) + ' MB',
            heapUsed: Math.round(usage.heapUsed / 1024 / 1024) + ' MB',
            external: Math.round(usage.external / 1024 / 1024) + ' MB',
            event: 'memory_usage'
        });
    }
    
    // Server statistics logging
    logServerStats(stats) {
        this.logger.info('Server statistics', {
            ...stats,
            event: 'server_stats'
        });
    }
    
    // Error handling wrapper
    handleError(error, context = {}) {
        this.logger.serverError(error, context);
        
        // In production, you might want to send errors to an external service
        if (process.env.NODE_ENV === 'production') {
            // Example: Send to external error tracking service
            // this.sendToErrorService(error, context);
        }
    }
    
    // Cleanup old logs
    cleanupLogs() {
        const logDir = path.dirname(this.logFile);
        const files = fs.readdirSync(logDir);
        const now = Date.now();
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
        
        files.forEach(file => {
            if (file.endsWith('.log')) {
                const filePath = path.join(logDir, file);
                const stats = fs.statSync(filePath);
                
                if (now - stats.mtime.getTime() > maxAge) {
                    fs.unlinkSync(filePath);
                    this.logger.info(`Cleaned up old log file: ${file}`);
                }
            }
        });
    }
    
    // Get logger instance for external use
    getWinstonLogger() {
        return this.logger;
    }
    
    // Set log level dynamically
    setLogLevel(level) {
        this.logger.level = level;
        this.logLevel = level;
    }
    
    // Get current log level
    getLogLevel() {
        return this.logLevel;
    }
}

module.exports = Logger;
