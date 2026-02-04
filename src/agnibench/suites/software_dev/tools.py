"""
Tools for the software development benchmark suite.

Provides tools for code navigation, debugging, and software engineering tasks.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agentbuilder.Tools.base import Tool, Response


# Storage for simulated data (populated by environment)
_software_dev_data: Dict[str, Any] = {
    "source_files": [],
    "error_logs": [],
    "test_results": [],
    "git_history": [],
    "documentation": [],
    "fixes_applied": [],
    "tests_run": [],
    "notes_added": [],
}


def set_software_dev_data(data: Dict[str, Any]) -> None:
    """Set the software dev data (called by environment)."""
    global _software_dev_data
    _software_dev_data = data


def get_software_dev_data() -> Dict[str, Any]:
    """Get current software dev data."""
    return _software_dev_data


# Pydantic models for tool parameters

class SearchCodebaseParams(BaseModel):
    """Parameters for searching the codebase."""
    query: Optional[str] = Field(default=None, description="Text to search in file names, content, or symbols")
    file_pattern: Optional[str] = Field(default=None, description="File path pattern (e.g., '*.py', 'src/auth/*')")
    symbol_type: Optional[str] = Field(default=None, description="Filter by symbol type: 'class', 'function', 'import'")
    has_bugs: Optional[bool] = Field(default=None, description="Filter to files with known bugs")


class ReadFileParams(BaseModel):
    """Parameters for reading a source file."""
    file_path: str = Field(description="Path to the file to read")
    start_line: Optional[int] = Field(default=None, description="Start reading from this line (1-indexed)")
    end_line: Optional[int] = Field(default=None, description="Stop reading at this line")


class SearchLogsParams(BaseModel):
    """Parameters for searching error/debug logs."""
    level: Optional[str] = Field(default=None, description="Log level: 'ERROR', 'WARNING', 'INFO', 'DEBUG'")
    file_path: Optional[str] = Field(default=None, description="Filter by source file path")
    query: Optional[str] = Field(default=None, description="Text to search in log messages")
    hours_back: int = Field(default=24, description="Search logs from the last N hours")


class GetStackTraceParams(BaseModel):
    """Parameters for getting a stack trace."""
    log_id: str = Field(description="ID of the error log entry")


class RunTestsParams(BaseModel):
    """Parameters for running tests."""
    file_path: Optional[str] = Field(default=None, description="Test file to run (runs all if not specified)")
    test_name: Optional[str] = Field(default=None, description="Specific test name to run")
    verbose: bool = Field(default=False, description="Include detailed output")


class GetGitHistoryParams(BaseModel):
    """Parameters for getting git history."""
    file_path: Optional[str] = Field(default=None, description="Filter by file path")
    author: Optional[str] = Field(default=None, description="Filter by author email")
    limit: int = Field(default=10, description="Maximum commits to return")


class GetFileDependenciesParams(BaseModel):
    """Parameters for getting file dependencies."""
    file_path: str = Field(description="Path to the file")
    direction: str = Field(default="both", description="'imports' (what this file imports), 'imported_by' (what imports this), or 'both'")


class SearchDocumentationParams(BaseModel):
    """Parameters for searching documentation."""
    query: str = Field(description="Search query")


class FindReferencesParams(BaseModel):
    """Parameters for finding references to a symbol."""
    symbol_name: str = Field(description="Name of the symbol (function, class, variable)")
    symbol_type: Optional[str] = Field(default=None, description="Type: 'function', 'class', 'variable'")


class ApplyFixParams(BaseModel):
    """Parameters for applying a fix."""
    file_path: str = Field(description="Path to the file to fix")
    line_number: int = Field(description="Line number to modify")
    old_code: str = Field(description="Current code to replace")
    new_code: str = Field(description="New code to insert")
    description: str = Field(description="Description of the fix")


class AddNoteParams(BaseModel):
    """Parameters for adding investigation notes."""
    title: str = Field(description="Note title")
    content: str = Field(description="Note content")
    related_files: List[str] = Field(default_factory=list, description="Related file paths")


# Pydantic result models

class FileSearchResult(BaseModel):
    """A file found in codebase search."""
    path: str
    language: Optional[str] = None
    lines: Optional[int] = None
    classes: List[str] = []
    functions: List[str] = []
    has_bugs: bool = False
    last_modified: Optional[str] = None


class SearchCodebaseResult(BaseModel):
    """Result of searching the codebase."""
    success: bool
    count: int
    files: List[FileSearchResult]


class ReadFileResult(BaseModel):
    """Result of reading a file."""
    success: bool
    path: Optional[str] = None
    language: Optional[str] = None
    total_lines: Optional[int] = None
    showing_lines: Optional[str] = None
    content: Optional[str] = None
    imports: Optional[List[str]] = None
    classes: Optional[List[str]] = None
    functions: Optional[List[str]] = None
    has_bugs: Optional[bool] = None
    bug_description: Optional[str] = None
    error: Optional[str] = None


class LogEntry(BaseModel):
    """A log entry in search results."""
    id: str
    timestamp: str
    level: str
    file: Optional[str] = None
    line: Optional[int] = None
    message: str
    has_stack_trace: bool = False


class SearchLogsResult(BaseModel):
    """Result of searching logs."""
    success: bool
    count: int
    logs: List[LogEntry]


class GetStackTraceResult(BaseModel):
    """Result of getting a stack trace."""
    success: bool
    log_id: Optional[str] = None
    timestamp: Optional[str] = None
    level: Optional[str] = None
    file: Optional[str] = None
    line: Optional[int] = None
    message: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TestResult(BaseModel):
    """A single test result."""
    file: str
    test_name: str
    status: str
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    failure_reason: Optional[str] = None


class RunTestsResult(BaseModel):
    """Result of running tests."""
    success: bool
    total: int
    passed: int
    failed: int
    results: List[TestResult]


class GetGitHistoryResult(BaseModel):
    """Result of getting git history."""
    success: bool
    count: int
    commits: List[Dict[str, Any]]


class GetFileDependenciesResult(BaseModel):
    """Result of getting file dependencies."""
    success: bool
    file: Optional[str] = None
    imports: Optional[List[str]] = None
    imported_by: Optional[List[str]] = None
    error: Optional[str] = None


class DocumentationResult(BaseModel):
    """A documentation search result."""
    title: str
    path: str
    last_updated: Optional[str] = None
    snippet: str


class SearchDocumentationResult(BaseModel):
    """Result of searching documentation."""
    success: bool
    count: int
    documents: List[DocumentationResult]


class SymbolReference(BaseModel):
    """A reference to a symbol in code."""
    file: str
    line: int
    content: str
    is_definition: bool = False


class FindReferencesResult(BaseModel):
    """Result of finding references."""
    success: bool
    symbol: str
    count: int
    references: List[SymbolReference]


class ApplyFixResult(BaseModel):
    """Result of applying a fix."""
    success: bool
    message: Optional[str] = None
    description: Optional[str] = None
    error: Optional[str] = None


class AddNoteResult(BaseModel):
    """Result of adding a note."""
    success: bool
    note_id: str
    message: str


# Tool implementation functions

def search_codebase(params: SearchCodebaseParams) -> SearchCodebaseResult:
    """Search the codebase for files, symbols, or content."""
    files = _software_dev_data.get("source_files", [])
    results = []

    for file in files:
        match = True

        if params.query:
            query_lower = params.query.lower()
            content_match = (
                query_lower in file.get("path", "").lower() or
                query_lower in file.get("content", "").lower() or
                any(query_lower in cls.lower() for cls in file.get("classes", [])) or
                any(query_lower in fn.lower() for fn in file.get("functions", []))
            )
            if not content_match:
                match = False

        if params.file_pattern and match:
            pattern = params.file_pattern.replace("*", "")
            if pattern not in file.get("path", ""):
                match = False

        if params.symbol_type and match:
            if params.symbol_type == "class" and not file.get("classes"):
                match = False
            elif params.symbol_type == "function" and not file.get("functions"):
                match = False
            elif params.symbol_type == "import" and not file.get("imports"):
                match = False

        if params.has_bugs is not None and match:
            if file.get("has_bugs", False) != params.has_bugs:
                match = False

        if match:
            results.append(FileSearchResult(
                path=file["path"],
                language=file.get("language"),
                lines=file.get("lines"),
                classes=file.get("classes", []),
                functions=file.get("functions", []),
                has_bugs=file.get("has_bugs", False),
                last_modified=file.get("last_modified"),
            ))

    return SearchCodebaseResult(
        success=True,
        count=len(results),
        files=results,
    )


def read_file(params: ReadFileParams) -> ReadFileResult:
    """Read contents of a source file."""
    files = _software_dev_data.get("source_files", [])

    for file in files:
        if file["path"] == params.file_path:
            content = file.get("content", "")
            lines = content.split("\n")

            start = (params.start_line or 1) - 1
            end = params.end_line or len(lines)

            selected_lines = lines[start:end]
            numbered_content = "\n".join(
                f"{i + start + 1:4d} | {line}"
                for i, line in enumerate(selected_lines)
            )

            return ReadFileResult(
                success=True,
                path=file["path"],
                language=file.get("language"),
                total_lines=len(lines),
                showing_lines=f"{start + 1}-{min(end, len(lines))}",
                content=numbered_content,
                imports=file.get("imports", []),
                classes=file.get("classes", []),
                functions=file.get("functions", []),
                has_bugs=file.get("has_bugs", False),
                bug_description=file.get("bug_description") if file.get("has_bugs") else None,
            )

    return ReadFileResult(
        success=False,
        error=f"File not found: {params.file_path}",
    )


def search_logs(params: SearchLogsParams) -> SearchLogsResult:
    """Search error and debug logs."""
    logs = _software_dev_data.get("error_logs", [])
    results = []

    for log in logs:
        match = True

        if params.level and log.get("level") != params.level:
            match = False

        if params.file_path and match:
            if params.file_path not in log.get("file", ""):
                match = False

        if params.query and match:
            if params.query.lower() not in log.get("message", "").lower():
                match = False

        if match:
            results.append(LogEntry(
                id=log["id"],
                timestamp=log["timestamp"],
                level=log["level"],
                file=log.get("file"),
                line=log.get("line"),
                message=log["message"],
                has_stack_trace=log.get("stack_trace") is not None,
            ))

    return SearchLogsResult(
        success=True,
        count=len(results),
        logs=results,
    )


def get_stack_trace(params: GetStackTraceParams) -> GetStackTraceResult:
    """Get detailed stack trace for an error."""
    logs = _software_dev_data.get("error_logs", [])

    for log in logs:
        if log["id"] == params.log_id:
            return GetStackTraceResult(
                success=True,
                log_id=log["id"],
                timestamp=log["timestamp"],
                level=log["level"],
                file=log.get("file"),
                line=log.get("line"),
                message=log["message"],
                stack_trace=log.get("stack_trace", "No stack trace available"),
                context=log.get("context", {}),
            )

    return GetStackTraceResult(
        success=False,
        error=f"Log entry not found: {params.log_id}",
    )


def run_tests(params: RunTestsParams) -> RunTestsResult:
    """Run tests and return results."""
    all_results = _software_dev_data.get("test_results", [])
    results = []

    for test in all_results:
        if params.file_path and params.file_path not in test.get("file", ""):
            continue
        if params.test_name and params.test_name not in test.get("test_name", ""):
            continue

        result = TestResult(
            file=test["file"],
            test_name=test["test_name"],
            status=test["status"],
            duration_ms=test.get("duration_ms"),
        )

        if params.verbose or test["status"] == "failed":
            result.error_message = test.get("error_message")
            result.failure_reason = test.get("failure_reason")

        results.append(result)

    # Track that tests were run
    _software_dev_data["tests_run"].append({
        "timestamp": datetime.now().isoformat(),
        "file_path": params.file_path,
        "test_name": params.test_name,
        "results_count": len(results),
    })

    passed = sum(1 for r in results if r.status == "passed")
    failed = sum(1 for r in results if r.status == "failed")

    return RunTestsResult(
        success=True,
        total=len(results),
        passed=passed,
        failed=failed,
        results=results,
    )


def get_git_history(params: GetGitHistoryParams) -> GetGitHistoryResult:
    """Get git commit history."""
    history = _software_dev_data.get("git_history", [])
    results = []

    for commit in history:
        match = True

        if params.file_path:
            if not any(params.file_path in f for f in commit.get("files_changed", [])):
                match = False

        if params.author and match:
            if params.author.lower() not in commit.get("author", "").lower():
                match = False

        if match:
            results.append(commit)

        if len(results) >= params.limit:
            break

    return GetGitHistoryResult(
        success=True,
        count=len(results),
        commits=results,
    )


def get_file_dependencies(params: GetFileDependenciesParams) -> GetFileDependenciesResult:
    """Get file dependencies (imports and importers)."""
    files = _software_dev_data.get("source_files", [])
    target_file = None

    for file in files:
        if file["path"] == params.file_path:
            target_file = file
            break

    if not target_file:
        return GetFileDependenciesResult(
            success=False,
            error=f"File not found: {params.file_path}",
        )

    imports = None
    imported_by = None

    # What this file imports
    if params.direction in ("imports", "both"):
        imports = target_file.get("imports", [])

    # What files import this one (simplified - check for path matches)
    if params.direction in ("imported_by", "both"):
        imported_by = []
        target_module = params.file_path.replace("/", ".").replace(".py", "").replace("src.", "")

        for file in files:
            if file["path"] != params.file_path:
                for imp in file.get("imports", []):
                    if target_module in imp or params.file_path.split("/")[-1].replace(".py", "") in imp:
                        imported_by.append(file["path"])
                        break

    return GetFileDependenciesResult(
        success=True,
        file=params.file_path,
        imports=imports,
        imported_by=imported_by,
    )


def search_documentation(params: SearchDocumentationParams) -> SearchDocumentationResult:
    """Search project documentation."""
    docs = _software_dev_data.get("documentation", [])
    results = []

    query_lower = params.query.lower()

    for doc in docs:
        if (query_lower in doc.get("title", "").lower() or
            query_lower in doc.get("content", "").lower()):
            results.append(DocumentationResult(
                title=doc["title"],
                path=doc["path"],
                last_updated=doc.get("last_updated"),
                snippet=doc.get("content", "")[:200] + "...",
            ))

    return SearchDocumentationResult(
        success=True,
        count=len(results),
        documents=results,
    )


def find_references(params: FindReferencesParams) -> FindReferencesResult:
    """Find all references to a symbol in the codebase."""
    files = _software_dev_data.get("source_files", [])
    references = []

    for file in files:
        content = file.get("content", "")
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if params.symbol_name in line:
                # Check symbol type if specified
                if params.symbol_type:
                    if params.symbol_type == "class" and f"class {params.symbol_name}" not in line:
                        if params.symbol_name not in file.get("classes", []):
                            continue
                    elif params.symbol_type == "function" and f"def {params.symbol_name}" not in line:
                        if params.symbol_name not in file.get("functions", []):
                            continue

                references.append(SymbolReference(
                    file=file["path"],
                    line=i + 1,
                    content=line.strip(),
                    is_definition=(
                        f"class {params.symbol_name}" in line or
                        f"def {params.symbol_name}" in line
                    ),
                ))

    return FindReferencesResult(
        success=True,
        symbol=params.symbol_name,
        count=len(references),
        references=references,
    )


def apply_fix(params: ApplyFixParams) -> ApplyFixResult:
    """Apply a code fix (simulated)."""
    files = _software_dev_data.get("source_files", [])

    for file in files:
        if file["path"] == params.file_path:
            # Track the fix
            _software_dev_data["fixes_applied"].append({
                "timestamp": datetime.now().isoformat(),
                "file": params.file_path,
                "line": params.line_number,
                "old_code": params.old_code,
                "new_code": params.new_code,
                "description": params.description,
            })

            return ApplyFixResult(
                success=True,
                message=f"Fix applied to {params.file_path} at line {params.line_number}",
                description=params.description,
            )

    return ApplyFixResult(
        success=False,
        error=f"File not found: {params.file_path}",
    )


def add_note(params: AddNoteParams) -> AddNoteResult:
    """Add investigation notes."""
    note = {
        "id": f"note_{len(_software_dev_data.get('notes_added', [])) + 1}",
        "timestamp": datetime.now().isoformat(),
        "title": params.title,
        "content": params.content,
        "related_files": params.related_files,
    }

    _software_dev_data["notes_added"].append(note)

    return AddNoteResult(
        success=True,
        note_id=note["id"],
        message="Note added successfully",
    )


# Create Tool objects

def get_software_dev_tools() -> List[Tool]:
    """Get all software development tools."""
    return [
        Tool(
            name="search_codebase",
            description="Search the codebase for files, classes, functions, or content. Use to find relevant code.",
            parameters=SearchCodebaseParams,
            function=search_codebase,
        ),
        Tool(
            name="read_file",
            description="Read the contents of a source file. Returns line numbers and code.",
            parameters=ReadFileParams,
            function=read_file,
        ),
        Tool(
            name="search_logs",
            description="Search error and debug logs. Filter by level, file, or content.",
            parameters=SearchLogsParams,
            function=search_logs,
        ),
        Tool(
            name="get_stack_trace",
            description="Get detailed stack trace for an error log entry.",
            parameters=GetStackTraceParams,
            function=get_stack_trace,
        ),
        Tool(
            name="run_tests",
            description="Run tests and get results. Can run all tests or filter by file/test name.",
            parameters=RunTestsParams,
            function=run_tests,
        ),
        Tool(
            name="get_git_history",
            description="Get git commit history. Filter by file or author.",
            parameters=GetGitHistoryParams,
            function=get_git_history,
        ),
        Tool(
            name="get_file_dependencies",
            description="Get file dependencies - what it imports and what imports it.",
            parameters=GetFileDependenciesParams,
            function=get_file_dependencies,
        ),
        Tool(
            name="search_documentation",
            description="Search project documentation for relevant information.",
            parameters=SearchDocumentationParams,
            function=search_documentation,
        ),
        Tool(
            name="find_references",
            description="Find all references to a symbol (function, class, variable) in the codebase.",
            parameters=FindReferencesParams,
            function=find_references,
        ),
        Tool(
            name="apply_fix",
            description="Apply a code fix to a file. Specify the line, old code, and new code.",
            parameters=ApplyFixParams,
            function=apply_fix,
        ),
        Tool(
            name="add_note",
            description="Add investigation notes to document findings.",
            parameters=AddNoteParams,
            function=add_note,
        ),
    ]
