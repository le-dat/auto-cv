"""Unit tests for parser service."""

import io
import pytest

from app.services.parser import (
    ParserService,
    PDFParser,
    DOCXParser,
    TextParser,
    PARSER_REGISTRY,
)


class TestTextParser:
    """Tests for TextParser."""

    @pytest.fixture
    def parser(self) -> TextParser:
        return TextParser()

    @pytest.mark.asyncio
    async def test_parse_returns_string_as_is(self, parser: TextParser):
        text = "Hello, this is plain text."
        result = await parser.parse(text)
        assert result == text

    @pytest.mark.asyncio
    async def test_parse_decodes_bytes_to_string(self, parser: TextParser):
        data = b"Hello, bytes!"
        result = await parser.parse(data)
        assert result == "Hello, bytes!"

    @pytest.mark.asyncio
    async def test_parse_handles_unicode(self, parser: TextParser):
        data = "Hello, 世界! Ñoño".encode("utf-8")
        result = await parser.parse(data)
        assert result == "Hello, 世界! Ñoño"


class TestParserService:
    """Tests for ParserService."""

    @pytest.fixture
    def service(self) -> ParserService:
        return ParserService()

    @pytest.mark.asyncio
    async def test_parse_text_passthrough(self, service: ParserService):
        text = "Some resume content"
        result = await service.parse_text(text)
        assert result == text

    @pytest.mark.asyncio
    async def test_parse_file_txt_extension(self, service: ParserService):
        content = b"Plain text resume"
        result = await service.parse_file(content, "resume.txt")
        assert result == "Plain text resume"

    @pytest.mark.asyncio
    async def test_parse_file_md_extension(self, service: ParserService):
        content = b"# Markdown Resume"
        result = await service.parse_file(content, "resume.md")
        assert result == "# Markdown Resume"

    @pytest.mark.asyncio
    async def test_parse_file_unknown_extension_defaults_to_text(
        self, service: ParserService
    ):
        content = b"Unknown format content"
        result = await service.parse_file(content, "resume.xyz")
        assert result == "Unknown format content"

    @pytest.mark.asyncio
    async def test_parse_file_no_extension_defaults_to_text(
        self, service: ParserService
    ):
        content = b"No extension content"
        result = await service.parse_file(content, "resume")
        assert result == "No extension content"

    @pytest.mark.asyncio
    async def test_parse_file_pdf_extension(self, service: ParserService):
        """PDFParser is registered for .pdf but requires a real PDF or path."""
        # TextParser would be used if PDF parsing failed; here we just verify routing
        content = b"not-a-real-pdf"
        # PDFParser.parse will fail on invalid PDF, but routing works
        with pytest.raises(Exception):
            await service.parse_file(content, "resume.pdf")


class TestParserRegistry:
    """Tests for parser registry."""

    def test_pdf_parser_registered(self):
        assert "pdf" in PARSER_REGISTRY
        assert isinstance(PARSER_REGISTRY["pdf"], PDFParser)

    def test_docx_parser_registered(self):
        assert "docx" in PARSER_REGISTRY
        assert isinstance(PARSER_REGISTRY["docx"], DOCXParser)

    def test_txt_parser_registered(self):
        assert "txt" in PARSER_REGISTRY
        assert isinstance(PARSER_REGISTRY["txt"], TextParser)

    def test_md_parser_registered(self):
        assert "md" in PARSER_REGISTRY
        assert isinstance(PARSER_REGISTRY["md"], TextParser)

    def test_text_parser_registered(self):
        assert "text" in PARSER_REGISTRY
        assert isinstance(PARSER_REGISTRY["text"], TextParser)
