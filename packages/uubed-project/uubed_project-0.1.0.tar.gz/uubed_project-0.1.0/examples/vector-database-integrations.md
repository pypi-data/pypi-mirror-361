# Vector Database Integration Examples

This document provides practical examples of integrating uubed position-safe encoding with major vector databases. These examples demonstrate how to leverage QuadB64 encoding to prevent substring pollution while maintaining high performance.

## Table of Contents

1. [Pinecone Integration](#pinecone-integration)
2. [Weaviate Integration](#weaviate-integration)
3. [Qdrant Integration](#qdrant-integration)
4. [ChromaDB Integration](#chromadb-integration)
5. [Elasticsearch Integration](#elasticsearch-integration)
6. [Performance Comparisons](#performance-comparisons)
7. [Best Practices](#best-practices)

## Pinecone Integration

### Basic Setup with Encoded Metadata

```python
import pinecone
import numpy as np
from uubed import encode

# Initialize Pinecone
pinecone.init(api_key="your-api-key", environment="your-env")

class UubedPineconeIndex:
    def __init__(self, index_name: str, dimension: int = 1024):
        self.index_name = index_name
        self.dimension = dimension
        
        # Create or connect to index
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine"
            )
        
        self.index = pinecone.Index(index_name)
    
    def upsert_with_encoding(self, documents: List[Dict[str, Any]]):
        """
        Upsert documents with uubed encoding stored in metadata.
        
        Args:
            documents: List of dicts with 'id', 'vector', and 'metadata'
        """
        vectors_to_upsert = []
        
        for doc in documents:
            # Original vector for Pinecone search
            vector = doc['vector']
            
            # Encode vector with multiple QuadB64 methods
            encoded_metadata = {
                'eq64_full': encode(vector, method='eq64'),  # Full precision
                'shq64_hash': encode(vector, method='shq64'),  # Similarity hash
                't8q64_sparse': encode(vector, method='t8q64'),  # Top-k indices
                'zoq64_spatial': encode(vector, method='zoq64')  # Z-order spatial
            }
            
            # Merge with original metadata
            combined_metadata = {**doc.get('metadata', {}), **encoded_metadata}
            
            vectors_to_upsert.append({
                'id': doc['id'],
                'values': vector,
                'metadata': combined_metadata
            })
        
        # Batch upsert for efficiency
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)
    
    def search_with_filters(self, query_vector: np.ndarray, 
                           encoding_filter: str = None, top_k: int = 10):
        """
        Search with optional encoding-based filters.
        
        Args:
            query_vector: Query embedding
            encoding_filter: Filter by encoded similarity (e.g., 'shq64_hash')
            top_k: Number of results
        """
        # Get initial results
        results = self.index.query(
            vector=query_vector.tolist(),
            top_k=top_k * 2,  # Get more for filtering
            include_metadata=True
        )
        
        if encoding_filter and encoding_filter in ['shq64_hash']:
            # Filter using encoded similarity
            query_encoded = encode(query_vector, method='shq64')
            
            filtered_results = []
            for match in results.matches:
                if encoding_filter in match.metadata:
                    # Simple string similarity for encoded values
                    stored_encoded = match.metadata[encoding_filter]
                    if hamming_similarity(query_encoded, stored_encoded) > 0.7:
                        filtered_results.append(match)
            
            return filtered_results[:top_k]
        
        return results.matches[:top_k]

# Usage Example
def pinecone_example():
    # Sample document embeddings (from OpenAI, etc.)
    documents = [
        {
            'id': 'doc_1',
            'vector': np.random.rand(1024).tolist(),
            'metadata': {
                'title': 'Machine Learning Basics',
                'category': 'education',
                'text': 'Introduction to neural networks...'
            }
        },
        {
            'id': 'doc_2', 
            'vector': np.random.rand(1024).tolist(),
            'metadata': {
                'title': 'Advanced Deep Learning',
                'category': 'education',
                'text': 'Transformer architectures and attention...'
            }
        }
    ]
    
    # Initialize index with uubed integration
    index = UubedPineconeIndex("uubed-demo", dimension=1024)
    
    # Upsert documents with encoding
    index.upsert_with_encoding(documents)
    
    # Search with encoding filters
    query = np.random.rand(1024)
    results = index.search_with_filters(
        query, 
        encoding_filter='shq64_hash',
        top_k=5
    )
    
    print(f"Found {len(results)} similar documents")
    for result in results:
        print(f"- {result.metadata['title']} (score: {result.score:.3f})")
```

### Advanced: Progressive Retrieval with Matryoshka Embeddings

```python
class MatryoshkaPineconeIndex(UubedPineconeIndex):
    """Enhanced Pinecone integration with Matryoshka/Mq64 support."""
    
    def upsert_matryoshka(self, documents: List[Dict[str, Any]]):
        """Upsert with Matryoshka embedding support."""
        vectors_to_upsert = []
        
        for doc in documents:
            full_vector = doc['vector']  # Full 1024D embedding
            
            # Extract progressive embeddings (Matryoshka style)
            embeddings_by_dim = {
                64: full_vector[:64],
                128: full_vector[:128], 
                256: full_vector[:256],
                512: full_vector[:512],
                1024: full_vector
            }
            
            # Encode each dimension level
            encoded_hierarchy = {}
            for dims, embedding in embeddings_by_dim.items():
                encoded_hierarchy[f'mq64_{dims}d'] = encode(
                    np.array(embedding), 
                    method='eq64'
                )
            
            metadata = {
                **doc.get('metadata', {}),
                **encoded_hierarchy,
                'matryoshka_levels': [64, 128, 256, 512, 1024]
            }
            
            vectors_to_upsert.append({
                'id': doc['id'],
                'values': full_vector,
                'metadata': metadata
            })
        
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self.index.upsert(vectors=batch)
    
    def progressive_search(self, query_vector: np.ndarray, top_k: int = 10):
        """
        Progressive search: start with low dimensions, refine with higher.
        """
        # Phase 1: Coarse search with 128D embeddings
        coarse_results = self.index.query(
            vector=query_vector[:128].tolist(),
            top_k=top_k * 5,  # Get more candidates
            include_metadata=True
        )
        
        # Phase 2: Re-rank with full 1024D embeddings
        refined_results = []
        query_full = query_vector[:1024] if len(query_vector) >= 1024 else query_vector
        
        for result in coarse_results.matches:
            # Get full embedding from metadata (if using Mq64 in future)
            # For now, use the stored vector
            stored_vector = result.values if hasattr(result, 'values') else []
            
            if stored_vector:
                # Compute refined similarity
                similarity = np.dot(query_full, stored_vector) / (
                    np.linalg.norm(query_full) * np.linalg.norm(stored_vector)
                )
                
                refined_results.append({
                    'id': result.id,
                    'score': similarity,
                    'metadata': result.metadata
                })
        
        # Sort by refined score and return top results
        refined_results.sort(key=lambda x: x['score'], reverse=True)
        return refined_results[:top_k]
```

## Weaviate Integration

### Schema Setup with QuadB64 Properties

```python
import weaviate
from uubed import encode, decode

class UubedWeaviateClient:
    def __init__(self, url: str = "http://localhost:8080"):
        self.client = weaviate.Client(url)
        self.setup_schema()
    
    def setup_schema(self):
        """Setup Weaviate schema with uubed encoding properties."""
        
        # Define class schema with encoding properties
        schema = {
            "class": "UubedDocument",
            "description": "Document with QuadB64 encoded embeddings",
            "vectorizer": "none",  # We'll provide vectors directly
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Document title"
                },
                {
                    "name": "content", 
                    "dataType": ["text"],
                    "description": "Document content"
                },
                {
                    "name": "eq64_encoding",
                    "dataType": ["text"],
                    "description": "Full precision QuadB64 encoding"
                },
                {
                    "name": "shq64_hash",
                    "dataType": ["text"], 
                    "description": "SimHash QuadB64 encoding"
                },
                {
                    "name": "t8q64_indices",
                    "dataType": ["text"],
                    "description": "Top-8 indices QuadB64 encoding"
                },
                {
                    "name": "zoq64_spatial",
                    "dataType": ["text"],
                    "description": "Z-order spatial QuadB64 encoding"
                },
                {
                    "name": "encoding_version",
                    "dataType": ["text"],
                    "description": "uubed version used for encoding"
                }
            ]
        }
        
        # Create schema if it doesn't exist
        if not self.client.schema.exists("UubedDocument"):
            self.client.schema.create_class(schema)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents with QuadB64 encoding."""
        
        with self.client.batch as batch:
            batch.batch_size = 100
            
            for doc in documents:
                vector = np.array(doc['vector'])
                
                # Generate all encoding variants
                encodings = {
                    'eq64_encoding': encode(vector, method='eq64'),
                    'shq64_hash': encode(vector, method='shq64'),
                    't8q64_indices': encode(vector, method='t8q64'),
                    'zoq64_spatial': encode(vector, method='zoq64')
                }
                
                # Prepare document properties
                properties = {
                    'title': doc.get('title', ''),
                    'content': doc.get('content', ''),
                    'encoding_version': '1.0.0',
                    **encodings
                }
                
                # Add to batch
                batch.add_data_object(
                    data_object=properties,
                    class_name="UubedDocument",
                    uuid=doc.get('id'),
                    vector=vector.tolist()
                )
    
    def search_by_encoding(self, encoding_type: str, encoding_value: str, 
                          limit: int = 10):
        """
        Search documents by encoded value (exact match).
        Useful for finding documents with specific encoding patterns.
        """
        
        query = (
            self.client.query
            .get("UubedDocument", ["title", "content", "eq64_encoding"])
            .where({
                "path": [encoding_type],
                "operator": "Equal", 
                "valueText": encoding_value
            })
            .limit(limit)
        )
        
        return query.do()
    
    def hybrid_search(self, query_vector: np.ndarray, query_text: str = None,
                     top_k: int = 10):
        """
        Hybrid search combining vector similarity and text search.
        Uses QuadB64 encodings for additional filtering.
        """
        
        # Encode query vector
        query_encodings = {
            'shq64': encode(query_vector, method='shq64'),
            't8q64': encode(query_vector, method='t8q64')
        }
        
        # Build near vector query
        near_vector = {"vector": query_vector.tolist()}
        
        query_builder = (
            self.client.query
            .get("UubedDocument", [
                "title", "content", "eq64_encoding", 
                "shq64_hash", "_additional {distance}"
            ])
            .with_near_vector(near_vector)
            .with_limit(top_k)
        )
        
        # Add text search if provided
        if query_text:
            query_builder = query_builder.with_where({
                "operator": "Like",
                "path": ["content"],
                "valueText": f"*{query_text}*"
            })
        
        results = query_builder.do()
        
        # Post-process with encoding similarity
        if 'data' in results and 'Get' in results['data']:
            documents = results['data']['Get']['UubedDocument']
            
            for doc in documents:
                if 'shq64_hash' in doc:
                    # Compute encoding similarity
                    stored_hash = doc['shq64_hash']
                    query_hash = query_encodings['shq64']
                    
                    # Simple Hamming distance for demo
                    similarity = hamming_similarity(stored_hash, query_hash)
                    doc['encoding_similarity'] = similarity
        
        return results

# Usage Example
def weaviate_example():
    client = UubedWeaviateClient()
    
    # Sample documents
    documents = [
        {
            'id': 'doc_1',
            'title': 'Introduction to Vector Databases',
            'content': 'Vector databases are specialized systems...',
            'vector': np.random.rand(768)  # Typical embedding size
        },
        {
            'id': 'doc_2',
            'title': 'QuadB64 Encoding Explained', 
            'content': 'Position-safe encoding prevents substring pollution...',
            'vector': np.random.rand(768)
        }
    ]
    
    # Add documents with encoding
    client.add_documents(documents)
    
    # Hybrid search
    query_vector = np.random.rand(768)
    results = client.hybrid_search(
        query_vector=query_vector,
        query_text="vector database",
        top_k=5
    )
    
    print("Hybrid search results:")
    for doc in results['data']['Get']['UubedDocument']:
        print(f"- {doc['title']} (distance: {doc['_additional']['distance']:.3f})")
```

## Qdrant Integration

### Collection Setup with Payload Encoding

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models
from uubed import encode
import numpy as np

class UubedQdrantClient:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "uubed_documents"
        self.setup_collection()
    
    def setup_collection(self):
        """Setup Qdrant collection optimized for uubed encodings."""
        
        # Check if collection exists
        collections = self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            
            # Create collection with appropriate configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Embedding dimension
                    distance=models.Distance.COSINE
                ),
                # Optimize for payload (metadata) queries
                optimizers_config=models.OptimizersConfig(
                    indexing_threshold=1000,
                    payload_indexing_threshold=1000
                )
            )
    
    def upsert_with_encoding(self, documents: List[Dict[str, Any]]):
        """Upsert documents with comprehensive QuadB64 encoding."""
        
        points = []
        
        for i, doc in enumerate(documents):
            vector = np.array(doc['vector'])
            
            # Generate complete encoding suite
            encoding_payload = {
                'eq64_full': encode(vector, method='eq64'),
                'shq64_hash': encode(vector, method='shq64'), 
                't8q64_sparse': encode(vector, method='t8q64'),
                'zoq64_spatial': encode(vector, method='zoq64'),
                
                # Metadata
                'title': doc.get('title', ''),
                'content': doc.get('content', ''),
                'category': doc.get('category', ''),
                'timestamp': doc.get('timestamp', ''),
                
                # Encoding metadata
                'uubed_version': '1.0.0',
                'encoding_timestamp': time.time(),
                'vector_norm': float(np.linalg.norm(vector)),
                'vector_mean': float(np.mean(vector)),
                'vector_std': float(np.std(vector))
            }
            
            point = models.PointStruct(
                id=doc.get('id', i),
                vector=vector.tolist(),
                payload=encoding_payload
            )
            points.append(point)
        
        # Batch upsert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def search_with_encoding_filter(self, query_vector: np.ndarray,
                                   encoding_filter: Dict[str, str] = None,
                                   top_k: int = 10):
        """
        Search with optional QuadB64 encoding filters.
        
        Args:
            query_vector: Query embedding
            encoding_filter: Dict with encoding type and pattern
            top_k: Number of results
        """
        
        # Build filter conditions
        filter_conditions = []
        
        if encoding_filter:
            for encoding_type, pattern in encoding_filter.items():
                if encoding_type in ['eq64_full', 'shq64_hash', 't8q64_sparse', 'zoq64_spatial']:
                    # Filter by encoding pattern (exact match or prefix)
                    filter_conditions.append(
                        models.FieldCondition(
                            key=encoding_type,
                            match=models.MatchText(text=pattern)
                        )
                    )
        
        # Combine filters
        query_filter = None
        if filter_conditions:
            query_filter = models.Filter(
                must=filter_conditions
            )
        
        # Perform search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            query_filter=query_filter,
            limit=top_k,
            with_payload=True
        )
        
        return search_result
    
    def find_similar_encodings(self, reference_encoding: str, 
                              encoding_type: str = 'shq64_hash',
                              similarity_threshold: float = 0.8):
        """
        Find documents with similar QuadB64 encodings.
        Useful for deduplication or finding near-duplicates.
        """
        
        # Search all documents (could be optimized with indexing)
        all_points = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,  # Adjust based on collection size
            with_payload=True
        )
        
        similar_docs = []
        
        for point in all_points[0]:  # all_points returns (points, next_page_offset)
            if encoding_type in point.payload:
                stored_encoding = point.payload[encoding_type]
                
                # Compute similarity (Hamming distance for demo)
                similarity = hamming_similarity(reference_encoding, stored_encoding)
                
                if similarity >= similarity_threshold:
                    similar_docs.append({
                        'id': point.id,
                        'similarity': similarity,
                        'payload': point.payload
                    })
        
        # Sort by similarity
        similar_docs.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_docs

# Utility function for demo
def hamming_similarity(s1: str, s2: str) -> float:
    """Compute normalized Hamming similarity between two strings."""
    if len(s1) != len(s2):
        return 0.0
    
    matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
    return matches / len(s1)

# Usage Example
def qdrant_example():
    client = UubedQdrantClient()
    
    # Sample documents with embeddings
    documents = [
        {
            'id': 1,
            'title': 'Vector Search Fundamentals',
            'content': 'Understanding the basics of vector similarity search...',
            'category': 'education',
            'vector': np.random.rand(1024)
        },
        {
            'id': 2,
            'title': 'Advanced Retrieval Techniques',
            'content': 'Hybrid search combining dense and sparse vectors...',
            'category': 'research',
            'vector': np.random.rand(1024)
        }
    ]
    
    # Upload with encoding
    client.upsert_with_encoding(documents)
    
    # Search with encoding filter
    query = np.random.rand(1024)
    results = client.search_with_encoding_filter(
        query_vector=query,
        encoding_filter={'category': 'education'},  # Category filter for demo
        top_k=5
    )
    
    print("Search results:")
    for result in results:
        print(f"- ID: {result.id}, Score: {result.score:.3f}")
        print(f"  Title: {result.payload['title']}")
        print(f"  ShQ64: {result.payload['shq64_hash'][:20]}...")
```

## ChromaDB Integration

### Simple Local Setup

```python
import chromadb
from chromadb.config import Settings
from uubed import encode
import numpy as np

class UubedChromaClient:
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Initialize ChromaDB with persistence
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="uubed_documents",
            metadata={"description": "Documents with QuadB64 encoding"}
        )
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents with QuadB64 encoding in metadata."""
        
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []
        
        for doc in documents:
            vector = np.array(doc['vector'])
            
            # Encode with multiple methods
            encoding_metadata = {
                'eq64_encoding': encode(vector, method='eq64'),
                'shq64_hash': encode(vector, method='shq64'),
                't8q64_indices': encode(vector, method='t8q64'),
                'zoq64_spatial': encode(vector, method='zoq64'),
                
                # Document metadata
                'title': doc.get('title', ''),
                'category': doc.get('category', ''),
                'source': doc.get('source', ''),
                'uubed_version': '1.0.0'
            }
            
            ids.append(str(doc.get('id', len(ids))))
            embeddings.append(vector.tolist())
            metadatas.append(encoding_metadata)
            documents_text.append(doc.get('content', ''))
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents_text
        )
    
    def query_with_encoding(self, query_vector: np.ndarray, 
                           where_filter: Dict[str, str] = None,
                           n_results: int = 10):
        """Query with optional metadata filtering on encodings."""
        
        results = self.collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=n_results,
            where=where_filter,
            include=['metadatas', 'documents', 'distances']
        )
        
        return results
    
    def find_by_encoding_pattern(self, encoding_type: str, 
                                pattern: str, exact_match: bool = True):
        """Find documents by encoding pattern."""
        
        # Get all documents (ChromaDB doesn't support regex filtering directly)
        all_results = self.collection.get(
            include=['metadatas', 'documents']
        )
        
        matching_docs = []
        
        for i, metadata in enumerate(all_results['metadatas']):
            if encoding_type in metadata:
                stored_encoding = metadata[encoding_type]
                
                if exact_match:
                    if stored_encoding == pattern:
                        matching_docs.append({
                            'id': all_results['ids'][i],
                            'document': all_results['documents'][i],
                            'metadata': metadata
                        })
                else:
                    # Substring match
                    if pattern in stored_encoding:
                        matching_docs.append({
                            'id': all_results['ids'][i],
                            'document': all_results['documents'][i], 
                            'metadata': metadata
                        })
        
        return matching_docs

# Usage Example
def chromadb_example():
    client = UubedChromaClient()
    
    # Sample documents
    documents = [
        {
            'id': 'doc_1',
            'title': 'Machine Learning Guide',
            'content': 'A comprehensive guide to machine learning concepts...',
            'category': 'education',
            'source': 'internal',
            'vector': np.random.rand(384)  # Smaller embedding for demo
        },
        {
            'id': 'doc_2',
            'title': 'Deep Learning Research',
            'content': 'Latest advances in deep learning architectures...',
            'category': 'research', 
            'source': 'arxiv',
            'vector': np.random.rand(384)
        }
    ]
    
    # Add documents
    client.add_documents(documents)
    
    # Query with filter
    query_vector = np.random.rand(384)
    results = client.query_with_encoding(
        query_vector=query_vector,
        where_filter={'category': 'education'},
        n_results=5
    )
    
    print("Query results:")
    for i, distance in enumerate(results['distances'][0]):
        metadata = results['metadatas'][0][i]
        print(f"- {metadata['title']} (distance: {distance:.3f})")
        print(f"  ShQ64: {metadata['shq64_hash'][:15]}...")
```

## Performance Comparisons

### Benchmark Suite

```python
import time
import statistics
from typing import List, Dict, Any

def benchmark_vector_db_integration():
    """Benchmark uubed integration across different vector databases."""
    
    # Generate test data
    num_docs = 1000
    embedding_dim = 768
    
    test_documents = []
    for i in range(num_docs):
        test_documents.append({
            'id': f'doc_{i}',
            'title': f'Document {i}',
            'content': f'Content for document {i}...',
            'vector': np.random.rand(embedding_dim)
        })
    
    query_vectors = [np.random.rand(embedding_dim) for _ in range(10)]
    
    # Benchmark results
    results = {}
    
    # Test each database integration
    databases = {
        'pinecone': UubedPineconeIndex,
        'qdrant': UubedQdrantClient,
        'chroma': UubedChromaClient
        # 'weaviate': UubedWeaviateClient  # Requires running instance
    }
    
    for db_name, db_class in databases.items():
        print(f"Benchmarking {db_name}...")
        
        try:
            # Initialize database
            if db_name == 'pinecone':
                # Skip Pinecone if not configured
                continue
            elif db_name == 'qdrant':
                db = db_class()
            elif db_name == 'chroma':
                db = db_class()
            
            # Benchmark insertion
            start_time = time.time()
            if hasattr(db, 'add_documents'):
                db.add_documents(test_documents)
            elif hasattr(db, 'upsert_with_encoding'):
                db.upsert_with_encoding(test_documents)
            insertion_time = time.time() - start_time
            
            # Benchmark queries
            query_times = []
            for query_vector in query_vectors:
                start_time = time.time()
                
                if hasattr(db, 'query_with_encoding'):
                    db.query_with_encoding(query_vector, n_results=10)
                elif hasattr(db, 'search_with_encoding_filter'):
                    db.search_with_encoding_filter(query_vector, top_k=10)
                
                query_times.append(time.time() - start_time)
            
            avg_query_time = statistics.mean(query_times)
            
            results[db_name] = {
                'insertion_time': insertion_time,
                'avg_query_time': avg_query_time,
                'docs_per_second_insert': num_docs / insertion_time,
                'queries_per_second': 1 / avg_query_time
            }
            
        except Exception as e:
            print(f"Error benchmarking {db_name}: {e}")
            results[db_name] = {'error': str(e)}
    
    return results

# Storage efficiency analysis
def analyze_storage_efficiency():
    """Analyze storage efficiency of QuadB64 encodings."""
    
    # Generate test embeddings
    test_sizes = [64, 128, 256, 512, 1024]
    encoding_methods = ['eq64', 'shq64', 't8q64', 'zoq64']
    
    efficiency_results = {}
    
    for size in test_sizes:
        test_embedding = np.random.rand(size).astype(np.float32)
        
        # Original size in bytes
        original_size = test_embedding.nbytes
        
        method_results = {}
        for method in encoding_methods:
            encoded = encode(test_embedding, method=method)
            encoded_size = len(encoded.encode('utf-8'))
            
            method_results[method] = {
                'encoded_size_bytes': encoded_size,
                'compression_ratio': original_size / encoded_size,
                'size_reduction_percent': (1 - encoded_size / original_size) * 100
            }
        
        efficiency_results[f'{size}d'] = {
            'original_size': original_size,
            'methods': method_results
        }
    
    return efficiency_results
```

## Best Practices

### 1. Encoding Method Selection

```python
def select_optimal_encoding(embedding: np.ndarray, use_case: str) -> str:
    """
    Select optimal QuadB64 encoding method based on use case.
    
    Args:
        embedding: Input embedding vector
        use_case: 'archival', 'similarity', 'sparse', 'spatial'
    
    Returns:
        Recommended encoding method
    """
    
    embedding_size = len(embedding)
    sparsity = np.sum(embedding == 0) / len(embedding)
    
    if use_case == 'archival':
        # Need exact reconstruction
        return 'eq64'
    
    elif use_case == 'similarity':
        # Fast similarity search
        return 'shq64'
    
    elif use_case == 'sparse' or sparsity > 0.5:
        # Sparse embeddings or need top features
        return 't8q64'
    
    elif use_case == 'spatial':
        # Spatial/geographic data or need prefix matching
        return 'zoq64'
    
    else:
        # Default: balance between accuracy and efficiency
        if embedding_size <= 256:
            return 'eq64'  # Small enough for full precision
        else:
            return 'shq64'  # Large enough to benefit from hashing
```

### 2. Metadata Organization

```python
def organize_encoding_metadata(vector: np.ndarray, 
                              document_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Organize QuadB64 encodings in metadata for optimal search performance.
    """
    
    # Generate encodings
    encodings = {
        'uubed_eq64': encode(vector, method='eq64'),
        'uubed_shq64': encode(vector, method='shq64'),
        'uubed_t8q64': encode(vector, method='t8q64'),
        'uubed_zoq64': encode(vector, method='zoq64')
    }
    
    # Add encoding metadata
    encoding_metadata = {
        'uubed_version': '1.0.0',
        'encoding_timestamp': time.time(),
        'vector_dimension': len(vector),
        'vector_norm': float(np.linalg.norm(vector)),
        'primary_encoding': 'uubed_shq64',  # Default for similarity search
        
        # Statistical properties for optimization
        'vector_mean': float(np.mean(vector)),
        'vector_std': float(np.std(vector)),
        'vector_sparsity': float(np.sum(vector == 0) / len(vector))
    }
    
    # Combine all metadata
    return {
        **document_metadata,
        **encodings,
        **encoding_metadata
    }
```

### 3. Error Handling and Validation

```python
def validate_encoding_integrity(original_vector: np.ndarray, 
                               encoded_string: str,
                               encoding_method: str) -> bool:
    """
    Validate that encoding/decoding maintains data integrity.
    """
    
    try:
        # Only eq64 supports roundtrip for validation
        if encoding_method == 'eq64':
            decoded = decode(encoded_string)
            decoded_vector = np.frombuffer(decoded, dtype=np.uint8)
            
            # Check if roundtrip is successful
            return np.array_equal(original_vector, decoded_vector)
        
        else:
            # For other methods, validate encoding format
            return validate_encoding_format(encoded_string, encoding_method)
    
    except Exception as e:
        print(f"Validation error: {e}")
        return False

def validate_encoding_format(encoded: str, method: str) -> bool:
    """Validate encoding format without decoding."""
    
    if method == 'eq64':
        # Should have dots every 8 characters
        return '.' in encoded and len(encoded.replace('.', '')) % 8 == 0
    
    elif method == 'shq64':
        # Should be exactly 16 characters
        return len(encoded) == 16
    
    elif method == 't8q64':
        # Should be exactly 16 characters (8 indices * 2 chars each)
        return len(encoded) == 16
    
    elif method == 'zoq64':
        # Should be exactly 8 characters
        return len(encoded) == 8
    
    return False
```

This comprehensive integration guide demonstrates practical patterns for using uubed with major vector databases, providing both basic usage examples and advanced optimization techniques for production deployments.