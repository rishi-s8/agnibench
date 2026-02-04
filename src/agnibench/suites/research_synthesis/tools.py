"""
Tools for the research synthesis benchmark suite.

Provides 7 tools for document search, analysis, and synthesis.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agentbuilder.Tools.base import Tool


# Storage for simulated data (populated by environment)
_research_data: Dict[str, Any] = {
    "documents": [],
    "notes": [],
    "summaries": [],
}


def set_research_data(data: Dict[str, Any]) -> None:
    """Set the research data (called by environment)."""
    global _research_data
    _research_data = data


def get_research_data() -> Dict[str, Any]:
    """Get current research data."""
    return _research_data


# Pydantic models for tool parameters

class SearchDocumentsParams(BaseModel):
    """Parameters for searching documents."""
    query: str = Field(description="Search query for document content")
    doc_type: Optional[str] = Field(default=None, description="Filter by document type (report, documentation, policy, analysis)")
    limit: int = Field(default=5, description="Maximum results to return")


class ReadDocumentParams(BaseModel):
    """Parameters for reading a document."""
    document_id: str = Field(description="ID of the document to read")


class ExtractFactsParams(BaseModel):
    """Parameters for extracting facts from text."""
    document_id: str = Field(description="ID of the document to extract facts from")
    focus_area: Optional[str] = Field(default=None, description="Specific topic to focus on")


class CompareSourcesParams(BaseModel):
    """Parameters for comparing two documents."""
    document_id_1: str = Field(description="First document ID")
    document_id_2: str = Field(description="Second document ID")
    comparison_aspect: Optional[str] = Field(default=None, description="Specific aspect to compare")


class TakeNotesParams(BaseModel):
    """Parameters for taking research notes."""
    note: str = Field(description="The note content to store")
    source_document: Optional[str] = Field(default=None, description="Document ID this note is based on")
    tags: List[str] = Field(default_factory=list, description="Tags for organizing notes")


class SearchWebParams(BaseModel):
    """Parameters for web search."""
    query: str = Field(description="Search query")
    limit: int = Field(default=5, description="Maximum results")


class GenerateSummaryParams(BaseModel):
    """Parameters for generating a summary."""
    document_ids: List[str] = Field(default_factory=list, description="Document IDs to summarize")
    include_notes: bool = Field(default=True, description="Include research notes in summary")
    focus_topic: Optional[str] = Field(default=None, description="Topic to focus the summary on")


# Tool implementation functions

def search_documents(params: SearchDocumentsParams) -> Dict[str, Any]:
    """Search the document corpus."""
    documents = _research_data.get("documents", [])
    results = []

    query_lower = params.query.lower()

    for doc in documents:
        # Check if query matches title or content
        title_match = query_lower in doc.get("title", "").lower()
        content_match = query_lower in doc.get("content", "").lower()
        tag_match = any(query_lower in tag.lower() for tag in doc.get("tags", []))

        if title_match or content_match or tag_match:
            # Apply type filter
            if params.doc_type:
                if doc.get("type", "").lower() != params.doc_type.lower():
                    continue

            results.append({
                "id": doc.get("id"),
                "title": doc.get("title"),
                "type": doc.get("type"),
                "author": doc.get("author"),
                "created_at": doc.get("created_at"),
                "preview": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", ""),
                "relevance": "high" if title_match else "medium",
            })

            if len(results) >= params.limit:
                break

    return {
        "query": params.query,
        "results": results,
        "count": len(results),
    }


def read_document(params: ReadDocumentParams) -> Dict[str, Any]:
    """Read a document's full content."""
    documents = _research_data.get("documents", [])

    for doc in documents:
        if doc.get("id") == params.document_id:
            return {
                "found": True,
                "document": doc,
            }

    return {
        "found": False,
        "error": f"Document '{params.document_id}' not found",
    }


def extract_facts(params: ExtractFactsParams) -> Dict[str, Any]:
    """Extract key facts from a document."""
    documents = _research_data.get("documents", [])

    for doc in documents:
        if doc.get("id") == params.document_id:
            content = doc.get("content", "")

            # Simulated fact extraction based on document content
            # In reality, this would use NLP or an LLM
            facts = doc.get("extracted_facts", [])

            if params.focus_area:
                facts = [f for f in facts if params.focus_area.lower() in f.lower()]

            return {
                "document_id": params.document_id,
                "document_title": doc.get("title"),
                "facts": facts,
                "focus_area": params.focus_area,
            }

    return {
        "error": f"Document '{params.document_id}' not found",
        "facts": [],
    }


def compare_sources(params: CompareSourcesParams) -> Dict[str, Any]:
    """Compare two documents."""
    documents = _research_data.get("documents", [])

    doc1 = None
    doc2 = None

    for doc in documents:
        if doc.get("id") == params.document_id_1:
            doc1 = doc
        if doc.get("id") == params.document_id_2:
            doc2 = doc

    if not doc1:
        return {"error": f"Document '{params.document_id_1}' not found"}
    if not doc2:
        return {"error": f"Document '{params.document_id_2}' not found"}

    # Simulated comparison
    comparison = {
        "documents": [
            {"id": doc1["id"], "title": doc1.get("title")},
            {"id": doc2["id"], "title": doc2.get("title")},
        ],
        "comparison_aspect": params.comparison_aspect,
        "similarities": doc1.get("comparisons", {}).get(doc2["id"], {}).get("similarities", []),
        "differences": doc1.get("comparisons", {}).get(doc2["id"], {}).get("differences", []),
        "contradictions": doc1.get("comparisons", {}).get(doc2["id"], {}).get("contradictions", []),
    }

    return comparison


def take_notes(params: TakeNotesParams) -> Dict[str, Any]:
    """Store a research note."""
    note = {
        "id": f"note_{len(_research_data.get('notes', []))+1}",
        "content": params.note,
        "source_document": params.source_document,
        "tags": params.tags,
        "created_at": datetime.now().isoformat(),
    }

    if "notes" not in _research_data:
        _research_data["notes"] = []
    _research_data["notes"].append(note)

    return {
        "success": True,
        "note_id": note["id"],
        "message": "Note saved successfully",
    }


def search_web(params: SearchWebParams) -> Dict[str, Any]:
    """Search the web for information (simulated)."""
    # Return simulated search results relevant to research
    simulated_results = [
        {
            "title": f"Latest research on {params.query}",
            "url": f"https://research.example.com/{params.query.replace(' ', '-')}",
            "snippet": f"Recent findings about {params.query} suggest important developments in the field...",
            "published": "2024-01-15",
        },
        {
            "title": f"{params.query}: A comprehensive overview",
            "url": f"https://wiki.example.com/{params.query.replace(' ', '_')}",
            "snippet": f"This article provides a comprehensive overview of {params.query} and related topics...",
            "published": "2024-02-01",
        },
    ]

    return {
        "query": params.query,
        "results": simulated_results[:params.limit],
        "count": len(simulated_results[:params.limit]),
    }


def generate_summary(params: GenerateSummaryParams) -> Dict[str, Any]:
    """Generate a summary from documents and notes."""
    documents = _research_data.get("documents", [])
    notes = _research_data.get("notes", [])

    # Gather content from specified documents
    doc_contents = []
    for doc in documents:
        if not params.document_ids or doc.get("id") in params.document_ids:
            doc_contents.append({
                "title": doc.get("title"),
                "key_points": doc.get("extracted_facts", [])[:3],
            })

    # Include notes if requested
    note_contents = []
    if params.include_notes:
        for note in notes:
            if params.document_ids:
                if note.get("source_document") in params.document_ids:
                    note_contents.append(note.get("content"))
            else:
                note_contents.append(note.get("content"))

    # Store the summary
    summary = {
        "id": f"summary_{len(_research_data.get('summaries', []))+1}",
        "document_count": len(doc_contents),
        "note_count": len(note_contents),
        "focus_topic": params.focus_topic,
        "sources": doc_contents,
        "notes_included": note_contents,
        "generated_at": datetime.now().isoformat(),
    }

    if "summaries" not in _research_data:
        _research_data["summaries"] = []
    _research_data["summaries"].append(summary)

    return {
        "summary_id": summary["id"],
        "summary": summary,
        "success": True,
    }


# Tool creation

def get_research_tools() -> List[Tool]:
    """Get all research synthesis tools."""
    return [
        Tool(
            name="search_documents",
            description="Search the document corpus by query. Returns document previews with relevance scores.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for document content"},
                    "doc_type": {"type": "string", "description": "Filter by type: report, documentation, policy, analysis"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 5}
                },
                "required": ["query"]
            },
            function=lambda **kwargs: search_documents(SearchDocumentsParams(**kwargs))
        ),
        Tool(
            name="read_document",
            description="Read the full content of a document by its ID.",
            parameters={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "ID of the document to read"}
                },
                "required": ["document_id"]
            },
            function=lambda **kwargs: read_document(ReadDocumentParams(**kwargs))
        ),
        Tool(
            name="extract_facts",
            description="Extract key facts and findings from a document. Optionally focus on a specific topic.",
            parameters={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "ID of the document"},
                    "focus_area": {"type": "string", "description": "Specific topic to focus on"}
                },
                "required": ["document_id"]
            },
            function=lambda **kwargs: extract_facts(ExtractFactsParams(**kwargs))
        ),
        Tool(
            name="compare_sources",
            description="Compare two documents to find similarities, differences, and contradictions.",
            parameters={
                "type": "object",
                "properties": {
                    "document_id_1": {"type": "string", "description": "First document ID"},
                    "document_id_2": {"type": "string", "description": "Second document ID"},
                    "comparison_aspect": {"type": "string", "description": "Specific aspect to compare"}
                },
                "required": ["document_id_1", "document_id_2"]
            },
            function=lambda **kwargs: compare_sources(CompareSourcesParams(**kwargs))
        ),
        Tool(
            name="take_notes",
            description="Save research notes for later reference. Can link to source documents.",
            parameters={
                "type": "object",
                "properties": {
                    "note": {"type": "string", "description": "The note content"},
                    "source_document": {"type": "string", "description": "Document ID this note is from"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for organizing"}
                },
                "required": ["note"]
            },
            function=lambda **kwargs: take_notes(TakeNotesParams(**kwargs))
        ),
        Tool(
            name="search_web",
            description="Search the web for additional information on a topic.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 5}
                },
                "required": ["query"]
            },
            function=lambda **kwargs: search_web(SearchWebParams(**kwargs))
        ),
        Tool(
            name="generate_summary",
            description="Generate a synthesis summary from documents and research notes.",
            parameters={
                "type": "object",
                "properties": {
                    "document_ids": {"type": "array", "items": {"type": "string"}, "description": "Document IDs to include"},
                    "include_notes": {"type": "boolean", "description": "Include research notes", "default": True},
                    "focus_topic": {"type": "string", "description": "Topic to focus the summary on"}
                },
                "required": []
            },
            function=lambda **kwargs: generate_summary(GenerateSummaryParams(**kwargs))
        ),
    ]
