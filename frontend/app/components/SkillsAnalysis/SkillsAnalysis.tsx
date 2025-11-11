"use client";

import React, { useState, useEffect } from "react";
import { FaDownload, FaFilter, FaChartBar, FaTrophy, FaClock } from "react-icons/fa";
import { MdCategory } from "react-icons/md";
import VerbaButton from "../Navigation/VerbaButton";
import { Credentials } from "@/app/types";
import { detectHost } from "@/app/api";

interface Skill {
  name: string;
  category: string;
  proficiency_score: number;
  occurrence_count: number;
  source_documents: string[];
  last_used: string;
}

interface SkillCategory {
  name: string;
  skills: Skill[];
}

interface SkillsData {
  skills_by_category: Record<string, Skill[]>;
  total_skills: number;
  top_skills: Skill[];
  recent_skills: Skill[];
  generated_at: string;
}

interface SkillsAnalysisProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const SkillsAnalysis: React.FC<SkillsAnalysisProps> = ({
  credentials,
  addStatusMessage,
}) => {
  const [skillsData, setSkillsData] = useState<SkillsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [categories, setCategories] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<"category" | "top" | "recent">("category");

  useEffect(() => {
    fetchCategories();
    fetchSkills();
  }, []);

  const fetchCategories = async () => {
    try {
      const host = await detectHost();
      const response = await fetch(`${host}/api/skills/categories`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credentials: credentials,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const categoryNames = data.categories.map((cat: any) => cat.name);
        setCategories(["all", ...categoryNames]);
      }
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchSkills = async () => {
    setIsLoading(true);
    try {
      const host = await detectHost();
      const response = await fetch(`${host}/api/skills`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credentials: credentials,
          start_date: startDate || null,
          end_date: endDate || null,
          category: selectedCategory === "all" ? null : selectedCategory,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSkillsData(data);
        addStatusMessage("Skills data loaded successfully", "SUCCESS");
      } else {
        const errorData = await response.json();
        addStatusMessage(
          errorData.error || "Failed to fetch skills data",
          "ERROR"
        );
      }
    } catch (error) {
      console.error("Error fetching skills:", error);
      addStatusMessage("Error fetching skills data", "ERROR");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterApply = () => {
    fetchSkills();
  };

  const handleFilterReset = () => {
    setStartDate("");
    setEndDate("");
    setSelectedCategory("all");
    setTimeout(() => fetchSkills(), 100);
  };

  const exportSkillsData = (format: "json" | "csv") => {
    if (!skillsData) return;

    try {
      let content: string;
      let filename: string;
      let mimeType: string;

      if (format === "json") {
        content = JSON.stringify(skillsData, null, 2);
        filename = `skills_export_${new Date().toISOString().split("T")[0]}.json`;
        mimeType = "application/json";
      } else {
        // CSV format
        const allSkills: Skill[] = [];
        Object.values(skillsData.skills_by_category).forEach((skills) => {
          allSkills.push(...skills);
        });

        const csvRows = [
          ["Name", "Category", "Proficiency Score", "Occurrences", "Last Used"].join(","),
          ...allSkills.map((skill) =>
            [
              `"${skill.name}"`,
              `"${skill.category}"`,
              skill.proficiency_score.toFixed(2),
              skill.occurrence_count,
              `"${new Date(skill.last_used).toLocaleDateString()}"`,
            ].join(",")
          ),
        ];

        content = csvRows.join("\n");
        filename = `skills_export_${new Date().toISOString().split("T")[0]}.csv`;
        mimeType = "text/csv";
      }

      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      addStatusMessage(`Skills data exported as ${format.toUpperCase()}`, "SUCCESS");
    } catch (error) {
      console.error("Error exporting skills:", error);
      addStatusMessage("Error exporting skills data", "ERROR");
    }
  };

  const getProficiencyColor = (score: number): string => {
    if (score >= 0.8) return "bg-success-verba";
    if (score >= 0.6) return "bg-primary-verba";
    if (score >= 0.4) return "bg-warning-verba";
    return "bg-button-verba";
  };

  const getProficiencyLabel = (score: number): string => {
    if (score >= 0.8) return "Expert";
    if (score >= 0.6) return "Advanced";
    if (score >= 0.4) return "Intermediate";
    return "Beginner";
  };

  const renderSkillCard = (skill: Skill) => (
    <div
      key={skill.name}
      className="bg-bg-verba rounded-lg p-4 shadow-sm border border-button-verba hover:border-primary-verba transition-colors"
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className="text-text-verba font-semibold">{skill.name}</h4>
        <span className={`badge badge-sm ${getProficiencyColor(skill.proficiency_score)} text-text-verba`}>
          {getProficiencyLabel(skill.proficiency_score)}
        </span>
      </div>

      {/* Proficiency Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-text-alt-verba mb-1">
          <span>Proficiency</span>
          <span>{(skill.proficiency_score * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-bg-alt-verba rounded-full h-2">
          <div
            className={`h-2 rounded-full ${getProficiencyColor(skill.proficiency_score)}`}
            style={{ width: `${skill.proficiency_score * 100}%` }}
          />
        </div>
      </div>

      <div className="flex justify-between text-xs text-text-alt-verba">
        <span>Used {skill.occurrence_count} times</span>
        <span>Last: {new Date(skill.last_used).toLocaleDateString()}</span>
      </div>
    </div>
  );

  const renderCategoryView = () => {
    if (!skillsData || Object.keys(skillsData.skills_by_category).length === 0) {
      return (
        <div className="text-center py-12 text-text-alt-verba">
          <p className="text-lg">No skills data available</p>
          <p className="text-sm">Start adding work logs to see your skills breakdown</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {Object.entries(skillsData.skills_by_category).map(([category, skills]) => (
          <div key={category} className="bg-bg-alt-verba rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <MdCategory className="text-primary-verba" size={24} />
              <h3 className="text-xl font-bold text-text-verba">
                {category.replace(/_/g, " ").toUpperCase()}
              </h3>
              <span className="badge badge-lg bg-button-verba text-text-verba">
                {skills.length} skills
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {skills.map((skill) => renderSkillCard(skill))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderTopSkills = () => {
    if (!skillsData || skillsData.top_skills.length === 0) {
      return (
        <div className="text-center py-12 text-text-alt-verba">
          <p className="text-lg">No top skills available</p>
        </div>
      );
    }

    return (
      <div className="bg-bg-alt-verba rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <FaTrophy className="text-warning-verba" size={28} />
          <h3 className="text-2xl font-bold text-text-verba">Top Skills</h3>
        </div>

        <div className="space-y-4">
          {skillsData.top_skills.map((skill, index) => (
            <div
              key={skill.name}
              className="bg-bg-verba rounded-lg p-4 shadow-sm border border-button-verba flex items-center gap-4"
            >
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-verba flex items-center justify-center text-text-verba font-bold text-xl">
                {index + 1}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="text-text-verba font-semibold text-lg">{skill.name}</h4>
                    <p className="text-text-alt-verba text-sm">{skill.category.replace(/_/g, " ")}</p>
                  </div>
                  <span className={`badge ${getProficiencyColor(skill.proficiency_score)} text-text-verba`}>
                    {getProficiencyLabel(skill.proficiency_score)}
                  </span>
                </div>
                <div className="w-full bg-bg-alt-verba rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${getProficiencyColor(skill.proficiency_score)}`}
                    style={{ width: `${skill.proficiency_score * 100}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-text-alt-verba mt-2">
                  <span>{skill.occurrence_count} occurrences</span>
                  <span>{(skill.proficiency_score * 100).toFixed(0)}% proficiency</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderRecentSkills = () => {
    if (!skillsData || skillsData.recent_skills.length === 0) {
      return (
        <div className="text-center py-12 text-text-alt-verba">
          <p className="text-lg">No recent skills available</p>
        </div>
      );
    }

    return (
      <div className="bg-bg-alt-verba rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <FaClock className="text-secondary-verba" size={28} />
          <h3 className="text-2xl font-bold text-text-verba">Recently Used Skills</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {skillsData.recent_skills.map((skill) => renderSkillCard(skill))}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      {/* Header with Stats */}
      <div className="bg-bg-alt-verba rounded-2xl p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h2 className="text-3xl font-bold text-text-verba mb-2">Skills Analysis</h2>
            <p className="text-text-alt-verba">
              Comprehensive breakdown of your professional skills
            </p>
          </div>

          {skillsData && (
            <div className="flex gap-4">
              <div className="stat bg-bg-verba rounded-lg p-4 min-w-[120px]">
                <div className="stat-title text-text-alt-verba text-xs">Total Skills</div>
                <div className="stat-value text-primary-verba text-2xl">{skillsData.total_skills}</div>
              </div>
              <div className="stat bg-bg-verba rounded-lg p-4 min-w-[120px]">
                <div className="stat-title text-text-alt-verba text-xs">Categories</div>
                <div className="stat-value text-secondary-verba text-2xl">
                  {Object.keys(skillsData.skills_by_category).length}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-bg-verba rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <FaFilter className="text-primary-verba" />
            <h3 className="text-text-verba font-semibold">Filters</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text text-text-alt-verba">Category</span>
              </label>
              <select
                className="select select-bordered bg-bg-alt-verba text-text-verba"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat === "all" ? "All Categories" : cat.replace(/_/g, " ").toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text text-text-alt-verba">Start Date</span>
              </label>
              <input
                type="date"
                className="input input-bordered bg-bg-alt-verba text-text-verba"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="form-control">
              <label className="label">
                <span className="label-text text-text-alt-verba">End Date</span>
              </label>
              <input
                type="date"
                className="input input-bordered bg-bg-alt-verba text-text-verba"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>

            <div className="form-control justify-end">
              <div className="flex gap-2">
                <button
                  className="btn btn-sm bg-primary-verba hover:bg-primary-verba/80 text-text-verba border-none"
                  onClick={handleFilterApply}
                  disabled={isLoading}
                >
                  Apply
                </button>
                <button
                  className="btn btn-sm bg-button-verba hover:bg-button-hover-verba text-text-verba border-none"
                  onClick={handleFilterReset}
                  disabled={isLoading}
                >
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex justify-between items-center">
        <div className="tabs tabs-boxed bg-bg-alt-verba p-1">
          <button
            className={`tab ${viewMode === "category" ? "tab-active bg-primary-verba text-text-verba" : "text-text-alt-verba"}`}
            onClick={() => setViewMode("category")}
          >
            <FaChartBar className="mr-2" />
            By Category
          </button>
          <button
            className={`tab ${viewMode === "top" ? "tab-active bg-primary-verba text-text-verba" : "text-text-alt-verba"}`}
            onClick={() => setViewMode("top")}
          >
            <FaTrophy className="mr-2" />
            Top Skills
          </button>
          <button
            className={`tab ${viewMode === "recent" ? "tab-active bg-primary-verba text-text-verba" : "text-text-alt-verba"}`}
            onClick={() => setViewMode("recent")}
          >
            <FaClock className="mr-2" />
            Recent
          </button>
        </div>

        {/* Export Buttons */}
        <div className="flex gap-2">
          <button
            className="btn btn-sm bg-secondary-verba hover:bg-secondary-verba/80 text-text-verba border-none"
            onClick={() => exportSkillsData("json")}
            disabled={!skillsData || isLoading}
          >
            <FaDownload className="mr-2" />
            Export JSON
          </button>
          <button
            className="btn btn-sm bg-secondary-verba hover:bg-secondary-verba/80 text-text-verba border-none"
            onClick={() => exportSkillsData("csv")}
            disabled={!skillsData || isLoading}
          >
            <FaDownload className="mr-2" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <span className="loading loading-spinner loading-lg text-primary-verba"></span>
            <p className="text-text-alt-verba">Loading skills data...</p>
          </div>
        ) : (
          <>
            {viewMode === "category" && renderCategoryView()}
            {viewMode === "top" && renderTopSkills()}
            {viewMode === "recent" && renderRecentSkills()}
          </>
        )}
      </div>

      {/* Footer Info */}
      {skillsData && !isLoading && (
        <div className="text-center text-xs text-text-alt-verba">
          Last updated: {new Date(skillsData.generated_at).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default SkillsAnalysis;
