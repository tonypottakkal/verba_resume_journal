import { ResumeConfig } from "@/app/types";

export const DEFAULT_RESUME_CONFIG: ResumeConfig = {
  skillExtraction: {
    enabled: true,
    model: "gpt-4",
    categories: [
      "Programming Languages",
      "Frameworks",
      "Tools",
      "Databases",
      "Cloud Platforms",
      "Soft Skills",
    ],
  },
  resumeGeneration: {
    model: "gpt-4",
    defaultFormat: "markdown",
    defaultSections: ["summary", "experience", "skills", "education"],
    maxLength: 2000,
  },
  proficiencyCalculation: {
    frequencyWeight: 0.4,
    contextWeight: 0.3,
    recencyWeight: 0.3,
    minOccurrences: 2,
  },
};

const STORAGE_KEY = "resumeConfig";

/**
 * Load resume configuration from localStorage
 */
export function loadResumeConfig(): ResumeConfig {
  if (typeof window === "undefined") {
    return DEFAULT_RESUME_CONFIG;
  }

  try {
    const savedConfig = localStorage.getItem(STORAGE_KEY);
    if (savedConfig) {
      return JSON.parse(savedConfig);
    }
  } catch (error) {
    console.error("Failed to load resume config:", error);
  }

  return DEFAULT_RESUME_CONFIG;
}

/**
 * Save resume configuration to localStorage
 */
export function saveResumeConfig(config: ResumeConfig): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  } catch (error) {
    console.error("Failed to save resume config:", error);
    throw error;
  }
}

/**
 * Reset resume configuration to defaults
 */
export function resetResumeConfig(): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error("Failed to reset resume config:", error);
    throw error;
  }
}

/**
 * Validate that proficiency calculation weights sum to 1.0
 */
export function validateProficiencyWeights(config: ResumeConfig): boolean {
  const sum =
    config.proficiencyCalculation.frequencyWeight +
    config.proficiencyCalculation.contextWeight +
    config.proficiencyCalculation.recencyWeight;

  return Math.abs(sum - 1.0) < 0.01;
}

/**
 * Get available LLM models for selection
 */
export function getAvailableModels(): string[] {
  return ["gpt-4", "gpt-3.5-turbo", "ollama", "cohere", "anthropic"];
}

/**
 * Get available resume formats
 */
export function getAvailableFormats(): Array<"markdown" | "pdf" | "docx"> {
  return ["markdown", "pdf", "docx"];
}

/**
 * Get available resume sections
 */
export function getAvailableSections(): string[] {
  return [
    "summary",
    "experience",
    "skills",
    "education",
    "projects",
    "certifications",
    "awards",
    "publications",
  ];
}
