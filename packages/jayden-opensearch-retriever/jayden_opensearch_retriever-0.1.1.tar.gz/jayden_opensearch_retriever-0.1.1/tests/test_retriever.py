"""
OpenSearchRetriever 테스트
"""

import pytest
from unittest.mock import Mock, patch
from opensearch_retriever import OpenSearchRetriever


class TestOpenSearchRetriever:
    """OpenSearchRetriever 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.retriever = OpenSearchRetriever(
            host="localhost",
            port=9200,
        )
    
    @patch('opensearch_retriever.retriever.OpenSearch')
    def test_init(self, mock_opensearch):
        """초기화 테스트"""
        retriever = OpenSearchRetriever(
            host="test-host",
            port=9200,
            username="user",
            password="pass",
        )
        
        assert retriever.host == "test-host"
        assert retriever.port == 9200
        mock_opensearch.assert_called_once()
    
    @patch('opensearch_retriever.retriever.OpenSearch')
    def test_search(self, mock_opensearch):
        """검색 기능 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_opensearch.return_value = mock_client
        mock_client.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_id": "1", "_source": {"title": "test"}}]
            }
        }
        
        retriever = OpenSearchRetriever()
        result = retriever.search("test-index", "test query")
        
        # 검증
        mock_client.search.assert_called_once()
        assert "hits" in result
    
    @patch('opensearch_retriever.retriever.OpenSearch')
    def test_get_by_id(self, mock_opensearch):
        """ID로 문서 조회 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_opensearch.return_value = mock_client
        mock_client.get.return_value = {
            "_id": "1",
            "_source": {"title": "test document"}
        }
        
        retriever = OpenSearchRetriever()
        result = retriever.get_by_id("test-index", "1")
        
        # 검증
        mock_client.get.assert_called_once_with(index="test-index", id="1")
        assert result["_id"] == "1"
    
    @patch('opensearch_retriever.retriever.OpenSearch')
    def test_index_document(self, mock_opensearch):
        """문서 인덱싱 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_opensearch.return_value = mock_client
        mock_client.index.return_value = {
            "_id": "1",
            "result": "created"
        }
        
        retriever = OpenSearchRetriever()
        document = {"title": "Test Document", "content": "Test content"}
        result = retriever.index_document("test-index", document)
        
        # 검증
        mock_client.index.assert_called_once()
        assert result["result"] == "created"
    
    @patch('opensearch_retriever.retriever.OpenSearch')
    def test_health_check(self, mock_opensearch):
        """상태 확인 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_opensearch.return_value = mock_client
        mock_client.cluster.health.return_value = {
            "status": "green",
            "cluster_name": "test-cluster"
        }
        
        retriever = OpenSearchRetriever()
        result = retriever.health_check()
        
        # 검증
        mock_client.cluster.health.assert_called_once()
        assert result["status"] == "green" 