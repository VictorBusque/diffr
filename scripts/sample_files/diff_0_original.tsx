import React from 'react';
import { CodeLine, WordDiff } from '../../types/types';
import './styles.css';

interface SnippetDiffProps {
    fileName: string;
    codeLines: CodeLine[];
    showCommand?: boolean;
    panelType: 'left' | 'right';
}

const SnippetDiff: React.FC<SnippetDiffProps> = ({
    fileName,
    codeLines,
    showCommand = true,
    panelType,
}) => {
    return (
        <div className={`snippet-diff-panel ${panelType}`}>
            <div className="snippet-title">{fileName}</div>
            {showCommand && (
                <div className="snippet-command">
                    <span className="prompt">$</span>
                    <span className="command">cat {fileName}</span>
                </div>
            )}
            <div className="snippet-content">
                {codeLines.map((line, index) => {
                    // Check if line has word diffs
                    const hasWordDiffs = line.wordDiffs && line.wordDiffs.length > 0;

                    return (
                        <div
                            key={index}
                            className={`code-line ${line.changeType || line.type || 'unchanged'}`}
                        >
                            <span className="line-number">{line.lineNumber}</span>
                            <span className="line-content">
                                {hasWordDiffs ? (
                                    renderWordDiffs(line.wordDiffs!)
                                ) : (
                                    line.content
                                )}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

// Helper function to render word-level diffs with better visibility
const renderWordDiffs = (wordDiffs: WordDiff[]) => {
    // Log what we're about to render to help with debugging
    console.log('Rendering word diffs:', wordDiffs);

    return wordDiffs.map((diff, index) => {
        // Apply more distinct styling based on diff type
        const className = `word-diff word-diff-${diff.type}`;

        return (
            <span
                key={index}
                className={className}
                // Add title attribute for tooltip on hover
                title={`${diff.type} text`}
            >
                {diff.text}
            </span>
        );
    });
};

export default SnippetDiff;
