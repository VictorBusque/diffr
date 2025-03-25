from dataclasses import dataclass, field
from enum import Enum


class DiffLineType(str, Enum):
    """Type of difference line: equal, insert, delete, or replace."""

    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"


class InlineDiffType(str, Enum):
    """Type of inline difference: equal, insert, or delete."""

    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"


# ANSI color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    BRIGHT_RED = "\033[1;91m"
    BRIGHT_GREEN = "\033[1;92m"
    STRIKE = "\033[9m"  # Strike-through formatting
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


@dataclass
class Range:
    """Represents a range of line numbers."""

    start: int
    end: int

    def __str__(self) -> str:
        """Return a string representation of the range."""
        if self.start == self.end:
            return f"{self.start}"
        return f"{self.start},{self.end}"


@dataclass
class InlineDiff:
    """Represents an inline difference within a line."""

    type: InlineDiffType
    value: str

    def __str__(self) -> str:
        """Return a colorized string representation of the inline diff."""
        if self.type == InlineDiffType.DELETE:
            return f"{Colors.STRIKE}{Colors.BRIGHT_RED}{self.value}{Colors.RESET}"
        elif self.type == InlineDiffType.INSERT:
            return f"{Colors.UNDERLINE}{Colors.BRIGHT_GREEN}{self.value}{Colors.RESET}"
        else:  # Equal
            return self.value


@dataclass
class DiffLine:
    """Represents a single line in a diff."""

    type: DiffLineType
    line_number_old: int | None = None
    line_number_new: int | None = None
    content_old: str | None = None
    content_new: str | None = None
    inline_diff: list[InlineDiff] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a clear, colorized string representation of the line."""

        def format_line(prefix, line_num, content, color, strike=False):
            if strike:
                return f"{prefix}{line_num:>4} {color}{Colors.STRIKE}{content}{Colors.RESET}"
            return f"{prefix}{line_num:>4} {color}{content}{Colors.RESET}"

        if self.type == DiffLineType.EQUAL:
            content = self.content_old or self.content_new or ""
            line_num = self.line_number_old or self.line_number_new or 0
            return format_line(" ", line_num, content, "")

        elif self.type == DiffLineType.DELETE:
            return format_line("-", self.line_number_old or 0, self.content_old or "", Colors.RED, strike=True)

        elif self.type == DiffLineType.INSERT:
            return format_line("+", self.line_number_new or 0, self.content_new or "", Colors.GREEN)

        elif self.type == DiffLineType.REPLACE:
            # Show both lines (old in red, new in green), with inline diff if present
            old_line_num = self.line_number_old or 0
            new_line_num = self.line_number_new or 0

            if self.inline_diff:
                inline_content = "".join(str(chunk) for chunk in self.inline_diff)
                return format_line("+", new_line_num, inline_content, Colors.GREEN)
            else:
                old_line = format_line("-", old_line_num, self.content_old or "", Colors.RED, strike=True)
                new_line = format_line("+", new_line_num, self.content_new or "", Colors.GREEN)
                return f"{old_line}\n{new_line}"

        return ""


@dataclass
class Hunk:
    """Represents a hunk in a diff, containing a group of changed lines."""

    old_range: Range
    new_range: Range
    lines: list[DiffLine] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the hunk with header and colorized lines."""
        header = f"@@ -{self.old_range} +{self.new_range} @@"
        lines = "\n".join(str(line) for line in self.lines)
        return f"{header}\n{lines}"


@dataclass
class Diff:
    """Represents a complete diff, containing multiple hunks."""

    hunks: list[Hunk] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the complete diff with all hunks."""
        if not self.hunks:
            return "No differences found."

        return "\n\n".join(str(hunk) for hunk in self.hunks)

    @classmethod
    def from_hunks(cls, data: dict) -> "Diff":
        """
        Create a Diff object from a dictionary representation.

        Args:
            data: Dictionary containing the diff data

        Returns:
            Diff object
        """
        hunks = []

        for hunk_data in data.get("hunks", []):
            old_range = Range(**hunk_data.get("old_range", {}))
            new_range = Range(**hunk_data.get("new_range", {}))

            lines = []
            for line_data in hunk_data.get("lines", []):
                inline_diffs = []
                for diff_data in line_data.get("inline_diff", []):
                    inline_diffs.append(
                        InlineDiff(type=InlineDiffType(diff_data.get("type")), value=diff_data.get("value"))
                    )

                lines.append(
                    DiffLine(
                        type=DiffLineType(line_data.get("type")),
                        line_number_old=line_data.get("line_number_old"),
                        line_number_new=line_data.get("line_number_new"),
                        content_old=line_data.get("content_old"),
                        content_new=line_data.get("content_new"),
                        inline_diff=inline_diffs,
                    )
                )

            hunks.append(Hunk(old_range=old_range, new_range=new_range, lines=lines))

        return cls(hunks=hunks)
