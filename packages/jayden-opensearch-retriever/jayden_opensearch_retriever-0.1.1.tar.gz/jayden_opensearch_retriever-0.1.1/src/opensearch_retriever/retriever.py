"""
OpenSearch Retriever 메인 모듈

OpenSearch에서 문서를 검색하고 검색하는 기능을 제공합니다.
"""

import json
from typing import Dict, List, Optional, Any
import requests
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from langchain_core.embeddings import Embeddings


class ParentChildRetriever:
    """OpenSearch 기반 문서 검색 및 검색 클래스"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9200,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_ssl: bool = False,
        verify_certs: bool = True,
        ssl_show_warn: bool = False,
        embedding_model: str = Embeddings,
    ):
        """
        OpenSearchRetriever 초기화
        
        Args:
            host: OpenSearch 호스트
            port: OpenSearch 포트
            username: 사용자명 (선택사항)
            password: 비밀번호 (선택사항)
            use_ssl: SSL 사용 여부
            verify_certs: 인증서 검증 여부
            ca_certs: CA 인증서 경로
        """
        self.host = host
        self.port = port
        self.embedding_model = embedding_model
        
        # OpenSearch 클라이언트 설정
        auth = (username, password) if username and password else None
        
        self.client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=auth,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            ssl_show_warn=False,
        )
    
    def vector_search(
        self,
        child_index: str,
        parent_index: str,
        query: str,
        k: int = 3,
    ) -> List:
        """
        문서 검색
        
        Args:
            index: 검색할 인덱스명
            query: 검색 쿼리
            k: 반환할 문서 수
            
        Returns:
            검색 결과 딕셔너리
        """
        query_vector = self.embedding_model.embed_query(query)

        search_body = {
            "size": k,
            "query": {
                "knn": {
                    "vector": { 
                        "vector": query_vector,
                        "k": k
                    }
                }
            }
        }
       
        try:
            parent_doc_ids = []

            response = self.client.search(
                index=child_index,
                body=search_body
            )

            for hit in response['hits']['hits']:
                # score = hit['_score']
                doc = hit['_source']
                metadata = doc.get('metadata', {})
                parent_id = metadata.get('parent_id')
                parent_doc_ids.append(parent_id)

            unique_parents = list(set(parent_doc_ids))

            response = self.client.mget(
                index=parent_index,
                body={"ids": unique_parents}
            )

            parent_documents = []
            for doc in response['docs']:
                if doc['found']:
                    parent_documents.append(doc['_source'])

            return parent_documents

        except Exception as e:
            raise RuntimeError(f"검색 중 오류 발생: {str(e)}")

    def embed_query(self, query: str) -> List[float]:
        """
        쿼리 임베딩
        """
        return self.embedding_model.embed_query(query)