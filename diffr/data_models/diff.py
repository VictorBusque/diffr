from pydantic import BaseModel


class WordDiff(BaseModel):
    word: str
    added: bool
    removed: bool

    def __str__(self) -> str:
        """Convert the word diff to a string representation.

        Returns:
            str: str: The string representation of the word diff.
        """
        if self.added:
            return f"\033[92m{self.word}\033[0m"  # Green for added words
        elif self.removed:
            return f"\033[91m{self.word}\033[0m"  # Red for removed words
        else:
            return self.word


class LineDiff(BaseModel):
    line_number: int
    content: str
    added: bool
    removed: bool
    word_diffs: list[WordDiff]

    def __str__(self) -> str:
        """Convert the line diff to a string representation.

        Returns:
            str: str: The string representation of the line diff.
        """
        word_diffs_str = " ".join(str(word_diff) for word_diff in self.word_diffs)
        if self.added:
            return f"\033[92m{self.line_number}: {word_diffs_str}\033[0m"  # Green for added lines
        elif self.removed:
            return f"\033[91m{self.line_number}: {word_diffs_str}\033[0m"  # Red for removed lines
        else:
            return f"{self.line_number}: {word_diffs_str}"


class BlockDiff(BaseModel):
    block_number: int
    lines: list[LineDiff]

    def __str__(self) -> str:
        """Convert the block diff to a string representation.

        Returns:
            str: str: The string representation of the block diff.
        """
        lines_str = "\n".join(str(line) for line in self.lines)
        return f"Block {self.block_number}:\n{lines_str}"


class FullDiff(BaseModel):
    blocks: list[BlockDiff]

    def __str__(self) -> str:
        """Convert the block diff to a string representation.

        Returns:
            str: str: The string representation of the block diff.
        """
        blocks_str = "\n\n".join(str(block) for block in self.blocks)
        return f"Full Diff:\n{blocks_str}"
