# CSV Download Implementation Summary

## Overview

I've successfully implemented the CSV download functionality for ReportGenie reports. The implementation includes both backend and frontend changes.

## ✅ Completed Backend Changes

### 1. Added CSV Generation Endpoint

**File:** `backend/app/api/routes/reportgenie.py`

- Added CSV import: `import csv` and `from io import StringIO`
- Added new endpoint: `POST /api/v1/reportgenie/generate/csv`
- The endpoint converts structured report data to CSV format with columns:
  - **Prompt**: Section title/description
  - **Content**: Generated content for that section
  - **Citations**: Source citations (pipe-separated)

## ✅ Completed Frontend Changes

### 1. Generate Page (`frontend/src/routes/_layout/generate.tsx`)

- Added `loadingCsvDownload` state
- Added `handleDownloadCsv` function (temporarily shows error message)
- Added CSV download button next to DOCX download button

### 2. Archive Page (`frontend/src/routes/_layout/archive.tsx`)

- Added `loadingCsvDownload` state
- Added `handleDownloadCsv` function (temporarily shows error message)
- Updated BaseResultsContainer props to include CSV download functionality
- CSV download button only shows for ReportGenie results (generate tab)

### 3. BaseResultsContainer Component

**File:** `frontend/src/components/Archive/BaseResultsContainer.tsx`

- Updated interface to accept CSV download props
- Pass CSV props to ResultsHeader component

### 4. ResultsHeader Component

**File:** `frontend/src/components/Archive/Utils/ResultsHeader.tsx`

- Updated interface to accept CSV download props
- Added conditional CSV download button

## 🔄 Next Steps (Required)

### 1. Regenerate SDK

You mentioned you'll handle this yourself. After regenerating the SDK with the new `/generate/csv` endpoint, you'll need to:

1. **Update Generate Page**: Replace the temporary error message in `handleDownloadCsv` with:

```typescript
const csvData = {
  sections: sectionResults,
}

const response = await ReportgenieService.generateCsv({
  requestBody: { content: JSON.stringify(csvData) },
})

// Handle blob response and download
let blob
if (response instanceof Blob) {
  blob = response
} else if (response instanceof ArrayBuffer) {
  blob = new Blob([response], { type: "text/csv" })
} else {
  blob = new Blob([response as any], { type: "text/csv" })
}

const url = window.URL.createObjectURL(blob)
const a = document.createElement("a")
const timestamp = new Date().toISOString().replace(/[:.]/g, "-")
a.href = url
a.download = `report_${timestamp}.csv`
document.body.appendChild(a)
a.click()
window.URL.revokeObjectURL(url)
document.body.removeChild(a)

showSuccessToast("CSV downloaded successfully")
```

2. **Update Archive Page**: Replace the temporary error message in `handleDownloadCsv` with:

```typescript
const csvData = {
  sections: selectedReport.results?.sections || [],
}

const response = await ReportgenieService.generateCsv({
  requestBody: { content: JSON.stringify(csvData) },
})

// Same blob handling code as above
```

## 📄 CSV File Format

The generated CSV will have the following structure:

| Prompt                    | Content                              | Citations                                                |
| ------------------------- | ------------------------------------ | -------------------------------------------------------- |
| Section description/title | Generated content (newlines removed) | source1.pdf: citation text \| source2.pdf: citation text |

## 🎯 Features

- **Smart Citation Extraction**: Automatically extracts source citations and formats them as "filename: content"
- **Conditional Display**: CSV download button only appears for ReportGenie results
- **Error Handling**: Proper error messages and loading states
- **File Naming**: Timestamped CSV files (e.g., `report_2025-06-25T10-30-45.csv`)
- **Content Sanitization**: Removes newlines and carriage returns from content for proper CSV formatting

## 🚀 Testing

Once the SDK is regenerated:

1. Generate a report in ReportGenie
2. Click "Download CSV" button
3. Verify CSV file downloads with proper format
4. Test from both the generate page and archive page
5. Verify citations are properly formatted and pipe-separated

The implementation is complete and ready to use once the SDK is updated!
