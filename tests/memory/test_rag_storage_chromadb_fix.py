#!/usr/bin/env python3
"""
Unit tests for ChromaDB KeyError '_type' configuration fix
========================================================

Tests validate the ChromaDB configuration compatibility handling
in RAGStorage when KeyError: '_type' occurs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from crewai.memory.storage.rag_storage import RAGStorage


class TestRAGStorageChromaDBFix:
    """Test ChromaDB configuration compatibility fix"""

    @patch('crewai.memory.storage.rag_storage.logging')
    @patch('crewai.memory.storage.rag_storage.EmbeddingConfigurator')
    @patch('chromadb.PersistentClient')
    def test_chromadb_type_error_with_reset_allowed(self, mock_client_class, mock_configurator_class, mock_logging):
        """Test ChromaDB '_type' KeyError handling when allow_reset=True"""
        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock embedding configurator
        mock_configurator = Mock()
        mock_configurator_class.return_value = mock_configurator
        mock_embedding_func = Mock()
        mock_configurator.configure_embedder.return_value = mock_embedding_func
        
        # Mock get_collection to raise KeyError with '_type'
        mock_client.get_collection.side_effect = KeyError("'_type'")
        
        # Mock successful create_collection
        mock_collection = Mock()
        mock_client.create_collection.return_value = mock_collection
        
        # Create RAGStorage with allow_reset=True
        storage = RAGStorage(
            type="test_type",
            allow_reset=True,
            embedder_config=Mock(),
            crew=None
        )
        
        # Verify reset was called
        mock_client.reset.assert_called_once()
        
        # Verify new collection was created
        mock_client.create_collection.assert_called_once_with(
            name="test_type",
            embedding_function=storage.embedder_config
        )
        
        # Verify warning was logged
        mock_logging.warning.assert_called_once()
        assert "ChromaDB configuration incompatibility detected" in mock_logging.warning.call_args[0][0]
        assert "_type" in mock_logging.warning.call_args[0][0]
        
        # Verify collection was set
        assert storage.collection == mock_collection

    @patch('chromadb.PersistentClient')
    def test_chromadb_type_error_with_reset_disabled(self, mock_client_class):
        """Test ChromaDB '_type' KeyError handling when allow_reset=False"""
        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock get_collection to raise KeyError with '_type'
        mock_client.get_collection.side_effect = KeyError("'_type'")
        
        # Create RAGStorage with allow_reset=False should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            RAGStorage(
                type="test_type",
                allow_reset=False,
                embedder_config=Mock(),
                crew=None
            )
        
        # Verify RuntimeError message
        error_msg = str(exc_info.value)
        assert "ChromaDB configuration incompatibility detected" in error_msg
        assert "_type" in error_msg
        assert "Set allow_reset=True" in error_msg
        
        # Verify reset was NOT called
        mock_client.reset.assert_not_called()
        
        # Verify create_collection was NOT called
        mock_client.create_collection.assert_not_called()

    @patch('chromadb.PersistentClient')
    def test_chromadb_other_keyerror_passthrough(self, mock_client_class):
        """Test that other KeyErrors are passed through unchanged"""
        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock get_collection to raise different KeyError
        original_error = KeyError("other_field")
        mock_client.get_collection.side_effect = original_error
        
        # Create RAGStorage should re-raise original KeyError
        with pytest.raises(KeyError) as exc_info:
            RAGStorage(
                type="test_type",
                allow_reset=True,
                embedder_config=Mock(),
                crew=None
            )
        
        # Verify original error is re-raised
        assert exc_info.value is original_error
        
        # Verify reset was NOT called
        mock_client.reset.assert_not_called()

    @patch('chromadb.PersistentClient') 
    def test_chromadb_successful_get_collection(self, mock_client_class):
        """Test normal successful collection retrieval"""
        # Setup mocks
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock successful get_collection
        mock_collection = Mock()
        mock_client.get_collection.return_value = mock_collection
        
        # Create RAGStorage
        storage = RAGStorage(
            type="test_type",
            allow_reset=True,
            embedder_config=Mock(),
            crew=None
        )
        
        # Verify get_collection was called
        mock_client.get_collection.assert_called_once_with(
            name="test_type",
            embedding_function=storage.embedder_config
        )
        
        # Verify reset was NOT called
        mock_client.reset.assert_not_called()
        
        # Verify collection was set correctly
        assert storage.collection == mock_collection


if __name__ == "__main__":
    pytest.main([__file__, "-v"])