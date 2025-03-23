from typing import List, Tuple
from diffr.data_models.diff import PatienceDiffResult, LineDiff, TokenDiff

# ANSI color codes for terminal output
GREEN = "\033[92m"  # For additions
RED = "\033[91m"    # For deletions
GRAY = "\033[90m"   # For context lines
RESET = "\033[0m"   # Reset color
BOLD = "\033[1m"    # Bold text
YELLOW_BG = "\033[43m"  # Yellow background for intra-line changes

def convert_to_patience_diff_result(diff_result: List[Tuple[str, str]]) -> PatienceDiffResult:
    """
    Convert raw diff output to PatienceDiffResult model.
    
    Args:
        diff_result: Raw output from patience_diff algorithm [(orig, updated), ...]
        
    Returns:
        PatienceDiffResult object containing LineDiff elements
    """
    diffs = []
    
    for orig, updated in diff_result:
        # Create a LineDiff for each line pair
        diffs.append(LineDiff(original=orig, updated=updated))
    
    return PatienceDiffResult(diffs=diffs)

class DiffViewer:
    """
    A viewer for displaying diffs in a user-friendly format with highlighting.
    """
    
    def __init__(self, show_line_numbers: bool = True, context_lines: int = 3):
        """
        Initialize the diff viewer.
        
        Args:
            show_line_numbers: Whether to show line numbers in the output
            context_lines: Number of unchanged lines to show before and after changes
        """
        self.show_line_numbers = show_line_numbers
        self.context_lines = context_lines
    
    def display_diff(self, diff_result: List[Tuple[str, str]], 
                     file_name: str = None, 
                     output_format: str = "terminal") -> str:
        """
        Display a diff with proper highlighting.
        
        Args:
            diff_result: Output from patience_diff algorithm
            file_name: Optional file name to display in the header
            output_format: Format for the output ('terminal', 'html', etc.)
        
        Returns:
            The formatted diff as a string
        """
        if not diff_result:
            return "No differences found."
        
        # Convert raw diff output to PatienceDiffResult
        patience_diff_result = convert_to_patience_diff_result(diff_result)
        
        # Add header if file name is provided
        header = ""
        if file_name:
            header = f"{BOLD}--- {file_name}{RESET}\n\n"
            
        if output_format == "terminal":
            # Use the __str__ method of PatienceDiffResult
            if self.show_line_numbers:
                # If we need line numbers, use the formatted version
                return header + self._format_terminal_diff(diff_result, file_name)
            else:
                # Otherwise use the built-in string representation
                return header + str(patience_diff_result)
        elif output_format == "html":
            # Future implementation for HTML output
            return "HTML output not implemented yet."
        else:
            return "Unsupported output format."
    
    def _format_terminal_diff(self, diff_result: List[Tuple[str, str]], file_name: str = None) -> str:
        """Format the diff for terminal output with ANSI colors."""
        lines = []
        
        # Add header if file name is provided
        if file_name:
            lines.append(f"{BOLD}--- {file_name}{RESET}")
            lines.append("")
        
        orig_line_num = 1
        upd_line_num = 1
        
        for orig, upd in diff_result:
            # Line was removed
            if upd == "":
                if self.show_line_numbers:
                    lines.append(f"{RED}-{orig_line_num:4d} | {orig}{RESET}")
                else:
                    lines.append(f"{RED}- {orig}{RESET}")
                orig_line_num += 1
            
            # Line was added
            elif orig == "":
                if self.show_line_numbers:
                    lines.append(f"{GREEN}+{upd_line_num:4d} | {upd}{RESET}")
                else:
                    lines.append(f"{GREEN}+ {upd}{RESET}")
                upd_line_num += 1
            
            # Line was unchanged
            else:
                if self.show_line_numbers:
                    lines.append(f"{GRAY} {orig_line_num:4d} | {orig}{RESET}")
                else:
                    lines.append(f"{GRAY}  {orig}{RESET}")
                orig_line_num += 1
                upd_line_num += 1
        
        return "\n".join(lines)
    
    def _highlight_intra_line_changes(self, old_line: str, new_line: str) -> Tuple[str, str]:
        """
        Highlight character-level differences within modified lines.
        
        Args:
            old_line: The original line
            new_line: The updated line
            
        Returns:
            Tuple of highlighted old and new lines
        """
        # This is a simplified implementation
        # For a real implementation, you would need a character-level diff algorithm
        # For now, just return the lines unchanged
        return old_line, new_line

    def _filter_context(self, diff_result: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Filter the diff result to only show context_lines of unchanged lines
        around modifications.
        
        Args:
            diff_result: Output from patience_diff algorithm
            
        Returns:
            Filtered diff with limited context
        """
        # Implementation would go here if you want to limit context lines
        # For now, just return the full diff
        return diff_result


if __name__ == "__main__":
    from diffr.algorithms.patience_cy import patience_diff


    text1 = """
    This is an example of text.
    It has multiple lines.
    Some lines will be changed.
    Some lines will remain the same.
    This is the end of the example.
    """

    text2 = """
    This is an example of text.
    It has multiple lines.
    Some lines have been changed.
    Some lines will remain the same.
    This is the end of the example.
    """

    # Sample diff result for demonstration purposes
    diff = patience_diff(text1, text2)
    
    viewer = DiffViewer(show_line_numbers=False, context_lines=2)
    print(viewer.display_diff(diff, file_name="example.txt"))
    
    # Also show with converted model directly
    patience_result = convert_to_patience_diff_result(diff)
    print("\nDirect model representation:")
    print(patience_result)