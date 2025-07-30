from abc import ABC, abstractmethod
from collections.abc import Callable

import numpy as np
import torch


class EmbeddingModel(ABC):
    """Wrapper class for embedding models used to represent sequences."""

    @staticmethod
    @abstractmethod
    def get_model_short_name(model_version: str) -> str:
        """Retrieve shortened name for model version.

        Should not contain any underscores. Represent spaces with '-'.

        Args:
            model_version: Version of model to fetch short name for.

        Returns:
            Shortened name of model version.
        """
        pass

    def __init__(self, model_version: str, device: torch.device):
        """Initialize EmbeddingModel.

        Args:
            model_version: Version of embedding model to use.
            device: PyTorch device to send embedding model.
        """
        self.model_version = model_version
        self.short_name = self.__class__.get_model_short_name(model_version)
        self.device = device

        self.is_sixtrack = False

        print("Disabling autograd for inference.")
        torch.autograd.set_grad_enabled(False)

    @abstractmethod
    def embed_sequence(
        self,
        sequence: str,
        agg_fn: Callable = torch.mean,
    ) -> torch.Tensor:
        """Embed sequence.

        Args:
            sequence: String of nucleotides to embed (uses DNA bases).
            agg_fn: Method used to aggregate across sequence dimension.

        Returns:
            Embedded sequence with shape (1 x H).
        """
        pass

    @abstractmethod
    def embed_sequence_sixtrack(
        self,
        sequence: str,
        cds: np.ndarray,
        splice: np.ndarray,
        agg_fn: Callable = torch.mean,
    ) -> torch.Tensor:
        """Embed sequence incorporating splice and cds information.

        Args:
            sequence: String of nucleotides to embed (uses DNA bases).
            cds: Binary encoding of first nucleotide of each codon in CDS.
            splice: Binary encoding of splice site locations.
            agg_fn: Method used to aggregate across sequence dimension.

        Returns:
            Embedded sequence with shape (1 x H).
        """
        pass

    def chunk_sequence(self, sequence: str, chunk_length: int) -> list[str]:
        """Split sequence into chunks of specified length with given overlap.

        Args:
            sequence: The input string sequence to be chunked.
            chunk_length: The length of each chunk.

        Returns:
            A list of string chunks, where each chunk has the specified length.
        """
        chunks = []
        for i in range(0, len(sequence), chunk_length):
            chunk = sequence[i:i + chunk_length]
            chunks.append(chunk)

        return chunks

    def chunk_tokens(
        self,
        sequence_tokens: list[int],
        chunk_length: int,
    ) -> list[list[int]]:
        """Chunk tokenized sequence into specified length.

        Args:
            sequence_tokens: The tokenized sequence to be chunked.
            chunk_length: The length of each chunk.

        Returns:
            A list of chunked tokens each with specified maximum length.
        """
        chunks = []
        for i in range(0, len(sequence_tokens), chunk_length):
            chunk = sequence_tokens[i:i + chunk_length]
            chunks.append(chunk)

        return chunks
