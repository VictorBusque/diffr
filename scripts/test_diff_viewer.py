import json

from diffr import diff_hunks
from diffr.data_models.diff_model import Diff

if __name__ == "__main__":
    original = """import React from 'react';
import { CodeLine, DiffBlock, DiffItem } from '../../types/types';
import SnippetDiff from '../snippetDiff/SnippetDiff';
import './styles.css';

interface DiffViewerProps {
    loading: boolean;
    isMobile: boolean;
    currentBlockIndex: number;
    diffBlocks: DiffBlock[];
    currentBlockContent: { original: string; modified: string };
    highlightedChanges: DiffItem[];
    explanations: string[];
}

const DiffViewer: React.FC<DiffViewerProps> = ({
    loading,
    isMobile,
    currentBlockIndex,
    diffBlocks,
    currentBlockContent,
    highlightedChanges,
    explanations,
}) => {
    if (loading) {
        return (
            <div className="terminal-window diff-viewer-loading">
                <div className="diff-viewer-spinner"></div>
                <p className="diff-viewer-loading-text">Analyzing diff blocks...</p>
            </div>
        );
    }

    // Split the current block content into lines.
    const originalLines = currentBlockContent.original.split('\n');
    const modifiedLines = currentBlockContent.modified.split('\n');

    // Create maps for quick lookup using the pre-calculated relative line numbers.
    const removedLinesMap = new Map<number, DiffItem>();
    const addedLinesMap = new Map<number, DiffItem>();

    highlightedChanges.forEach((change) => {
        if (change.relativeLineNumber !== undefined) {
            if (change.type === 'removed') {
                removedLinesMap.set(change.relativeLineNumber, change);
            } else if (change.type === 'added') {
                addedLinesMap.set(change.relativeLineNumber, change);
            }
        }
    });

    // Map original lines to CodeLine format using relative numbering.
    const originalCodeLines: CodeLine[] = originalLines.map((line, i) => {
        const relativeLineNumber = i + 1;
        const changeItem = removedLinesMap.get(relativeLineNumber);

        return {
            lineNumber: relativeLineNumber,
            content: line,
            type: changeItem ? 'removed' : 'unchanged',
            changeType: changeItem ? 'removed' : 'unchanged', // Add changeType for compatibility
            wordDiffs: changeItem?.wordDiffs,
        };
    });

    // Map modified lines similarly.
    const modifiedCodeLines: CodeLine[] = modifiedLines.map((line, i) => {
        const relativeLineNumber = i + 1;
        const changeItem = addedLinesMap.get(relativeLineNumber);

        return {
            lineNumber: relativeLineNumber,
            content: line,
            changeType: changeItem ? 'added' : 'unchanged', // Add changeType for compatibility
            wordDiffs: changeItem?.wordDiffs,
        };
    });

    return (
        <div className="terminal-window diff-viewer-container">
            <div className="terminal-content">
                {/* Header */}
                <div className="command-line">
                    <span className="prompt">$</span>
                    <span className="command">
                        diffr compare --block {currentBlockIndex + 1}/{diffBlocks.length}
                    </span>
                </div>

                {/* Diff Panels */}
                <div className={`diff-viewer-panels ${isMobile ? 'mobile' : ''}`}>
                    <SnippetDiff
                        fileName="Original"
                        codeLines={originalCodeLines}
                        showCommand={false}
                        panelType="left"
                    />
                    <SnippetDiff
                        fileName="Modified"
                        codeLines={modifiedCodeLines}
                        showCommand={false}
                        panelType="right"
                    />
                </div>
                <div className="command-line">
                    <span className="prompt">$</span>
                    <span className="command">diffr explain --block {currentBlockIndex + 1}/{diffBlocks.length}</span>
                </div>
                {/* Analysis Section */}
                <div className="diff-viewer-analysis">
                    <div className="analysis-content">
                        <p>{explanations[currentBlockIndex] || 'No analysis available.'}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DiffViewer;
"""
    updated = """import React from 'react';
import { CodeLine, DiffBlock, DiffItem } from '../../types/types';
import SnippetDiff from '../snippetDiff/SnippetDiff';
import './styles.css';

interface DiffViewerProps {
    loading: boolean;
    isMobile: boolean;
    currentBlockIndex: number;
    diffBlocks: DiffBlock[];
    currentBlockContent: { original: string; modified: string };
    highlightedChanges: DiffItem[];
    explanations: string[];
}

const DiffViewer: React.FC<DiffViewerProps> = ({
    loading,
    isMobile,
    currentBlockIndex,
    diffBlocks,
    currentBlockContent,
    highlightedChanges,
    explanations,
}) => {
    if (loading) {
        return (
            <div className="terminal-window diff-viewer-loading">
                <div className="diff-viewer-spinner"></div>
                <p className="diff-viewer-loading-text">Analyzing diff blocks...</p>
            </div>
        );
    }

    // Split the current block content into lines.
    const originalLines = currentBlockContent.original.split('\n');
    const modifiedLines = currentBlockContent.modified.split('\n');

    // Create maps for quick lookup using the pre-calculated relative line numbers.
    const removedLinesMap = new Map<number, DiffItem>();
    const addedLinesMap = new Map<number, DiffItem>();

    highlightedChanges.forEach((change) => {
        if (change.relativeLineNumber !== undefined) {
            if (change.type === 'removed') {
                removedLinesMap.set(change.relativeLineNumber, change);
            } else if (change.type === 'added') {
                addedLinesMap.set(change.relativeLineNumber, change);
            }
        }
    });

    // Map original lines to CodeLine format using relative numbering.
    const originalCodeLines: CodeLine[] = originalLines.map((line, i) => {
        const relativeLineNumber = i + 1;
        const changeItem = removedLinesMap.get(relativeLineNumber);

        return {
            lineNumber: relativeLineNumber,
            content: line,
            type: changeItem ? 'removed' : 'unchanged',
            changeType: changeItem ? 'removed' : 'unchanged', // Add changeType for compatibility
            wordDiffs: changeItem?.wordDiffs || [],
        };
    });

    // Map modified lines similarly.
    const modifiedCodeLines: CodeLine[] = modifiedLines.map((line, i) => {
        const relativeLineNumber = i + 1;
        const changeItem = addedLinesMap.get(relativeLineNumber);

        return {
            lineNumber: relativeLineNumber,
            content: line,
            type: changeItem ? 'added' : 'unchanged',
            changeType: changeItem ? 'added' : 'unchanged', // Add changeType for compatibility
            wordDiffs: changeItem?.wordDiffs || [],
        };
    });

    return (
        <div className="terminal-window diff-viewer-container">
            <div className="terminal-content">
                {/* Header */}
                <div className="command-line">
                    <span className="prompt">$</span>
                    <span className="command">
                        diffr compare --block {currentBlockIndex + 1}/{diffBlocks.length}
                    </span>
                </div>

                {/* Diff Panels */}
                <div className={`diff-viewer-panels ${isMobile ? 'mobile' : ''}`}>
                    <SnippetDiff
                        fileName="Original"
                        codeLines={originalCodeLines}
                        showCommand={false}
                        panelType="left"
                    />
                    <SnippetDiff
                        fileName="Modified"
                        codeLines={modifiedCodeLines}
                        showCommand={false}
                        panelType="right"
                    />
                </div>
                <div className="command-line">
                    <span className="prompt">$</span>
                    <span className="command">diffr explain --block {currentBlockIndex + 1}/{diffBlocks.length}</span>
                </div>
                {/* Analysis Section */}
                <div className="diff-viewer-analysis">
                    <div className="analysis-content">
                        <p>{explanations[currentBlockIndex] || 'No analysis available.'}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DiffViewer;
"""
    output = diff_hunks(original, updated, 0.4)
    print(json.dumps(output, indent=2))
    diff = Diff.from_hunks(output)
    print(diff)
