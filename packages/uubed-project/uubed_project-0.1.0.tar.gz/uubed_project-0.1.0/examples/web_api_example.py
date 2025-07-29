#!/usr/bin/env python3
"""
Web API examples for uubed.

This module demonstrates building REST APIs with UUBED encoding, including:
- FastAPI integration
- Flask integration
- API design patterns
- Authentication and rate limiting
- WebSocket support
- OpenAPI documentation

Requirements:
    - uubed (core library)
    - numpy
    - Optional: fastapi, flask, uvicorn, pydantic
"""

import json
import time
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import asyncio
from collections import defaultdict

from uubed import (
    encode, decode, batch_encode,
    validate_embedding_input, UubedError
)

# Optional imports
try:
    from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field, validator
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Note: Install fastapi, uvicorn, and pydantic for FastAPI examples")

try:
    from flask import Flask, request, jsonify, Response
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Note: Install flask and flask-limiter for Flask examples")


# ============================================================================
# Common Models and Utilities
# ============================================================================

@dataclass
class APIResponse:
    """Standard API response structure."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True


class APIKeyManager:
    """Simple API key management."""
    
    def __init__(self):
        # In production, use proper database
        self.api_keys = {
            "demo-key-123": {
                "name": "Demo User",
                "created": datetime.utcnow(),
                "rate_limit": 100,
                "enabled": True
            }
        }
    
    def validate_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info."""
        user = self.api_keys.get(api_key)
        if user and user["enabled"]:
            return user
        return None


# ============================================================================
# FastAPI Implementation
# ============================================================================

def create_fastapi_app():
    """Create FastAPI application with UUBED endpoints."""
    if not FASTAPI_AVAILABLE:
        print("FastAPI not available. Showing example structure only.")
        return None
    
    # Pydantic models
    class EmbeddingRequest(BaseModel):
        """Request model for encoding embeddings."""
        embedding: List[float] = Field(..., description="Embedding vector")
        method: str = Field("auto", description="Encoding method")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
        
        @validator('embedding')
        def validate_embedding(cls, v):
            if not v or len(v) == 0:
                raise ValueError("Embedding cannot be empty")
            if len(v) > 10000:
                raise ValueError("Embedding too large (max 10000 dimensions)")
            return v
    
    class BatchEmbeddingRequest(BaseModel):
        """Request model for batch encoding."""
        embeddings: List[List[float]] = Field(..., description="List of embeddings")
        method: str = Field("auto", description="Encoding method")
        
        @validator('embeddings')
        def validate_embeddings(cls, v):
            if not v or len(v) == 0:
                raise ValueError("Embeddings list cannot be empty")
            if len(v) > 1000:
                raise ValueError("Batch too large (max 1000 embeddings)")
            return v
    
    class EncodingResponse(BaseModel):
        """Response model for encoded embeddings."""
        encoded: str
        method: str
        original_dim: int
        encoded_size: int
        compression_ratio: float
        encoding_time_ms: float
    
    # Create app
    app = FastAPI(
        title="UUBED Encoding API",
        description="High-performance embedding encoding service",
        version="1.0.0"
    )
    
    # Security
    security = HTTPBearer()
    key_manager = APIKeyManager()
    rate_limiter = RateLimiter(requests_per_minute=100)
    
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify API token."""
        token = credentials.credentials
        user = key_manager.validate_key(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Check rate limit
        if not rate_limiter.is_allowed(token):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        return user
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    # Single embedding encoding
    @app.post("/api/v1/encode", response_model=EncodingResponse)
    async def encode_embedding(
        request: EmbeddingRequest,
        user: Dict = Depends(verify_token)
    ):
        """Encode a single embedding."""
        try:
            start_time = time.time()
            
            # Convert to numpy array
            embedding = np.array(request.embedding, dtype=np.float32)
            embedding_uint8 = (embedding * 255).clip(0, 255).astype(np.uint8)
            
            # Validate
            validate_embedding_input(embedding_uint8, method=request.method)
            
            # Encode
            encoded = encode(embedding_uint8, method=request.method)
            
            # Calculate metrics
            encoding_time = (time.time() - start_time) * 1000
            compression_ratio = embedding_uint8.nbytes / len(encoded)
            
            return EncodingResponse(
                encoded=encoded,
                method=request.method,
                original_dim=len(embedding),
                encoded_size=len(encoded),
                compression_ratio=compression_ratio,
                encoding_time_ms=encoding_time
            )
            
        except UubedError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # Batch encoding
    @app.post("/api/v1/encode/batch")
    async def encode_batch(
        request: BatchEmbeddingRequest,
        background_tasks: BackgroundTasks,
        user: Dict = Depends(verify_token)
    ):
        """Encode multiple embeddings in batch."""
        try:
            # Convert to numpy
            embeddings = np.array(request.embeddings, dtype=np.float32)
            embeddings_uint8 = (embeddings * 255).clip(0, 255).astype(np.uint8)
            
            # Encode
            encoded_list = batch_encode(embeddings_uint8, method=request.method)
            
            # Log in background
            background_tasks.add_task(
                log_batch_request,
                user_id=user["name"],
                batch_size=len(embeddings),
                method=request.method
            )
            
            return {
                "success": True,
                "encoded": encoded_list,
                "count": len(encoded_list),
                "method": request.method
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # Streaming endpoint
    @app.post("/api/v1/encode/stream")
    async def encode_stream_endpoint(user: Dict = Depends(verify_token)):
        """Stream encoding for real-time processing."""
        async def generate():
            """Generate streaming response."""
            for i in range(10):  # Demo: generate 10 embeddings
                # Simulate real-time embedding
                embedding = np.random.rand(384).astype(np.float32)
                embedding_uint8 = (embedding * 255).astype(np.uint8)
                
                # Encode
                encoded = encode(embedding_uint8, method="shq64")
                
                # Yield result
                result = {
                    "index": i,
                    "encoded": encoded,
                    "timestamp": time.time()
                }
                
                yield f"data: {json.dumps(result)}\n\n"
                
                await asyncio.sleep(0.1)  # Simulate processing time
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    
    # WebSocket endpoint (would require additional setup)
    # @app.websocket("/ws/encode")
    # async def websocket_encode(websocket: WebSocket):
    #     await websocket.accept()
    #     # Handle real-time encoding via WebSocket
    
    def log_batch_request(user_id: str, batch_size: int, method: str):
        """Background task to log batch requests."""
        print(f"Batch request: user={user_id}, size={batch_size}, method={method}")
    
    return app


# ============================================================================
# Flask Implementation
# ============================================================================

def create_flask_app():
    """Create Flask application with UUBED endpoints."""
    if not FLASK_AVAILABLE:
        print("Flask not available. Showing example structure only.")
        return None
    
    app = Flask(__name__)
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"]
    )
    
    # API key validation decorator
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({
                    "error": "API key required",
                    "success": False
                }), 401
            
            # Validate key (simplified)
            if api_key != "demo-flask-key":
                return jsonify({
                    "error": "Invalid API key",
                    "success": False
                }), 401
            
            return f(*args, **kwargs)
        return decorated_function
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    @app.route('/api/v1/encode', methods=['POST'])
    @require_api_key
    @limiter.limit("50 per minute")
    def encode_endpoint():
        """Encode embedding endpoint."""
        try:
            data = request.get_json()
            
            if not data or 'embedding' not in data:
                return jsonify({
                    "error": "Missing embedding data",
                    "success": False
                }), 400
            
            # Process embedding
            embedding = np.array(data['embedding'], dtype=np.float32)
            embedding_uint8 = (embedding * 255).clip(0, 255).astype(np.uint8)
            
            method = data.get('method', 'auto')
            
            # Encode
            start_time = time.time()
            encoded = encode(embedding_uint8, method=method)
            encoding_time = (time.time() - start_time) * 1000
            
            response = APIResponse(
                success=True,
                data={
                    "encoded": encoded,
                    "method": method,
                    "encoding_time_ms": encoding_time,
                    "original_dim": len(embedding),
                    "encoded_size": len(encoded)
                }
            )
            
            return jsonify(response.to_dict())
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 500
    
    @app.route('/api/v1/encode/batch', methods=['POST'])
    @require_api_key
    @limiter.limit("10 per minute")
    def batch_encode_endpoint():
        """Batch encoding endpoint."""
        try:
            data = request.get_json()
            
            if not data or 'embeddings' not in data:
                return jsonify({
                    "error": "Missing embeddings data",
                    "success": False
                }), 400
            
            # Process batch
            embeddings = np.array(data['embeddings'], dtype=np.float32)
            embeddings_uint8 = (embeddings * 255).clip(0, 255).astype(np.uint8)
            
            method = data.get('method', 'auto')
            
            # Encode batch
            encoded_list = batch_encode(embeddings_uint8, method=method)
            
            return jsonify({
                "success": True,
                "encoded": encoded_list,
                "count": len(encoded_list),
                "method": method
            })
            
        except Exception as e:
            return jsonify({
                "error": str(e),
                "success": False
            }), 500
    
    # Server-sent events endpoint
    @app.route('/api/v1/encode/stream')
    @require_api_key
    def stream_encode():
        """Stream encoding endpoint."""
        def generate():
            """Generate streaming data."""
            for i in range(10):
                # Simulate embedding
                embedding = np.random.rand(256).astype(np.float32)
                embedding_uint8 = (embedding * 255).astype(np.uint8)
                
                # Encode
                encoded = encode(embedding_uint8, method="shq64")
                
                # Send event
                data = json.dumps({
                    "index": i,
                    "encoded": encoded,
                    "timestamp": time.time()
                })
                
                yield f"data: {data}\n\n"
                
                time.sleep(0.1)
        
        return Response(
            generate(),
            mimetype="text/event-stream"
        )
    
    return app


# ============================================================================
# API Client Examples
# ============================================================================

class UubedAPIClient:
    """Example client for UUBED API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None  # Would use requests.Session() in real implementation
    
    def encode_embedding(self, embedding: np.ndarray, method: str = "auto") -> Dict[str, Any]:
        """Encode single embedding via API."""
        # This is a mock implementation
        # Real implementation would use requests library
        
        url = f"{self.base_url}/api/v1/encode"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "embedding": embedding.tolist(),
            "method": method
        }
        
        # Simulate API call
        print(f"POST {url}")
        print(f"Headers: {headers}")
        print(f"Data: embedding of shape {embedding.shape}, method={method}")
        
        # Mock response
        return {
            "encoded": "mock_encoded_string",
            "method": method,
            "encoding_time_ms": 0.5
        }
    
    def encode_batch(self, embeddings: np.ndarray, method: str = "auto") -> List[str]:
        """Encode batch of embeddings."""
        url = f"{self.base_url}/api/v1/encode/batch"
        
        # Mock implementation
        print(f"POST {url}")
        print(f"Batch size: {len(embeddings)}")
        
        return ["mock_encoded_1", "mock_encoded_2", "..."]
    
    async def encode_stream(self, embedding_generator):
        """Stream encoding with async generator."""
        url = f"{self.base_url}/api/v1/encode/stream"
        
        print(f"Streaming to {url}")
        
        # Mock streaming
        async for embedding in embedding_generator:
            # Would send to API
            encoded = encode(embedding, method="shq64")
            yield encoded


# ============================================================================
# Example Usage and Best Practices
# ============================================================================

def api_design_best_practices():
    """Demonstrate API design best practices."""
    print("=== API Design Best Practices ===")
    
    print("\n1. Versioning:")
    print("   - Use versioned endpoints (/api/v1/...)")
    print("   - Support backward compatibility")
    print("   - Deprecate old versions gracefully")
    
    print("\n2. Authentication:")
    print("   - Use API keys or JWT tokens")
    print("   - Implement rate limiting per user")
    print("   - Log all API access")
    
    print("\n3. Error Handling:")
    print("   - Return consistent error format")
    print("   - Include error codes and messages")
    print("   - Log errors for debugging")
    
    print("\n4. Performance:")
    print("   - Implement caching where appropriate")
    print("   - Use async/await for I/O operations")
    print("   - Support batch operations")
    
    print("\n5. Documentation:")
    print("   - Auto-generate OpenAPI/Swagger docs")
    print("   - Include code examples")
    print("   - Document rate limits and quotas")
    
    # Example error response format
    error_response = {
        "success": False,
        "error": {
            "code": "INVALID_EMBEDDING",
            "message": "Embedding dimension must be between 1 and 10000",
            "details": {
                "provided_dim": 15000,
                "max_dim": 10000
            }
        },
        "timestamp": time.time()
    }
    
    print("\nExample error response:")
    print(json.dumps(error_response, indent=2))
    print()


def deployment_considerations():
    """Show deployment considerations for UUBED API."""
    print("=== Deployment Considerations ===")
    
    print("\n1. Containerization (Docker):")
    print("""
    FROM python:3.9-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install -r requirements.txt
    COPY . .
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    """)
    
    print("\n2. Environment Configuration:")
    env_config = {
        "UUBED_API_PORT": 8000,
        "UUBED_WORKERS": 4,
        "UUBED_MAX_BATCH_SIZE": 1000,
        "UUBED_RATE_LIMIT": 100,
        "UUBED_LOG_LEVEL": "INFO"
    }
    
    for key, value in env_config.items():
        print(f"   {key}={value}")
    
    print("\n3. Monitoring:")
    print("   - Request/response times")
    print("   - Error rates by endpoint")
    print("   - Memory and CPU usage")
    print("   - Active connections")
    
    print("\n4. Scaling:")
    print("   - Horizontal scaling with load balancer")
    print("   - Caching layer (Redis)")
    print("   - Queue for batch processing")
    print("   - CDN for static assets")
    
    print("\n5. Security:")
    print("   - HTTPS only")
    print("   - API key rotation")
    print("   - Request validation")
    print("   - SQL injection prevention")
    print()


def performance_optimization_example():
    """Show performance optimization techniques."""
    print("=== Performance Optimization ===")
    
    # Connection pooling example
    print("1. Connection Pooling:")
    print("""
    from asyncpg import create_pool
    
    async def init_db():
        return await create_pool(
            dsn='postgresql://user:pass@localhost/db',
            min_size=10,
            max_size=20
        )
    """)
    
    # Caching example
    print("\n2. Response Caching:")
    print("""
    from functools import lru_cache
    import hashlib
    
    @lru_cache(maxsize=1000)
    def cached_encode(embedding_hash: str, method: str):
        # Cache frequently encoded embeddings
        return encode_result
    """)
    
    # Batch processing optimization
    print("\n3. Batch Processing:")
    optimal_batch_sizes = {
        "shq64": 1000,
        "t8q64": 500,
        "zoq64": 2000,
        "eq64": 100
    }
    
    print("   Optimal batch sizes by method:")
    for method, size in optimal_batch_sizes.items():
        print(f"   - {method}: {size} embeddings")
    
    print("\n4. Async Processing:")
    print("   - Use async/await for I/O operations")
    print("   - Background tasks for logging")
    print("   - Async database queries")
    print("   - Non-blocking file operations")
    print()


def run_demo_server():
    """Run demo server (mock)."""
    print("=== Demo Server ===")
    
    if FASTAPI_AVAILABLE:
        print("\nTo run FastAPI server:")
        print("  uvicorn web_api_example:app --reload")
        print("\nAPI documentation available at:")
        print("  http://localhost:8000/docs")
        
        # Create app for export
        app = create_fastapi_app()
    
    elif FLASK_AVAILABLE:
        print("\nTo run Flask server:")
        print("  python web_api_example.py")
        print("  (Add app.run() at the end of the file)")
    
    else:
        print("\nNo web framework available.")
        print("Install fastapi or flask to run actual server.")
    
    print("\nExample API calls:")
    print("""
    # Single embedding
    curl -X POST http://localhost:8000/api/v1/encode \\
      -H "Authorization: Bearer demo-key-123" \\
      -H "Content-Type: application/json" \\
      -d '{"embedding": [0.1, 0.2, 0.3, ...], "method": "shq64"}'
    
    # Batch encoding
    curl -X POST http://localhost:8000/api/v1/encode/batch \\
      -H "Authorization: Bearer demo-key-123" \\
      -H "Content-Type: application/json" \\
      -d '{"embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...]], "method": "auto"}'
    """)
    print()


if __name__ == "__main__":
    print("UUBED Web API Examples")
    print("=" * 50)
    
    # Show examples
    api_design_best_practices()
    deployment_considerations()
    performance_optimization_example()
    run_demo_server()
    
    # Note about running the actual server
    print("\nTo run the actual API server:")
    print("1. Make sure FastAPI or Flask is installed")
    print("2. For FastAPI: uvicorn web_api_example:app --reload")
    print("3. For Flask: Add app.run() and run this file")
    
    # Export app for uvicorn if available
    if FASTAPI_AVAILABLE:
        app = create_fastapi_app()