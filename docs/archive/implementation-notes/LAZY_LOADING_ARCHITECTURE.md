# Lazy Loading Architecture Diagram

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Archive Tab                                              │ │
│  │                                                          │ │
│  │  [Select Report] → Click                                │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 1: LOAD SUMMARY                         │
│                                                                 │
│  Frontend: useToolArchive.loadVeradocReport()                  │
│  ↓                                                              │
│  API Call: GET /veradoc/history/{id}?include_qa_pairs=false    │
│  ↓                                                              │
│  Backend: get_veradoc_detail()                                 │
│  ├─ Fetch from database                                        │
│  ├─ Build response with qa_pairs_summary                       │
│  └─ Return ~2 KB                                               │
│  ↓                                                              │
│  Frontend: Display summary + question headers                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DISPLAY: QUESTION HEADERS                      │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Final Evaluation:                                      │   │
│  │ [Markdown content here...]                             │   │
│  │                                                        │   │
│  │ Questions & Answers (100):                             │   │
│  │                                                        │   │
│  │  ▶ Question 1: Does the policy comply with...          │   │
│  │  ▶ Question 2: What are the coverage limits for...     │   │
│  │  ▶ Question 3: Are there exclusions for...             │   │
│  │  ▶ Question 4: ...                                      │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                      USER CLICKS QUESTION 2
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           STAGE 2: LOAD INDIVIDUAL QA PAIR                      │
│                                                                 │
│  Component: LazyQAPairDisplay                                  │
│  ├─ Show spinner ⏳                                            │
│  ├─ API Call: GET /veradoc/history/{id}/qa-pair/1            │
│  └─ Backend: get_veradoc_qa_pair()                            │
│      ├─ Fetch qa_pairs[1] from database                       │
│      ├─ Return question, answer, context, citations           │
│      └─ Response: ~100 KB                                     │
│  ↓                                                              │
│  Component: Hide spinner, expand question                      │
│  ├─ Cache QA pair details                                      │
│  └─ Render: QAPairDisplay component                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DISPLAY: EXPANDED QUESTION                     │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ Final Evaluation: [...]                                │   │
│  │                                                        │   │
│  │ Questions & Answers (100):                             │   │
│  │                                                        │   │
│  │  ▶ Question 1: Does the policy comply with...          │   │
│  │                                                        │   │
│  │  ▼ Question 2: What are the coverage limits for...     │   │
│  │     ┌──────────────────────────────────────────┐       │   │
│  │     │ Answer: The coverage limits are...       │       │   │
│  │     │                                          │       │   │
│  │     │ Policy Context: [Relevant text...]      │       │   │
│  │     │                                          │       │   │
│  │     │ Citations:                               │       │   │
│  │     │ • policy.pdf (page 5)                    │       │   │
│  │     │ • schedule_a.pdf (page 12)               │       │   │
│  │     └──────────────────────────────────────────┘       │   │
│  │                                                        │   │
│  │  ▶ Question 3: Are there exclusions for...             │   │
│  │  ▶ Question 4: ...                                      │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
Archive Page (_layout/archive.tsx)
    ↓
useToolArchive Hook (hooks/useToolArchive.ts)
│   ├─ loadVeradocReport() → Loads summary + headers
│   └─ State: selectedVeradocReport
    ↓
VeradocResults Component (Archive/Results/VeradocResults.tsx)
│   ├─ Renders final_evaluation (Markdown)
│   ├─ Checks for qa_pairs_summary (new format)
│   └─ Maps qa_pairs_summary → LazyQAPairDisplay[]
    ↓
LazyQAPairDisplay Component (Archive/Results/LazyQAPairDisplay.tsx)
    ├─ State: isOpen, isLoading, qaPairDetail
    ├─ onClick: Load QA pair if not cached
    │   └─ VeradocService.getVeradocQaPair()
    └─ Render: QAPairDisplay (when loaded)
```

## Data Flow

### Initial Load (Summary)

```
┌────────────┐     includeQaPairs=false     ┌──────────┐
│  Frontend  │ ─────────────────────────────→│ Backend  │
└────────────┘                               └──────────┘
                                                   │
                                                   ↓
                                        ┌─────────────────────┐
                                        │ LlmInteraction DB   │
                                        │ extra_data.qa_pairs │
                                        └─────────────────────┘
                                                   │
                                                   ↓
                                        Build qa_pairs_summary:
                                        [
                                          { index: 0, question: "..." },
                                          { index: 1, question: "..." },
                                          ...
                                        ]
                                                   │
┌────────────┐     Response (~2 KB)           ┌──────────┐
│  Frontend  │ ←──────────────────────────────│ Backend  │
└────────────┘                                └──────────┘
     │
     ↓
Display: Summary + Question Headers
```

### On-Demand Load (Individual QA Pair)

```
User clicks Question 2
     │
     ↓
┌─────────────────────┐
│ LazyQAPairDisplay   │
│ - Show spinner      │
│ - Make API call     │
└─────────────────────┘
     │
     ↓
┌────────────┐  GET /qa-pair/1  ┌──────────┐
│  Frontend  │ ────────────────→│ Backend  │
└────────────┘                  └──────────┘
                                     │
                                     ↓
                          ┌─────────────────────┐
                          │ LlmInteraction DB   │
                          │ extra_data.qa_pairs │
                          └─────────────────────┘
                                     │
                                     ↓
                          Return qa_pairs[1]:
                          {
                            index: 1,
                            question: "...",
                            answer: "...",
                            context: "...",
                            source_citations: [...]
                          }
                                     │
┌────────────┐  Response (~100 KB)  ┌──────────┐
│  Frontend  │ ←────────────────────│ Backend  │
└────────────┘                      └──────────┘
     │
     ↓
┌─────────────────────┐
│ LazyQAPairDisplay   │
│ - Hide spinner      │
│ - Cache data        │
│ - Expand section    │
│ - Render QAPair     │
└─────────────────────┘
```

## State Management

### Frontend State (per QA Pair)

```typescript
interface QAPairState {
  isOpen: boolean        // Accordion expanded?
  isLoading: boolean     // Currently fetching?
  qaPairDetail: any      // Cached QA pair data
}

// States per question:
Question 1: { isOpen: false, isLoading: false, qaPairDetail: null }
Question 2: { isOpen: true,  isLoading: false, qaPairDetail: {...} }  ← Loaded & cached
Question 3: { isOpen: false, isLoading: false, qaPairDetail: null }
```

### Interaction Flow

```
[Collapsed] → Click → [Loading] → [Expanded (Cached)]
    ▶                    ⏳              ▼
    │                    │               │
    └────← Click ────────┴───← Click ────┘
         (no load)           (cached)
```

## API Endpoints

### 1. Summary Endpoint (Existing, Modified)

```
GET /api/v1/veradoc/history/{report_id}?include_qa_pairs=false

Response Structure:
{
  "id": "uuid",
  "date_created": "2025-10-06T...",
  "results": {
    "final_evaluation": "# Evaluation\n...",
    "interaction_id": "uuid",
    "qa_pairs_summary": [          ← NEW
      { "index": 0, "question": "..." },
      { "index": 1, "question": "..." }
    ],
    "qa_pairs_count": 100
  }
}

Size: ~2 KB
Load Time: ~0.1s
```

### 2. Individual QA Pair Endpoint (New)

```
GET /api/v1/veradoc/history/{report_id}/qa-pair/{qa_index}

Response Structure:
{
  "index": 1,
  "question": "What are the coverage limits?",
  "answer": "The coverage limits are...",
  "context": "Relevant policy text from document...",
  "source_citations": [
    {
      "source": "policy.pdf",
      "page": 5,
      "content": "excerpt..."
    }
  ]
}

Size: ~100 KB
Load Time: ~0.2s
```

### 3. Full Report Endpoint (Legacy)

```
GET /api/v1/veradoc/history/{report_id}?include_qa_pairs=true

Response Structure:
{
  "id": "uuid",
  "results": {
    "final_evaluation": "...",
    "qa_pairs": [                 ← OLD FORMAT
      {
        "question": "...",
        "answer": "...",
        "context": "...",
        "source_citations": [...]
      },
      // ... 99 more
    ]
  }
}

Size: ~60 MB
Load Time: ~5s
```

## Caching Strategy

```
Question Click #1:
  ├─ Check: qaPairDetail === null? YES
  ├─ Fetch from API
  ├─ Store in state: qaPairDetail = {...}
  └─ Expand

Question Click #2 (same question):
  ├─ Check: qaPairDetail === null? NO
  ├─ Skip API call (use cached data)
  └─ Expand instantly

Question Click on Different Question:
  ├─ Independent state
  ├─ Check its own cache
  └─ Load if needed
```

## Error Handling

```
API Call Fails
    ↓
Catch Error
    ↓
Show Toast: "Failed to load question details"
    ↓
Keep Question Collapsed
    ↓
User can retry by clicking again
```

## Performance Characteristics

### Initial Load
- **Network**: 2 KB download
- **Time**: ~100ms
- **Render**: Summary + 100 question headers

### Per-Question Load
- **Network**: 100 KB download (first time only)
- **Time**: ~200ms
- **Render**: Answer + Context + Citations

### Comparison

| User Action | Old Method | New Method |
|------------|-----------|-----------|
| Load report, view 0 questions | 60 MB | 2 KB |
| Load report, view 1 question | 60 MB | 102 KB |
| Load report, view 5 questions | 60 MB | 502 KB |
| Load report, view all 100 questions | 60 MB | ~10 MB |

**Typical savings: 99% bandwidth reduction**
