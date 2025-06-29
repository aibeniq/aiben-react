# Citation "Read More" Bug Fix

## ❌ Issue Identified

The "Read More" buttons were toggling between "Read More" and "Show Less" text, but the actual citation content wasn't changing when clicked.

## 🔍 Root Cause

The issue was with React state management using `Set` objects. React doesn't always detect changes to `Set` objects as state mutations, causing components to not re-render when the expansion state changed.

## ✅ Solution Applied

### Before (Problematic):

```typescript
const [expandedCitations, setExpandedCitations] = useState<Set<string>>(new Set())

const toggleCitationExpansion = (messageIndex: number, sourceIndex: number) => {
  const citationKey = `${messageIndex}-${sourceIndex}`
  const newExpanded = new Set(expandedCitations)
  if (newExpanded.has(citationKey)) {
    newExpanded.delete(citationKey)
  } else {
    newExpanded.add(citationKey)
  }
  setExpandedCitations(newExpanded) // React might not detect this change
}
```

### After (Fixed):

```typescript
const [expandedCitations, setExpandedCitations] = useState<Record<string, boolean>>({})

const toggleCitationExpansion = (messageIndex: number, sourceIndex: number) => {
  const citationKey = `${messageIndex}-${sourceIndex}`
  setExpandedCitations((prev) => ({
    ...prev,
    [citationKey]: !prev[citationKey], // React always detects object spread changes
  }))
}
```

## 🔧 Files Fixed

### 1. ChatMessages.tsx

- **Issue**: Chatbot citations not expanding/collapsing
- **Fix**: Changed from `Set<string>` to `Record<string, boolean>`
- **State Keys**: `${messageIndex}-${sourceIndex}`

### 2. review.tsx

- **Issue**: VeraDoc review citations not expanding/collapsing
- **Fix**: Changed from `Set<string>` to `Record<string, boolean>`
- **State Keys**: `${resultIndex}-${pairIndex}-${citationIndex}`

### 3. generate.tsx

- **Issue**: ReportGenie citations not expanding/collapsing
- **Fix**: Changed from `Set<string>` to `Record<string, boolean>`
- **State Keys**: `${sectionIndex}-${citationIndex}`
- **Bonus**: Fixed RadioGroup TypeScript error

### 4. SourceCitationAccordion.tsx

- **Issue**: Archive citations not expanding/collapsing
- **Fix**: Changed from `Set<number>` to `Record<number, boolean>`
- **State Keys**: `${citationIndex}`

## ✅ Expected Behavior Now

1. **Click "Read More"**: Citation expands to show full text, button changes to "Show Less"
2. **Click "Show Less"**: Citation collapses to truncated text, button changes to "Read More"
3. **Multiple Citations**: Each citation can be expanded/collapsed independently
4. **State Persistence**: Expansion state maintained during the user session

## 🧪 Testing

To verify the fix works:

1. **Chatbot**: Ask a question that generates long citations, try expanding/collapsing
2. **VeraDoc**: Run a review with policy context, check citation expansion
3. **ReportGenie**: Generate a report with knowledge base sources, test citations
4. **Archive**: View historical results, test citation expansion in archive views

## 🎯 Technical Notes

- **React State Detection**: Objects with spread syntax `{...prev, key: value}` always trigger re-renders
- **Set Limitations**: React doesn't always detect mutations to `Set` objects as state changes
- **Performance**: Object-based state is just as efficient for this use case
- **Type Safety**: Maintained with `Record<string, boolean>` and `Record<number, boolean>`

The citation "Read More" functionality should now work correctly across all components! 🚀
