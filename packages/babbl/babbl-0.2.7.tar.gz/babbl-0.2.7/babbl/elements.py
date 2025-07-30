"""Custom elements that are not supported by marko."""

import re
from typing import TYPE_CHECKING, List, Optional

from marko import block
from marko.element import Element

if TYPE_CHECKING:
    from marko.source import Source


class Table(block.BlockElement):
    """Table element for markdown tables."""

    priority = 6
    pattern = re.compile(r"^\s*\|.*\|.*$", re.MULTILINE)

    def __init__(self, headers: List[str], rows: List[List[str]]):
        self.headers = headers
        self.rows = rows
        self.children = []

    @classmethod
    def match(cls, source: "Source") -> bool:
        """Check if the current position contains a table."""
        lines = []
        pos = source.pos

        # collect consecutive lines that look like table rows
        while pos < len(source._buffer):
            line = source._buffer[pos:].split("\n")[0]
            if not line.strip():
                break
            if "|" in line and len(line.split("|")) > 2:
                lines.append(line)
                pos += len(line) + 1  # +1 for newline
            else:
                break

        if len(lines) < 2:
            return False

        # check if there's a header separator
        has_separator = any(re.match(r"^\s*\|[\s\-:|]+\|\s*$", line) for line in lines)

        return has_separator

    @classmethod
    def parse(cls, source: "Source") -> "Table":
        """Parse a table from the source."""
        lines = []
        start_pos = source.pos

        # collect table lines
        while not source.exhausted:
            line = source.next_line()
            if not line or not line.strip():
                break
            if "|" in line and len(line.split("|")) > 2:
                lines.append(line.strip())
                source.consume()
            else:
                break

        if len(lines) < 2:
            source.pos = start_pos
            raise ValueError("Invalid table structure")

        # parse headers and separator
        header_line = lines[0]
        separator_line = lines[1]
        data_lines = lines[2:]

        # parse headers
        headers = cls._parse_row(header_line)

        # validate separator
        if not cls._is_valid_separator(separator_line, len(headers)):
            source.pos = start_pos
            raise ValueError("Invalid table separator")

        # parse data rows
        rows = []
        for line in data_lines:
            if line.strip() and "|" in line:
                row = cls._parse_row(line)
                # pad row if necessary
                while len(row) < len(headers):
                    row.append("")
                rows.append(row[: len(headers)])  # truncate if too long

        return cls(headers, rows)

    @staticmethod
    def _parse_row(line: str) -> List[str]:
        """Parse a table row into cells."""
        # remove leading/trailing pipes and split
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]

        # split by | and strip whitespace
        cells = [cell.strip() for cell in line.split("|")]
        return cells

    @staticmethod
    def _is_valid_separator(line: str, num_columns: int) -> bool:
        """Check if a line is a valid table separator."""
        if not re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
            return False

        cells = Table._parse_row(line)
        if len(cells) != num_columns:
            return False

        # check that each cell contains only dashes, colons, and spaces
        for cell in cells:
            if not re.match(r"^[\s\-:]+$", cell):
                return False

        return True


class TableHead(Element):
    """Table head element."""

    def __init__(self, headers: List[str]):
        self.headers = headers
        self.children: List[Element] = []


class TableBody(Element):
    """Table body element."""

    def __init__(self, rows: List[List[str]]):
        self.rows = rows
        self.children: List[Element] = []


class TableRow(Element):
    """Table row element."""

    def __init__(self, cells: List[str]):
        self.cells = cells
        self.children: List[Element] = []


class TableCell(Element):
    """Table cell element."""

    def __init__(self, content: str):
        self.content = content
        self.children: List[Element] = []


class TableHeaderCell(Element):
    """Table header cell element."""

    def __init__(self, content: str):
        self.content = content
        self.children: List[Element] = []


def parse_table_from_text(text: str) -> Table | None:
    """Parse a table from text content."""
    lines = text.strip().split("\n")
    table_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            break
        if "|" in line and len(line.split("|")) > 2:
            table_lines.append(line)
        else:
            break

    if len(table_lines) < 2:
        return None

    # check for header separator
    has_separator = any(
        re.match(r"^\s*\|[\s\-:|]+\|\s*$", line) for line in table_lines
    )

    if not has_separator:
        return None

    try:
        # parse headers and separator
        header_line = table_lines[0]
        separator_line = table_lines[1]
        data_lines = table_lines[2:]

        # parse headers
        headers = Table._parse_row(header_line)

        # validate separator
        if not Table._is_valid_separator(separator_line, len(headers)):
            return None

        # parse data rows
        rows = []
        for line in data_lines:
            if line.strip() and "|" in line:
                row = Table._parse_row(line)
                # pad row if necessary
                while len(row) < len(headers):
                    row.append("")
                rows.append(row[: len(headers)])  # truncate if too long

        return Table(headers, rows)
    except Exception:
        return None


class CodeReference(block.BlockElement):
    """Code reference element for referencing code from files."""

    priority = 7
    # Support both old @code-ref syntax and new markdown link syntax
    old_pattern = re.compile(r"^\s*@code-ref\s+([^\s]+)\s+(.+)$", re.MULTILINE)
    # Pattern for [description](path#anchor) format - only match code-like anchors on their own line
    link_pattern = re.compile(
        r"^\s*\[([^\]]+)\]\(([^)]*#[a-zA-Z_L][^)]*)\)\s*$", re.MULTILINE
    )
    # Pattern for HTML file links without anchors
    html_pattern = re.compile(r"^\s*\[([^\]]+)\]\(([^)]*\.html)\)\s*$", re.MULTILINE)
    # Pattern for simple #reference format on its own line
    hash_pattern = re.compile(r"^\s*#([a-zA-Z_][a-zA-Z0-9_]*)\s*$", re.MULTILINE)

    def __init__(self, file_path: str, reference: str, syntax_type: str = "old"):
        self.file_path = file_path
        self.reference = reference
        self.syntax_type = syntax_type  # "old", "link", or "hash"
        self.children = []

    @classmethod
    def match(cls, source: "Source") -> bool:
        """Check if the current position contains a code reference."""
        if source.exhausted:
            return False
        line = source._buffer[source.pos :].split("\n")[0].strip()

        # Check if this is a code reference pattern
        is_match = (
            bool(cls.old_pattern.match(line))
            or bool(cls.link_pattern.match(line))
            or bool(cls.html_pattern.match(line))
            or bool(cls.hash_pattern.match(line))
        )

        # Additional check: make sure next_line() will work in parse()
        if is_match:
            # Test if next_line() would return None
            test_line = source.next_line()
            if test_line is None:
                # If next_line() returns None, don't match to avoid the error
                return False
            # We don't consume here, just test

        return is_match

    @classmethod
    def parse(cls, source: "Source") -> "CodeReference":
        """Parse a code reference from the source."""
        # Get the line using next_line()
        line = source.next_line()
        if line is None:
            raise ValueError("Expected code reference line but reached end of source")

        line = line.strip()
        source.consume()

        # Try old @code-ref syntax first
        match = cls.old_pattern.match(line)
        if match:
            file_path = match.group(1)
            reference = match.group(2).strip()
            return cls(file_path, reference, "old")

        # Try markdown link syntax
        match = cls.link_pattern.match(line)
        if match:
            description = match.group(1)
            url = match.group(2)

            # Parse the URL to extract file path and reference
            file_path, reference = cls._parse_link_url(url, description)
            return cls(file_path, reference, "link")

        # Try HTML file link syntax
        match = cls.html_pattern.match(line)
        if match:
            description = match.group(1)
            file_path = match.group(2)
            # For HTML files, use "body" as the default reference
            return cls(file_path, "body", "html")

        # Try simple hash reference
        match = cls.hash_pattern.match(line)
        if match:
            reference = match.group(1)
            # For hash references, we'll need to determine the file path from context
            # For now, use empty string - this will be handled by the processor
            return cls("", reference, "hash")

        raise ValueError("Invalid code reference format")

    @classmethod
    def _parse_link_url(cls, url: str, description: str) -> tuple[str, str]:
        """Parse a link URL to extract file path and reference."""
        # Handle anchor-style references like ../path/file.py#L10
        if "#" in url:
            file_path, anchor = url.split("#", 1)

            # Convert GitHub-style line anchors to our format
            if anchor.startswith("L"):
                try:
                    # Check for range format L1-L20
                    if "-L" in anchor:
                        # Format: L1-L20
                        parts = anchor.split("-L")
                        start_line = parts[0][1:]  # Remove 'L' from start
                        end_line = parts[1]
                        reference = f"lines {start_line}-{end_line}"
                    # Also check for old format L1-20 (without second L)
                    elif "-" in anchor and anchor.count("-") == 1:
                        # Format: L1-20
                        parts = anchor.split("-")
                        if parts[0].startswith("L") and parts[1].isdigit():
                            start_line = parts[0][1:]  # Remove 'L' from start
                            end_line = parts[1]
                            reference = f"lines {start_line}-{end_line}"
                        else:
                            line_num = int(anchor[1:])
                            reference = f"line {line_num}"
                    else:
                        line_num = int(anchor[1:])
                        reference = f"line {line_num}"
                except ValueError:
                    reference = anchor
            else:
                reference = anchor
        else:
            file_path = url
            # For HTML files, default to extracting body content
            if file_path.lower().endswith(".html"):
                reference = "body"
            else:
                # Try to extract reference from description
                # Look for patterns like "line 1", "lines 1-5", function names, etc.
                desc_lower = description.lower()
                if "line " in desc_lower:
                    # Extract line reference from description
                    line_match = re.search(r"line\s+(\d+)", desc_lower)
                    if line_match:
                        reference = f"line {line_match.group(1)}"
                    else:
                        # Try range
                        range_match = re.search(
                            r"lines\s+(\d+)[-:]\s*(\d+)", desc_lower
                        )
                        if range_match:
                            reference = (
                                f"lines {range_match.group(1)}-{range_match.group(2)}"
                            )
                        else:
                            reference = description
                else:
                    # Assume description is the reference (function/class name)
                    reference = description.split()[-1] if description else "content"

        return file_path, reference
