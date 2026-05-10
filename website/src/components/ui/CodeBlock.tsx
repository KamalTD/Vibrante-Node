'use client'

import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface CodeLine {
  type: 'keyword' | 'string' | 'comment' | 'function' | 'class' | 'decorator' | 'number' | 'builtin' | 'plain' | 'punctuation'
  content: string
}

type Token = CodeLine

function tokenizePython(code: string): Token[][] {
  const lines = code.split('\n')
  return lines.map((line) => {
    const tokens: Token[] = []
    let remaining = line

    // Simple tokenizer — processes line by line
    while (remaining.length > 0) {
      // Comment
      if (remaining.startsWith('#')) {
        tokens.push({ type: 'comment', content: remaining })
        break
      }

      // String (double quoted)
      const strMatch = remaining.match(/^(f?"[^"]*"|f?'[^']*')/)
      if (strMatch) {
        tokens.push({ type: 'string', content: strMatch[0] })
        remaining = remaining.slice(strMatch[0].length)
        continue
      }

      // Decorator
      const decoratorMatch = remaining.match(/^@\w+/)
      if (decoratorMatch) {
        tokens.push({ type: 'decorator', content: decoratorMatch[0] })
        remaining = remaining.slice(decoratorMatch[0].length)
        continue
      }

      // Keywords
      const keywords = ['async', 'def', 'class', 'return', 'from', 'import', 'if', 'else', 'elif', 'for', 'in', 'not', 'and', 'or', 'True', 'False', 'None', 'await', 'self', 'super', 'raise', 'try', 'except', 'with', 'as', 'pass', 'break', 'continue', 'lambda', 'yield']
      let foundKeyword = false
      for (const kw of keywords) {
        const re = new RegExp(`^(${kw})(?=[^a-zA-Z0-9_]|$)`)
        if (re.test(remaining)) {
          tokens.push({ type: 'keyword', content: kw })
          remaining = remaining.slice(kw.length)
          foundKeyword = true
          break
        }
      }
      if (foundKeyword) continue

      // Builtins
      const builtins = ['print', 'len', 'list', 'dict', 'str', 'int', 'float', 'bool', 'range', 'enumerate', 'zip', 'map', 'filter', 'isinstance', 'getattr', 'setattr', 'hasattr', 'type', 'inputs', 'get']
      let foundBuiltin = false
      for (const bi of builtins) {
        const re = new RegExp(`^(${bi})(?=[^a-zA-Z0-9_]|$)`)
        if (re.test(remaining)) {
          tokens.push({ type: 'builtin', content: bi })
          remaining = remaining.slice(bi.length)
          foundBuiltin = true
          break
        }
      }
      if (foundBuiltin) continue

      // Number
      const numMatch = remaining.match(/^\d+\.?\d*/)
      if (numMatch) {
        tokens.push({ type: 'number', content: numMatch[0] })
        remaining = remaining.slice(numMatch[0].length)
        continue
      }

      // Word (function or identifier)
      const wordMatch = remaining.match(/^[a-zA-Z_]\w*/)
      if (wordMatch) {
        const word = wordMatch[0]
        // Check if followed by ( => function
        const afterWord = remaining.slice(word.length)
        if (afterWord.startsWith('(')) {
          tokens.push({ type: 'function', content: word })
        } else {
          tokens.push({ type: 'plain', content: word })
        }
        remaining = remaining.slice(word.length)
        continue
      }

      // Default: take one character
      tokens.push({ type: 'plain', content: remaining[0] })
      remaining = remaining.slice(1)
    }

    return tokens
  })
}

const tokenColors: Record<Token['type'], string> = {
  keyword: '#c792ea',
  string: '#c3e88d',
  comment: '#546e7a',
  function: '#82aaff',
  class: '#ffcb6b',
  decorator: '#f07178',
  number: '#f78c6c',
  builtin: '#89ddff',
  plain: '#d4d4d4',
  punctuation: '#89ddff',
}

interface CodeBlockProps {
  code: string
  language?: string
  title?: string
  className?: string
  showLineNumbers?: boolean
}

export function CodeBlock({
  code,
  language = 'python',
  title,
  className = '',
  showLineNumbers = true,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const tokenizedLines = tokenizePython(code)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={`rounded-xl overflow-hidden border border-border bg-card ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-surface">
        <div className="flex items-center gap-3">
          {/* Traffic lights */}
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/60" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
            <div className="w-3 h-3 rounded-full bg-green-500/60" />
          </div>
          {title && (
            <span className="text-xs font-mono text-text-secondary">{title}</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-text-secondary font-mono">{language}</span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-text-secondary hover:text-text-primary bg-white/5 hover:bg-white/10 rounded-md transition-colors"
          >
            {copied ? (
              <>
                <svg className="w-3.5 h-3.5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code */}
      <div className="overflow-x-auto">
        <pre className="p-4 text-sm font-mono leading-relaxed">
          {tokenizedLines.map((lineTokens, lineIdx) => (
            <div key={lineIdx} className="flex gap-4 hover:bg-white/2 rounded px-1">
              {showLineNumbers && (
                <span className="select-none text-text-secondary/40 w-6 text-right flex-shrink-0 text-xs mt-0.5">
                  {lineIdx + 1}
                </span>
              )}
              <span>
                {lineTokens.map((token, tokIdx) => (
                  <span
                    key={tokIdx}
                    style={{
                      color: tokenColors[token.type],
                      fontStyle: token.type === 'comment' ? 'italic' : 'normal',
                    }}
                  >
                    {token.content}
                  </span>
                ))}
              </span>
            </div>
          ))}
        </pre>
      </div>
    </div>
  )
}
