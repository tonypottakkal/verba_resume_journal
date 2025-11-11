"use client";

import React, { useState, useEffect } from "react";
import { Credentials, ResumeConfig } from "@/app/types";
import VerbaButton from "@/app/components/Navigation/VerbaButton";
import { FaCheckCircle } from "react-icons/fa";
import { MdCancel } from "react-icons/md";
import {
  loadResumeConfig,
  saveResumeConfig as saveConfigUtil,
  resetResumeConfig,
  validateProficiencyWeights,
  getAvailableModels,
  getAvailableSections,
} from "@/app/utils/resumeConfig";
import {
  saveResumeConfigToBackend,
  loadResumeConfigFromBackend,
} from "@/app/api";

interface ResumeConfigComponentProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const ResumeConfigComponent: React.FC<ResumeConfigComponentProps> = ({
  credentials,
  addStatusMessage,
}) => {
  const [config, setConfig] = useState<ResumeConfig>(loadResumeConfig());
  const [loading, setLoading] = useState(false);

  // Load configuration from backend on mount if credentials are available
  useEffect(() => {
    const loadFromBackend = async () => {
      if (credentials && credentials.url && credentials.key) {
        try {
          const backendConfig = await loadResumeConfigFromBackend(credentials);
          if (backendConfig) {
            setConfig(backendConfig);
            // Also save to localStorage for offline access
            saveConfigUtil(backendConfig);
          }
        } catch (error) {
          console.error("Failed to load config from backend:", error);
          // Continue with local config
        }
      }
    };

    loadFromBackend();
  }, [credentials]);

  const saveConfig = async () => {
    // Validate weights before saving
    if (!validateProficiencyWeights(config)) {
      addStatusMessage(
        "Proficiency weights must sum to 1.0",
        "WARNING"
      );
      return;
    }

    setLoading(true);
    try {
      // Save to localStorage first
      saveConfigUtil(config);
      
      // Try to save to backend if credentials are available
      if (credentials && credentials.url && credentials.key) {
        const backendSuccess = await saveResumeConfigToBackend(config, credentials);
        if (backendSuccess) {
          addStatusMessage("Resume configuration saved to server", "SUCCESS");
        } else {
          addStatusMessage(
            "Configuration saved locally (server unavailable)",
            "WARNING"
          );
        }
      } else {
        addStatusMessage("Resume configuration saved locally", "SUCCESS");
      }
    } catch (error) {
      console.error("Failed to save config:", error);
      addStatusMessage("Failed to save configuration", "ERROR");
    } finally {
      setLoading(false);
    }
  };

  const handleResetConfig = () => {
    resetResumeConfig();
    setConfig(loadResumeConfig());
    addStatusMessage("Configuration reset to defaults", "SUCCESS");
  };

  const updateSkillExtraction = (field: string, value: any) => {
    setConfig((prev) => ({
      ...prev,
      skillExtraction: {
        ...prev.skillExtraction,
        [field]: value,
      },
    }));
  };

  const updateResumeGeneration = (field: string, value: any) => {
    setConfig((prev) => ({
      ...prev,
      resumeGeneration: {
        ...prev.resumeGeneration,
        [field]: value,
      },
    }));
  };

  const updateProficiencyCalculation = (field: string, value: any) => {
    setConfig((prev) => ({
      ...prev,
      proficiencyCalculation: {
        ...prev.proficiencyCalculation,
        [field]: value,
      },
    }));
  };

  const toggleSection = (section: string) => {
    const sections = config.resumeGeneration.defaultSections;
    if (sections.includes(section)) {
      updateResumeGeneration(
        "defaultSections",
        sections.filter((s) => s !== section)
      );
    } else {
      updateResumeGeneration("defaultSections", [...sections, section]);
    }
  };

  return (
    <div className="flex flex-col w-full h-full p-4">
      <div className="flex justify-between items-center mb-4">
        <p className="text-2xl font-bold">Resume Configuration</p>
      </div>

      <div className="flex-grow overflow-y-auto">
        <div className="gap-6 flex flex-col p-4">
          {/* Skill Extraction Settings */}
          <div className="flex flex-col gap-3">
            <p className="font-bold text-lg">Skill Extraction</p>
            
            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Enable Skill Extraction</p>
              <input
                type="checkbox"
                className="toggle toggle-primary"
                checked={config.skillExtraction.enabled}
                onChange={(e) =>
                  updateSkillExtraction("enabled", e.target.checked)
                }
              />
            </div>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Extraction Model</p>
              <select
                value={config.skillExtraction.model}
                onChange={(e) =>
                  updateSkillExtraction("model", e.target.value)
                }
                className="select bg-bg-verba"
                disabled={!config.skillExtraction.enabled}
              >
                {getAvailableModels().map((model) => (
                  <option key={model} value={model}>
                    {model.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Resume Generation Settings */}
          <div className="flex flex-col gap-3">
            <p className="font-bold text-lg">Resume Generation</p>
            
            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Generation Model</p>
              <select
                value={config.resumeGeneration.model}
                onChange={(e) =>
                  updateResumeGeneration("model", e.target.value)
                }
                className="select bg-bg-verba"
              >
                {getAvailableModels().map((model) => (
                  <option key={model} value={model}>
                    {model.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Default Format</p>
              <select
                value={config.resumeGeneration.defaultFormat}
                onChange={(e) =>
                  updateResumeGeneration(
                    "defaultFormat",
                    e.target.value as "markdown" | "pdf" | "docx"
                  )
                }
                className="select bg-bg-verba"
              >
                <option value="markdown">Markdown</option>
                <option value="pdf">PDF</option>
                <option value="docx">DOCX</option>
              </select>
            </div>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Max Length (words)</p>
              <input
                type="number"
                className="input bg-bg-verba w-32"
                value={config.resumeGeneration.maxLength}
                onChange={(e) =>
                  updateResumeGeneration("maxLength", parseInt(e.target.value))
                }
                min={500}
                max={5000}
                step={100}
              />
            </div>

            <div className="flex flex-col gap-2">
              <p className="flex min-w-[12vw]">Default Sections</p>
              <div className="flex flex-wrap gap-2">
                {getAvailableSections().map((section) => (
                  <label
                    key={section}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      className="checkbox checkbox-sm checkbox-primary"
                      checked={config.resumeGeneration.defaultSections.includes(
                        section
                      )}
                      onChange={() => toggleSection(section)}
                    />
                    <span className="capitalize">{section}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {/* Proficiency Calculation Settings */}
          <div className="flex flex-col gap-3">
            <p className="font-bold text-lg">Proficiency Calculation</p>
            <p className="text-sm text-text-alt-verba">
              Adjust weights for skill proficiency scoring (must sum to 1.0)
            </p>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Frequency Weight</p>
              <input
                type="number"
                className="input bg-bg-verba w-32"
                value={config.proficiencyCalculation.frequencyWeight}
                onChange={(e) =>
                  updateProficiencyCalculation(
                    "frequencyWeight",
                    parseFloat(e.target.value)
                  )
                }
                min={0}
                max={1}
                step={0.1}
              />
            </div>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Context Weight</p>
              <input
                type="number"
                className="input bg-bg-verba w-32"
                value={config.proficiencyCalculation.contextWeight}
                onChange={(e) =>
                  updateProficiencyCalculation(
                    "contextWeight",
                    parseFloat(e.target.value)
                  )
                }
                min={0}
                max={1}
                step={0.1}
              />
            </div>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Recency Weight</p>
              <input
                type="number"
                className="input bg-bg-verba w-32"
                value={config.proficiencyCalculation.recencyWeight}
                onChange={(e) =>
                  updateProficiencyCalculation(
                    "recencyWeight",
                    parseFloat(e.target.value)
                  )
                }
                min={0}
                max={1}
                step={0.1}
              />
            </div>

            <div className="flex gap-3 justify-between items-center text-text-verba">
              <p className="flex min-w-[12vw]">Min Occurrences</p>
              <input
                type="number"
                className="input bg-bg-verba w-32"
                value={config.proficiencyCalculation.minOccurrences}
                onChange={(e) =>
                  updateProficiencyCalculation(
                    "minOccurrences",
                    parseInt(e.target.value)
                  )
                }
                min={1}
                max={10}
              />
            </div>

            {/* Weight validation warning */}
            {Math.abs(
              config.proficiencyCalculation.frequencyWeight +
                config.proficiencyCalculation.contextWeight +
                config.proficiencyCalculation.recencyWeight -
                1.0
            ) > 0.01 && (
              <div className="alert alert-warning">
                <span className="text-sm">
                  Warning: Weights should sum to 1.0 (currently:{" "}
                  {(
                    config.proficiencyCalculation.frequencyWeight +
                    config.proficiencyCalculation.contextWeight +
                    config.proficiencyCalculation.recencyWeight
                  ).toFixed(2)}
                  )
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-2 mt-3">
        <VerbaButton
          title="Save"
          onClick={saveConfig}
          className="max-w-min"
          Icon={FaCheckCircle}
          disabled={loading}
        />
        <VerbaButton
          title="Reset"
          onClick={handleResetConfig}
          className="max-w-min"
          Icon={MdCancel}
          disabled={loading}
        />
      </div>
    </div>
  );
};

export default ResumeConfigComponent;
