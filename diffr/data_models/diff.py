from pydantic import BaseModel, Field
from typing import List, Union, Literal

# ANSI color codes
class Colors:
    RED = "\033[91m"        # Deletion color
    GREEN = "\033[92m"      # Addition color
    BRIGHT_RED = "\033[31;1m"   # Highlighted deletion
    BRIGHT_GREEN = "\033[32;1m"  # Highlighted addition
    RESET = "\033[0m"       # Reset to default color

class DiffInput(BaseModel):
    """
    Input model for the diff algorithm.
    """
    original: str
    updated: str

class DiffElement(BaseModel):
    """
    Base class for diff elements.
    """
    type: str

class LineDiff(DiffElement):
    """
    Represents a line-level diff.
    For unchanged lines, both original and updated contain the same text.
    For insertions or deletions, one side will be empty.
    """
    type: Literal['line'] = 'line'
    original: str
    updated: str
    
    def __str__(self) -> str:
        if self.original == self.updated:
            return self.original
        elif not self.original:
            return f"{Colors.GREEN}+ {self.updated}{Colors.RESET}"
        elif not self.updated:
            return f"{Colors.RED}- {self.original}{Colors.RESET}"
        else:
            return f"{Colors.RED}- {self.original}{Colors.RESET}\n{Colors.GREEN}+ {self.updated}{Colors.RESET}"

class TokenDiff(DiffElement):
    """
    Represents a token-level diff.
    The operation indicates whether the token was inserted, deleted, or is equal.
    """
    type: Literal['token'] = 'token'
    operation: Literal['insert', 'delete', 'equal']
    token: str
    
    def __str__(self) -> str:
        if self.operation == 'equal':
            return self.token
        elif self.operation == 'insert':
            return f"{Colors.BRIGHT_GREEN}{self.token}{Colors.RESET}"
        else:  # delete
            return f"{Colors.BRIGHT_RED}{self.token}{Colors.RESET}"

class PatienceDiffResult(BaseModel):
    """
    The overall diff result.
    It contains a list of diff elements, which can be either line-level or token-level differences.
    """
    diffs: List[Union[LineDiff, TokenDiff]]
    
    def __str__(self) -> str:
        result = []
        current_line = ""
        
        for diff in self.diffs:
            if diff.type == 'line':
                # If we have a current line with tokens, add it to result first
                if current_line:
                    result.append(current_line)
                    current_line = ""
                result.append(str(diff))
            else:  # Token diff
                current_line += str(diff)
                
        # Don't forget to add the last line if it contains tokens
        if current_line:
            result.append(current_line)
            
        return "\n".join(result)
