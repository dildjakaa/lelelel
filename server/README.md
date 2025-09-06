# 3D Shooter Multiplayer Server

A robust Node.js multiplayer game server for the 3D Shooter Game, optimized for deployment on Render.com.

## Features

- **Real-time multiplayer** with Socket.io WebSocket connections
- **Room/lobby system** for multiple concurrent game matches
- **Player authentication** and session management
- **Anti-cheat system** with server-side validation
- **Game state management** with hit registration and scoring
- **Rate limiting** and security measures
- **Comprehensive logging** and monitoring
- **Render.com optimized** for easy deployment

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the server:**
   ```bash
   npm start
   # or for development with auto-reload:
   npm run dev
   ```

### Render.com Deployment

1. **Connect your repository** to Render.com
2. **Create a new Web Service** using this repository
3. **Set environment variables** in Render dashboard
4. **Deploy!** The server will automatically build and start

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3000 | Server port |
| `NODE_ENV` | production | Environment mode |
| `HOST` | 0.0.0.0 | Server host |
| `MAX_PLAYERS_PER_ROOM` | 8 | Maximum players per room |
| `MAX_ROOMS` | 10 | Maximum concurrent rooms |
| `GAME_TICK_RATE` | 60 | Game update frequency (FPS) |
| `MAP_SIZE` | 50 | Game map size |
| `JWT_SECRET` | - | JWT signing secret (required) |
| `BCRYPT_ROUNDS` | 12 | Password hashing rounds |
| `RATE_LIMIT_WINDOW_MS` | 900000 | Rate limit window (15 min) |
| `RATE_LIMIT_MAX_REQUESTS` | 100 | Max requests per window |
| `USE_REDIS` | false | Enable Redis for scaling |
| `CORS_ORIGIN` | "*" | CORS allowed origins |
| `LOG_LEVEL` | info | Logging level |

## API Endpoints

### REST API

- `GET /health` - Health check
- `GET /api/info` - Server information
- `GET /api/stats` - Server statistics
- `GET /api/rooms` - List available rooms
- `POST /api/auth/login` - Player authentication

### WebSocket Events

#### Client → Server
- `authenticate` - Authenticate player
- `join_room` - Join a game room
- `leave_room` - Leave current room
- `create_room` - Create new room
- `player_move` - Update player position
- `player_rotate` - Update player rotation
- `player_shoot` - Fire weapon
- `player_reload` - Reload weapon
- `player_damage` - Report damage taken
- `ping` - Connection health check

#### Server → Client
- `authenticated` - Authentication successful
- `room_joined` - Successfully joined room
- `player_joined` - Another player joined
- `player_left` - Player left room
- `game_started` - Game started
- `game_ended` - Game ended
- `player_moved` - Player position update
- `player_rotated` - Player rotation update
- `player_shot` - Player fired weapon
- `player_damaged` - Player took damage
- `pong` - Response to ping

## Game Modes

### Deathmatch
- Free-for-all combat
- Respawn enabled
- Individual scoring
- 8 players max

### Team Deathmatch
- Two teams (A vs B)
- Respawn enabled
- Team-based scoring
- 8 players max

### Elimination
- Two teams (A vs B)
- No respawn
- Last team standing wins
- 8 players max

## Anti-Cheat System

The server includes comprehensive anti-cheat measures:

- **Movement validation** - Speed and position checks
- **Rate limiting** - Prevents spam and rapid actions
- **Hit validation** - Server-side hit detection
- **Position validation** - Prevents impossible movements
- **Violation tracking** - Automatic player kicking

## Architecture

```
src/
├── app.js          # Main server application
├── game.js         # Game logic and state management
├── player.js       # Player management and authentication
├── room.js         # Room/lobby system
├── anti-cheat.js   # Anti-cheat validation
└── logger.js       # Logging system
```

## Performance

- **Optimized for 60 FPS** game updates
- **Memory efficient** player tracking
- **Scalable architecture** for multiple rooms
- **Rate limiting** to prevent abuse
- **Connection pooling** for WebSocket management

## Monitoring

The server provides comprehensive monitoring:

- **Health checks** at `/health`
- **Performance metrics** in logs
- **Player statistics** tracking
- **Anti-cheat violation** logging
- **Memory usage** monitoring

## Security

- **JWT authentication** for players
- **Rate limiting** on all endpoints
- **CORS protection** configurable
- **Input validation** on all data
- **Anti-cheat measures** prevent cheating

## Scaling

For high-traffic deployments:

1. **Enable Redis** for shared state
2. **Use load balancer** for multiple instances
3. **Configure database** for persistent data
4. **Monitor performance** metrics

## Development

### Running Tests
```bash
npm test
```

### Linting
```bash
npm run lint
```

### Building
```bash
npm run build
```

## Deployment on Render.com

1. **Fork this repository**
2. **Connect to Render.com**
3. **Create new Web Service**
4. **Set environment variables**
5. **Deploy!**

The server will automatically:
- Build from source
- Install dependencies
- Start on port 3000
- Handle graceful shutdowns
- Scale based on traffic

## Support

For issues and questions:
- Check the logs in Render dashboard
- Monitor the `/health` endpoint
- Review anti-cheat violations
- Check player connection status

## License

MIT License - see LICENSE file for details.
