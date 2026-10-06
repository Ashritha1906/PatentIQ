import os
import time
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from backend.knowledge_expansion.config import EMBEDDING_MODEL_NAME, EMBEDDING_DIM, VERSION_METADATA_DIR

logger = logging.getLogger("IncrementalEmbeddings")

# Global singleton reference for model
_sentence_transformer_model: Optional[SentenceTransformer] = None

def get_embedding_model() -> SentenceTransformer:
    """Loads and caches the SentenceTransformer model to save initialization latency."""
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        logger.info(f"Initializing Sentence Transformer model: {EMBEDDING_MODEL_NAME}...")
        start_time = time.time()
        
        # Determine device
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
            
        logger.info(f"Incremental embeddings executing on device: {device.upper()}")
        _sentence_transformer_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        logger.info(f"Model loaded successfully in {time.time() - start_time:.2f} seconds.")
        
    return _sentence_transformer_model

class IncrementalEmbeddingGenerator:
    """
    Handles embedding generation for newly indexed patents.
    Ensures vector dimensions remain at exactly 384 and implements batch encoding.
    """
    def __init__(self, batch_size: int = 64, checkpoint_filename: str = "embeddings_checkpoint.npy"):
        self.batch_size = batch_size
        self.checkpoint_path = os.path.join(VERSION_METADATA_DIR, checkpoint_filename)

    def generate(self, patents: List[Dict[str, Any]], resume: bool = True) -> List[List[float]]:
        """
        Generates dense vector representations for the list of patents.
        Processes in batches and saves progress to check files to resume if interrupted.
        """
        if not patents:
            return []

        model = get_embedding_model()
        texts = [p["patent_text"] for p in patents]
        total_records = len(texts)
        
        logger.info(f"Generating embeddings for {total_records} new patent documents...")
        
        # Resume configuration
        start_idx = 0
        embeddings_list = []
        
        if resume and os.path.exists(self.checkpoint_path):
            try:
                loaded_embeddings = np.load(self.checkpoint_path)
                if loaded_embeddings.shape[0] < total_records and loaded_embeddings.shape[1] == EMBEDDING_DIM:
                    start_idx = loaded_embeddings.shape[0]
                    embeddings_list = loaded_embeddings.tolist()
                    logger.info(f"Resuming embedding generation from index {start_idx} (loaded {len(embeddings_list)} checkpoints).")
                else:
                    logger.warning("Checkpoint dimensions mismatch. Recalculating all embeddings.")
                    if os.path.exists(self.checkpoint_path):
                        os.remove(self.checkpoint_path)
            except Exception as e:
                logger.error(f"Failed to load embedding checkpoint: {e}")

        # Batch encoding loop
        start_time = time.time()
        
        for i in range(start_idx, total_records, self.batch_size):
            end_idx = min(i + self.batch_size, total_records)
            batch_texts = texts[i:end_idx]
            
            logger.info(f"  Encoding batch {i // self.batch_size + 1}: index {i} to {end_idx}...")
            batch_embeddings = model.encode(
                batch_texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            embeddings_list.extend(batch_embeddings.tolist())
            
            # Save checkpoint
            if resume:
                try:
                    np.save(self.checkpoint_path, np.array(embeddings_list, dtype=np.float32))
                except Exception as e:
                    logger.error(f"Failed to save embedding checkpoint: {e}")

        duration = time.time() - start_time
        speed = total_records / duration if duration > 0 else 0
        logger.info(f"Embedding generation completed: {total_records} items in {duration:.2f}s ({speed:.2f} items/sec).")
        
        # Clean up checkpoint on completion
        if os.path.exists(self.checkpoint_path):
            try:
                os.remove(self.checkpoint_path)
            except Exception as e:
                logger.warning(f"Could not remove completed checkpoint file: {e}")
                
        return embeddings_list
