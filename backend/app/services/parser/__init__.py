"""Parser service with Strategy pattern for multiple input formats."""

from typing import Protocol

import fitz  # PyMuPDF


class ParserStrategy(Protocol):
    """Protocol for document parsers."""

    async def parse(self, content: bytes | str) -> str:
        """Parse content and return plain text."""
        ...


class PDFParser:
    """Parser for PDF documents using PyMuPDF."""

    async def parse(self, content: bytes | str) -> str:
        """Extract text from PDF."""
        if isinstance(content, str):
            # Assume it's a file path
            doc = fitz.open(content)
        else:
            doc = fitz.open(stream=content, filetype="pdf")

        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)


class DOCXParser:
    """Parser for DOCX documents."""

    async def parse(self, content: bytes | str) -> str:
        """Extract text from DOCX."""
        import io

        from docx import Document

        if isinstance(content, bytes):
            content = io.BytesIO(content)

        doc = Document(content)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)


class TextParser:
    """Parser for plain text."""

    async def parse(self, content: bytes | str) -> str:
        """Return text as-is."""
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="replace")
        return content


# Registry of parsers by file extension
PARSER_REGISTRY: dict[str, ParserStrategy] = {
    "pdf": PDFParser(),
    "docx": DOCXParser(),
    "txt": TextParser(),
    "text": TextParser(),
    "md": TextParser(),
}


class ParserService:
    """Service that auto-detects format and delegates parsing."""

    async def parse_file(self, content: bytes, filename: str) -> str:
        """Parse file content based on filename extension."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        parser = PARSER_REGISTRY.get(ext, TextParser())
        return await parser.parse(content)

    async def parse_text(self, text: str) -> str:
        """Parse text (no-op passthrough)."""
        return text
