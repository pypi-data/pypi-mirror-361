"""
HACS Tools Package

This package provides core tools and utilities for working with HACS resources,
including CRUD operations, search functionality, validation, memory management,
evidence handling, and structured data processing.
"""

# CRUD Operations
from .crud import (
    AuditEvent,
    ConflictError,
    CreateObservation,
    CreatePatient,
    CreateResource,
    CRUDError,
    CRUDOperation,
    DeleteResource,
    GetAuditLog,
    ListResources,
    PermissionError,
    PermissionManager,
    ReadObservation,
    ReadPatient,
    ReadResource,
    ResourceNotFoundError,
    StorageBackend,
    StorageManager,
    UpdateResource,
    get_storage_manager,
    set_storage_backend,
)

# Evidence management
from .evidence import (
    EvidenceManager,
    EvidenceSearchResult,
)

# Memory management
from .memory import (
    MemoryManager,
    MemorySearchResult,
)

# Search functionality
from .search import (
    FHIRSearch,
    SearchMethod,
    SearchResult,
    SemanticSearch,
)

# Structured data processing
from .structured import (
    FunctionSpecError,
    ToolCallPattern,
    ToolCallResult,
    ToolExecutor,
    generate_function_spec,
)

# Validation
from .validation import (
    DataValidator,
    ValidationLevel,
    ValidationResult,
)

# Base vectorization classes and protocols
from .vectorization import (
    EmbeddingModel,
    HACSVectorizer,
    VectorMetadata,
    VectorStore,
)

__all__ = [
    # CRUD operations
    "CreateResource",
    "ReadResource",
    "UpdateResource",
    "DeleteResource",
    "ListResources",
    "GetAuditLog",
    "CreatePatient",
    "ReadPatient",
    "CreateObservation",
    "ReadObservation",
    "StorageBackend",
    "CRUDOperation",
    "CRUDError",
    "PermissionError",
    "ResourceNotFoundError",
    "ConflictError",
    "AuditEvent",
    "StorageManager",
    "PermissionManager",
    "set_storage_backend",
    "get_storage_manager",
    # Search functionality
    "SemanticSearch",
    "FHIRSearch",
    "SearchMethod",
    "SearchResult",
    # Memory management
    "MemoryManager",
    "MemorySearchResult",
    # Evidence management
    "EvidenceManager",
    "EvidenceSearchResult",
    # Validation
    "DataValidator",
    "ValidationLevel",
    "ValidationResult",
    # Structured data processing
    "generate_function_spec",
    "FunctionSpecError",
    "ToolCallPattern",
    "ToolCallResult",
    "ToolExecutor",
    # Base vectorization
    "EmbeddingModel",
    "VectorStore",
    "VectorMetadata",
    "HACSVectorizer",
]


def hello() -> str:
    return "Hello from hacs-tools!"
