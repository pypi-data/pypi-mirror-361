#!/usr/bin/env python3
"""
Multimodal embeddings examples for uubed.

This module demonstrates working with multimodal models like CLIP, ALIGN,
and other vision-language models, including:
- Text and image embedding encoding
- Cross-modal search
- Embedding alignment and fusion
- Efficient storage of multimodal features

Requirements:
    - uubed (core library)
    - numpy
    - PIL (optional, for image processing)
    - torch (optional, for model inference)
    - transformers (optional, for pre-trained models)
"""

import numpy as np
import json
import time
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import hashlib

from uubed import encode, decode, batch_encode, UubedError

# Optional imports
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Note: Install Pillow for image processing examples")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Note: Install torch for model inference examples")

try:
    from transformers import CLIPModel, CLIPProcessor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Note: Install transformers for CLIP examples")


class ModalityType(Enum):
    """Types of modalities in multimodal systems."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    POINT_CLOUD = "point_cloud"


@dataclass
class MultimodalEmbedding:
    """Container for multimodal embeddings."""
    modality: ModalityType
    embedding: np.ndarray
    metadata: Dict[str, Any]
    source_id: str
    timestamp: float
    
    def __post_init__(self):
        if self.embedding.dtype != np.uint8:
            self.embedding = (self.embedding * 255).clip(0, 255).astype(np.uint8)


class MultimodalEncoder:
    """Encoder for multimodal embeddings with uubed."""
    
    def __init__(self, 
                 text_method: str = "shq64",
                 image_method: str = "t8q64",
                 fusion_method: str = "eq64"):
        self.encoding_methods = {
            ModalityType.TEXT: text_method,
            ModalityType.IMAGE: image_method,
            ModalityType.AUDIO: "zoq64",
            ModalityType.VIDEO: "shq64",
            ModalityType.POINT_CLOUD: "t8q64"
        }
        self.fusion_method = fusion_method
        self.encoded_cache = {}
    
    def encode_multimodal(self, 
                         embedding: MultimodalEmbedding) -> Dict[str, Any]:
        """Encode a multimodal embedding."""
        method = self.encoding_methods.get(
            embedding.modality, 
            "shq64"  # Default
        )
        
        # Encode embedding
        encoded = encode(embedding.embedding, method=method)
        
        # Create encoded representation
        result = {
            "modality": embedding.modality.value,
            "encoded": encoded,
            "encoding_method": method,
            "metadata": embedding.metadata,
            "source_id": embedding.source_id,
            "timestamp": embedding.timestamp,
            "embedding_dim": len(embedding.embedding),
            "signature": self._compute_signature(encoded)
        }
        
        # Cache for cross-modal search
        cache_key = f"{embedding.modality.value}:{embedding.source_id}"
        self.encoded_cache[cache_key] = result
        
        return result
    
    def encode_paired_embeddings(self,
                               emb1: MultimodalEmbedding,
                               emb2: MultimodalEmbedding) -> Dict[str, Any]:
        """Encode paired embeddings (e.g., image-text pairs)."""
        # Encode individual embeddings
        encoded1 = self.encode_multimodal(emb1)
        encoded2 = self.encode_multimodal(emb2)
        
        # Create paired representation
        return {
            "pair_id": f"{emb1.source_id}:{emb2.source_id}",
            "modalities": [emb1.modality.value, emb2.modality.value],
            "encodings": [encoded1, encoded2],
            "alignment_score": self._compute_alignment(
                emb1.embedding, emb2.embedding
            )
        }
    
    def fuse_embeddings(self,
                       embeddings: List[MultimodalEmbedding],
                       fusion_type: str = "concatenate") -> Dict[str, Any]:
        """Fuse multiple modality embeddings."""
        if fusion_type == "concatenate":
            # Concatenate embeddings
            fused = np.concatenate([emb.embedding for emb in embeddings])
        elif fusion_type == "average":
            # Average embeddings (requires same dimension)
            stacked = np.stack([emb.embedding for emb in embeddings])
            fused = np.mean(stacked, axis=0).astype(np.uint8)
        elif fusion_type == "weighted":
            # Weighted fusion based on modality importance
            weights = {
                ModalityType.IMAGE: 0.4,
                ModalityType.TEXT: 0.4,
                ModalityType.AUDIO: 0.2
            }
            weighted_sum = np.zeros_like(embeddings[0].embedding, dtype=np.float32)
            total_weight = 0
            
            for emb in embeddings:
                weight = weights.get(emb.modality, 0.1)
                weighted_sum += emb.embedding * weight
                total_weight += weight
            
            fused = (weighted_sum / total_weight).astype(np.uint8)
        else:
            raise ValueError(f"Unknown fusion type: {fusion_type}")
        
        # Encode fused embedding
        encoded_fused = encode(fused, method=self.fusion_method)
        
        return {
            "fusion_type": fusion_type,
            "modalities": [emb.modality.value for emb in embeddings],
            "source_ids": [emb.source_id for emb in embeddings],
            "fused_encoded": encoded_fused,
            "fused_dim": len(fused),
            "encoding_method": self.fusion_method
        }
    
    def _compute_signature(self, encoded: str) -> str:
        """Compute signature for fast lookup."""
        return hashlib.md5(encoded.encode()).hexdigest()[:16]
    
    def _compute_alignment(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute alignment score between embeddings."""
        # Simple cosine similarity
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(emb1, emb2) / (norm1 * norm2))


def clip_integration_example():
    """
    Demonstrate integration with CLIP for image-text embeddings.
    
    Shows encoding and cross-modal search capabilities.
    """
    print("=== CLIP Integration Example ===")
    
    # Simulate CLIP embeddings if libraries not available
    def simulate_clip_embeddings(text: str = None, 
                               image_path: str = None) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate CLIP text and image embeddings."""
        # CLIP typically produces 512-dim embeddings
        dim = 512
        
        if text:
            # Simulate text embedding with some structure
            text_hash = hash(text)
            np.random.seed(text_hash % 2**32)
            text_emb = np.random.randn(dim).astype(np.float32)
            text_emb = text_emb / np.linalg.norm(text_emb)
        else:
            text_emb = None
        
        if image_path:
            # Simulate image embedding
            img_hash = hash(image_path)
            np.random.seed(img_hash % 2**32)
            image_emb = np.random.randn(dim).astype(np.float32)
            image_emb = image_emb / np.linalg.norm(image_emb)
        else:
            image_emb = None
        
        return text_emb, image_emb
    
    # Create multimodal encoder
    encoder = MultimodalEncoder(
        text_method="shq64",
        image_method="t8q64"
    )
    
    # Example data
    text_image_pairs = [
        ("A photo of a cat", "cat_001.jpg"),
        ("A beautiful sunset over the ocean", "sunset_beach.jpg"),
        ("Modern architecture building", "building_42.jpg"),
        ("Fresh fruits on a table", "fruits_display.jpg"),
        ("Person riding a bicycle", "cyclist_01.jpg")
    ]
    
    print("Encoding CLIP embeddings...")
    encoded_pairs = []
    
    for text, image_path in text_image_pairs:
        # Get embeddings (simulated)
        text_emb, image_emb = simulate_clip_embeddings(text, image_path)
        
        # Create multimodal embeddings
        text_embedding = MultimodalEmbedding(
            modality=ModalityType.TEXT,
            embedding=text_emb,
            metadata={"content": text, "language": "en"},
            source_id=f"text_{hash(text) % 10000}",
            timestamp=time.time()
        )
        
        image_embedding = MultimodalEmbedding(
            modality=ModalityType.IMAGE,
            embedding=image_emb,
            metadata={"path": image_path, "format": "jpg"},
            source_id=f"img_{hash(image_path) % 10000}",
            timestamp=time.time()
        )
        
        # Encode pair
        encoded_pair = encoder.encode_paired_embeddings(
            text_embedding, 
            image_embedding
        )
        encoded_pairs.append(encoded_pair)
        
        print(f"  Encoded pair: {text[:30]}... <-> {image_path}")
        print(f"    Alignment score: {encoded_pair['alignment_score']:.3f}")
    
    # Cross-modal search example
    print("\nCross-modal search:")
    query_text = "A cute animal"
    query_text_emb, _ = simulate_clip_embeddings(text=query_text)
    
    query_embedding = MultimodalEmbedding(
        modality=ModalityType.TEXT,
        embedding=query_text_emb,
        metadata={"content": query_text},
        source_id="query_001",
        timestamp=time.time()
    )
    
    # Encode query
    encoded_query = encoder.encode_multimodal(query_embedding)
    print(f"  Query: '{query_text}'")
    print(f"  Encoded query signature: {encoded_query['signature']}")
    
    # In real implementation, would search for similar signatures
    print("  Similar images: [Would search encoded image database]")
    print()


def multimodal_fusion_example():
    """
    Demonstrate fusion of embeddings from multiple modalities.
    
    Shows different fusion strategies and their applications.
    """
    print("=== Multimodal Fusion Example ===")
    
    encoder = MultimodalEncoder()
    
    # Create sample embeddings from different modalities
    print("Creating multimodal embeddings...")
    
    # Text embedding
    text_emb = MultimodalEmbedding(
        modality=ModalityType.TEXT,
        embedding=np.random.randn(768).astype(np.float32),
        metadata={"content": "Product description text", "tokens": 50},
        source_id="text_prod_001",
        timestamp=time.time()
    )
    
    # Image embedding
    image_emb = MultimodalEmbedding(
        modality=ModalityType.IMAGE,
        embedding=np.random.randn(768).astype(np.float32),
        metadata={"resolution": "1024x768", "channels": 3},
        source_id="img_prod_001",
        timestamp=time.time()
    )
    
    # Audio embedding (e.g., from product video)
    audio_emb = MultimodalEmbedding(
        modality=ModalityType.AUDIO,
        embedding=np.random.randn(768).astype(np.float32),
        metadata={"duration_sec": 30, "sample_rate": 44100},
        source_id="audio_prod_001",
        timestamp=time.time()
    )
    
    # Test different fusion strategies
    fusion_strategies = ["concatenate", "average", "weighted"]
    
    for strategy in fusion_strategies:
        print(f"\n{strategy.capitalize()} fusion:")
        
        if strategy == "concatenate":
            # Can fuse different dimensions
            embeddings = [text_emb, image_emb, audio_emb]
        else:
            # Requires same dimension
            embeddings = [text_emb, image_emb, audio_emb]
        
        try:
            fused_result = encoder.fuse_embeddings(
                embeddings,
                fusion_type=strategy
            )
            
            print(f"  Fused dimension: {fused_result['fused_dim']}")
            print(f"  Encoded length: {len(fused_result['fused_encoded'])}")
            print(f"  Modalities: {', '.join(fused_result['modalities'])}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print()


def efficient_storage_patterns():
    """
    Demonstrate efficient storage patterns for multimodal embeddings.
    
    Shows how to organize and store large collections.
    """
    print("=== Efficient Storage Patterns ===")
    
    class MultimodalStorage:
        """Efficient storage for multimodal embeddings."""
        
        def __init__(self):
            self.encoder = MultimodalEncoder()
            self.index = {
                "by_modality": {},
                "by_source": {},
                "by_signature": {},
                "pairs": []
            }
            self.storage_stats = {
                "total_embeddings": 0,
                "total_bytes": 0,
                "compression_ratio": 0
            }
        
        def store_embedding(self, embedding: MultimodalEmbedding) -> str:
            """Store embedding and return storage key."""
            # Encode
            encoded = self.encoder.encode_multimodal(embedding)
            
            # Generate storage key
            storage_key = f"{embedding.modality.value}:{encoded['signature']}"
            
            # Update indices
            modality = embedding.modality.value
            if modality not in self.index["by_modality"]:
                self.index["by_modality"][modality] = []
            self.index["by_modality"][modality].append(storage_key)
            
            self.index["by_source"][embedding.source_id] = storage_key
            self.index["by_signature"][encoded['signature']] = encoded
            
            # Update stats
            self.storage_stats["total_embeddings"] += 1
            self.storage_stats["total_bytes"] += len(encoded['encoded'])
            original_size = embedding.embedding.nbytes
            self.storage_stats["compression_ratio"] = (
                original_size * self.storage_stats["total_embeddings"] /
                self.storage_stats["total_bytes"]
            )
            
            return storage_key
        
        def store_collection(self, 
                           embeddings: List[MultimodalEmbedding],
                           collection_name: str) -> Dict[str, Any]:
            """Store a collection of embeddings efficiently."""
            collection_keys = []
            
            print(f"Storing collection '{collection_name}'...")
            
            for emb in embeddings:
                key = self.store_embedding(emb)
                collection_keys.append(key)
            
            # Create collection metadata
            collection_meta = {
                "name": collection_name,
                "keys": collection_keys,
                "modality_breakdown": self._get_modality_breakdown(embeddings),
                "timestamp": time.time()
            }
            
            return collection_meta
        
        def _get_modality_breakdown(self, 
                                   embeddings: List[MultimodalEmbedding]) -> Dict[str, int]:
            """Get count by modality."""
            breakdown = {}
            for emb in embeddings:
                modality = emb.modality.value
                breakdown[modality] = breakdown.get(modality, 0) + 1
            return breakdown
        
        def get_storage_report(self) -> Dict[str, Any]:
            """Generate storage efficiency report."""
            return {
                "total_embeddings": self.storage_stats["total_embeddings"],
                "total_storage_bytes": self.storage_stats["total_bytes"],
                "average_bytes_per_embedding": (
                    self.storage_stats["total_bytes"] / 
                    self.storage_stats["total_embeddings"]
                    if self.storage_stats["total_embeddings"] > 0 else 0
                ),
                "compression_ratio": self.storage_stats["compression_ratio"],
                "modality_counts": {
                    k: len(v) for k, v in self.index["by_modality"].items()
                }
            }
    
    # Create storage system
    storage = MultimodalStorage()
    
    # Generate sample dataset
    embeddings = []
    
    # Text embeddings
    for i in range(50):
        embeddings.append(MultimodalEmbedding(
            modality=ModalityType.TEXT,
            embedding=np.random.randn(768).astype(np.float32),
            metadata={"doc_id": f"doc_{i}", "language": "en"},
            source_id=f"text_{i}",
            timestamp=time.time()
        ))
    
    # Image embeddings
    for i in range(50):
        embeddings.append(MultimodalEmbedding(
            modality=ModalityType.IMAGE,
            embedding=np.random.randn(768).astype(np.float32),
            metadata={"image_id": f"img_{i}", "format": "jpg"},
            source_id=f"image_{i}",
            timestamp=time.time()
        ))
    
    # Store collection
    collection_meta = storage.store_collection(embeddings, "demo_collection")
    
    # Show report
    report = storage.get_storage_report()
    print(f"\nStorage Report:")
    print(f"  Total embeddings: {report['total_embeddings']}")
    print(f"  Total storage: {report['total_storage_bytes'] / 1024:.2f} KB")
    print(f"  Avg bytes/embedding: {report['average_bytes_per_embedding']:.1f}")
    print(f"  Compression ratio: {report['compression_ratio']:.2f}x")
    print(f"  Modality breakdown: {report['modality_counts']}")
    print()


def cross_modal_search_example():
    """
    Demonstrate cross-modal search capabilities.
    
    Shows searching across different modalities.
    """
    print("=== Cross-Modal Search Example ===")
    
    class CrossModalSearchEngine:
        """Search engine for cross-modal queries."""
        
        def __init__(self):
            self.encoder = MultimodalEncoder()
            self.embeddings_db = []
            self.cross_modal_index = {}
        
        def index_multimodal_content(self, content: Dict[str, Any]):
            """Index content with multiple modalities."""
            content_id = content["id"]
            indexed_modalities = []
            
            # Index each modality
            for modality, data in content["modalities"].items():
                embedding = MultimodalEmbedding(
                    modality=ModalityType(modality),
                    embedding=data["embedding"],
                    metadata=data.get("metadata", {}),
                    source_id=f"{content_id}_{modality}",
                    timestamp=time.time()
                )
                
                encoded = self.encoder.encode_multimodal(embedding)
                
                # Store in database
                self.embeddings_db.append({
                    "content_id": content_id,
                    "modality": modality,
                    "encoded": encoded,
                    "embedding": embedding
                })
                
                indexed_modalities.append(modality)
            
            # Build cross-modal connections
            if len(indexed_modalities) > 1:
                self.cross_modal_index[content_id] = indexed_modalities
        
        def search_cross_modal(self, 
                             query_embedding: MultimodalEmbedding,
                             target_modality: Optional[ModalityType] = None,
                             top_k: int = 5) -> List[Dict[str, Any]]:
            """Search across modalities."""
            # Encode query
            query_encoded = self.encoder.encode_multimodal(query_embedding)
            query_signature = query_encoded["signature"]
            
            # Search strategy: find similar signatures
            results = []
            
            for item in self.embeddings_db:
                # Filter by target modality if specified
                if target_modality and item["modality"] != target_modality.value:
                    continue
                
                # Compute similarity (simplified - using signature prefix)
                item_signature = item["encoded"]["signature"]
                similarity = sum(a == b for a, b in zip(
                    query_signature, item_signature
                )) / len(query_signature)
                
                results.append({
                    "content_id": item["content_id"],
                    "modality": item["modality"],
                    "similarity": similarity,
                    "cross_modal_available": item["content_id"] in self.cross_modal_index
                })
            
            # Sort by similarity
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results[:top_k]
    
    # Create search engine
    search_engine = CrossModalSearchEngine()
    
    # Index multimodal content
    print("Indexing multimodal content...")
    
    content_items = [
        {
            "id": "product_001",
            "modalities": {
                "text": {
                    "embedding": np.random.randn(512).astype(np.float32),
                    "metadata": {"title": "Wireless Headphones", "description": "Premium audio"}
                },
                "image": {
                    "embedding": np.random.randn(512).astype(np.float32),
                    "metadata": {"main_image": "headphones_001.jpg"}
                }
            }
        },
        {
            "id": "product_002",
            "modalities": {
                "text": {
                    "embedding": np.random.randn(512).astype(np.float32),
                    "metadata": {"title": "Smart Watch", "description": "Fitness tracking"}
                },
                "image": {
                    "embedding": np.random.randn(512).astype(np.float32),
                    "metadata": {"main_image": "watch_002.jpg"}
                },
                "video": {
                    "embedding": np.random.randn(512).astype(np.float32),
                    "metadata": {"demo_video": "watch_demo.mp4"}
                }
            }
        }
    ]
    
    for content in content_items:
        search_engine.index_multimodal_content(content)
        print(f"  Indexed: {content['id']} with {len(content['modalities'])} modalities")
    
    # Perform cross-modal search
    print("\nCross-modal search examples:")
    
    # Text query -> Find images
    text_query = MultimodalEmbedding(
        modality=ModalityType.TEXT,
        embedding=np.random.randn(512).astype(np.float32),
        metadata={"query": "technology gadget"},
        source_id="query_text_001",
        timestamp=time.time()
    )
    
    print("\n1. Text -> Image search:")
    results = search_engine.search_cross_modal(
        text_query,
        target_modality=ModalityType.IMAGE,
        top_k=3
    )
    
    for r in results:
        print(f"  - {r['content_id']} ({r['modality']}): "
              f"similarity={r['similarity']:.3f}, "
              f"cross-modal={r['cross_modal_available']}")
    
    # Image query -> Find text
    image_query = MultimodalEmbedding(
        modality=ModalityType.IMAGE,
        embedding=np.random.randn(512).astype(np.float32),
        metadata={"query_image": "query.jpg"},
        source_id="query_img_001",
        timestamp=time.time()
    )
    
    print("\n2. Image -> Text search:")
    results = search_engine.search_cross_modal(
        image_query,
        target_modality=ModalityType.TEXT,
        top_k=3
    )
    
    for r in results:
        print(f"  - {r['content_id']} ({r['modality']}): "
              f"similarity={r['similarity']:.3f}")
    
    print()


def alignment_quality_assessment():
    """
    Assess and improve alignment quality between modalities.
    
    Shows techniques for measuring and improving cross-modal alignment.
    """
    print("=== Alignment Quality Assessment ===")
    
    class AlignmentAnalyzer:
        """Analyze alignment quality between modalities."""
        
        def __init__(self, encoder: MultimodalEncoder):
            self.encoder = encoder
        
        def assess_alignment(self,
                           pairs: List[Tuple[MultimodalEmbedding, MultimodalEmbedding]]
                           ) -> Dict[str, Any]:
            """Assess alignment quality of embedding pairs."""
            alignment_scores = []
            encoding_similarities = []
            
            for emb1, emb2 in pairs:
                # Compute raw alignment
                alignment = self.encoder._compute_alignment(
                    emb1.embedding, emb2.embedding
                )
                alignment_scores.append(alignment)
                
                # Compare encoded versions
                enc1 = self.encoder.encode_multimodal(emb1)
                enc2 = self.encoder.encode_multimodal(emb2)
                
                # Signature similarity
                sig_sim = sum(a == b for a, b in zip(
                    enc1["signature"], enc2["signature"]
                )) / len(enc1["signature"])
                encoding_similarities.append(sig_sim)
            
            # Compute statistics
            return {
                "num_pairs": len(pairs),
                "alignment_scores": {
                    "mean": np.mean(alignment_scores),
                    "std": np.std(alignment_scores),
                    "min": np.min(alignment_scores),
                    "max": np.max(alignment_scores)
                },
                "encoding_similarities": {
                    "mean": np.mean(encoding_similarities),
                    "std": np.std(encoding_similarities)
                },
                "well_aligned_pairs": sum(s > 0.7 for s in alignment_scores),
                "poorly_aligned_pairs": sum(s < 0.3 for s in alignment_scores)
            }
        
        def improve_alignment(self,
                            emb1: MultimodalEmbedding,
                            emb2: MultimodalEmbedding,
                            method: str = "projection") -> Tuple[np.ndarray, np.ndarray]:
            """Improve alignment between embeddings."""
            if method == "projection":
                # Project to common space
                # Simple linear projection (in practice, would use learned projection)
                common_dim = min(len(emb1.embedding), len(emb2.embedding))
                
                proj1 = emb1.embedding[:common_dim]
                proj2 = emb2.embedding[:common_dim]
                
                # Normalize
                proj1 = proj1 / (np.linalg.norm(proj1) + 1e-8)
                proj2 = proj2 / (np.linalg.norm(proj2) + 1e-8)
                
                return proj1, proj2
                
            elif method == "cca":
                # Canonical Correlation Analysis (simplified)
                # In practice, would use proper CCA implementation
                return emb1.embedding, emb2.embedding
            
            else:
                raise ValueError(f"Unknown alignment method: {method}")
    
    # Create analyzer
    encoder = MultimodalEncoder()
    analyzer = AlignmentAnalyzer(encoder)
    
    # Generate test pairs
    print("Generating test embedding pairs...")
    pairs = []
    
    # Well-aligned pairs (simulated)
    for i in range(10):
        base = np.random.randn(512).astype(np.float32)
        
        # Add small noise for second embedding
        text_emb = MultimodalEmbedding(
            modality=ModalityType.TEXT,
            embedding=base + np.random.randn(512) * 0.1,
            metadata={},
            source_id=f"aligned_text_{i}",
            timestamp=time.time()
        )
        
        image_emb = MultimodalEmbedding(
            modality=ModalityType.IMAGE,
            embedding=base + np.random.randn(512) * 0.1,
            metadata={},
            source_id=f"aligned_img_{i}",
            timestamp=time.time()
        )
        
        pairs.append((text_emb, image_emb))
    
    # Poorly aligned pairs
    for i in range(5):
        text_emb = MultimodalEmbedding(
            modality=ModalityType.TEXT,
            embedding=np.random.randn(512).astype(np.float32),
            metadata={},
            source_id=f"random_text_{i}",
            timestamp=time.time()
        )
        
        image_emb = MultimodalEmbedding(
            modality=ModalityType.IMAGE,
            embedding=np.random.randn(512).astype(np.float32),
            metadata={},
            source_id=f"random_img_{i}",
            timestamp=time.time()
        )
        
        pairs.append((text_emb, image_emb))
    
    # Assess alignment
    assessment = analyzer.assess_alignment(pairs)
    
    print("\nAlignment Assessment:")
    print(f"  Total pairs: {assessment['num_pairs']}")
    print(f"  Alignment scores: mean={assessment['alignment_scores']['mean']:.3f}, "
          f"std={assessment['alignment_scores']['std']:.3f}")
    print(f"  Well-aligned pairs: {assessment['well_aligned_pairs']}")
    print(f"  Poorly-aligned pairs: {assessment['poorly_aligned_pairs']}")
    
    # Test alignment improvement
    print("\nTesting alignment improvement:")
    poor_pair = pairs[-1]  # Take a poorly aligned pair
    
    original_alignment = encoder._compute_alignment(
        poor_pair[0].embedding, poor_pair[1].embedding
    )
    
    improved1, improved2 = analyzer.improve_alignment(
        poor_pair[0], poor_pair[1], method="projection"
    )
    
    improved_alignment = encoder._compute_alignment(improved1, improved2)
    
    print(f"  Original alignment: {original_alignment:.3f}")
    print(f"  Improved alignment: {improved_alignment:.3f}")
    print(f"  Improvement: {improved_alignment - original_alignment:.3f}")
    print()


if __name__ == "__main__":
    print("UUBED Multimodal Embeddings Examples")
    print("=" * 50)
    
    # Run examples
    clip_integration_example()
    multimodal_fusion_example()
    efficient_storage_patterns()
    cross_modal_search_example()
    alignment_quality_assessment()
    
    print("\nAll multimodal examples completed!")