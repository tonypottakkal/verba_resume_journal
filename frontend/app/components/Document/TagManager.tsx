"use client";

import React, { useState, useEffect } from "react";
import { Credentials } from "@/app/types";
import { updateDocumentTags, getDocumentTags, getAllTags } from "@/app/api";
import { MdAdd, MdClose, MdCheck } from "react-icons/md";

interface TagManagerProps {
  documentId: string;
  credentials: Credentials;
  onTagsUpdated?: (tags: string[]) => void;
}

const TagManager: React.FC<TagManagerProps> = ({
  documentId,
  credentials,
  onTagsUpdated,
}) => {
  const [tags, setTags] = useState<string[]>([]);
  const [allTags, setAllTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTags();
    loadAllTags();
  }, [documentId]);

  const loadTags = async () => {
    try {
      const documentTags = await getDocumentTags(documentId, credentials);
      setTags(documentTags);
    } catch (err) {
      console.error("Failed to load tags:", err);
      setError("Failed to load tags");
    }
  };

  const loadAllTags = async () => {
    try {
      const allAvailableTags = await getAllTags(credentials);
      setAllTags(allAvailableTags);
    } catch (err) {
      console.error("Failed to load all tags:", err);
    }
  };

  const handleAddTag = () => {
    const trimmedTag = newTag.trim();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      const updatedTags = [...tags, trimmedTag];
      setTags(updatedTags);
      setNewTag("");
      setShowSuggestions(false);
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    const updatedTags = tags.filter((tag) => tag !== tagToRemove);
    setTags(updatedTags);
  };

  const handleSaveTags = async () => {
    setIsSaving(true);
    setError(null);
    
    try {
      const result = await updateDocumentTags(documentId, tags, credentials);
      
      if (result.success) {
        setIsEditing(false);
        if (onTagsUpdated) {
          onTagsUpdated(tags);
        }
        // Reload all tags to update suggestions
        await loadAllTags();
      } else {
        setError(result.error || "Failed to save tags");
      }
    } catch (err) {
      console.error("Failed to save tags:", err);
      setError("Failed to save tags");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setNewTag("");
    setShowSuggestions(false);
    loadTags(); // Reload original tags
  };

  const handleSuggestionClick = (tag: string) => {
    if (!tags.includes(tag)) {
      setTags([...tags, tag]);
    }
    setNewTag("");
    setShowSuggestions(false);
  };

  const filteredSuggestions = allTags.filter(
    (tag) =>
      !tags.includes(tag) &&
      tag.toLowerCase().includes(newTag.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <p className="font-bold text-xs text-text-alt-verba">Tags</p>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-xs text-secondary-verba hover:text-primary-verba transition-colors"
          >
            Edit
          </button>
        )}
      </div>

      {error && (
        <div className="text-xs text-warning-verba bg-bg-verba p-2 rounded">
          {error}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {tags.length === 0 && !isEditing && (
          <p className="text-sm text-text-alt-verba italic">No tags</p>
        )}
        
        {tags.map((tag) => (
          <div
            key={tag}
            className="flex items-center gap-1 bg-secondary-verba text-button-text-verba px-2 py-1 rounded-full text-xs"
          >
            <span>{tag}</span>
            {isEditing && (
              <button
                onClick={() => handleRemoveTag(tag)}
                className="hover:text-warning-verba transition-colors"
              >
                <MdClose size={14} />
              </button>
            )}
          </div>
        ))}
      </div>

      {isEditing && (
        <div className="flex flex-col gap-2 mt-2">
          <div className="relative">
            <div className="flex gap-2">
              <input
                type="text"
                value={newTag}
                onChange={(e) => {
                  setNewTag(e.target.value);
                  setShowSuggestions(e.target.value.length > 0);
                }}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleAddTag();
                  }
                }}
                placeholder="Add new tag..."
                className="flex-1 px-3 py-2 text-sm bg-bg-verba text-text-verba border border-button-verba rounded focus:outline-none focus:border-secondary-verba"
              />
              <button
                onClick={handleAddTag}
                disabled={!newTag.trim()}
                className="px-3 py-2 bg-secondary-verba text-button-text-verba rounded hover:bg-primary-verba transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <MdAdd size={20} />
              </button>
            </div>

            {showSuggestions && filteredSuggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-bg-alt-verba border border-button-verba rounded shadow-lg max-h-40 overflow-y-auto">
                {filteredSuggestions.slice(0, 10).map((tag) => (
                  <button
                    key={tag}
                    onClick={() => handleSuggestionClick(tag)}
                    className="w-full text-left px-3 py-2 text-sm text-text-verba hover:bg-button-verba transition-colors"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-2 justify-end">
            <button
              onClick={handleCancelEdit}
              disabled={isSaving}
              className="px-4 py-2 text-sm bg-button-verba text-button-text-verba rounded hover:bg-button-hover-verba transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveTags}
              disabled={isSaving}
              className="px-4 py-2 text-sm bg-secondary-verba text-button-text-verba rounded hover:bg-primary-verba transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <span className="loading loading-spinner loading-xs"></span>
                  Saving...
                </>
              ) : (
                <>
                  <MdCheck size={16} />
                  Save Tags
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TagManager;
