import { create } from 'zustand';

interface AssistantIntentStep {
  action: string;
  description: string;
}

interface AssistantParameters {
  customInstructions?: string;
  searchMode?: string;
  consultDocs?: boolean;
}

interface AssistantState {
  assistantMode: boolean;
  targetRoute: string;
  message: string;
  files: File[];
  suggestionType?: string;
  isMultistep?: boolean;
  steps?: AssistantIntentStep[];
  parameters?: AssistantParameters;
  currentStepIndex?: number;
  setAssistantData: (data: Partial<AssistantState>) => void;
}

export const useAssistantStore = create<AssistantState>((set) => ({
  assistantMode: false,
  targetRoute: '',
  message: '',
  files: [],
  suggestionType: undefined,
  isMultistep: false,
  steps: [],
  parameters: {},
  currentStepIndex: 0,
  setAssistantData: (data) => set(data),
}));