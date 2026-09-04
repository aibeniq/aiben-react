# Citation "Read More" Functionality Implementation

## Overview

Added expandable "Read More" functionality to all citation displays throughout the chatbot application. Citations longer than 300 characters are now truncated with a "Read More" button that allows users to expand and view the full citation content.

## ✅ Files Modified

### 1. ChatMessages.tsx

**File**: `frontend/src/components/Chatbot/ChatMessages.tsx`

- **Primary chatbot citations display**
- Added state management for citation expansion
- Implemented truncation at 300 characters
- Added "Read More" / "Show Less" toggle buttons

### 2. review.tsx (VeraDoc Results)

**File**: `frontend/src/routes/_layout/review.tsx`

- **VeraDoc review results citations**
- Added citation expansion state and functions
- Updated citation display to include truncation logic
- Unique citation keys based on result, pair, and citation indices

### 3. generate.tsx (ReportGenie Results)

**File**: `frontend/src/routes/_layout/generate.tsx`

- **ReportGenie generation results citations**
- Added citation expansion state and functions
- Updated section citation displays
- Unique citation keys based on section and citation indices

### 4. SourceCitationAccordion.tsx (Archive Results)

**File**: `frontend/src/components/Archive/Utils/SourceCitationAccordion.tsx`

- **Reusable citation component for archive views**
- Added state management within the component
- Applied to VeraDoc archive, ReportGenie archive, and other archive views

## ✅ Implementation Details

### Truncation Logic

```typescript
const shouldTruncate = citationText.length > 300
const displayText =
  shouldTruncate && !isExpanded ? citationText.substring(0, 300) + "..." : citationText
```

### State Management

```typescript
// Track expanded citations using unique keys
const [expandedCitations, setExpandedCitations] = useState<Set<string>>(new Set())

// Toggle function with unique citation identifiers
const toggleCitationExpansion = (/* unique params */) => {
  const citationKey = `${param1}-${param2}-${param3}`
  const newExpanded = new Set(expandedCitations)
  if (newExpanded.has(citationKey)) {
    newExpanded.delete(citationKey)
  } else {
    newExpanded.add(citationKey)
  }
  setExpandedCitations(newExpanded)
}
```

### UI Components

```tsx
{
  shouldTruncate && (
    <Button
      size="xs"
      variant="ghost"
      mt={1}
      onClick={() => toggleCitationExpansion(/* params */)}
      colorPalette="blue"
    >
      {isExpanded ? "Show Less" : "Read More"}
    </Button>
  )
}
```

## ✅ Features

### 1. **Smart Truncation**

- Only shows "Read More" for citations longer than 300 characters
- Preserves short citations without unnecessary buttons
- Clear "..." indicator for truncated content

### 2. **Individual Control**

- Each citation can be expanded/collapsed independently
- State maintained separately for each citation
- No interference between multiple citations in the same view

### 3. **Consistent Styling**

- Small, ghost-style buttons that don't overwhelm the UI
- Blue color palette matching the overall design
- Consistent spacing and positioning across all components

### 4. **Unique Identification**

- Different citation key patterns for different contexts:
  - ChatMessages: `${messageIndex}-${sourceIndex}`
  - Review: `${resultIndex}-${pairIndex}-${citationIndex}`
  - Generate: `${sectionIndex}-${citationIndex}`
  - Archive: `${citationIndex}` (component-level state)

## ✅ User Experience Benefits

### 1. **Improved Readability**

- Long citations no longer overwhelm the interface
- Users can focus on the relevant information first
- Clean, organized presentation of citation data

### 2. **On-Demand Detail**

- Users can expand only the citations they're interested in
- Quick scanning of multiple citations without scrolling
- Full content available when needed

### 3. **Preserved Context**

- Expansion state maintained during the user session
- Multiple citations can be expanded simultaneously
- No unexpected collapses or state resets

## ✅ Coverage

The "Read More" functionality is now implemented across:

- ✅ **Main Chatbot** (ChatMessages component)
- ✅ **VeraDoc Review Results** (review.tsx)
- ✅ **ReportGenie Generation Results** (generate.tsx)
- ✅ **Archive Views** (SourceCitationAccordion component)
- ✅ **All Citation Displays** (comprehensive coverage)

## ✅ Testing

To test the functionality:

1. **Chatbot**: Ask questions that generate citations > 300 characters
2. **VeraDoc**: Run document reviews and check citation displays
3. **ReportGenie**: Generate reports with knowledge base citations
4. **Archive**: View historical results with citations

Each location should show truncated citations with "Read More" buttons for long content.

## ✅ Ready for Production

The implementation is complete and provides a consistent, user-friendly way to handle long citations across the entire application. Users can now easily manage citation visibility without being overwhelmed by lengthy source text.

**All citation displays now have expandable "Read More" functionality! 🎉**
