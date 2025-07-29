#!/usr/bin/env python3
"""
Search engine integration examples for uubed.

This module demonstrates how to integrate uubed with Elasticsearch and Solr
for efficient embedding storage and retrieval. Shows:
- Custom analyzers for encoded embeddings
- Efficient indexing strategies
- Hybrid text and vector search
- Performance optimization techniques

Requirements:
    - uubed (core library)
    - numpy
    - Optional: elasticsearch, pysolr
"""

import json
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib

from uubed import encode, decode, batch_encode

# Optional imports with graceful fallback
try:
    from elasticsearch import Elasticsearch, helpers
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    print("Note: Install elasticsearch for Elasticsearch examples")

try:
    import pysolr
    SOLR_AVAILABLE = True
except ImportError:
    SOLR_AVAILABLE = False
    print("Note: Install pysolr for Solr examples")


class SearchEngineAdapter:
    """Base adapter for search engine integration with uubed."""
    
    def __init__(self, encoding_method: str = "shq64"):
        self.encoding_method = encoding_method
        self.stats = {
            "documents_indexed": 0,
            "queries_processed": 0,
            "encoding_time_ms": 0,
            "storage_saved_bytes": 0
        }
    
    def prepare_document(self, doc_id: str, content: str, 
                        embedding: np.ndarray, 
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare document with encoded embedding for indexing."""
        start_time = time.time()
        
        # Encode embedding
        if embedding.dtype != np.uint8:
            embedding_uint8 = (embedding * 255).clip(0, 255).astype(np.uint8)
        else:
            embedding_uint8 = embedding
        
        encoded = encode(embedding_uint8, method=self.encoding_method)
        
        # Calculate storage savings
        original_size = embedding.nbytes
        encoded_size = len(encoded)
        self.stats["storage_saved_bytes"] += (original_size - encoded_size)
        
        # Track timing
        encoding_time = (time.time() - start_time) * 1000
        self.stats["encoding_time_ms"] += encoding_time
        
        # Create document structure
        doc = {
            "id": doc_id,
            "content": content,
            "encoded_embedding": encoded,
            "encoding_method": self.encoding_method,
            "embedding_dim": len(embedding),
            "indexed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add encoding hash for fast lookup
        doc["embedding_hash"] = hashlib.md5(encoded.encode()).hexdigest()[:16]
        
        self.stats["documents_indexed"] += 1
        return doc
    
    def create_search_query(self, query_text: str = None,
                           query_embedding: np.ndarray = None,
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create hybrid search query combining text and encoded embedding."""
        query = {}
        
        if query_text:
            query["text"] = query_text
        
        if query_embedding is not None:
            # Encode query embedding
            if query_embedding.dtype != np.uint8:
                query_embedding = (query_embedding * 255).clip(0, 255).astype(np.uint8)
            
            encoded_query = encode(query_embedding, method=self.encoding_method)
            query["encoded_embedding"] = encoded_query
            query["embedding_hash"] = hashlib.md5(encoded_query.encode()).hexdigest()[:16]
        
        if filters:
            query["filters"] = filters
        
        self.stats["queries_processed"] += 1
        return query


def elasticsearch_integration_example():
    """
    Demonstrate Elasticsearch integration with uubed.
    
    Shows index mapping, bulk indexing, and complex queries.
    """
    if not ELASTICSEARCH_AVAILABLE:
        print("=== Elasticsearch Integration (Simulated) ===")
        print("Elasticsearch client not available. Showing example structure.")
    else:
        print("=== Elasticsearch Integration Example ===")
    
    # Mock Elasticsearch client
    class MockElasticsearch:
        def __init__(self):
            self.indices = {}
        
        class indices:
            @staticmethod
            def create(index, body):
                print(f"  Created index: {index}")
                return {"acknowledged": True}
            
            @staticmethod
            def exists(index):
                return False
        
        def bulk(self, body):
            count = len([b for b in body if "_source" in b]) // 2
            return {"items": [{"index": {"_id": i}} for i in range(count)]}
        
        def search(self, index, body):
            return {
                "hits": {
                    "total": {"value": 3},
                    "hits": [
                        {
                            "_id": f"doc_{i}",
                            "_score": 0.9 - i*0.1,
                            "_source": {
                                "content": f"Document {i}",
                                "encoded_embedding": "encoded_data"
                            }
                        }
                        for i in range(3)
                    ]
                }
            }
    
    # Initialize adapter
    adapter = SearchEngineAdapter(encoding_method="shq64")
    
    # Initialize Elasticsearch client
    if ELASTICSEARCH_AVAILABLE:
        es = Elasticsearch(['localhost:9200'])
    else:
        es = MockElasticsearch()
    
    # Define index mapping optimized for encoded embeddings
    index_name = "uubed_documents"
    index_mapping = {
        "mappings": {
            "properties": {
                "content": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "encoded_embedding": {
                    "type": "keyword",  # Store as keyword for exact matching
                    "index": True
                },
                "embedding_hash": {
                    "type": "keyword",  # For fast hash-based lookup
                    "index": True
                },
                "encoding_method": {
                    "type": "keyword"
                },
                "embedding_dim": {
                    "type": "integer"
                },
                "indexed_at": {
                    "type": "date"
                },
                "metadata": {
                    "type": "object",
                    "dynamic": True
                }
            }
        },
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "index": {
                "similarity": {
                    "default": {
                        "type": "BM25"
                    }
                }
            }
        }
    }
    
    # Create index
    print("Creating Elasticsearch index...")
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=index_mapping)
    
    # Prepare documents for bulk indexing
    print("\nPreparing documents for bulk indexing...")
    documents = []
    bulk_actions = []
    
    for i in range(100):
        # Generate document
        embedding = np.random.rand(768).astype(np.float32)
        doc = adapter.prepare_document(
            doc_id=f"doc_{i}",
            content=f"This is document {i} containing information about topic {i % 10}",
            embedding=embedding,
            metadata={
                "category": f"cat_{i % 5}",
                "importance": i % 10,
                "author": f"author_{i % 3}"
            }
        )
        documents.append(doc)
        
        # Prepare bulk action
        bulk_actions.append({
            "_index": index_name,
            "_id": doc["id"],
            "_source": doc
        })
    
    # Bulk index
    print("Performing bulk indexing...")
    if ELASTICSEARCH_AVAILABLE:
        # Real bulk indexing
        helpers.bulk(es, bulk_actions)
    else:
        # Simulated bulk
        es.bulk(bulk_actions)
    
    print(f"Indexed {len(documents)} documents")
    
    # Example queries
    print("\n=== Query Examples ===")
    
    # 1. Text search with embedding filter
    print("\n1. Hybrid text + embedding search:")
    query_embedding = np.random.rand(768).astype(np.float32)
    search_query = adapter.create_search_query(
        query_text="information about topic",
        query_embedding=query_embedding
    )
    
    es_query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": search_query["text"]}}
                ],
                "filter": [
                    {"term": {"embedding_hash": search_query["embedding_hash"][:8]}}
                ]
            }
        },
        "size": 5
    }
    
    results = es.search(index=index_name, body=es_query)
    print(f"Found {results['hits']['total']['value']} documents")
    
    # 2. Aggregation by encoding method
    print("\n2. Aggregation by encoding method:")
    agg_query = {
        "size": 0,
        "aggs": {
            "by_method": {
                "terms": {
                    "field": "encoding_method"
                },
                "aggs": {
                    "avg_dim": {
                        "avg": {
                            "field": "embedding_dim"
                        }
                    }
                }
            }
        }
    }
    
    # 3. More like this with encoded embeddings
    print("\n3. Find similar documents by encoding:")
    similar_query = {
        "query": {
            "more_like_this": {
                "fields": ["content", "encoded_embedding"],
                "like": [
                    {
                        "_index": index_name,
                        "_id": "doc_0"
                    }
                ],
                "min_term_freq": 1,
                "min_doc_freq": 1
            }
        }
    }
    
    # Show stats
    print(f"\nAdapter statistics:")
    print(f"  Documents indexed: {adapter.stats['documents_indexed']}")
    print(f"  Storage saved: {adapter.stats['storage_saved_bytes'] / 1024:.2f} KB")
    print(f"  Avg encoding time: {adapter.stats['encoding_time_ms'] / adapter.stats['documents_indexed']:.2f} ms")
    print()


def solr_integration_example():
    """
    Demonstrate Solr integration with uubed.
    
    Shows schema design, custom field types, and faceted search.
    """
    if not SOLR_AVAILABLE:
        print("=== Solr Integration (Simulated) ===")
        print("Solr client not available. Showing example structure.")
    else:
        print("=== Solr Integration Example ===")
    
    # Mock Solr client
    class MockSolr:
        def __init__(self, url):
            self.url = url
            self.docs = []
        
        def add(self, docs, commit=True):
            self.docs.extend(docs)
            return f"Added {len(docs)} documents"
        
        def search(self, q, **kwargs):
            return {
                "response": {
                    "numFound": 3,
                    "docs": [
                        {
                            "id": f"doc_{i}",
                            "content": f"Document {i}",
                            "encoded_embedding": "encoded",
                            "score": 0.9 - i*0.1
                        }
                        for i in range(3)
                    ]
                },
                "facet_counts": {
                    "facet_fields": {
                        "category": ["cat_0", 10, "cat_1", 8, "cat_2", 5]
                    }
                }
            }
        
        def commit(self):
            return "Committed"
    
    # Initialize adapter
    adapter = SearchEngineAdapter(encoding_method="t8q64")
    
    # Initialize Solr client
    solr_url = "http://localhost:8983/solr/uubed"
    if SOLR_AVAILABLE:
        solr = pysolr.Solr(solr_url, timeout=10)
    else:
        solr = MockSolr(solr_url)
    
    # Solr schema (would be defined in schema.xml or managed schema)
    print("Solr schema design for uubed:")
    print("""
    <field name="id" type="string" indexed="true" stored="true" required="true"/>
    <field name="content" type="text_general" indexed="true" stored="true"/>
    <field name="encoded_embedding" type="string" indexed="true" stored="true"/>
    <field name="embedding_hash" type="string" indexed="true" stored="true"/>
    <field name="encoding_method" type="string" indexed="true" stored="true" facet="true"/>
    <field name="category" type="string" indexed="true" stored="true" facet="true"/>
    <field name="importance" type="pint" indexed="true" stored="true"/>
    <field name="indexed_at" type="pdate" indexed="true" stored="true"/>
    """)
    
    # Prepare and index documents
    print("\nIndexing documents in Solr...")
    solr_docs = []
    
    for i in range(50):
        embedding = np.random.rand(512).astype(np.float32)
        doc = adapter.prepare_document(
            doc_id=f"solr_doc_{i}",
            content=f"Solr document {i} about search technology and information retrieval",
            embedding=embedding,
            metadata={
                "category": f"cat_{i % 3}",
                "importance": i % 10,
                "tags": [f"tag_{i % 5}", f"tag_{i % 7}"]
            }
        )
        
        # Flatten for Solr
        solr_doc = {
            "id": doc["id"],
            "content": doc["content"],
            "encoded_embedding": doc["encoded_embedding"],
            "embedding_hash": doc["embedding_hash"],
            "encoding_method": doc["encoding_method"],
            "embedding_dim": doc["embedding_dim"],
            "indexed_at": doc["indexed_at"],
            "category": doc["metadata"].get("category"),
            "importance": doc["metadata"].get("importance"),
            "tags": doc["metadata"].get("tags", [])
        }
        solr_docs.append(solr_doc)
    
    # Batch add
    result = solr.add(solr_docs, commit=True)
    print(f"Indexing result: {result}")
    
    # Query examples
    print("\n=== Solr Query Examples ===")
    
    # 1. Basic search with facets
    print("\n1. Search with faceting:")
    results = solr.search(
        "search technology",
        **{
            "facet": "true",
            "facet.field": ["category", "encoding_method"],
            "facet.limit": 5,
            "rows": 5
        }
    )
    
    print(f"Found {results['response']['numFound']} documents")
    if "facet_counts" in results:
        print("Facets:")
        for field, counts in results["facet_counts"]["facet_fields"].items():
            print(f"  {field}: {dict(zip(counts[::2], counts[1::2]))}")
    
    # 2. Filter by encoded embedding prefix
    print("\n2. Filter by embedding signature:")
    query_embedding = np.random.rand(512).astype(np.float32)
    query_data = adapter.create_search_query(query_embedding=query_embedding)
    
    # Search for similar encodings (using prefix match)
    prefix_search = solr.search(
        f'embedding_hash:{query_data["embedding_hash"][:8]}*',
        **{"rows": 10}
    )
    
    print(f"Found {prefix_search['response']['numFound']} with similar encoding")
    
    # 3. Complex boolean query
    print("\n3. Complex query with boost:")
    complex_query = (
        'content:"information retrieval"^2.0 OR '
        'content:search^1.5 AND '
        'category:cat_0 AND '
        'importance:[5 TO 10]'
    )
    
    complex_results = solr.search(
        complex_query,
        **{
            "defType": "edismax",
            "qf": "content^2.0 encoded_embedding^1.0",
            "rows": 5
        }
    )
    
    print(f"Complex query found {complex_results['response']['numFound']} documents")
    print()


def real_time_indexing_example():
    """
    Demonstrate real-time indexing with streaming embeddings.
    
    Shows how to handle continuous streams of embeddings efficiently.
    """
    print("=== Real-time Indexing Example ===")
    
    class RealTimeIndexer:
        def __init__(self, adapter: SearchEngineAdapter, 
                     batch_size: int = 10, 
                     flush_interval: float = 5.0):
            self.adapter = adapter
            self.batch_size = batch_size
            self.flush_interval = flush_interval
            self.buffer = []
            self.last_flush = time.time()
            self.stats = {
                "total_indexed": 0,
                "batches_flushed": 0,
                "avg_latency_ms": 0
            }
        
        def add_document(self, doc_id: str, content: str, 
                        embedding: np.ndarray, metadata: Dict = None):
            """Add document to buffer and flush if needed."""
            start_time = time.time()
            
            # Prepare document
            doc = self.adapter.prepare_document(
                doc_id=doc_id,
                content=content,
                embedding=embedding,
                metadata=metadata
            )
            
            self.buffer.append(doc)
            
            # Check flush conditions
            should_flush = (
                len(self.buffer) >= self.batch_size or
                (time.time() - self.last_flush) >= self.flush_interval
            )
            
            if should_flush:
                self.flush()
            
            # Update latency
            latency = (time.time() - start_time) * 1000
            self.stats["avg_latency_ms"] = (
                (self.stats["avg_latency_ms"] * self.stats["total_indexed"] + latency) /
                (self.stats["total_indexed"] + 1)
            )
            self.stats["total_indexed"] += 1
        
        def flush(self):
            """Flush buffer to search engine."""
            if not self.buffer:
                return
            
            print(f"  Flushing batch of {len(self.buffer)} documents...")
            
            # In real implementation, this would index to ES/Solr
            # Here we just simulate the indexing
            time.sleep(0.1)  # Simulate network latency
            
            self.buffer.clear()
            self.last_flush = time.time()
            self.stats["batches_flushed"] += 1
        
        def get_stats(self) -> Dict:
            return self.stats.copy()
    
    # Create indexer
    adapter = SearchEngineAdapter(encoding_method="shq64")
    indexer = RealTimeIndexer(adapter, batch_size=10, flush_interval=2.0)
    
    # Simulate streaming documents
    print("Simulating real-time document stream...")
    print("(Press Ctrl+C to stop simulation)")
    
    try:
        for i in range(50):
            # Simulate document arrival
            time.sleep(0.1)  # 10 docs per second
            
            # Generate document
            embedding = np.random.rand(384).astype(np.float32)
            indexer.add_document(
                doc_id=f"stream_doc_{i}",
                content=f"Real-time document {i} from stream",
                embedding=embedding,
                metadata={
                    "stream_id": "stream_001",
                    "timestamp": time.time()
                }
            )
            
            # Show progress
            if i % 10 == 0:
                stats = indexer.get_stats()
                print(f"  Processed: {stats['total_indexed']}, "
                      f"Batches: {stats['batches_flushed']}, "
                      f"Avg latency: {stats['avg_latency_ms']:.2f}ms")
    
    except KeyboardInterrupt:
        print("\nStopping stream...")
    
    # Final flush
    indexer.flush()
    
    # Show final stats
    final_stats = indexer.get_stats()
    print(f"\nFinal statistics:")
    print(f"  Total documents: {final_stats['total_indexed']}")
    print(f"  Total batches: {final_stats['batches_flushed']}")
    print(f"  Average latency: {final_stats['avg_latency_ms']:.2f}ms")
    print(f"  Throughput: {final_stats['total_indexed'] / (time.time() - adapter.stats['encoding_time_ms']/1000):.1f} docs/sec")
    print()


def advanced_search_patterns():
    """
    Demonstrate advanced search patterns using encoded embeddings.
    
    Shows complex query strategies and optimization techniques.
    """
    print("=== Advanced Search Patterns ===")
    
    class AdvancedSearchEngine:
        def __init__(self, adapter: SearchEngineAdapter):
            self.adapter = adapter
            self.index = {}  # Simple in-memory index
            self.encoding_cache = {}  # Cache for frequently used encodings
        
        def index_document(self, doc: Dict[str, Any]):
            """Index document with multiple access patterns."""
            doc_id = doc["id"]
            
            # Store in main index
            self.index[doc_id] = doc
            
            # Create inverted indices for fast lookup
            # By encoding hash prefix (for similarity)
            hash_prefix = doc["embedding_hash"][:4]
            if hash_prefix not in self.encoding_cache:
                self.encoding_cache[hash_prefix] = []
            self.encoding_cache[hash_prefix].append(doc_id)
        
        def knn_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
            """Approximate k-NN search using encoding similarity."""
            # Encode query
            query_data = self.adapter.create_search_query(
                query_embedding=query_embedding
            )
            query_hash = query_data["embedding_hash"]
            
            # Find candidates with similar encoding prefixes
            candidates = []
            for prefix_len in [4, 3, 2]:  # Progressively broader search
                prefix = query_hash[:prefix_len]
                if prefix in self.encoding_cache:
                    candidates.extend(self.encoding_cache[prefix])
                    if len(candidates) >= k * 2:  # Enough candidates
                        break
            
            # Score candidates (in real system, would compute actual distances)
            scored = []
            for doc_id in set(candidates):
                doc = self.index[doc_id]
                # Simulate scoring based on encoding similarity
                score = sum(a == b for a, b in zip(
                    query_hash, doc["embedding_hash"]
                )) / len(query_hash)
                scored.append((score, doc))
            
            # Return top-k
            scored.sort(reverse=True, key=lambda x: x[0])
            return [doc for _, doc in scored[:k]]
        
        def diversity_search(self, query_embedding: np.ndarray, 
                           k: int = 5, diversity_weight: float = 0.3) -> List[Dict]:
            """Search with result diversification."""
            # Get initial candidates
            candidates = self.knn_search(query_embedding, k=k*3)
            
            # Diversify results
            diverse_results = []
            used_categories = set()
            used_prefixes = set()
            
            for doc in candidates:
                # Check diversity criteria
                category = doc.get("metadata", {}).get("category", "unknown")
                encoding_prefix = doc["embedding_hash"][:2]
                
                diversity_score = 0
                if category not in used_categories:
                    diversity_score += 0.5
                if encoding_prefix not in used_prefixes:
                    diversity_score += 0.5
                
                # Combined score (would include relevance in real system)
                doc["diversity_score"] = diversity_score * diversity_weight
                
                diverse_results.append(doc)
                used_categories.add(category)
                used_prefixes.add(encoding_prefix)
                
                if len(diverse_results) >= k:
                    break
            
            return diverse_results
        
        def explain_search(self, query_embedding: np.ndarray, 
                          doc_id: str) -> Dict[str, Any]:
            """Explain why a document matched a query."""
            if doc_id not in self.index:
                return {"error": "Document not found"}
            
            doc = self.index[doc_id]
            query_data = self.adapter.create_search_query(
                query_embedding=query_embedding
            )
            
            # Analyze match
            explanation = {
                "doc_id": doc_id,
                "encoding_similarity": sum(
                    a == b for a, b in zip(
                        query_data["embedding_hash"], 
                        doc["embedding_hash"]
                    )
                ) / len(query_data["embedding_hash"]),
                "encoding_method_match": query_data.get("encoding_method") == doc["encoding_method"],
                "common_prefix_length": len(os.path.commonprefix([
                    query_data["embedding_hash"], 
                    doc["embedding_hash"]
                ])),
                "factors": []
            }
            
            # Add scoring factors
            if explanation["encoding_similarity"] > 0.8:
                explanation["factors"].append("High encoding similarity")
            if explanation["common_prefix_length"] >= 4:
                explanation["factors"].append("Strong prefix match")
            
            return explanation
    
    # Create search engine
    adapter = SearchEngineAdapter(encoding_method="shq64")
    engine = AdvancedSearchEngine(adapter)
    
    # Index sample documents
    print("Indexing documents for advanced search...")
    categories = ["tech", "science", "business", "health", "education"]
    
    for i in range(100):
        embedding = np.random.rand(768).astype(np.float32)
        doc = adapter.prepare_document(
            doc_id=f"adv_doc_{i}",
            content=f"Document {i} about {categories[i % len(categories)]}",
            embedding=embedding,
            metadata={
                "category": categories[i % len(categories)],
                "quality_score": np.random.rand(),
                "publish_date": f"2024-01-{(i % 30) + 1:02d}"
            }
        )
        engine.index_document(doc)
    
    # Demonstrate search patterns
    query_embedding = np.random.rand(768).astype(np.float32)
    
    # 1. Basic k-NN search
    print("\n1. k-NN Search Results:")
    knn_results = engine.knn_search(query_embedding, k=5)
    for doc in knn_results:
        print(f"  - {doc['id']}: {doc['content'][:50]}...")
    
    # 2. Diversity search
    print("\n2. Diversity Search Results:")
    diverse_results = engine.diversity_search(query_embedding, k=5, diversity_weight=0.4)
    for doc in diverse_results:
        print(f"  - {doc['id']}: category={doc['metadata']['category']}, "
              f"diversity_score={doc.get('diversity_score', 0):.2f}")
    
    # 3. Search explanation
    print("\n3. Search Explanation:")
    if knn_results:
        explanation = engine.explain_search(query_embedding, knn_results[0]["id"])
        print(f"  Document: {explanation['doc_id']}")
        print(f"  Encoding similarity: {explanation['encoding_similarity']:.2%}")
        print(f"  Common prefix length: {explanation['common_prefix_length']}")
        print(f"  Factors: {', '.join(explanation['factors'])}")
    
    print()


if __name__ == "__main__":
    print("UUBED Search Engine Integration Examples")
    print("=" * 50)
    
    # Add missing import
    import os
    
    # Run examples
    elasticsearch_integration_example()
    solr_integration_example()
    real_time_indexing_example()
    advanced_search_patterns()
    
    print("\nAll search engine examples completed!")