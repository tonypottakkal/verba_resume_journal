"use client";

import React, { useState, useEffect, useRef } from "react";
import { MdDelete, MdEdit, MdSave, MdCancel } from "react-icons/md";
import { IoIosSend } from "react-icons/io";
import { FaLightbulb } from "react-icons/fa";
import VerbaButton from "../Navigation/VerbaButton";
import { Credentials } from "@/app/types";
import { detectHost } from "@/app/api";

interface WorkLogEntry {
  id: string;
  content: string;
  timestamp: string;
  user_id: string;
  extracted_skills: string[];
  metadata: Record<string, any>;
}

interface WorkLogChatProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const WorkLogChat: React.FC<WorkLogChatProps> = ({
  credentials,
  addStatusMessage,
}) => {
  const [userInput, setUserInput] = useState("");
  const [logs, setLogs] = useState<WorkLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingLogId, setEditingLogId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const [previewSkills, setPreviewSkills] = useState<string[]>([]);
  const [isExtractingSkills, setIsExtractingSkills] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const skillExtractionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchWorkLogs();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  // Real-time skill extraction preview
  useEffect(() => {
    if (userInput.trim().length > 20) {
      if (skillExtractionTimeoutRef.current) {
        clearTimeout(skillExtractionTimeoutRef.current);
      }

      skillExtractionTimeoutRef.current = setTimeout(() => {
        extractSkillsPreview(userInput);
      }, 1000);
    } else {
      setPreviewSkills([]);
    }

    return () => {
      if (skillExtractionTimeoutRef.current) {
        clearTimeout(skillExtractionTimeoutRef.current);
      }
    };
  }, [userInput]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchWorkLogs = async () => {
    try {
      const host = await detectHost();
      const response = await fetch(`${host}/api/worklogs`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
      } else {
        addStatusMessage("Failed to fetch work logs", "ERROR");
      }
    } catch (error) {
      console.error("Error fetching work logs:", error);
      addStatusMessage("Error fetching work logs", "ERROR");
    }
  };

  const extractSkillsPreview = async (text: string) => {
    if (isExtractingSkills) return;

    setIsExtractingSkills(true);
    try {
      const host = await detectHost();
      const response = await fetch(`${host}/api/skills/extract`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          credentials: credentials,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewSkills(data.skills || []);
      }
    } catch (error) {
      console.error("Error extracting skills:", error);
    } finally {
      setIsExtractingSkills(false);
    }
  };

  const createWorkLog = async () => {
    if (!userInput.trim() || isLoading) return;

    const content = userInput;
    setUserInput("");
    setPreviewSkills([]);
    setIsLoading(true);

    try {
      addStatusMessage("Creating work log entry...", "INFO");
      const host = await detectHost();
      const response = await fetch(`${host}/api/worklogs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: content,
          credentials: credentials,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setLogs([...logs, data.log]);
        addStatusMessage("Work log entry created successfully", "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to create work log",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error creating work log:", error);
      addStatusMessage("Error creating work log entry", "ERROR");
    } finally {
      setIsLoading(false);
    }
  };

  const updateWorkLog = async (logId: string, newContent: string) => {
    if (!newContent.trim()) return;

    try {
      addStatusMessage("Updating work log entry...", "INFO");
      const host = await detectHost();
      const response = await fetch(`${host}/api/worklogs/${logId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: newContent,
          credentials: credentials,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setLogs(logs.map((log) => (log.id === logId ? data.log : log)));
        setEditingLogId(null);
        setEditContent("");
        addStatusMessage("Work log entry updated successfully", "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to update work log",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error updating work log:", error);
      addStatusMessage("Error updating work log entry", "ERROR");
    }
  };

  const deleteWorkLog = async (logId: string) => {
    try {
      addStatusMessage("Deleting work log entry...", "INFO");
      const host = await detectHost();
      const response = await fetch(`${host}/api/worklogs/${logId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credentials: credentials,
        }),
      });

      if (response.ok) {
        setLogs(logs.filter((log) => log.id !== logId));
        addStatusMessage("Work log entry deleted successfully", "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to delete work log",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error deleting work log:", error);
      addStatusMessage("Error deleting work log entry", "ERROR");
    }
  };

  const startEditing = (log: WorkLogEntry) => {
    setEditingLogId(log.id);
    setEditContent(log.content);
  };

  const cancelEditing = () => {
    setEditingLogId(null);
    setEditContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      createWorkLog();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Work Log Entries */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {logs.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-text-alt-verba">
            <p className="text-lg">No work log entries yet</p>
            <p className="text-sm">Start documenting your accomplishments below</p>
          </div>
        )}

        {logs.map((log) => (
          <div
            key={log.id}
            className="bg-bg-verba rounded-lg p-4 shadow-sm border border-button-verba"
          >
            <div className="flex justify-between items-start mb-2">
              <p className="text-xs text-text-alt-verba">
                {formatTimestamp(log.timestamp)}
              </p>
              <div className="flex gap-2">
                {editingLogId === log.id ? (
                  <>
                    <button
                      onClick={() => updateWorkLog(log.id, editContent)}
                      className="btn btn-circle btn-xs bg-secondary-verba hover:bg-secondary-verba/80 text-text-verba border-none"
                      title="Save"
                    >
                      <MdSave size={14} />
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="btn btn-circle btn-xs bg-button-verba hover:bg-button-hover-verba text-text-verba border-none"
                      title="Cancel"
                    >
                      <MdCancel size={14} />
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => startEditing(log)}
                      className="btn btn-circle btn-xs bg-button-verba hover:bg-button-hover-verba text-text-verba border-none"
                      title="Edit"
                    >
                      <MdEdit size={14} />
                    </button>
                    <button
                      onClick={() => deleteWorkLog(log.id)}
                      className="btn btn-circle btn-xs bg-warning-verba hover:bg-warning-verba/80 text-text-verba border-none"
                      title="Delete"
                    >
                      <MdDelete size={14} />
                    </button>
                  </>
                )}
              </div>
            </div>

            {editingLogId === log.id ? (
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="textarea textarea-bordered w-full bg-bg-alt-verba text-text-verba min-h-[100px]"
              />
            ) : (
              <p className="text-text-verba whitespace-pre-wrap">{log.content}</p>
            )}

            {log.extracted_skills && log.extracted_skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {log.extracted_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="badge badge-sm bg-primary-verba text-text-verba"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-3 text-text-alt-verba">
            <span className="loading loading-dots loading-md"></span>
            <p>Creating work log entry...</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-bg-alt-verba rounded-2xl p-4 space-y-3">
        {/* Skill Preview */}
        {previewSkills.length > 0 && (
          <div className="flex items-start gap-2 p-3 bg-bg-verba rounded-lg">
            <FaLightbulb className="text-primary-verba mt-1 flex-shrink-0" size={16} />
            <div className="flex-1">
              <p className="text-xs text-text-alt-verba mb-2">
                Detected skills:
              </p>
              <div className="flex flex-wrap gap-2">
                {previewSkills.map((skill, index) => (
                  <span
                    key={index}
                    className="badge badge-sm bg-primary-verba/20 text-text-verba border-primary-verba"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Text Input */}
        <div className="flex gap-2 items-end">
          <textarea
            className="textarea textarea-bordered flex-1 bg-bg-verba text-text-verba placeholder-text-alt-verba min-h-[80px] max-h-[200px] resize-y"
            placeholder="Document your work accomplishments, projects, or tasks..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <VerbaButton
            type="button"
            Icon={IoIosSend}
            onClick={createWorkLog}
            disabled={isLoading || !userInput.trim()}
            selected_color="bg-primary-verba"
            title="Send"
          />
        </div>

        <p className="text-xs text-text-alt-verba">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default WorkLogChat;
