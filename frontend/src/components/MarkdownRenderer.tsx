import React from 'react'

interface MarkdownRendererProps {
  content: string
}

/**
 * Simple Markdown Renderer
 * Renders basic markdown without external dependencies
 * Supports: headers, bold, italic, code, lists, links, line breaks
 */
const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const renderMarkdown = (text: string): React.ReactNode[] => {
    const lines = text.split('\n')
    const processed: React.ReactNode[] = []
    let inCodeBlock = false
    let codeBlockContent: string[] = []
    let currentList: React.ReactNode[] = []
    let listKey = 0

    lines.forEach((line, index) => {
      // Code blocks
      if (line.trim().startsWith('```')) {
        if (inCodeBlock) {
          // End code block
          const code = codeBlockContent.join('\n')
          codeBlockContent = []
          inCodeBlock = false
          // Close any open list before code block
          if (currentList.length > 0) {
            processed.push(
              <ul key={`list-${listKey++}`} className="markdown-list">
                {currentList}
              </ul>
            )
            currentList = []
          }
          processed.push(
            <pre key={`code-${index}`} className="markdown-code-block">
              <code>{code}</code>
            </pre>
          )
        } else {
          // Start code block - close any open list
          if (currentList.length > 0) {
            processed.push(
              <ul key={`list-${listKey++}`} className="markdown-list">
                {currentList}
              </ul>
            )
            currentList = []
          }
          inCodeBlock = true
        }
        return
      }

      if (inCodeBlock) {
        codeBlockContent.push(line)
        return
      }

      // Headers
      if (line.startsWith('### ')) {
        if (currentList.length > 0) {
          processed.push(
            <ul key={`list-${listKey++}`} className="markdown-list">
              {currentList}
            </ul>
          )
          currentList = []
        }
        processed.push(
          <h3 key={`h3-${index}`} className="markdown-h3">
            {processInlineMarkdown(line.substring(4))}
          </h3>
        )
        return
      }
      
      if (line.startsWith('## ')) {
        if (currentList.length > 0) {
          processed.push(
            <ul key={`list-${listKey++}`} className="markdown-list">
              {currentList}
            </ul>
          )
          currentList = []
        }
        processed.push(
          <h2 key={`h2-${index}`} className="markdown-h2">
            {processInlineMarkdown(line.substring(3))}
          </h2>
        )
        return
      }
      
      if (line.startsWith('# ')) {
        if (currentList.length > 0) {
          processed.push(
            <ul key={`list-${listKey++}`} className="markdown-list">
              {currentList}
            </ul>
          )
          currentList = []
        }
        processed.push(
          <h1 key={`h1-${index}`} className="markdown-h1">
            {processInlineMarkdown(line.substring(2))}
          </h1>
        )
        return
      }

      // Lists
      const listMatch = line.match(/^(\s*)([-*]|\d+\.)\s+(.+)$/)
      if (listMatch) {
        const listText = listMatch[3]
        currentList.push(
          <li key={`li-${index}`} className="markdown-list-item">
            {processInlineMarkdown(listText)}
          </li>
        )
        return
      }

      // End list on empty line
      if (line.trim() === '' && currentList.length > 0) {
        processed.push(
          <ul key={`list-${listKey++}`} className="markdown-list">
            {currentList}
          </ul>
        )
        currentList = []
        processed.push(<br key={`br-${index}`} />)
        return
      }

      // Horizontal rule
      if (line.trim() === '---' || line.trim() === '***') {
        if (currentList.length > 0) {
          processed.push(
            <ul key={`list-${listKey++}`} className="markdown-list">
              {currentList}
            </ul>
          )
          currentList = []
        }
        processed.push(<hr key={`hr-${index}`} className="markdown-hr" />)
        return
      }

      // Regular paragraph
      if (line.trim()) {
        if (currentList.length > 0) {
          processed.push(
            <ul key={`list-${listKey++}`} className="markdown-list">
              {currentList}
            </ul>
          )
          currentList = []
        }
        processed.push(
          <p key={`p-${index}`} className="markdown-paragraph">
            {processInlineMarkdown(line)}
          </p>
        )
        return
      }

      // Empty line
      if (currentList.length > 0) {
        processed.push(
          <ul key={`list-${listKey++}`} className="markdown-list">
            {currentList}
          </ul>
        )
        currentList = []
      }
      processed.push(<br key={`br-${index}`} />)
    })

    // Close any remaining list
    if (currentList.length > 0) {
      processed.push(
        <ul key={`list-${listKey++}`} className="markdown-list">
          {currentList}
        </ul>
      )
    }

    return processed
  }

  const processInlineMarkdown = (text: string): React.ReactNode[] => {
    const parts: React.ReactNode[] = []
    let keyCounter = 0

    // Process in order: code blocks first (to avoid conflicts), then bold, italic, links
    // Use a recursive approach to handle nested formatting
    
    const processText = (str: string, depth: number = 0): React.ReactNode[] => {
      if (depth > 5) return [str] // Prevent infinite recursion
      
      const result: React.ReactNode[] = []
      let lastIndex = 0
      const matches: Array<{ start: number; end: number; type: string; content: string; extra?: string }> = []
      
      // Find code blocks first (highest priority)
      const codeRegex = /`([^`]+)`/g
      let match
      while ((match = codeRegex.exec(str)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          type: 'code',
          content: match[1]
        })
      }
      
      // Find links
      const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g
      while ((match = linkRegex.exec(str)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          type: 'link',
          content: match[1],
          extra: match[2]
        })
      }
      
      // Find bold (must not be inside code)
      const boldRegex = /\*\*([^*]+)\*\*/g
      while ((match = boldRegex.exec(str)) !== null) {
        // Check if this is inside a code block
        const isInCode = matches.some(m => m.type === 'code' && match.index >= m.start && match.index < m.end)
        if (!isInCode) {
          matches.push({
            start: match.index,
            end: match.index + match[0].length,
            type: 'bold',
            content: match[1]
          })
        }
      }
      
      // Find italic (must not be inside code or bold)
      // Use a simpler regex that doesn't require lookbehind
      const italicRegex = /\*([^*]+?)\*/g
      while ((match = italicRegex.exec(str)) !== null) {
        // Skip if it's actually bold (starts with **)
        if (match.index > 0 && str[match.index - 1] === '*') continue
        if (match.index + match[0].length < str.length && str[match.index + match[0].length] === '*') continue
        const isInCode = matches.some(m => m.type === 'code' && match.index >= m.start && match.index < m.end)
        const isInBold = matches.some(m => m.type === 'bold' && match.index >= m.start && match.index < m.end)
        if (!isInCode && !isInBold) {
          matches.push({
            start: match.index,
            end: match.index + match[0].length,
            type: 'italic',
            content: match[1]
          })
        }
      }
      
      // Sort by position
      matches.sort((a, b) => a.start - b.start)
      
      // Remove overlapping (keep first)
      const nonOverlapping: typeof matches = []
      matches.forEach(m => {
        if (nonOverlapping.length === 0 || m.start >= nonOverlapping[nonOverlapping.length - 1].end) {
          nonOverlapping.push(m)
        }
      })
      
      // Build result
      nonOverlapping.forEach(m => {
        if (m.start > lastIndex) {
          result.push(str.substring(lastIndex, m.start))
        }
        
        const key = `inline-${keyCounter++}`
        switch (m.type) {
          case 'code':
            result.push(<code key={key} className="markdown-inline-code">{m.content}</code>)
            break
          case 'bold':
            result.push(<strong key={key}>{m.content}</strong>)
            break
          case 'italic':
            result.push(<em key={key}>{m.content}</em>)
            break
          case 'link':
            result.push(
              <a key={key} href={m.extra} target="_blank" rel="noopener noreferrer" className="markdown-link">
                {m.content}
              </a>
            )
            break
        }
        
        lastIndex = m.end
      })
      
      if (lastIndex < str.length) {
        result.push(str.substring(lastIndex))
      }
      
      return result.length > 0 ? result : [str]
    }
    
    return processText(text)
  }

  return <div className="markdown-content">{renderMarkdown(content)}</div>
}

export default MarkdownRenderer
