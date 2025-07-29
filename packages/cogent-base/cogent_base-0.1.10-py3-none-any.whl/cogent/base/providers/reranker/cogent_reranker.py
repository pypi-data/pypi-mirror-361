"""
Copyright (c) 2025 Mirasurf
"""

import logging
from typing import List, Optional, Union

from cogent.base.config import get_cogent_config
from cogent.base.models.chunk import ObjectChunk
from cogent.base.providers.reranker.base_reranker import BaseReranker

logger = logging.getLogger(__name__)


class CogentReranker(BaseReranker):
    """
    Cogent reranker that provides a unified interface for different reranker providers.
    Uses registered rerankers from the config file and routes to appropriate implementations.
    """

    def __init__(self, reranker_key: str):
        """
        Initialize Cogent reranker with a reranker key from registered_rerankers.

        Args:
            reranker_key: The key of the reranker in the registered_rerankers config
        """
        settings = get_cogent_config()
        self.reranker_key = reranker_key
        self.reranker_impl: Optional[BaseReranker] = None

        # Get the reranker configuration from registered_rerankers
        if (
            not hasattr(settings.reranker, "registered_rerankers")
            or reranker_key not in settings.reranker.registered_rerankers
        ):
            raise ValueError(f"Reranker '{reranker_key}' not found in registered_rerankers configuration")

        self.reranker_config = settings.reranker.registered_rerankers[reranker_key]
        self.provider = settings.reranker.reranker_provider

        # Initialize the appropriate reranker implementation
        if self.provider == "flag":
            from cogent.base.providers.reranker.flag_reranker import FlagReranker

            self.reranker_impl = FlagReranker(
                model_name=self.reranker_config.get("model_name", "BAAI/bge-reranker-v2-gemma"),
                query_max_length=self.reranker_config.get("query_max_length", 256),
                passage_max_length=self.reranker_config.get("passage_max_length", 512),
                use_fp16=self.reranker_config.get("use_fp16", True),
                device=self.reranker_config.get("device", "mps"),
            )
        elif self.provider == "litellm":
            from cogent.base.providers.reranker.litellm_reranker import LiteLLMReranker

            self.reranker_impl = LiteLLMReranker(reranker_key)
        else:
            raise ValueError(f"Provider '{self.provider}' not supported")

        logger.info(f"Initialized Cogent reranker with reranker_key={reranker_key}, config={self.reranker_config}")

    async def rerank(
        self,
        query: str,
        chunks: List[ObjectChunk],
    ) -> List[ObjectChunk]:
        """Rerank chunks based on their relevance to the query"""
        return await self.reranker_impl.rerank(query, chunks)

    async def compute_score(
        self,
        query: str,
        text: Union[str, List[str]],
    ) -> Union[float, List[float]]:
        """Compute relevance scores between query and text"""
        return await self.reranker_impl.compute_score(query, text)
