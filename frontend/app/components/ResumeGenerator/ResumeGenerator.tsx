"use client";

import React, { useState, useRef, useEffect } from "react";
import { MdFileDownload, MdRefresh, MdDescription } from "react-icons/md";
import { IoIosSend } from "react-icons/io";
import { FaFilePdf, FaFileWord, FaMarkdown } from "react-icons/fa";
import VerbaButton from "../Navigation/VerbaButton";
import { Credentials } from "@/app/types";
import { detectHost } from "@/app/api";

interface ResumeGeneratorProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

interface ResumeOptions {
  format: "pdf" | "docx" | "markdown";
  sections: string[];
  maxLength: number;
}

interface Resume {
  id: string;
  content: string;
  jobDescriptionId: string;
  generatedAt: string;
  targetRole: string;
  format: string;
}

const AVAILABLE_SECTIONS = [
  "summary",
  "experience",
  "skills",
  "education",
  "certifications",
  "projects",
];

const ResumeGenerator: React.FC<ResumeGeneratorProps> = ({
  credentials,
  addStatusMessage,
}) => {
  const [jobDescription, setJobDescription] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResume, setGeneratedResume] = useState<Resume | null>(null);
  const [resumeOptions, setResumeOptions] = useState<ResumeOptions>({
    format: "markdown",
    sections: ["summary", "experience", "skills", "education"],
    maxLength: 2000,
  });
  const [error, setError] = useState<string | null>(null);
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (previewRef.current && generatedResume) {
      previewRef.current.scrollTop = 0;
    }
  }, [generatedResume]);

  const handleSectionToggle = (section: string) => {
    setResumeOptions((prev) => ({
      ...prev,
      sections: prev.sections.includes(section)
        ? prev.sections.filter((s) => s !== section)
        : [...prev.sections, section],
    }));
  };

  const generateResume = async () => {
    if (!jobDescription.trim()) {
      addStatusMessage("Please enter a job description", "WARNING");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      addStatusMessage("Generating resume...", "INFO");
      const host = await detectHost();
      const response = await fetch(`${host}/api/resumes/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description: jobDescription,
          target_role: targetRole || "Target Position",
          options: resumeOptions,
          credentials: credentials,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedResume(data.resume);
        addStatusMessage("Resume generated successfully!", "SUCCESS");
      } else {
        const errorData = await response.json();
        const errorMessage = errorData.error || "Failed to generate resume";
        setError(errorMessage);
        addStatusMessage(errorMessage, "ERROR");
      }
    } catch (error) {
      console.error("Error generating resume:", error);
      const errorMessage = "Error generating resume. Please try again.";
      setError(errorMessage);
      addStatusMessage(errorMessage, "ERROR");
    } finally {
      setIsGenerating(false);
    }
  };

  const exportResume = async (format: "pdf" | "docx" | "markdown") => {
    if (!generatedResume) {
      addStatusMessage("No resume to export", "WARNING");
      return;
    }

    try {
      addStatusMessage(`Exporting resume as ${format.toUpperCase()}...`, "INFO");
      const host = await detectHost();
      const response = await fetch(
        `${host}/api/resumes/${generatedResume.id}/export`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            format: format,
            credentials: credentials,
          }),
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `resume_${generatedResume.targetRole.replace(/\s+/g, "_")}.${format === "docx" ? "docx" : format === "pdf" ? "pdf" : "md"}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        addStatusMessage(`Resume exported as ${format.toUpperCase()}`, "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || `Failed to export resume as ${format}`,
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error exporting resume:", error);
      addStatusMessage(`Error exporting resume as ${format}`, "ERROR");
    }
  };

  const regenerateResume = () => {
    if (generatedResume) {
      setGeneratedResume(null);
      generateResume();
    }
  };

  const resetForm = () => {
    setJobDescription("");
    setTargetRole("");
    setGeneratedResume(null);
    setError(null);
    setResumeOptions({
      format: "markdown",
      sections: ["summary", "experience", "skills", "education"],
      maxLength: 2000,
    });
  };

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-full">
      {/* Left Panel - Input and Options */}
      <div className="flex flex-col gap-4 lg:w-1/2 overflow-y-auto">
        {/* Job Description Input */}
        <div className="bg-bg-alt-verba rounded-2xl p-4 space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <MdDescription className="text-primary-verba" size={20} />
            <h3 className="text-lg font-semibold text-text-verba">
              Job Description
            </h3>
          </div>

          <input
            type="text"
            className="input input-bordered w-full bg-bg-verba text-text-verba placeholder-text-alt-verba"
            placeholder="Target Role (e.g., Senior Software Engineer)"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            disabled={isGenerating}
          />

          <textarea
            className="textarea textarea-bordered w-full bg-bg-verba text-text-verba placeholder-text-alt-verba min-h-[200px] resize-y"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            disabled={isGenerating}
          />

          <div className="flex gap-2">
            <VerbaButton
              type="button"
              Icon={IoIosSend}
              title="Generate Resume"
              onClick={generateResume}
              disabled={isGenerating || !jobDescription.trim()}
              selected={true}
              selected_color="bg-primary-verba"
              loading={isGenerating}
              className="flex-1"
            />
            {generatedResume && (
              <VerbaButton
                type="button"
                Icon={MdRefresh}
                title="Regenerate"
                onClick={regenerateResume}
                disabled={isGenerating}
                selected_color="bg-secondary-verba"
              />
            )}
          </div>
        </div>

        {/* Resume Options */}
        <div className="bg-bg-alt-verba rounded-2xl p-4 space-y-4">
          <h3 className="text-lg font-semibold text-text-verba">
            Resume Options
          </h3>

          {/* Format Selection */}
          <div className="space-y-2">
            <label className="text-sm text-text-alt-verba">Output Format</label>
            <div className="flex gap-2">
              <button
                className={`btn btn-sm flex-1 ${resumeOptions.format === "markdown" ? "bg-primary-verba text-text-verba" : "bg-button-verba text-text-alt-verba"}`}
                onClick={() =>
                  setResumeOptions((prev) => ({ ...prev, format: "markdown" }))
                }
                disabled={isGenerating}
              >
                <FaMarkdown size={16} />
                Markdown
              </button>
              <button
                className={`btn btn-sm flex-1 ${resumeOptions.format === "pdf" ? "bg-primary-verba text-text-verba" : "bg-button-verba text-text-alt-verba"}`}
                onClick={() =>
                  setResumeOptions((prev) => ({ ...prev, format: "pdf" }))
                }
                disabled={isGenerating}
              >
                <FaFilePdf size={16} />
                PDF
              </button>
              <button
                className={`btn btn-sm flex-1 ${resumeOptions.format === "docx" ? "bg-primary-verba text-text-verba" : "bg-button-verba text-text-alt-verba"}`}
                onClick={() =>
                  setResumeOptions((prev) => ({ ...prev, format: "docx" }))
                }
                disabled={isGenerating}
              >
                <FaFileWord size={16} />
                DOCX
              </button>
            </div>
          </div>

          {/* Sections Selection */}
          <div className="space-y-2">
            <label className="text-sm text-text-alt-verba">
              Include Sections
            </label>
            <div className="grid grid-cols-2 gap-2">
              {AVAILABLE_SECTIONS.map((section) => (
                <label
                  key={section}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    className="checkbox checkbox-sm checkbox-primary"
                    checked={resumeOptions.sections.includes(section)}
                    onChange={() => handleSectionToggle(section)}
                    disabled={isGenerating}
                  />
                  <span className="text-sm text-text-verba capitalize">
                    {section}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Max Length */}
          <div className="space-y-2">
            <label className="text-sm text-text-alt-verba">
              Max Length (words): {resumeOptions.maxLength}
            </label>
            <input
              type="range"
              min="500"
              max="3000"
              step="100"
              value={resumeOptions.maxLength}
              onChange={(e) =>
                setResumeOptions((prev) => ({
                  ...prev,
                  maxLength: parseInt(e.target.value),
                }))
              }
              className="range range-primary range-sm"
              disabled={isGenerating}
            />
            <div className="flex justify-between text-xs text-text-alt-verba">
              <span>500</span>
              <span>1750</span>
              <span>3000</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Preview */}
      <div className="flex flex-col gap-4 lg:w-1/2">
        <div className="bg-bg-alt-verba rounded-2xl p-4 flex-1 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-verba">
              Resume Preview
            </h3>
            {generatedResume && (
              <div className="flex gap-2">
                <VerbaButton
                  type="button"
                  Icon={FaMarkdown}
                  title="MD"
                  onClick={() => exportResume("markdown")}
                  disabled={isGenerating}
                  circle={true}
                />
                <VerbaButton
                  type="button"
                  Icon={FaFilePdf}
                  title="PDF"
                  onClick={() => exportResume("pdf")}
                  disabled={isGenerating}
                  circle={true}
                />
                <VerbaButton
                  type="button"
                  Icon={FaFileWord}
                  title="DOCX"
                  onClick={() => exportResume("docx")}
                  disabled={isGenerating}
                  circle={true}
                />
              </div>
            )}
          </div>

          <div
            ref={previewRef}
            className="flex-1 overflow-y-auto bg-bg-verba rounded-lg p-4"
          >
            {isGenerating && (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <span className="loading loading-spinner loading-lg text-primary-verba"></span>
                <p className="text-text-alt-verba">
                  Generating your tailored resume...
                </p>
              </div>
            )}

            {error && !isGenerating && (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <div className="alert alert-error bg-warning-verba/20 border-warning-verba">
                  <p className="text-text-verba">{error}</p>
                </div>
              </div>
            )}

            {!generatedResume && !isGenerating && !error && (
              <div className="flex flex-col items-center justify-center h-full text-text-alt-verba">
                <MdDescription size={64} className="mb-4 opacity-50" />
                <p className="text-lg">No resume generated yet</p>
                <p className="text-sm">
                  Enter a job description and click Generate Resume
                </p>
              </div>
            )}

            {generatedResume && !isGenerating && (
              <div className="prose prose-sm max-w-none text-text-verba">
                <div className="mb-4 pb-4 border-b border-button-verba">
                  <p className="text-xs text-text-alt-verba mb-1">
                    Generated on{" "}
                    {new Date(generatedResume.generatedAt).toLocaleString()}
                  </p>
                  <p className="text-xs text-text-alt-verba">
                    Target Role: {generatedResume.targetRole}
                  </p>
                </div>
                <div
                  className="whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{
                    __html: generatedResume.content
                      .replace(/\n/g, "<br/>")
                      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                      .replace(/\*(.*?)\*/g, "<em>$1</em>"),
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeGenerator;
