"""
Quantum Data Embedding Suite

A comprehensive package for advanced classical-to-quantum data embedding techniques
designed to maximize quantum advantage in machine learning applications.
"""

__version__ = "0.1.0"
__author__ = "Krishna Bajpai"
__email__ = "bajpaikrishna715@gmail.com"

from .pipeline import QuantumEmbeddingPipeline
from .embeddings import (
    AngleEmbedding,
    AmplitudeEmbedding,
    IQPEmbedding,
    DataReuploadingEmbedding,
    HamiltonianEmbedding,
)
from .kernels import QuantumKernel, FidelityKernel, ProjectedKernel
from .metrics import (
    expressibility,
    trainability,
    gradient_variance,
    effective_dimension,
)

__all__ = [
    "QuantumEmbeddingPipeline",
    "AngleEmbedding",
    "AmplitudeEmbedding", 
    "IQPEmbedding",
    "DataReuploadingEmbedding",
    "HamiltonianEmbedding",
    "QuantumKernel",
    "FidelityKernel",
    "ProjectedKernel",
    "expressibility",
    "trainability",
    "gradient_variance",
    "effective_dimension",
]
