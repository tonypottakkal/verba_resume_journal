"use client";

import React, { useState, useEffect } from "react";
import {
  MdDelete,
  MdRefresh,
  MdFileDownload,
  MdDescription,
  MdCalendarToday,
  MdWork,
  MdChevronRight,
  MdClose,
} from "react-icons/md";
import { FaFilePdf, FaFileWord, FaMarkdown } from "react-icons/fa";
import VerbaButton from "../Navigation/VerbaButton";
import { Credentials } from "@/app/types";
import { detectHost } from "@/app/api";

interface ResumeRecord {
  id: string;
  content: string;
  job_description: string;
  target_role: string;
  format: string;
  generated_at: string;
  source_log_ids: string[];
  metadata: Record<string, any>;
}

interface ResumeHistoryProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const ResumeHistory: React.FC<ResumeHistoryProps> = ({
  credentials,
  addStatusMessage,
}) => {
  const [resumes, setResumes] = useState<ResumeRecord[]>([]);
  const [selectedResume, setSelectedResume] = useState<ResumeRecord | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [filterRole, setFilterRole] = useState("");
  const [filterStartDate, setFilterStartDate] = useState("");
  const [filterEndDate, setFilterEndDate] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const ITEMS_PER_PAGE = 10;

  useEffect(() => {
    fetchResumes();
  }, [currentPage, filterRole, filterStartDate, filterEndDate]);

  const fetchResumes = async () => {
    setIsLoading(true);
    try {
      const host = await detectHost();
      const offset = (currentPage - 1) * ITEMS_PER_PAGE;

      const response = await fetch(`${host}/api/resumes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credentials: credentials,
          target_role: filterRole || null,
          start_date: filterStartDate || null,
          end_date: filterEndDate || null,
          limit: ITEMS_PER_PAGE,
          offset: offset,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResumes(data.resumes || []);
        setTotalCount(data.total_count || 0);
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to fetch resume history",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error fetching resumes:", error);
      addStatusMessage("Error fetching resume history", "ERROR");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectResume = async (resume: ResumeRecord) => {
    if (selectedResume?.id === resume.id) {
      setSelectedResume(null);
    } else {
      setSelectedResume(resume);
    }
  };

  const handleRegenerateResume = async (resumeId: string) => {
    setIsRegenerating(true);
    try {
      addStatusMessage("Regenerating resume with updated data...", "INFO");
      const host = await detectHost();
      const response = await fetch(
        `${host}/api/resumes/${resumeId}/regenerate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            credentials: credentials,
            resume_id: resumeId,
            use_updated_data: true,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        // Update the resume in the list
        setResumes(
          resumes.map((r) =>
            r.id === resumeId
              ? {
                  ...r,
                  content: data.resume.content,
                  generated_at: data.resume.generated_at,
                }
              : r
          )
        );
        // Update selected resume if it's the one being regenerated
        if (selectedResume?.id === resumeId) {
          setSelectedResume({
            ...selectedResume,
            content: data.resume.content,
            generated_at: data.resume.generated_at,
          });
        }
        addStatusMessage("Resume regenerated successfully!", "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to regenerate resume",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error regenerating resume:", error);
      addStatusMessage("Error regenerating resume", "ERROR");
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleDeleteResume = async (resumeId: string) => {
    try {
      addStatusMessage("Deleting resume...", "INFO");
      const host = await detectHost();
      const response = await fetch(`${host}/api/resumes/${resumeId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credentials: credentials,
          resume_id: resumeId,
        }),
      });

      if (response.ok) {
        setResumes(resumes.filter((r) => r.id !== resumeId));
        if (selectedResume?.id === resumeId) {
          setSelectedResume(null);
        }
        setTotalCount(totalCount - 1);
        addStatusMessage("Resume deleted successfully", "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to delete resume",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error deleting resume:", error);
      addStatusMessage("Error deleting resume", "ERROR");
    } finally {
      setShowDeleteConfirm(null);
    }
  };

  const handleExportResume = async (
    resumeId: string,
    format: "pdf" | "docx" | "markdown",
    targetRole: string
  ) => {
    setIsExporting(true);
    try {
      addStatusMessage(`Exporting resume as ${format.toUpperCase()}...`, "INFO");
      const host = await detectHost();
      const response = await fetch(`${host}/api/resumes/${resumeId}/export`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credentials: credentials,
          resume_id: resumeId,
          format: format,
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `resume_${targetRole.replace(/\s+/g, "_")}.${format === "docx" ? "docx" : format === "pdf" ? "pdf" : "md"}`;
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
    } finally {
      setIsExporting(false);
    }
  };

  const handleApplyFilters = () => {
    setCurrentPage(1);
    fetchResumes();
  };

  const handleClearFilters = () => {
    setFilterRole("");
    setFilterStartDate("");
    setFilterEndDate("");
    setCurrentPage(1);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-full">
      {/* Left Panel - Resume List and Filters */}
      <div className="flex flex-col gap-4 lg:w-1/2 overflow-y-auto">
        {/* Filters */}
        <div className="bg-bg-alt-verba rounded-2xl p-4 space-y-3">
          <h3 className="text-lg font-semibold text-text-verba mb-2">
            Filter Resumes
          </h3>

          <div className="space-y-2">
            <label className="text-sm text-text-alt-verba">Target Role</label>
            <input
              type="text"
              className="input input-bordered input-sm w-full bg-bg-verba text-text-verba placeholder-text-alt-verba"
              placeholder="e.g., Senior Software Engineer"
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-2">
              <label className="text-sm text-text-alt-verba">Start Date</label>
              <input
                type="date"
                className="input input-bordered input-sm w-full bg-bg-verba text-text-verba"
                value={filterStartDate}
                onChange={(e) => setFilterStartDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-text-alt-verba">End Date</label>
              <input
                type="date"
                className="input input-bordered input-sm w-full bg-bg-verba text-text-verba"
                value={filterEndDate}
                onChange={(e) => setFilterEndDate(e.target.value)}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <VerbaButton
              type="button"
              title="Apply Filters"
              onClick={handleApplyFilters}
              selected={true}
              selected_color="bg-primary-verba"
              className="flex-1"
            />
            <VerbaButton
              type="button"
              title="Clear"
              onClick={handleClearFilters}
              selected_color="bg-button-verba"
            />
          </div>
        </div>

        {/* Resume List */}
        <div className="bg-bg-alt-verba rounded-2xl p-4 flex-1 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-verba">
              Resume History ({totalCount})
            </h3>
            <VerbaButton
              type="button"
              Icon={MdRefresh}
              title="Refresh"
              onClick={fetchResumes}
              disabled={isLoading}
              circle={true}
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-2">
            {isLoading && (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <span className="loading loading-spinner loading-lg text-primary-verba"></span>
                <p className="text-text-alt-verba">Loading resumes...</p>
              </div>
            )}

            {!isLoading && resumes.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-text-alt-verba">
                <MdDescription size={64} className="mb-4 opacity-50" />
                <p className="text-lg">No resumes found</p>
                <p className="text-sm">
                  Generate your first resume to see it here
                </p>
              </div>
            )}

            {!isLoading &&
              resumes.map((resume) => (
                <div
                  key={resume.id}
                  className={`bg-bg-verba rounded-lg p-3 cursor-pointer transition-all border-2 ${
                    selectedResume?.id === resume.id
                      ? "border-primary-verba"
                      : "border-transparent hover:border-button-verba"
                  }`}
                  onClick={() => handleSelectResume(resume)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <MdWork className="text-primary-verba flex-shrink-0" size={16} />
                        <h4 className="text-text-verba font-semibold truncate">
                          {resume.target_role}
                        </h4>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-text-alt-verba">
                        <MdCalendarToday size={12} />
                        <span>{formatDate(resume.generated_at)}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="badge badge-xs bg-button-verba text-text-verba">
                          {resume.format.toUpperCase()}
                        </span>
                        {resume.source_log_ids && resume.source_log_ids.length > 0 && (
                          <span className="text-xs text-text-alt-verba">
                            {resume.source_log_ids.length} work logs
                          </span>
                        )}
                      </div>
                    </div>
                    <MdChevronRight
                      className={`text-text-alt-verba flex-shrink-0 transition-transform ${
                        selectedResume?.id === resume.id ? "rotate-90" : ""
                      }`}
                      size={20}
                    />
                  </div>
                </div>
              ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-button-verba">
              <button
                className="btn btn-sm bg-button-verba hover:bg-button-hover-verba text-text-verba border-none"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1 || isLoading}
              >
                Previous
              </button>
              <span className="text-sm text-text-alt-verba">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="btn btn-sm bg-button-verba hover:bg-button-hover-verba text-text-verba border-none"
                onClick={() =>
                  setCurrentPage(Math.min(totalPages, currentPage + 1))
                }
                disabled={currentPage === totalPages || isLoading}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Resume Details */}
      <div className="flex flex-col gap-4 lg:w-1/2">
        <div className="bg-bg-alt-verba rounded-2xl p-4 flex-1 flex flex-col">
          {!selectedResume ? (
            <div className="flex flex-col items-center justify-center h-full text-text-alt-verba">
              <MdDescription size={64} className="mb-4 opacity-50" />
              <p className="text-lg">No resume selected</p>
              <p className="text-sm">Select a resume from the list to view details</p>
            </div>
          ) : (
            <>
              {/* Header with Actions */}
              <div className="flex items-center justify-between mb-4 pb-4 border-b border-button-verba">
                <h3 className="text-lg font-semibold text-text-verba">
                  Resume Details
                </h3>
                <div className="flex gap-2">
                  <VerbaButton
                    type="button"
                    Icon={MdRefresh}
                    title="Regenerate"
                    onClick={() => handleRegenerateResume(selectedResume.id)}
                    disabled={isRegenerating || isExporting}
                    loading={isRegenerating}
                    circle={true}
                  />
                  <VerbaButton
                    type="button"
                    Icon={FaMarkdown}
                    title="Export MD"
                    onClick={() =>
                      handleExportResume(
                        selectedResume.id,
                        "markdown",
                        selectedResume.target_role
                      )
                    }
                    disabled={isExporting || isRegenerating}
                    circle={true}
                  />
                  <VerbaButton
                    type="button"
                    Icon={FaFilePdf}
                    title="Export PDF"
                    onClick={() =>
                      handleExportResume(
                        selectedResume.id,
                        "pdf",
                        selectedResume.target_role
                      )
                    }
                    disabled={isExporting || isRegenerating}
                    circle={true}
                  />
                  <VerbaButton
                    type="button"
                    Icon={FaFileWord}
                    title="Export DOCX"
                    onClick={() =>
                      handleExportResume(
                        selectedResume.id,
                        "docx",
                        selectedResume.target_role
                      )
                    }
                    disabled={isExporting || isRegenerating}
                    circle={true}
                  />
                  <VerbaButton
                    type="button"
                    Icon={MdDelete}
                    title="Delete"
                    onClick={() => setShowDeleteConfirm(selectedResume.id)}
                    disabled={isExporting || isRegenerating}
                    selected_color="bg-warning-verba"
                    circle={true}
                  />
                </div>
              </div>

              {/* Metadata */}
              <div className="mb-4 space-y-2">
                <div className="flex items-center gap-2">
                  <MdWork className="text-primary-verba" size={18} />
                  <span className="text-text-verba font-semibold">
                    {selectedResume.target_role}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-sm text-text-alt-verba">
                  <MdCalendarToday size={14} />
                  <span>Generated: {formatDate(selectedResume.generated_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="badge badge-sm bg-button-verba text-text-verba">
                    {selectedResume.format.toUpperCase()}
                  </span>
                  {selectedResume.source_log_ids &&
                    selectedResume.source_log_ids.length > 0 && (
                      <span className="text-sm text-text-alt-verba">
                        Based on {selectedResume.source_log_ids.length} work log
                        {selectedResume.source_log_ids.length !== 1 ? "s" : ""}
                      </span>
                    )}
                </div>
              </div>

              {/* Job Description */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-text-verba mb-2">
                  Job Description
                </h4>
                <div className="bg-bg-verba rounded-lg p-3 max-h-[200px] overflow-y-auto">
                  <p className="text-sm text-text-verba whitespace-pre-wrap">
                    {selectedResume.job_description}
                  </p>
                </div>
              </div>

              {/* Resume Content */}
              <div className="flex-1 flex flex-col">
                <h4 className="text-sm font-semibold text-text-verba mb-2">
                  Resume Content
                </h4>
                <div className="flex-1 bg-bg-verba rounded-lg p-4 overflow-y-auto">
                  <div
                    className="prose prose-sm max-w-none text-text-verba whitespace-pre-wrap"
                    dangerouslySetInnerHTML={{
                      __html: selectedResume.content
                        .replace(/\n/g, "<br/>")
                        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                        .replace(/\*(.*?)\*/g, "<em>$1</em>"),
                    }}
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-bg-alt-verba rounded-2xl p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-text-verba">
                Confirm Delete
              </h3>
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="btn btn-circle btn-sm bg-button-verba hover:bg-button-hover-verba text-text-verba border-none"
              >
                <MdClose size={18} />
              </button>
            </div>
            <p className="text-text-verba mb-6">
              Are you sure you want to delete this resume? This action cannot be
              undone.
            </p>
            <div className="flex gap-3 justify-end">
              <VerbaButton
                type="button"
                title="Cancel"
                onClick={() => setShowDeleteConfirm(null)}
                selected_color="bg-button-verba"
              />
              <VerbaButton
                type="button"
                title="Delete"
                onClick={() => handleDeleteResume(showDeleteConfirm)}
                selected={true}
                selected_color="bg-warning-verba"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeHistory;
