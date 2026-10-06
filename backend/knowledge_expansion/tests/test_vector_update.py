import unittest
from unittest.mock import patch, MagicMock
from backend.knowledge_expansion.vector_updater import VectorDatabaseUpdater, VectorUpdaterError
from backend.knowledge_expansion.duplicate_checker import DuplicateChecker

class TestVectorUpdaterAndDuplicates(unittest.TestCase):
    """Unit tests for ChromaDB insert validations and duplicate checkers."""

    @patch("backend.knowledge_expansion.vector_updater.ChromaVectorStore.insert")
    def test_update_db_success(self, mock_insert):
        """Verifies vector insert triggers Chroma collection append and counts grow."""
        patents = [
            {"application_number": "US2024101", "patent_text": "text 1", "title": "A", "field_of_invention": "CS", "classification_ipc": "G06", "applicant_name": "Org"}
        ]
        embeddings = [[0.1] * 384]

        # Mock database stats
        mock_col = MagicMock()
        mock_col.count.side_effect = [10, 11] # 10 before, 11 after
        
        updater = VectorDatabaseUpdater(db_path="test_db")
        updater._collection = mock_col
        
        stats = updater.update(patents, embeddings)
        
        self.assertEqual(stats["inserted"], 1)
        self.assertEqual(stats["count_before"], 10)
        self.assertEqual(stats["count_after"], 11)
        self.assertTrue(stats["integrity_verified"])
        
        # Verify vector store insert was triggered
        mock_insert.assert_called_once()

    def test_update_dimension_mismatch(self):
        """Verifies updater raises error on patent-to-embedding count mismatches."""
        patents = [{"application_number": "1"}]
        embeddings = [] # Mismatch
        
        updater = VectorDatabaseUpdater(db_path="test_db")
        with self.assertRaises(VectorUpdaterError):
            updater.update(patents, embeddings)

    @patch("backend.knowledge_expansion.duplicate_checker.DuplicateChecker._get_collection")
    def test_duplicate_checker_filters_correctly(self, mock_get_col):
        """Verifies duplicate filter removes existing items and identifies unique entries."""
        mock_col = MagicMock()
        # Mock get query behavior: "US/1" returns hit (exists), "US/2" returns empty (unique)
        def mock_get_side_effect(ids, include=None):
            if ids[0] == "US/1":
                return {"ids": ["US/1"]}
            return {"ids": []}
            
        mock_col.get.side_effect = mock_get_side_effect
        mock_get_col.return_value = mock_col
        
        checker = DuplicateChecker(db_path="test_db")
        
        patents = [
            {"application_number": "US/1", "patent_text": "text 1"}, # duplicate
            {"application_number": "US/2", "patent_text": "text 2"}, # unique
            {"application_number": "US/2", "patent_text": "text 2"}  # duplicate inside same batch
        ]
        
        results = checker.check_batch(patents)
        
        self.assertEqual(len(results["unique"]), 1)
        self.assertEqual(results["unique"][0]["application_number"], "US/2")
        self.assertEqual(len(results["duplicates"]), 2)

if __name__ == "__main__":
    unittest.main()
