import os
import json
import logging
from typing import Dict, Any, Generator, Optional
from backend.knowledge_expansion.config import VERSION_METADATA_DIR
from backend.knowledge_expansion.lens_client import LensPatentClient

logger = logging.getLogger("PaginationEngine")

class ResumablePaginator:
    """
    Manages paginated retrieval loops across Lens.org search API requests.
    Supports checkpoint saves to resume interrupted synchronizations.
    """
    def __init__(self, client: LensPatentClient, checkpoint_filename: str = "sync_checkpoint.json"):
        self.client = client
        self.checkpoint_path = os.path.join(VERSION_METADATA_DIR, checkpoint_filename)

    def save_checkpoint(self, query_dsl: Dict[str, Any], from_idx: int, scroll_id: Optional[str] = None) -> None:
        """Saves current pagination state to disk."""
        data = {
            "query_dsl": query_dsl,
            "from_idx": from_idx,
            "scroll_id": scroll_id
        }
        try:
            with open(self.checkpoint_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Paginator checkpoint saved: offset {from_idx}")
        except Exception as e:
            logger.error(f"Failed to save pagination checkpoint: {e}")

    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Loads and returns current checkpoint state if available."""
        if not os.path.exists(self.checkpoint_path):
            return None
        try:
            with open(self.checkpoint_path, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded existing pagination checkpoint at offset {data.get('from_idx')}")
            return data
        except Exception as e:
            logger.error(f"Failed to load pagination checkpoint: {e}")
            return None

    def clear_checkpoint(self) -> None:
        """Removes the checkpoint file once synchronization completes successfully."""
        if os.path.exists(self.checkpoint_path):
            try:
                os.remove(self.checkpoint_path)
                logger.info("Pagination checkpoint cleared.")
            except Exception as e:
                logger.error(f"Failed to clear pagination checkpoint: {e}")

    def paginate(self, query_dsl: Dict[str, Any], batch_size: int = 50, max_results: int = 500, use_checkpoint: bool = True) -> Generator[Dict[str, Any], None, None]:
        """
        Yields pages of patent results. Supports resuming from loaded checkpoints.
        Limits total documents processed using max_results.
        """
        from_idx = 0
        scroll_id = None
        
        # Load previous run state if requested
        if use_checkpoint:
            checkpoint = self.load_checkpoint()
            if checkpoint:
                # Confirm queries match before resuming
                if checkpoint.get("query_dsl") == query_dsl:
                    from_idx = checkpoint.get("from_idx", 0)
                    scroll_id = checkpoint.get("scroll_id")
                    logger.info(f"Resuming sync from offset: {from_idx}")
                else:
                    logger.warning("Checkpoint query mismatch. Starting new synchronization.")
                    self.clear_checkpoint()

        total_results = None
        
        while from_idx < max_results:
            try:
                logger.info(f"Paginating patents: requesting from {from_idx} (batch size {batch_size})")
                
                # Fetch page
                response = self.client.search(
                    query_dsl=query_dsl,
                    size=batch_size,
                    from_idx=from_idx,
                    scroll_id=scroll_id
                )
                
                # Extract results
                results = response.get("results", [])
                total_results = response.get("total", 0)
                scroll_id = response.get("scroll_id")
                
                if not results:
                    logger.info("No further records returned by Lens API. Stopping pagination.")
                    break
                
                yield response
                
                from_idx += len(results)
                
                # Save checkpoint state after successful processing of the current page
                if use_checkpoint:
                    self.save_checkpoint(query_dsl, from_idx, scroll_id)
                
                if from_idx >= total_results:
                    logger.info(f"Reached end of search results ({from_idx}/{total_results}). Stopping pagination.")
                    break
                    
            except Exception as e:
                logger.error(f"Paginator encountered error at offset {from_idx}: {e}")
                # Re-raise to let the coordinator handle the pipeline break safely
                raise e

        # Clear checkpoint on successful completion
        if use_checkpoint:
            self.clear_checkpoint()
