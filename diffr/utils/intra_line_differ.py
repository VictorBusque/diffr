from typing import List
from difflib import SequenceMatcher
from diffr.data_models.diff import TokenDiff

def compute_token_diffs(original: str, updated: str) -> List[TokenDiff]:
    """
    Compute token-level (character-level) diffs between two strings.
    Uses Python's SequenceMatcher for finding the differences.
    
    Args:
        original: Original text string
        updated: Updated text string
        
    Returns:
        List of TokenDiff objects representing the differences
    """
    diffs = []
    matcher = SequenceMatcher(None, original, updated)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Equal parts
            diffs.append(TokenDiff(
                operation='equal',
                token=original[i1:i2]
            ))
        elif tag == 'delete':
            # Parts in original but not in updated
            diffs.append(TokenDiff(
                operation='delete',
                token=original[i1:i2]
            ))
        elif tag == 'insert':
            # Parts in updated but not in original
            diffs.append(TokenDiff(
                operation='insert',
                token=updated[j1:j2]
            ))
        elif tag == 'replace':
            # Parts that were replaced
            diffs.append(TokenDiff(
                operation='delete',
                token=original[i1:i2]
            ))
            diffs.append(TokenDiff(
                operation='insert',
                token=updated[j1:j2]
            ))
    
    return diffs
