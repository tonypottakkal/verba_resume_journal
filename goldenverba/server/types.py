from typing import Literal
from pydantic import BaseModel
from enum import Enum


class Credentials(BaseModel):
    deployment: Literal["Weaviate", "Docker", "Local", "Custom"]
    url: str
    key: str


class ConversationItem(BaseModel):
    type: str
    content: str


class ChunksPayload(BaseModel):
    uuid: str
    page: int
    pageSize: int
    credentials: Credentials


class GetChunkPayload(BaseModel):
    uuid: str
    embedder: str
    credentials: Credentials


class GetVectorPayload(BaseModel):
    uuid: str
    showAll: bool
    credentials: Credentials


class ConnectPayload(BaseModel):
    credentials: Credentials
    port: str


class DataBatchPayload(BaseModel):
    chunk: str
    isLastChunk: bool
    total: int
    fileID: str
    order: int
    credentials: Credentials


class LoadPayload(BaseModel):
    reader: str
    chunker: str
    embedder: str
    fileBytes: list[str]
    fileNames: list[str]
    filePath: str
    document_type: str
    chunkUnits: int
    chunkOverlap: int


class ImportPayload(BaseModel):
    data: list
    textValues: list[str]
    config: dict


class GetComponentPayload(BaseModel):
    component: str


class SetComponentPayload(BaseModel):
    component: str
    selected_component: str


# Import


class FileStatus(str, Enum):
    READY = "READY"
    CREATE_NEW = "CREATE_NEW"
    STARTING = "STARTING"
    LOADING = "LOADING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INGESTING = "INGESTING"
    NER = "NER"
    EXTRACTION = "EXTRACTION"
    SUMMARIZING = "SUMMARIZING"
    DONE = "DONE"
    ERROR = "ERROR"


class ConfigSetting(BaseModel):
    type: str
    value: str | int
    description: str
    values: list[str]


class RAGComponentConfig(BaseModel):
    name: str
    variables: list[str]
    library: list[str]
    description: str
    config: dict[str, ConfigSetting]
    type: str
    available: bool


class RAGComponentClass(BaseModel):
    selected: str
    components: dict[str, RAGComponentConfig]


class RAGConfig(BaseModel):
    Reader: RAGComponentClass
    Chunker: RAGComponentClass
    Embedder: RAGComponentClass
    Retriever: RAGComponentClass
    Generator: RAGComponentClass


class StatusReport(BaseModel):
    fileID: str
    status: str
    message: str
    took: float


class CreateNewDocument(BaseModel):
    new_file_id: str
    filename: str
    original_file_id: str


class FileConfig(BaseModel):
    fileID: str
    filename: str
    isURL: bool
    overwrite: bool
    extension: str
    source: str
    content: str
    labels: list[str]
    rag_config: dict[str, RAGComponentClass]
    file_size: int
    status: FileStatus
    metadata: str
    status_report: dict


class ImportStreamPayload(BaseModel):
    fileMap: dict[str, FileConfig]


class VerbaConfig(BaseModel):
    RAG: dict[str, RAGComponentClass]
    SETTING: dict


class DocumentFilter(BaseModel):
    title: str
    uuid: str


class GetSuggestionsPayload(BaseModel):
    query: str
    limit: int
    credentials: Credentials


class DeleteSuggestionPayload(BaseModel):
    uuid: str
    credentials: Credentials


class GetAllSuggestionsPayload(BaseModel):
    page: int
    pageSize: int
    credentials: Credentials


class QueryPayload(BaseModel):
    query: str
    RAG: dict[str, RAGComponentClass]
    labels: list[str]
    documentFilter: list[DocumentFilter]
    credentials: Credentials


class DatacountPayload(BaseModel):
    embedding_model: str
    documentFilter: list[DocumentFilter]
    credentials: Credentials


class SetRAGConfigPayload(BaseModel):
    rag_config: RAGConfig
    credentials: Credentials


class SetUserConfigPayload(BaseModel):
    user_config: dict
    credentials: Credentials


class SetThemeConfigPayload(BaseModel):
    theme: dict
    themes: dict
    credentials: Credentials


class ChunkScore(BaseModel):
    uuid: str
    score: float
    chunk_id: int
    embedder: str


class GetContentPayload(BaseModel):
    uuid: str
    page: int
    chunkScores: list[ChunkScore]
    credentials: Credentials


class GeneratePayload(BaseModel):
    query: str
    context: str
    conversation: list[ConversationItem]
    rag_config: dict[str, RAGComponentClass]


class ConfigPayload(BaseModel):
    config: VerbaConfig


class RAGConfigPayload(BaseModel):
    config: VerbaConfig


class SearchQueryPayload(BaseModel):
    query: str
    labels: list[str]
    page: int
    pageSize: int
    credentials: Credentials


class GetDocumentPayload(BaseModel):
    uuid: str
    credentials: Credentials


class ResetPayload(BaseModel):
    resetMode: str
    credentials: Credentials


# Work Log Management Payloads


class CreateWorkLogPayload(BaseModel):
    content: str
    user_id: str
    extracted_skills: list[str] | None = None
    metadata: dict | None = None
    credentials: Credentials


class GetWorkLogsPayload(BaseModel):
    user_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = 100
    offset: int = 0
    credentials: Credentials


class UpdateWorkLogPayload(BaseModel):
    log_id: str
    content: str | None = None
    extracted_skills: list[str] | None = None
    metadata: dict | None = None
    credentials: Credentials


class DeleteWorkLogPayload(BaseModel):
    log_id: str
    credentials: Credentials


class GetWorkLogByIdPayload(BaseModel):
    log_id: str
    credentials: Credentials


class GetSkillsPayload(BaseModel):
    credentials: Credentials
    start_date: str | None = None
    end_date: str | None = None
    category: str | None = None
    limit: int = 100
    offset: int = 0


class GetSkillCategoriesPayload(BaseModel):
    credentials: Credentials


class ExtractSkillsPayload(BaseModel):
    credentials: Credentials
    text: str
    use_cache: bool = True


# Resume Generation and Tracking Payloads


class GenerateResumePayload(BaseModel):
    credentials: Credentials
    job_description: str
    target_role: str | None = None
    format: Literal["markdown", "pdf", "docx"] = "markdown"
    sections: list[str] | None = None
    max_length: int = 2000
    tone: str = "professional"
    user_id: str | None = None
    session_id: str | None = None
    user_feedback: str | None = None


class GetResumesPayload(BaseModel):
    credentials: Credentials
    user_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    target_role: str | None = None
    limit: int = 50
    offset: int = 0


class GetResumeByIdPayload(BaseModel):
    credentials: Credentials
    resume_id: str


class RegenerateResumePayload(BaseModel):
    credentials: Credentials
    resume_id: str
    use_updated_data: bool = True


class DeleteResumePayload(BaseModel):
    credentials: Credentials
    resume_id: str


class ExportResumePayload(BaseModel):
    credentials: Credentials
    resume_id: str
    format: Literal["pdf", "docx", "markdown"]


class CreateConversationSessionPayload(BaseModel):
    credentials: Credentials
    session_id: str | None = None
    metadata: dict[str, Any] | None = None


class GetConversationHistoryPayload(BaseModel):
    credentials: Credentials
    session_id: str
    format: Literal["list", "dict", "openai"] = "openai"


class ResetConversationSessionPayload(BaseModel):
    credentials: Credentials
    session_id: str


class DeleteConversationSessionPayload(BaseModel):
    credentials: Credentials
    session_id: str


# Document Metadata and Tag Management Payloads


class UpdateDocumentTagsPayload(BaseModel):
    credentials: Credentials
    document_id: str
    tags: list[str]


class GetDocumentTagsPayload(BaseModel):
    credentials: Credentials
    document_id: str


class GetAllTagsPayload(BaseModel):
    credentials: Credentials


class SearchDocumentsByTagsPayload(BaseModel):
    credentials: Credentials
    tags: list[str]
    match_all: bool = False  # If True, document must have all tags; if False, any tag
    page: int = 1
    pageSize: int = 10
