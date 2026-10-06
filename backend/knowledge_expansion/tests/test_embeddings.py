import unittest
import os
import shutil
import numpy as np
from unittest.mock import patch, MagicMock
from backend.knowledge_expansion.config import VERSION_METADATA_DIR
from backend.knowledge_expansion.incremental_embeddings import IncrementalEmbeddingGenerator

class TestIncrementalEmbeddings(unittest.TestCase):
    """Unit tests for incremental embedding generator and checkpointing workflows."""

    def setUp(self):
        self.generator = IncrementalEmbeddingGenerator(batch_size=2, checkpoint_filename="test_checkpoint.npy")
        self.mock_patents = [
            {"application_number": "1", "patent_text": "Text representation one"},
            {"application_number": "2", "patent_text": "Text representation two"},
            {"application_number": "3", "patent_text": "Text representation three"}
        ]
        
    def tearDown(self):
        # Clear test checkpoint if any remain
        checkpoint_path = os.path.join(VERSION_METADATA_DIR, "test_checkpoint.npy")
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)

    @patch("backend.knowledge_expansion.incremental_embeddings.get_embedding_model")
    def test_generate_embeddings_success(self, mock_get_model):
        """Verifies successful batch encoding returns list of vectors."""
        mock_model = MagicMock()
        # Mock encode returns vector coordinates
        mock_model.encode.side_effect = [
            np.random.rand(2, 384).astype(np.float32), # Batch 1 (size 2)
            np.random.rand(1, 384).astype(np.float32)  # Batch 2 (size 1)
        ]
        mock_get_model.return_value = mock_model

        embeddings = self.generator.generate(self.mock_patents, resume=False)
        
        self.assertEqual(len(embeddings), 3)
        self.assertEqual(len(embeddings[0]), 384)
        self.assertEqual(mock_model.encode.call_count, 2)

    @patch("backend.knowledge_expansion.incremental_embeddings.get_embedding_model")
    def test_checkpoint_resume_flow(self, mock_get_model):
        """Verifies generator resumes from existing checkpoint without re-encoding already finished batches."""
        checkpoint_path = os.path.join(VERSION_METADATA_DIR, "test_checkpoint.npy")
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        
        # Pre-seed checkpoint with 2 records
        pre_seeded = np.random.rand(2, 384).astype(np.float32)
        np.save(checkpoint_path, pre_seeded)
        
        mock_model = MagicMock()
        # Should only encode the remaining 3rd record (1 item)
        mock_model.encode.return_value = np.random.rand(1, 384).astype(np.float32)
        mock_get_model.return_value = mock_model
        
        embeddings = self.generator.generate(self.mock_patents, resume=True)
        
        self.assertEqual(len(embeddings), 3)
        # Should only trigger encode call once for the remaining batch
        mock_model.encode.assert_called_once()
        self.assertFalse(os.path.exists(checkpoint_path)) # Cleaned on complete

if __name__ == "__main__":
    unittest.main()
