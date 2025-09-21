/**
 * Utility function to clean RTF formatting marks from text content.
 * This is based on the backend rtf_to_text function but adapted for frontend use.
 * 
 * Removes RTF control words, formatting codes, and other RTF-specific markup
 * to display clean, readable text in citations.
 */
export function cleanRTFFormatting(text: string): string {
  if (!text || typeof text !== 'string') {
    return text || ''
  }

  // If it doesn't look like RTF content, return as-is
  if (!text.includes('\\') && !text.includes('{') && !text.includes('}')) {
    return text
  }

  let cleanText = text

  // Remove RTF header info
  cleanText = cleanText.replace(/{\\rtf\d+[^}]*}/g, '')

  // Remove font table (comprehensive)
  cleanText = cleanText.replace(/{\\fonttbl[^{}]*(?:{[^{}]*}[^{}]*)*}/g, '')

  // Remove color table
  cleanText = cleanText.replace(/{\\colortbl[^}]*}/g, '')

  // Remove style definitions
  cleanText = cleanText.replace(/{\\stylesheet[^{}]*(?:{[^{}]*}[^{}]*)*}/g, '')

  // Remove info group
  cleanText = cleanText.replace(/{\\info[^{}]*(?:{[^{}]*}[^{}]*)*}/g, '')

  // Remove document formatting information
  cleanText = cleanText.replace(/\\viewkind\d+/g, '')
  cleanText = cleanText.replace(/\\uc\d+/g, '')
  cleanText = cleanText.replace(/\\deff\d+/g, '')
  cleanText = cleanText.replace(/\\deflang\d+/g, '')
  cleanText = cleanText.replace(/\\deflangfe\d+/g, '')
  cleanText = cleanText.replace(/\\ansi\b/g, '')
  cleanText = cleanText.replace(/\\pard\b/g, '')

  // Remove positioning and spacing controls
  cleanText = cleanText.replace(/\\tx\d+/g, '') // Tab positions
  cleanText = cleanText.replace(/\\li\d+/g, '') // Left indent
  cleanText = cleanText.replace(/\\ri\d+/g, '') // Right indent
  cleanText = cleanText.replace(/\\fi-?\d+/g, '') // First line indent (including negative)
  cleanText = cleanText.replace(/\\sb\d+/g, '') // Space before
  cleanText = cleanText.replace(/\\sa\d+/g, '') // Space after
  cleanText = cleanText.replace(/\\sl\d+/g, '') // Line spacing
  cleanText = cleanText.replace(/\\slmult\d+/g, '') // Line spacing multiple

  // Handle hexadecimal character codes (\'XX where XX is hex)
  cleanText = cleanText.replace(/\\'([0-9a-fA-F]{2})/g, (_, hex) => {
    const charCode = parseInt(hex, 16)
    // Convert common character codes to their actual characters
    switch (charCode) {
      case 0xe9: return 'é'  // é
      case 0xe0: return 'à'  // à
      case 0xe8: return 'è'  // è
      case 0xea: return 'ê'  // ê
      case 0xec: return 'ì'  // ì
      case 0xf2: return 'ò'  // ò
      case 0xf9: return 'ù'  // ù
      case 0xe1: return 'á'  // á
      case 0xed: return 'í'  // í
      case 0xf3: return 'ó'  // ó
      case 0xfa: return 'ú'  // ú
      case 0xfc: return 'ü'  // ü
      case 0xf1: return 'ñ'  // ñ
      case 0xe7: return 'ç'  // ç
      case 0xef: return 'ï'  // ï
      case 0x93: return '"'  // Smart quote left
      case 0x94: return '"'  // Smart quote right
      case 0x91: return "'"  // Smart apostrophe left
      case 0x92: return "'"  // Smart apostrophe right
      case 0x96: return '–'  // En dash
      case 0x97: return '—'  // Em dash
      case 0xa0: return ' '  // Non-breaking space
      default:
        // For other characters, try to convert them or return empty if unprintable
        if (charCode >= 32 && charCode <= 126) {
          return String.fromCharCode(charCode)
        }
        return '' // Remove unprintable characters
    }
  })

  // Handle paragraph and line control words
  cleanText = cleanText.replace(/\\par\b/g, '\n') // Paragraph breaks
  cleanText = cleanText.replace(/\\line\b/g, '\n') // Line breaks
  cleanText = cleanText.replace(/\\tab\b/g, '\t') // Tabs
  cleanText = cleanText.replace(/\\cell\b/g, '\t') // Table cells
  cleanText = cleanText.replace(/\\row\b/g, '\n') // Table rows

  // Handle special characters
  cleanText = cleanText.replace(/\\bullet\b/g, '•') // Bullet points
  cleanText = cleanText.replace(/\\endash\b/g, '–') // En dash
  cleanText = cleanText.replace(/\\emdash\b/g, '—') // Em dash
  cleanText = cleanText.replace(/\\ldblquote\b/g, '"') // Left double quote
  cleanText = cleanText.replace(/\\rdblquote\b/g, '"') // Right double quote
  cleanText = cleanText.replace(/\\lquote\b/g, "'") // Left single quote
  cleanText = cleanText.replace(/\\rquote\b/g, "'") // Right single quote

  // Handle tilde escapes and other special formatting
  cleanText = cleanText.replace(/\\~([^\\]*?)~/g, '$1') // Remove tilde escapes
  cleanText = cleanText.replace(/\\~/g, ' ') // Non-breaking space

  // Handle double backslashes and escaped backslashes
  cleanText = cleanText.replace(/\\\\/g, '') // Remove double backslashes entirely
  cleanText = cleanText.replace(/\\(?=[^a-zA-Z0-9])/g, '') // Remove backslashes before non-alphanumeric chars

  // Handle bullet points that appear as negative numbers
  cleanText = cleanText.replace(/-720\s*/g, '• ') // Common RTF bullet point indicator

  // Remove font formatting control words
  cleanText = cleanText.replace(/\\[bi]\d*\b/g, '') // Bold, italic
  cleanText = cleanText.replace(/\\ul\d*\b/g, '') // Underline
  cleanText = cleanText.replace(/\\strike\d*\b/g, '') // Strikethrough
  cleanText = cleanText.replace(/\\fs\d+\b/g, '') // Font size
  cleanText = cleanText.replace(/\\f\d+\b/g, '') // Font family
  cleanText = cleanText.replace(/\\cf\d+\b/g, '') // Color
  cleanText = cleanText.replace(/\\highlight\d+\b/g, '') // Highlight

  // Remove groups that we don't need (like {\*\generator...})
  cleanText = cleanText.replace(/{\\\*[^}]*}/g, '')

  // Remove any remaining control words (backslash followed by letters and optional number)
  cleanText = cleanText.replace(/\\[a-zA-Z]+\d*/g, '')

  // Remove any remaining single backslashes followed by non-word characters
  cleanText = cleanText.replace(/\\[^a-zA-Z0-9\s]/g, '')

  // Remove any remaining braces that aren't part of the text
  cleanText = cleanText.replace(/[{}]/g, '')

  // Clean up extra whitespace
  cleanText = cleanText.replace(/\s+/g, ' ') // Multiple spaces to single space
  cleanText = cleanText.replace(/ *\n */g, '\n') // Remove spaces around newlines
  cleanText = cleanText.replace(/^\s+/g, '') // Remove leading whitespace
  cleanText = cleanText.trim()

  return cleanText
}