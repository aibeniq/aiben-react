# Frontend Integration Guide - ReportGenie Progress Bars

## Quick Start

All ReportGenie endpoints now support real-time progress tracking, just like Knowledge Base creation!

## API Endpoints

### 1. Report Generation (Review)

#### Create Task (Optional but Recommended)
```javascript
POST /api/reportgenie/generate/task
Response: { "task_id": "uuid-string" }
```

#### Generate Report
```javascript
POST /api/reportgenie/generate
Form Data:
  - task_id (optional): uuid from task creation
  - knowledge_base_id: string
  - sections: JSON string
  - outline_id: string
  - search_mode: "vector" | "full_text"
  - custom_instructions: string (optional)
  
Response: { results: { ..., task_id: "uuid-string" } }
```

**Progress Stages:**
- `setup` (10%) - "Initializing report generation..."
- `generating` (80%) - "Processing section 3/10: Executive Summary..."
- `finalizing` (10%) - "Compiling final report..."

---

### 2. Outline Generation (Generate)

#### Create Task
```javascript
POST /api/reportgenie/generate-outline/task
Response: { "task_id": "uuid-string" }
```

#### Generate Outline
```javascript
POST /api/reportgenie/generate-outline
Form Data:
  - task_id (optional): uuid from task creation
  - description: string
  - report_type: string
  - num_sections: number (optional)
  - files: File[] (optional example documents)
  
Response: { sections: [...], description_analysis: "...", task_id: "uuid" }
```

**Progress Stages:**
- `processing_files` (20%) - "Processing file 1/3: example.pdf..."
- `generating` (70%) - "Generating outline sections with LLM..." or "Analyzing chunk 2/5..."
- `finalizing` (10%) - "Parsing and finalizing sections..."

---

### 3. Outline Optimization (Match/Compare)

#### Create Task
```javascript
POST /api/reportgenie/optimize-outline/task
Response: { "task_id": "uuid-string" }
```

#### Optimize Outline
```javascript
POST /api/reportgenie/optimize-outline
Form Data:
  - task_id (optional): uuid from task creation
  - knowledge_base_id: string
  - outline_id: string
  - sections: JSON string
  - custom_instructions: string (optional)
  - search_mode: "vector" | "full_text"
  - files: File[] (ground truth document)
  
Response: { ..., task_id: "uuid" }
```

**Progress Stages:**
- `setup` (10%) - "Initializing outline optimization..."
- `processing_document` (10%) - "Processing ground-truth document..."
- `generating` (40%) - "Generating section 2/8: Introduction..."
- `matching` (20%) - "Matching chunk 15/42..."
- `comparing` (15%) - "Comparing section 5/8..."
- `finalizing` (5%) - "Finalizing optimization results..."

---

### 4. Progress Polling

```javascript
GET /api/reportgenie/progress/{task_id}
Response: {
  "task_id": "uuid",
  "operation": "Generating report",
  "percentage": 45.5,
  "status": "in_progress" | "completed" | "failed" | "started",
  "message": "Processing section 5/10: Market Analysis...",
  "current_stage": "generating",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime",
  "error_message": "..." (only if status === "failed"),
  "stages": {
    "setup": {
      "name": "setup",
      "weight": 0.1,
      "current": 1,
      "total": 1,
      "message": "Setup complete",
      "completed": true,
      "percentage": 100
    },
    "generating": {
      "name": "generating", 
      "weight": 0.8,
      "current": 5,
      "total": 10,
      "message": "Processing section 5/10...",
      "completed": false,
      "percentage": 50
    },
    ...
  }
}
```

---

## React Implementation Example

```typescript
import { useState, useEffect, useCallback } from 'react';

interface ProgressData {
  task_id: string;
  operation: string;
  percentage: number;
  status: 'started' | 'in_progress' | 'completed' | 'failed';
  message: string;
  current_stage: string;
  stages: Record<string, any>;
  error_message?: string;
}

export function useReportGenieProgress() {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  // Create a progress task
  const createTask = useCallback(async (type: 'generate' | 'generate-outline' | 'optimize-outline') => {
    const response = await fetch(`/api/reportgenie/${type}/task`, {
      method: 'POST',
    });
    const { task_id } = await response.json();
    setTaskId(task_id);
    return task_id;
  }, []);

  // Poll for progress
  useEffect(() => {
    if (!taskId) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/reportgenie/progress/${taskId}`);
        if (response.ok) {
          const data = await response.json();
          setProgress(data);

          // Stop polling when complete or failed
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error('Error fetching progress:', error);
      }
    }, 1000); // Poll every second

    return () => clearInterval(interval);
  }, [taskId]);

  return { progress, createTask, setTaskId };
}

// Usage in a component
export function ReportGenerationPage() {
  const { progress, createTask, setTaskId } = useReportGenieProgress();
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);

    // Option 1: Pre-create task
    const taskId = await createTask('generate');

    // Option 2: Or submit without task_id and extract it from response
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('knowledge_base_id', kbId);
    formData.append('sections', JSON.stringify(sections));
    formData.append('outline_id', outlineId);
    formData.append('search_mode', 'vector');

    try {
      const response = await fetch('/api/reportgenie/generate', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      // Handle success
    } catch (error) {
      // Handle error
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div>
      {isGenerating && progress && (
        <ProgressBar
          percentage={progress.percentage}
          message={progress.message}
          currentStage={progress.current_stage}
          stages={progress.stages}
        />
      )}
      <button onClick={handleGenerate}>Generate Report</button>
    </div>
  );
}
```

---

## Progress Bar Component Example

```typescript
interface Stage {
  name: string;
  weight: number;
  current: number;
  total: number;
  message: string;
  completed: boolean;
  percentage: number;
}

interface ProgressBarProps {
  percentage: number;
  message: string;
  currentStage: string;
  stages: Record<string, Stage>;
}

export function ProgressBar({ percentage, message, currentStage, stages }: ProgressBarProps) {
  return (
    <div className="progress-container">
      {/* Main progress bar */}
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      {/* Percentage and message */}
      <div className="progress-info">
        <span className="percentage">{percentage.toFixed(1)}%</span>
        <span className="message">{message}</span>
      </div>

      {/* Stage indicators */}
      <div className="stage-indicators">
        {Object.entries(stages).map(([key, stage]) => (
          <div 
            key={key}
            className={`stage ${stage.completed ? 'completed' : ''} ${key === currentStage ? 'active' : ''}`}
          >
            <div className="stage-name">{stage.name}</div>
            <div className="stage-progress">
              {stage.completed ? '✓' : `${stage.current}/${stage.total}`}
            </div>
          </div>
        ))}
      </div>

      {/* Detailed current stage progress */}
      {stages[currentStage] && (
        <div className="stage-detail">
          <div className="stage-detail-name">
            {stages[currentStage].name}
          </div>
          <div className="stage-detail-bar">
            <div 
              className="stage-detail-fill"
              style={{ width: `${stages[currentStage].percentage}%` }}
            />
          </div>
          <div className="stage-detail-message">
            {stages[currentStage].message}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Error Handling

```typescript
const handleGenerate = async () => {
  const taskId = await createTask('generate');
  
  try {
    const response = await fetch('/api/reportgenie/generate', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Generation failed');
    }

    const data = await response.json();
    
    // Wait for completion via progress polling
    // The useEffect hook will update progress state
    
  } catch (error) {
    // Check if progress has error information
    if (progress?.status === 'failed') {
      console.error('Task failed:', progress.error_message);
      // Show error to user
    } else {
      console.error('Request failed:', error);
    }
  }
};
```

---

## Best Practices

1. **Pre-create tasks** for better UX - users see "Waiting to start..." immediately
2. **Poll at 1-second intervals** - balances responsiveness and server load
3. **Stop polling** when status is 'completed' or 'failed'
4. **Show stage-by-stage progress** for transparency
5. **Handle errors gracefully** - check `error_message` field
6. **Clean up intervals** in useEffect cleanup function
7. **Show estimated time** based on progress percentage (optional enhancement)
8. **Allow cancellation** (future feature - foundation is in place)

---

## Testing

```typescript
// Mock progress responses for testing
const mockProgress = {
  task_id: "test-123",
  operation: "Generating report",
  percentage: 50,
  status: "in_progress",
  message: "Processing section 5/10: Executive Summary...",
  current_stage: "generating",
  stages: {
    setup: {
      name: "setup",
      weight: 0.1,
      current: 1,
      total: 1,
      message: "Setup complete",
      completed: true,
      percentage: 100
    },
    generating: {
      name: "generating",
      weight: 0.8,
      current: 5,
      total: 10,
      message: "Processing section 5/10: Executive Summary...",
      completed: false,
      percentage: 50
    },
    finalizing: {
      name: "finalizing",
      weight: 0.1,
      current: 0,
      total: 1,
      message: "",
      completed: false,
      percentage: 0
    }
  }
};
```

---

## Notes

- Progress is stored in Redis with 1-hour TTL
- Same pattern as Knowledge Base creation for consistency
- All operations support optional task_id parameter
- Frontend can pre-create tasks OR extract task_id from response
- Progress percentage is weighted by stage importance
- Detailed messages show exactly what's being processed

---

**For Questions:** Refer to backend implementation at `/backend/app/api/routes/reportgenie.py`
