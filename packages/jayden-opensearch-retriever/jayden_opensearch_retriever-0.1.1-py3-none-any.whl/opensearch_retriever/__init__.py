"""
OpenSearch Retriever

OpenSearch 기반 벡터 검색 및 부모-자식 문서 검색 도구
"""

__version__ = "0.1.0"
__author__ = "Jayden"
__email__ = "jayden.kim@nxtcloud.kr"

from .retriever import ParentChildRetriever

__all__ = ["ParentChildRetriever"] 