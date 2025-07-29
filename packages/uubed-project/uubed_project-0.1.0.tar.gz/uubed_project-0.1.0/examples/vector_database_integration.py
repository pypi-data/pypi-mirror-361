#!/usr/bin/env python3
"""
Vector database integration examples for uubed.

This module demonstrates how to integrate uubed with popular vector databases
including Pinecone, Weaviate, and Qdrant. Shows best practices for:
- Encoding embeddings before storage
- Efficient batch operations
- Metadata handling
- Search and retrieval patterns

Requirements:
    - uubed (core library)
    - numpy
    - Optional: pinecone-client, weaviate-client, qdrant-client
"""

import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

from uubed import encode, decode, batch_encode

# Optional imports with graceful fallback
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Note: Install pinecone-client for Pinecone examples")

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    print("Note: Install weaviate-client for Weaviate examples")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Note: Install qdrant-client for Qdrant examples")


@dataclass
class Document:
    """Sample document structure for examples."""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict[str, Any]


class UubedVectorDBAdapter:
    """Base adapter for integrating uubed with vector databases."""
    
    def __init__(self, encoding_method: str = "shq64"):
        self.encoding_method = encoding_method
        self.stats = {
            "encoded": 0,
            "decoded": 0,
            "storage_saved_bytes": 0
        }
    
    def encode_for_storage(self, embedding: np.ndarray) -> Dict[str, Any]:
        """Encode embedding for efficient storage."""
        # Convert to uint8
        if embedding.dtype != np.uint8:
            embedding = (embedding * 255).clip(0, 255).astype(np.uint8)
        
        # Encode
        encoded = encode(embedding, method=self.encoding_method)
        
        # Track stats
        original_size = embedding.nbytes
        encoded_size = len(encoded)
        self.stats["encoded"] += 1
        self.stats["storage_saved_bytes"] += (original_size - encoded_size)
        
        return {
            "encoded": encoded,
            "method": self.encoding_method,
            "original_dim": len(embedding),
            "encoded_size": encoded_size
        }
    
    def decode_from_storage(self, encoded_data: Dict[str, Any]) -> np.ndarray:
        """Decode embedding from storage format."""
        if encoded_data["method"] == "eq64":
            # Only eq64 supports exact decoding
            decoded_bytes = decode(encoded_data["encoded"])
            embedding = np.frombuffer(decoded_bytes, dtype=np.uint8)
        else:
            # For other methods, we'd need to store original or use approximation
            # This is a placeholder - in practice, you'd store originals for non-eq64
            embedding = np.zeros(encoded_data["original_dim"], dtype=np.uint8)
        
        self.stats["decoded"] += 1
        return embedding
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return {
            **self.stats,
            "compression_ratio": self.stats["storage_saved_bytes"] / 
                                (self.stats["encoded"] * 1536) if self.stats["encoded"] > 0 else 0
        }


def pinecone_integration_example():
    """
    Demonstrate integration with Pinecone vector database.
    
    Shows how to use uubed for efficient storage in Pinecone.
    """
    if not PINECONE_AVAILABLE:
        print("=== Pinecone Integration (Simulated) ===")
        print("Pinecone client not available. Showing example structure.")
    else:
        print("=== Pinecone Integration Example ===")
    
    # Simulated Pinecone operations
    class MockPineconeIndex:
        def __init__(self):
            self.vectors = {}
        
        def upsert(self, vectors):
            for v in vectors:
                self.vectors[v["id"]] = v
            return {"upserted_count": len(vectors)}
        
        def query(self, vector, top_k=5, include_metadata=True):
            # Simulate query results
            return {
                "matches": [
                    {"id": f"doc_{i}", "score": 0.9 - i*0.1, 
                     "metadata": {"encoded_embedding": "mock_encoded"}}
                    for i in range(min(top_k, 3))
                ]
            }
    
    # Initialize adapter
    adapter = UubedVectorDBAdapter(encoding_method="shq64")
    
    # Create sample documents
    documents = []
    for i in range(100):
        doc = Document(
            id=f"doc_{i}",
            content=f"This is document {i} with sample content.",
            embedding=np.random.rand(1536).astype(np.float32),
            metadata={"category": f"cat_{i % 5}", "timestamp": time.time()}
        )
        documents.append(doc)
    
    # Initialize Pinecone (or mock)
    if PINECONE_AVAILABLE:
        # Real Pinecone initialization would go here
        index = MockPineconeIndex()  # Using mock for example
    else:
        index = MockPineconeIndex()
    
    # Batch encode and upsert
    print("Encoding and storing documents...")
    vectors_to_upsert = []
    
    for doc in documents:
        # Encode embedding
        encoded_data = adapter.encode_for_storage(doc.embedding)
        
        # Prepare vector for Pinecone
        vector_data = {
            "id": doc.id,
            "values": doc.embedding.tolist(),  # Original for similarity search
            "metadata": {
                **doc.metadata,
                "content": doc.content[:100],  # Truncate for metadata
                "encoded_embedding": encoded_data["encoded"],  # Store encoded version
                "encoding_method": encoded_data["method"]
            }
        }
        vectors_to_upsert.append(vector_data)
    
    # Upsert in batches
    batch_size = 50
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i+batch_size]
        result = index.upsert(vectors=batch)
        print(f"  Upserted batch {i//batch_size + 1}: {result}")
    
    # Query example
    print("\nQuerying similar documents...")
    query_embedding = np.random.rand(1536).astype(np.float32)
    results = index.query(
        vector=query_embedding.tolist(),
        top_k=5,
        include_metadata=True
    )
    
    print(f"Found {len(results['matches'])} similar documents:")
    for match in results["matches"]:
        print(f"  - {match['id']}: score={match['score']:.3f}")
    
    # Show compression stats
    stats = adapter.get_compression_stats()
    print(f"\nCompression stats: {stats}")
    print()


def weaviate_integration_example():
    """
    Demonstrate integration with Weaviate vector database.
    
    Shows schema design and batch operations with uubed encoding.
    """
    if not WEAVIATE_AVAILABLE:
        print("=== Weaviate Integration (Simulated) ===")
        print("Weaviate client not available. Showing example structure.")
    else:
        print("=== Weaviate Integration Example ===")
    
    # Mock Weaviate client for demonstration
    class MockWeaviateClient:
        def __init__(self):
            self.objects = []
            
        class schema:
            @staticmethod
            def create_class(class_obj):
                print(f"  Created class: {class_obj['class']}")
        
        class batch:
            def __init__(self):
                self.objects = []
            
            def add_data_object(self, data_object, class_name, uuid=None):
                self.objects.append({
                    "data": data_object,
                    "class": class_name,
                    "uuid": uuid
                })
            
            def create_objects(self):
                return {"success": len(self.objects)}
        
        class query:
            @staticmethod
            def get(class_name):
                class QueryBuilder:
                    def with_near_vector(self, content):
                        return self
                    def with_limit(self, limit):
                        return self
                    def with_additional(self, fields):
                        return self
                    def do(self):
                        return {
                            "data": {
                                "Get": {
                                    "Document": [
                                        {"content": f"Sample doc {i}", "encoded_embedding": "encoded_data"}
                                        for i in range(3)
                                    ]
                                }
                            }
                        }
                return QueryBuilder()
    
    # Initialize adapter
    adapter = UubedVectorDBAdapter(encoding_method="t8q64")
    
    # Initialize Weaviate client
    client = MockWeaviateClient()
    
    # Define schema with encoded embedding storage
    document_schema = {
        "class": "Document",
        "description": "Document with uubed-encoded embeddings",
        "properties": [
            {
                "name": "content",
                "dataType": ["text"],
                "description": "Document content"
            },
            {
                "name": "encoded_embedding",
                "dataType": ["text"],
                "description": "UUBED-encoded embedding"
            },
            {
                "name": "encoding_method",
                "dataType": ["text"],
                "description": "Encoding method used"
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Document category"
            }
        ]
    }
    
    # Create schema
    print("Creating Weaviate schema...")
    client.schema.create_class(document_schema)
    
    # Batch import documents
    print("\nImporting documents with encoded embeddings...")
    batch = client.batch
    
    for i in range(50):
        # Create document
        embedding = np.random.rand(768).astype(np.float32)
        encoded_data = adapter.encode_for_storage(embedding)
        
        # Add to batch
        batch.add_data_object(
            data_object={
                "content": f"Document {i}: This is sample content for testing.",
                "encoded_embedding": encoded_data["encoded"],
                "encoding_method": encoded_data["method"],
                "category": f"category_{i % 3}"
            },
            class_name="Document"
        )
    
    # Execute batch
    result = batch.create_objects()
    print(f"Batch import result: {result}")
    
    # Query example
    print("\nQuerying with vector similarity...")
    query_vector = np.random.rand(768).astype(np.float32)
    
    result = client.query.get("Document").with_near_vector({
        "vector": query_vector.tolist()
    }).with_limit(5).with_additional(["distance"]).do()
    
    print("Query results:")
    if "data" in result and "Get" in result["data"]:
        for doc in result["data"]["Get"]["Document"]:
            print(f"  - Content: {doc['content'][:50]}...")
            print(f"    Encoded embedding: {doc['encoded_embedding'][:20]}...")
    print()


def qdrant_integration_example():
    """
    Demonstrate integration with Qdrant vector database.
    
    Shows collection management and payload optimization with uubed.
    """
    if not QDRANT_AVAILABLE:
        print("=== Qdrant Integration (Simulated) ===")
        print("Qdrant client not available. Showing example structure.")
    else:
        print("=== Qdrant Integration Example ===")
    
    # Mock Qdrant client
    class MockQdrantClient:
        def __init__(self):
            self.collections = {}
        
        def create_collection(self, collection_name, vectors_config):
            self.collections[collection_name] = {
                "config": vectors_config,
                "points": []
            }
            print(f"  Created collection: {collection_name}")
        
        def upsert(self, collection_name, points):
            if collection_name in self.collections:
                self.collections[collection_name]["points"].extend(points)
            return {"status": "ok", "count": len(points)}
        
        def search(self, collection_name, query_vector, limit=5):
            # Simulate search results
            return [
                {"id": i, "score": 0.9 - i*0.1, 
                 "payload": {"content": f"Doc {i}", "encoded": "encoded_data"}}
                for i in range(min(limit, 3))
            ]
    
    # Initialize adapter with compression focus
    adapter = UubedVectorDBAdapter(encoding_method="zoq64")
    
    # Initialize Qdrant client
    if QDRANT_AVAILABLE:
        # Real Qdrant client initialization would go here
        client = MockQdrantClient()
    else:
        client = MockQdrantClient()
    
    # Create collection
    print("Creating Qdrant collection...")
    collection_name = "documents"
    
    if QDRANT_AVAILABLE:
        vectors_config = VectorParams(size=384, distance=Distance.COSINE)
    else:
        vectors_config = {"size": 384, "distance": "Cosine"}
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=vectors_config
    )
    
    # Prepare and insert points
    print("\nInserting points with compressed payloads...")
    points = []
    
    for i in range(100):
        # Generate embedding
        embedding = np.random.rand(384).astype(np.float32)
        encoded_data = adapter.encode_for_storage(embedding)
        
        # Create point with encoded embedding in payload
        if QDRANT_AVAILABLE:
            point = PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "content": f"Document {i} with sample content",
                    "encoded_embedding": encoded_data["encoded"],
                    "encoding_method": encoded_data["method"],
                    "original_size": embedding.nbytes,
                    "compressed_size": len(encoded_data["encoded"]),
                    "compression_ratio": embedding.nbytes / len(encoded_data["encoded"])
                }
            )
        else:
            point = {
                "id": i,
                "vector": embedding.tolist(),
                "payload": {
                    "content": f"Document {i} with sample content",
                    "encoded_embedding": encoded_data["encoded"],
                    "encoding_method": encoded_data["method"],
                    "original_size": embedding.nbytes,
                    "compressed_size": len(encoded_data["encoded"]),
                    "compression_ratio": embedding.nbytes / len(encoded_data["encoded"])
                }
            }
        points.append(point)
    
    # Batch upsert
    batch_size = 50
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        result = client.upsert(
            collection_name=collection_name,
            points=batch
        )
        print(f"  Batch {i//batch_size + 1}: {result}")
    
    # Search example
    print("\nSearching with compressed storage...")
    query_embedding = np.random.rand(384).astype(np.float32)
    
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=5
    )
    
    print("Search results:")
    total_saved = 0
    for result in results:
        payload = result["payload"] if isinstance(result, dict) else result.payload
        saved = payload["original_size"] - payload["compressed_size"]
        total_saved += saved
        
        print(f"  - ID: {result['id'] if isinstance(result, dict) else result.id}")
        print(f"    Score: {result['score'] if isinstance(result, dict) else result.score:.3f}")
        print(f"    Compression: {payload['compression_ratio']:.2f}x")
        print(f"    Space saved: {saved} bytes")
    
    print(f"\nTotal space saved in results: {total_saved} bytes")
    
    # Show overall stats
    stats = adapter.get_compression_stats()
    print(f"\nOverall compression stats:")
    print(f"  Total encoded: {stats['encoded']}")
    print(f"  Total space saved: {stats['storage_saved_bytes']} bytes")
    print(f"  Average compression: {stats['compression_ratio']:.2f}x")
    print()


def hybrid_search_example():
    """
    Demonstrate hybrid search combining vector similarity and encoded metadata.
    
    Shows advanced search patterns using uubed encodings.
    """
    print("=== Hybrid Search Example ===")
    
    class HybridSearchEngine:
        def __init__(self, adapter: UubedVectorDBAdapter):
            self.adapter = adapter
            self.documents = []
            self.encoded_index = {}  # Map encoded strings to doc IDs
        
        def index_document(self, doc: Document):
            """Index document with multiple encoding strategies."""
            # Full embedding encoding for storage
            storage_encoding = self.adapter.encode_for_storage(doc.embedding)
            
            # Additional encodings for different search strategies
            embeddings_uint8 = (doc.embedding * 255).astype(np.uint8)
            
            encodings = {
                "storage": storage_encoding["encoded"],
                "similarity": encode(embeddings_uint8, method="shq64"),
                "features": encode(embeddings_uint8, method="t8q64"),
                "spatial": encode(embeddings_uint8[:min(len(embeddings_uint8), 512)], 
                                method="zoq64")
            }
            
            # Store document with encodings
            indexed_doc = {
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "encodings": encodings,
                "embedding": doc.embedding  # In practice, might not store this
            }
            
            self.documents.append(indexed_doc)
            
            # Build reverse indices
            for encoding_type, encoded_str in encodings.items():
                key = f"{encoding_type}:{encoded_str}"
                if key not in self.encoded_index:
                    self.encoded_index[key] = []
                self.encoded_index[key].append(doc.id)
        
        def search_by_encoding(self, query_embedding: np.ndarray, 
                             encoding_type: str = "similarity") -> List[str]:
            """Search using encoded similarity."""
            query_uint8 = (query_embedding * 255).astype(np.uint8)
            
            # Choose encoding method based on type
            method_map = {
                "similarity": "shq64",
                "features": "t8q64",
                "spatial": "zoq64"
            }
            
            query_encoded = encode(query_uint8, method=method_map.get(encoding_type, "shq64"))
            key = f"{encoding_type}:{query_encoded}"
            
            return self.encoded_index.get(key, [])
        
        def hybrid_search(self, query_embedding: np.ndarray, 
                         filters: Dict[str, Any] = None) -> List[Dict]:
            """Combine multiple search strategies."""
            results = {}
            
            # 1. Exact encoding match (very fast)
            exact_matches = self.search_by_encoding(query_embedding, "similarity")
            for doc_id in exact_matches:
                results[doc_id] = results.get(doc_id, 0) + 1.0
            
            # 2. Feature-based search
            feature_matches = self.search_by_encoding(query_embedding, "features")
            for doc_id in feature_matches:
                results[doc_id] = results.get(doc_id, 0) + 0.7
            
            # 3. Spatial search (for compatible embeddings)
            if len(query_embedding) >= 512:
                spatial_matches = self.search_by_encoding(
                    query_embedding[:512], "spatial"
                )
                for doc_id in spatial_matches:
                    results[doc_id] = results.get(doc_id, 0) + 0.5
            
            # 4. Apply metadata filters
            if filters:
                filtered_results = {}
                for doc in self.documents:
                    if doc["id"] in results:
                        match = all(
                            doc["metadata"].get(k) == v 
                            for k, v in filters.items()
                        )
                        if match:
                            filtered_results[doc["id"]] = results[doc["id"]]
                results = filtered_results
            
            # Sort by score and return
            sorted_results = sorted(
                results.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [
                {
                    "id": doc_id,
                    "score": score,
                    "document": next(d for d in self.documents if d["id"] == doc_id)
                }
                for doc_id, score in sorted_results[:10]
            ]
    
    # Create search engine
    adapter = UubedVectorDBAdapter(encoding_method="eq64")
    engine = HybridSearchEngine(adapter)
    
    # Index sample documents
    print("Indexing documents with multiple encoding strategies...")
    categories = ["tech", "science", "business"]
    
    for i in range(30):
        doc = Document(
            id=f"doc_{i}",
            content=f"Document {i} about {categories[i % 3]} topics.",
            embedding=np.random.rand(768).astype(np.float32),
            metadata={
                "category": categories[i % 3],
                "date": f"2024-01-{(i % 30) + 1:02d}",
                "importance": i % 5
            }
        )
        engine.index_document(doc)
    
    # Perform hybrid search
    print("\nPerforming hybrid search...")
    query = np.random.rand(768).astype(np.float32)
    
    # Search without filters
    results = engine.hybrid_search(query)
    print(f"\nTop results (no filters):")
    for r in results[:5]:
        print(f"  - {r['id']}: score={r['score']:.2f}, "
              f"category={r['document']['metadata']['category']}")
    
    # Search with filters
    filtered_results = engine.hybrid_search(
        query, 
        filters={"category": "tech"}
    )
    print(f"\nTop results (category='tech'):")
    for r in filtered_results[:5]:
        print(f"  - {r['id']}: score={r['score']:.2f}, "
              f"date={r['document']['metadata']['date']}")
    
    print()


def benchmark_storage_efficiency():
    """
    Benchmark storage efficiency across different vector databases.
    
    Compare storage requirements with and without uubed encoding.
    """
    print("=== Storage Efficiency Benchmark ===")
    
    # Test configurations
    embedding_dims = [384, 768, 1536, 3072]
    num_documents = 10000
    encoding_methods = ["eq64", "shq64", "t8q64", "zoq64"]
    
    results = []
    
    for dim in embedding_dims:
        print(f"\nTesting dimension: {dim}")
        
        # Generate test embeddings
        embeddings = np.random.rand(num_documents, dim).astype(np.float32)
        
        # Calculate baseline storage
        baseline_storage = embeddings.nbytes
        baseline_mb = baseline_storage / (1024 * 1024)
        
        print(f"  Baseline storage: {baseline_mb:.2f} MB")
        
        for method in encoding_methods:
            adapter = UubedVectorDBAdapter(encoding_method=method)
            
            # Encode all embeddings
            encoded_sizes = []
            start_time = time.time()
            
            for emb in embeddings:
                encoded_data = adapter.encode_for_storage(emb)
                encoded_sizes.append(len(encoded_data["encoded"]))
            
            encoding_time = time.time() - start_time
            
            # Calculate compressed storage
            compressed_storage = sum(encoded_sizes)
            compressed_mb = compressed_storage / (1024 * 1024)
            compression_ratio = baseline_storage / compressed_storage
            
            # Store results
            result = {
                "dimension": dim,
                "method": method,
                "baseline_mb": baseline_mb,
                "compressed_mb": compressed_mb,
                "compression_ratio": compression_ratio,
                "encoding_time": encoding_time,
                "throughput": num_documents / encoding_time
            }
            results.append(result)
            
            print(f"  {method}: {compressed_mb:.2f} MB "
                  f"({compression_ratio:.2f}x compression, "
                  f"{encoding_time:.2f}s)")
    
    # Summary table
    print("\n" + "="*70)
    print("Storage Efficiency Summary")
    print("="*70)
    print(f"{'Dim':>6} {'Method':>8} {'Original':>10} {'Compressed':>12} "
          f"{'Ratio':>8} {'Speed':>10}")
    print("-"*70)
    
    for r in results:
        print(f"{r['dimension']:>6} {r['method']:>8} "
              f"{r['baseline_mb']:>9.1f}MB {r['compressed_mb']:>11.1f}MB "
              f"{r['compression_ratio']:>7.1f}x "
              f"{r['throughput']:>8.0f}/s")
    
    print()


if __name__ == "__main__":
    print("UUBED Vector Database Integration Examples")
    print("=" * 50)
    
    # Run examples
    pinecone_integration_example()
    weaviate_integration_example()
    qdrant_integration_example()
    hybrid_search_example()
    benchmark_storage_efficiency()
    
    print("\nAll vector database examples completed!")