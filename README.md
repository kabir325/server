# Server - Smart AI Load Balancer

The server component handles client registration, model assignment, and distributed query processing.

## 📦 Components

- **smart_load_balancer_server.py** - Main gRPC server (Port 50051)
- **smart_load_balancer_http_wrapper_v4.py** - HTTP API wrapper (Port 5001)
- **model_manager.py** - Model discovery and assignment
- **performance_evaluator.py** - System performance evaluation
- **rag_manager.py** - RAG (Retrieval Augmented Generation)
- **chat_manager.py** - Chat session management

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate gRPC Files
```bash
python generate_grpc_files.py
```

This creates:
- `load_balancer_pb2.py`
- `load_balancer_pb2_grpc.py`

## ▶️ Starting the Server

### Option 1: Start Both Services (Recommended)
```bash
python start_smart_loadbalancer.py
```

This starts:
- gRPC Server on port 50051
- HTTP Wrapper on port 5001

### Option 2: Start Separately

**Terminal 1 - gRPC Server:**
```bash
python smart_load_balancer_server.py
```

**Terminal 2 - HTTP Wrapper:**
```bash
python smart_load_balancer_http_wrapper_v4.py
```

### Option 3: Windows Batch File
```bash
start_server.bat
```

## 🔧 Configuration

### Ports
- **50051** - gRPC server (client communication)
- **5001** - HTTP wrapper (frontend communication)

### Environment
- Python 3.8+
- At least 4GB RAM
- Ports 50051 and 5001 available

## 📡 API Endpoints (HTTP Wrapper)

### Core Endpoints
- `GET /` - Service information
- `GET /health` - Health check
- `GET /status` - System status (clients, models)
- `POST /query` - Process AI query
- `POST /reassign` - Trigger model reassignment

### Chat Endpoints
- `GET /chat/sessions` - List chat sessions
- `POST /chat/sessions` - Create new session
- `GET /chat/sessions/<id>` - Get session history
- `DELETE /chat/sessions/<id>` - Delete session
- `PUT /chat/sessions/<id>/title` - Update session title

### RAG Endpoints
- `POST /rag/documents` - Add document
- `POST /rag/search` - Search documents
- `DELETE /rag/documents/<id>` - Delete document

## 🎯 How It Works

### 1. Client Registration
```
Client connects → Server evaluates hardware → Assigns optimal model
```

### 2. Query Processing
```
HTTP request → gRPC Server → Distribute to all clients → Aggregate responses
```

### 3. Model Assignment
- Evaluates client CPU, RAM, GPU
- Calculates performance score (0-100)
- Assigns model based on capability:
  - High performance (80+) → Large models (8B+)
  - Medium performance (60-80) → Medium models (3B)
  - Low performance (<60) → Small models (1B)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :50051
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:50051 | xargs kill -9
```

### gRPC Files Not Found
```bash
python generate_grpc_files.py
```

### No Clients Connecting
- Check firewall allows port 50051
- Verify server IP address
- Ensure server is running
- Check client logs for errors

### HTTP Wrapper Can't Connect to gRPC Server
- Ensure gRPC server is running first
- Check port 50051 is not blocked
- Verify localhost/127.0.0.1 connectivity

## 📊 Monitoring

### Server Terminal Output
```
✅ Client registered: client-HOSTNAME-abc123
   Performance Score: 85.0
   Assigned Model: llama3.2:3b
   Total Clients: 2
```

### Health Check
```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "healthy": true,
  "connected_clients": 2,
  "active_models": 2,
  "message": "Server healthy. 2 clients, 2 active models."
}
```

### Status Check
```bash
curl http://localhost:5001/status
```

Response:
```json
{
  "total_clients": 2,
  "active_clients": 2,
  "available_models": ["llama3.2:1b", "llama3.2:3b"],
  "healthy": true
}
```

## 🔐 Security Notes

**Development Mode:**
- No authentication
- CORS enabled for all origins
- HTTP (not HTTPS)

**For Production:**
- Add API authentication (JWT, API keys)
- Restrict CORS to specific origins
- Enable HTTPS/TLS
- Encrypt gRPC communication
- Add rate limiting
- Implement request validation

## 📝 Files

```
server/
├── smart_load_balancer_server.py          # Main gRPC server
├── smart_load_balancer_http_wrapper_v4.py # HTTP API
├── model_manager.py                       # Model management
├── performance_evaluator.py               # Performance scoring
├── rag_manager.py                         # RAG functionality
├── chat_manager.py                        # Chat management
├── load_balancer.proto                    # gRPC protocol
├── generate_grpc_files.py                 # Proto compiler
├── requirements.txt                       # Dependencies
├── setup.bat                              # Setup script
├── start_server.bat                       # Starter script
└── start_smart_loadbalancer.py            # Unified starter
```

## 🎓 Advanced Usage

### Interactive Server Mode
When running `smart_load_balancer_server.py` directly, you can:
- Enter prompts to test distributed processing
- Type `reassign` to trigger model reassignment
- Type `stats` to view system statistics
- Type `quit` to exit

### Custom Model Assignment
Edit `model_manager.py` to customize:
- Performance scoring algorithm
- Model assignment strategy
- Grouping logic

### Logging
Adjust logging level in the code:
```python
logging.basicConfig(level=logging.INFO)  # or DEBUG, WARNING, ERROR
```
