from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import asyncio

from goldenverba.server.helpers import LoggerManager, BatchManager
from weaviate.client import WeaviateAsyncClient

import os
from pathlib import Path

from dotenv import load_dotenv
from starlette.websockets import WebSocketDisconnect
from wasabi import msg  # type: ignore[import]

from goldenverba import verba_manager

from goldenverba.server.types import (
    ResetPayload,
    QueryPayload,
    GeneratePayload,
    Credentials,
    GetDocumentPayload,
    ConnectPayload,
    DatacountPayload,
    GetSuggestionsPayload,
    GetAllSuggestionsPayload,
    DeleteSuggestionPayload,
    GetContentPayload,
    SetThemeConfigPayload,
    SetUserConfigPayload,
    SearchQueryPayload,
    SetRAGConfigPayload,
    GetChunkPayload,
    GetVectorPayload,
    DataBatchPayload,
    ChunksPayload,
    CreateWorkLogPayload,
    GetWorkLogsPayload,
    UpdateWorkLogPayload,
    DeleteWorkLogPayload,
    GetWorkLogByIdPayload,
    GetSkillsPayload,
    GetSkillCategoriesPayload,
    ExtractSkillsPayload,
    GenerateResumePayload,
    GetResumesPayload,
    GetResumeByIdPayload,
    RegenerateResumePayload,
    DeleteResumePayload,
    ExportResumePayload,
    CreateConversationSessionPayload,
    GetConversationHistoryPayload,
    ResetConversationSessionPayload,
    DeleteConversationSessionPayload,
    UpdateDocumentTagsPayload,
    GetDocumentTagsPayload,
    GetAllTagsPayload,
    SearchDocumentsByTagsPayload,
)

load_dotenv()

# Check if runs in production
production_key = os.environ.get("VERBA_PRODUCTION")
tag = os.environ.get("VERBA_GOOGLE_TAG", "")


if production_key:
    msg.info(f"Verba runs in {production_key} mode")
    production = production_key
else:
    production = "Local"

manager = verba_manager.VerbaManager()

client_manager = verba_manager.ClientManager()

### Lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await client_manager.disconnect()


# FastAPI App
app = FastAPI(lifespan=lifespan)

# Allow requests only from the same origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This will be restricted by the custom middleware
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware to check if the request is from the same origin
@app.middleware("http")
async def check_same_origin(request: Request, call_next):
    # Allow public access to /api/health
    if request.url.path == "/api/health":
        return await call_next(request)

    origin = request.headers.get("origin")
    
    # Allow requests without Origin header (same-origin requests from browser)
    # Allow requests with matching origin
    # Allow localhost requests
    if (
        origin is None or
        origin == str(request.base_url).rstrip("/") or
        (origin and origin.startswith("http://localhost:") and request.base_url.hostname == "localhost") or
        (origin and origin.startswith("http://127.0.0.1:"))
    ):
        return await call_next(request)
    else:
        # Only apply restrictions to /api/ routes (except /api/health)
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Not allowed",
                    "details": {
                        "request_origin": origin,
                        "expected_origin": str(request.base_url),
                        "request_method": request.method,
                        "request_url": str(request.url),
                        "expected_header": "Origin header matching the server's base URL or localhost",
                    },
                },
            )

        # Allow non-API routes to pass through
        return await call_next(request)


BASE_DIR = Path(__file__).resolve().parent

# Serve all static files (including _next assets)
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend/out"), name="app")


@app.get("/")
@app.head("/")
async def serve_frontend():
    response = FileResponse(os.path.join(BASE_DIR, "frontend/out/index.html"))
    # Add cache-busting headers to force browser to reload
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


### INITIAL ENDPOINTS


# Define health check endpoint
@app.get("/api/health")
async def health_check():

    await client_manager.clean_up()

    if production == "Local":
        deployments = await manager.get_deployments()
    else:
        deployments = {"WEAVIATE_URL_VERBA": "", "WEAVIATE_API_KEY_VERBA": ""}

    # Check new resume components status
    resume_components = {
        "worklog_manager": manager.worklog_manager is not None,
        "skills_extractor": manager.skills_extractor is not None,
        "resume_generator": manager.resume_generator is not None,
        "resume_tracker": manager.resume_tracker is not None,
        "skill_extraction_enabled": os.getenv("ENABLE_SKILL_EXTRACTION", "true").lower() == "true",
        "resume_tracking_enabled": os.getenv("ENABLE_RESUME_TRACKING", "true").lower() == "true",
        "pdf_export_enabled": os.getenv("ENABLE_PDF_EXPORT", "false").lower() == "true"
    }
    
    return JSONResponse(
        content={
            "message": "Alive!",
            "production": production,
            "gtag": tag,
            "deployments": deployments,
            "default_deployment": os.getenv("DEFAULT_DEPLOYMENT", ""),
            "resume_components": resume_components
        }
    )


@app.post("/api/connect")
async def connect_to_verba(payload: ConnectPayload):
    try:
        client = await client_manager.connect(payload.credentials, payload.port)
        if isinstance(
            client, WeaviateAsyncClient
        ):  # Check if client is an AsyncClient object
            config = await manager.load_rag_config(client)
            user_config = await manager.load_user_config(client)
            theme, themes = await manager.load_theme_config(client)
            return JSONResponse(
                status_code=200,
                content={
                    "connected": True,
                    "error": "",
                    "rag_config": config,
                    "user_config": user_config,
                    "theme": theme,
                    "themes": themes,
                },
            )
        else:
            raise TypeError(
                "Couldn't connect to Weaviate, client is not an AsyncClient object"
            )
    except Exception as e:
        msg.fail(f"Failed to connect to Weaviate {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "connected": False,
                "error": f"Failed to connect to Weaviate {str(e)}",
                "rag_config": {},
                "theme": {},
                "themes": {},
            },
        )


### WEBSOCKETS


@app.websocket("/ws/generate_stream")
async def websocket_generate_stream(websocket: WebSocket):
    await websocket.accept()
    while True:  # Start a loop to keep the connection alive.
        try:
            data = await websocket.receive_text()
            # Parse and validate the JSON string using Pydantic model
            payload = GeneratePayload.model_validate_json(data)

            msg.good(f"Received generate stream call for {payload.query}")

            full_text = ""
            async for chunk in manager.generate_stream_answer(
                payload.rag_config,
                payload.query,
                payload.context,
                payload.conversation,
            ):
                full_text += chunk["message"]
                if chunk["finish_reason"] == "stop":
                    chunk["full_text"] = full_text
                await websocket.send_json(chunk)

        except WebSocketDisconnect:
            msg.warn("WebSocket connection closed by client.")
            break  # Break out of the loop when the client disconnects

        except Exception as e:
            msg.fail(f"WebSocket Error: {str(e)}")
            await websocket.send_json(
                {"message": e, "finish_reason": "stop", "full_text": str(e)}
            )
        msg.good("Succesfully streamed answer")


@app.websocket("/ws/import_files")
async def websocket_import_files(websocket: WebSocket):

    if production == "Demo":
        return

    await websocket.accept()
    logger = LoggerManager(websocket)
    batcher = BatchManager()

    while True:
        try:
            data = await websocket.receive_text()
            batch_data = DataBatchPayload.model_validate_json(data)
            fileConfig = batcher.add_batch(batch_data)
            if fileConfig is not None:
                client = await client_manager.connect(batch_data.credentials)
                await asyncio.create_task(
                    manager.import_document(client, fileConfig, logger)
                )

        except WebSocketDisconnect:
            msg.warn("Import WebSocket connection closed by client.")
            break
        except Exception as e:
            msg.fail(f"Import WebSocket Error: {str(e)}")
            break


### CONFIG ENDPOINTS


# Get Configuration
@app.post("/api/get_rag_config")
async def retrieve_rag_config(payload: Credentials):
    try:
        client = await client_manager.connect(payload)
        config = await manager.load_rag_config(client)
        return JSONResponse(
            status_code=200, content={"rag_config": config, "error": ""}
        )

    except Exception as e:
        msg.warn(f"Could not retrieve configuration: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "rag_config": {},
                "error": f"Could not retrieve rag configuration: {str(e)}",
            },
        )


@app.post("/api/set_rag_config")
async def update_rag_config(payload: SetRAGConfigPayload):
    if production == "Demo":
        return JSONResponse(
            content={
                "status": "200",
                "status_msg": "Config can't be updated in Production Mode",
            }
        )

    try:
        client = await client_manager.connect(payload.credentials)
        await manager.set_rag_config(client, payload.rag_config.model_dump())
        return JSONResponse(
            content={
                "status": 200,
            }
        )
    except Exception as e:
        msg.warn(f"Failed to set new RAG Config {str(e)}")
        return JSONResponse(
            content={
                "status": 400,
                "status_msg": f"Failed to set new RAG Config {str(e)}",
            }
        )


@app.post("/api/get_user_config")
async def retrieve_user_config(payload: Credentials):
    try:
        client = await client_manager.connect(payload)
        config = await manager.load_user_config(client)
        return JSONResponse(
            status_code=200, content={"user_config": config, "error": ""}
        )

    except Exception as e:
        msg.warn(f"Could not retrieve user configuration: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "user_config": {},
                "error": f"Could not retrieve rag configuration: {str(e)}",
            },
        )


@app.post("/api/set_user_config")
async def update_user_config(payload: SetUserConfigPayload):
    if production == "Demo":
        return JSONResponse(
            content={
                "status": "200",
                "status_msg": "Config can't be updated in Production Mode",
            }
        )

    try:
        client = await client_manager.connect(payload.credentials)
        await manager.set_user_config(client, payload.user_config)
        return JSONResponse(
            content={
                "status": 200,
                "status_msg": "User config updated",
            }
        )
    except Exception as e:
        msg.warn(f"Failed to set new RAG Config {str(e)}")
        return JSONResponse(
            content={
                "status": 400,
                "status_msg": f"Failed to set new RAG Config {str(e)}",
            }
        )


# Get Configuration
@app.post("/api/get_theme_config")
async def retrieve_theme_config(payload: Credentials):
    try:
        client = await client_manager.connect(payload)
        theme, themes = await manager.load_theme_config(client)
        return JSONResponse(
            status_code=200, content={"theme": theme, "themes": themes, "error": ""}
        )

    except Exception as e:
        msg.warn(f"Could not retrieve configuration: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "theme": None,
                "themes": None,
                "error": f"Could not retrieve theme configuration: {str(e)}",
            },
        )


@app.post("/api/set_theme_config")
async def update_theme_config(payload: SetThemeConfigPayload):
    if production == "Demo":
        return JSONResponse(
            content={
                "status": "200",
                "status_msg": "Config can't be updated in Production Mode",
            }
        )

    try:
        client = await client_manager.connect(payload.credentials)
        await manager.set_theme_config(
            client, {"theme": payload.theme, "themes": payload.themes}
        )
        return JSONResponse(
            content={
                "status": 200,
            }
        )
    except Exception as e:
        msg.warn(f"Failed to set new RAG Config {str(e)}")
        return JSONResponse(
            content={
                "status": 400,
                "status_msg": f"Failed to set new RAG Config {str(e)}",
            }
        )


### RAG ENDPOINTS


# Receive query and return chunks and query answer
@app.post("/api/query")
async def query(payload: QueryPayload):
    msg.good(f"Received query: {payload.query}")
    try:
        client = await client_manager.connect(payload.credentials)
        documents_uuid = [document.uuid for document in payload.documentFilter]
        documents, context = await manager.retrieve_chunks(
            client, payload.query, payload.RAG, payload.labels, documents_uuid
        )

        return JSONResponse(
            content={"error": "", "documents": documents, "context": context}
        )
    except Exception as e:
        msg.warn(f"Query failed: {str(e)}")
        return JSONResponse(
            content={"error": f"Query failed: {str(e)}", "documents": [], "context": ""}
        )


### DOCUMENT ENDPOINTS


# Retrieve specific document based on UUID
@app.post("/api/get_document")
async def get_document(payload: GetDocumentPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        document = await manager.weaviate_manager.get_document(
            client,
            payload.uuid,
            properties=[
                "title",
                "extension",
                "fileSize",
                "labels",
                "source",
                "meta",
                "metadata",
            ],
        )
        if document is not None:
            document["content"] = ""
            msg.good(f"Succesfully retrieved document: {document['title']}")
            return JSONResponse(
                content={
                    "error": "",
                    "document": document,
                }
            )
        else:
            msg.warn(f"Could't retrieve document")
            return JSONResponse(
                content={
                    "error": "Couldn't retrieve requested document",
                    "document": None,
                }
            )
    except Exception as e:
        msg.fail(f"Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "error": str(e),
                "document": None,
            }
        )


@app.post("/api/get_datacount")
async def get_document_count(payload: DatacountPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        document_uuids = [document.uuid for document in payload.documentFilter]
        datacount = await manager.weaviate_manager.get_datacount(
            client, payload.embedding_model, document_uuids
        )
        return JSONResponse(
            content={
                "datacount": datacount,
            }
        )
    except Exception as e:
        msg.fail(f"Document Count retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "datacount": 0,
            }
        )


@app.post("/api/get_labels")
async def get_labels(payload: Credentials):
    try:
        client = await client_manager.connect(payload)
        labels = await manager.weaviate_manager.get_labels(client)
        return JSONResponse(
            content={
                "labels": labels,
            }
        )
    except Exception as e:
        msg.fail(f"Document Labels retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "labels": [],
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/get_content")
async def get_content(payload: GetContentPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        content, maxPage = await manager.get_content(
            client, payload.uuid, payload.page - 1, payload.chunkScores
        )
        msg.good(f"Succesfully retrieved content from {payload.uuid}")
        return JSONResponse(
            content={"error": "", "content": content, "maxPage": maxPage}
        )
    except Exception as e:
        msg.fail(f"Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "error": str(e),
                "document": None,
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/get_vectors")
async def get_vectors(payload: GetVectorPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        vector_groups = await manager.weaviate_manager.get_vectors(
            client, payload.uuid, payload.showAll
        )
        return JSONResponse(
            content={
                "error": "",
                "vector_groups": vector_groups,
            }
        )
    except Exception as e:
        msg.fail(f"Vector retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "error": str(e),
                "payload": {"embedder": "None", "vectors": []},
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/get_chunks")
async def get_chunks(payload: ChunksPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        chunks = await manager.weaviate_manager.get_chunks(
            client, payload.uuid, payload.page, payload.pageSize
        )
        return JSONResponse(
            content={
                "error": "",
                "chunks": chunks,
            }
        )
    except Exception as e:
        msg.fail(f"Chunk retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "error": str(e),
                "chunks": None,
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/get_chunk")
async def get_chunk(payload: GetChunkPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        chunk = await manager.weaviate_manager.get_chunk(
            client, payload.uuid, payload.embedder
        )
        return JSONResponse(
            content={
                "error": "",
                "chunk": chunk,
            }
        )
    except Exception as e:
        msg.fail(f"Chunk retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "error": str(e),
                "chunk": None,
            }
        )


## Retrieve and search documents imported to Weaviate
@app.post("/api/get_all_documents")
async def get_all_documents(payload: SearchQueryPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        documents, total_count = await manager.weaviate_manager.get_documents(
            client,
            payload.query,
            payload.pageSize,
            payload.page,
            payload.labels,
            properties=["title", "extension", "fileSize", "labels", "source", "meta"],
        )
        labels = await manager.weaviate_manager.get_labels(client)

        msg.good(f"Succesfully retrieved document: {len(documents)} documents")
        return JSONResponse(
            content={
                "documents": documents,
                "labels": labels,
                "error": "",
                "totalDocuments": total_count,
            }
        )
    except Exception as e:
        msg.fail(f"Retrieving all documents failed: {str(e)}")
        return JSONResponse(
            content={
                "documents": [],
                "label": [],
                "error": f"All Document retrieval failed: {str(e)}",
                "totalDocuments": 0,
            }
        )


# Delete specific document based on UUID
@app.post("/api/delete_document")
async def delete_document(payload: GetDocumentPayload):
    if production == "Demo":
        msg.warn("Can't delete documents when in Production Mode")
        return JSONResponse(status_code=200, content={})

    try:
        client = await client_manager.connect(payload.credentials)
        msg.info(f"Deleting {payload.uuid}")
        await manager.weaviate_manager.delete_document(client, payload.uuid)
        return JSONResponse(status_code=200, content={})

    except Exception as e:
        msg.fail(f"Deleting Document with ID {payload.uuid} failed: {str(e)}")
        return JSONResponse(status_code=400, content={})


### DOCUMENT TAG MANAGEMENT ENDPOINTS


@app.post("/api/documents/{document_id}/tags")
async def update_document_tags(document_id: str, payload: UpdateDocumentTagsPayload):
    """
    Update tags for a specific document.
    
    Args:
        document_id: UUID of the document
        payload: UpdateDocumentTagsPayload containing tags and credentials
        
    Returns:
        JSONResponse with success status or error
    """
    if production == "Demo":
        msg.warn("Can't update document tags when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Document tag updates are disabled in Demo mode",
                "success": False
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        # Verify document_id matches payload
        if payload.document_id != document_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Document ID in URL does not match payload",
                    "success": False
                }
            )
        
        success = await manager.weaviate_manager.update_document_tags(
            client=client,
            document_id=document_id,
            tags=payload.tags
        )
        
        msg.good(f"Updated tags for document: {document_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "success": success,
                "document_id": document_id,
                "tags": payload.tags
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to update document tags: {str(e)}")
        status_code = 404 if "not found" in str(e).lower() else 500
        return JSONResponse(
            status_code=status_code,
            content={
                "error": f"Failed to update document tags: {str(e)}",
                "success": False
            }
        )


@app.post("/api/documents/{document_id}/tags/get")
async def get_document_tags(document_id: str, payload: GetDocumentTagsPayload):
    """
    Get tags for a specific document.
    
    Args:
        document_id: UUID of the document
        payload: GetDocumentTagsPayload containing credentials
        
    Returns:
        JSONResponse with document tags or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        # Verify document_id matches payload
        if payload.document_id != document_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Document ID in URL does not match payload",
                    "tags": []
                }
            )
        
        tags = await manager.weaviate_manager.get_document_tags(
            client=client,
            document_id=document_id
        )
        
        msg.info(f"Retrieved tags for document: {document_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "document_id": document_id,
                "tags": tags
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to get document tags: {str(e)}")
        status_code = 404 if "not found" in str(e).lower() else 500
        return JSONResponse(
            status_code=status_code,
            content={
                "error": f"Failed to get document tags: {str(e)}",
                "tags": []
            }
        )


@app.post("/api/tags")
async def get_all_tags(payload: GetAllTagsPayload):
    """
    Get all unique tags across all documents.
    
    Args:
        payload: GetAllTagsPayload containing credentials
        
    Returns:
        JSONResponse with list of all tags or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        tags = await manager.weaviate_manager.get_all_tags(client=client)
        
        msg.info(f"Retrieved {len(tags)} unique tags")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "tags": tags,
                "total_count": len(tags)
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to get all tags: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to get all tags: {str(e)}",
                "tags": [],
                "total_count": 0
            }
        )


@app.post("/api/documents/search_by_tags")
async def search_documents_by_tags(payload: SearchDocumentsByTagsPayload):
    """
    Search documents by tags.
    
    Args:
        payload: SearchDocumentsByTagsPayload containing search criteria
        
    Returns:
        JSONResponse with matching documents or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        documents, total_count = await manager.weaviate_manager.search_documents_by_tags(
            client=client,
            tags=payload.tags,
            match_all=payload.match_all,
            page=payload.page,
            pageSize=payload.pageSize,
            properties=["title", "extension", "fileSize", "labels", "source", "meta", "tags"]
        )
        
        msg.info(f"Found {len(documents)} documents matching tags: {payload.tags}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "documents": documents,
                "total_count": total_count,
                "page": payload.page,
                "pageSize": payload.pageSize,
                "tags": payload.tags,
                "match_all": payload.match_all
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to search documents by tags: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to search documents by tags: {str(e)}",
                "documents": [],
                "total_count": 0
            }
        )


### ADMIN


@app.post("/api/reset")
async def reset_verba(payload: ResetPayload):
    if production == "Demo":
        return JSONResponse(status_code=200, content={})

    try:
        client = await client_manager.connect(payload.credentials)
        if payload.resetMode == "ALL":
            await manager.weaviate_manager.delete_all(client)
        elif payload.resetMode == "DOCUMENTS":
            await manager.weaviate_manager.delete_all_documents(client)
        elif payload.resetMode == "CONFIG":
            await manager.weaviate_manager.delete_all_configs(client)
        elif payload.resetMode == "SUGGESTIONS":
            await manager.weaviate_manager.delete_all_suggestions(client)

        msg.info(f"Resetting Verba in ({payload.resetMode}) mode")

        return JSONResponse(status_code=200, content={})

    except Exception as e:
        msg.warn(f"Failed to reset Verba {str(e)}")
        return JSONResponse(status_code=500, content={})


# Get Status meta data
@app.post("/api/get_meta")
async def get_meta(payload: Credentials):
    try:
        client = await client_manager.connect(payload)
        node_payload, collection_payload = await manager.weaviate_manager.get_metadata(
            client
        )
        return JSONResponse(
            content={
                "error": "",
                "node_payload": node_payload,
                "collection_payload": collection_payload,
            }
        )
    except Exception as e:
        return JSONResponse(
            content={
                "error": f"Couldn't retrieve metadata {str(e)}",
                "node_payload": {},
                "collection_payload": {},
            }
        )


### Suggestions


@app.post("/api/get_suggestions")
async def get_suggestions(payload: GetSuggestionsPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        suggestions = await manager.weaviate_manager.retrieve_suggestions(
            client, payload.query, payload.limit
        )
        return JSONResponse(
            content={
                "suggestions": suggestions,
            }
        )
    except Exception:
        return JSONResponse(
            content={
                "suggestions": [],
            }
        )


@app.post("/api/get_all_suggestions")
async def get_all_suggestions(payload: GetAllSuggestionsPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        suggestions, total_count = (
            await manager.weaviate_manager.retrieve_all_suggestions(
                client, payload.page, payload.pageSize
            )
        )
        return JSONResponse(
            content={
                "suggestions": suggestions,
                "total_count": total_count,
            }
        )
    except Exception:
        return JSONResponse(
            content={
                "suggestions": [],
                "total_count": 0,
            }
        )


@app.post("/api/delete_suggestion")
async def delete_suggestion(payload: DeleteSuggestionPayload):
    try:
        client = await client_manager.connect(payload.credentials)
        await manager.weaviate_manager.delete_suggestions(client, payload.uuid)
        return JSONResponse(
            content={
                "status": 200,
            }
        )
    except Exception:
        return JSONResponse(
            content={
                "status": 400,
            }
        )


### WORK LOG MANAGEMENT ENDPOINTS


@app.post("/api/worklogs")
async def create_worklog(request: Request):
    """
    Create a new work log entry.
    
    Args:
        request: Request containing work log content and optional metadata
        
    Returns:
        JSONResponse with created work log entry or error
    """
    if production == "Demo":
        msg.warn("Can't create work logs when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Work log creation is disabled in Demo mode",
                "log": None
            }
        )
    
    try:
        # Parse request body
        body = await request.json()
        content = body.get("content", "")
        user_id = body.get("user_id", "default_user")
        extracted_skills = body.get("extracted_skills", [])
        metadata = body.get("metadata", {})
        credentials = body.get("credentials", {})
        
        if not content:
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Content is required",
                    "log": None
                }
            )
        
        # Get client
        if credentials:
            client = await client_manager.connect(Credentials(**credentials))
        else:
            client = await client_manager.get_client()
        
        # Create work log entry using WorkLogManager
        from goldenverba.components.worklog_manager import WorkLogManager
        worklog_manager = WorkLogManager()
        
        entry = await worklog_manager.create_log_entry(
            client=client,
            content=content,
            user_id=user_id,
            extracted_skills=extracted_skills,
            metadata=metadata
        )
        
        msg.good(f"Created work log entry: {entry.id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "error": "",
                "log": {
                    "id": entry.id,
                    "content": entry.content,
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": entry.user_id,
                    "extracted_skills": entry.extracted_skills,
                    "metadata": entry.metadata
                }
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to create work log entry: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to create work log entry: {str(e)}",
                "log": None
            }
        )


@app.get("/api/worklogs")
async def get_worklogs(
    user_id: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Retrieve work log entries with optional filtering.
    
    Args:
        user_id: Optional user ID filter
        start_date: Optional start date filter (ISO format)
        end_date: Optional end date filter (ISO format)
        limit: Maximum number of entries to return
        offset: Number of entries to skip
        
    Returns:
        JSONResponse with list of work log entries or error
    """
    try:
        # Use default credentials for GET request
        client = await client_manager.get_client()
        
        from goldenverba.components.worklog_manager import WorkLogManager
        from datetime import datetime
        
        worklog_manager = WorkLogManager()
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        entries = await worklog_manager.get_log_entries(
            client=client,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        
        # Get total count
        total_count = await worklog_manager.count_log_entries(
            client=client,
            user_id=user_id
        )
        
        logs = [
            {
                "id": entry.id,
                "content": entry.content,
                "timestamp": entry.timestamp.isoformat(),
                "user_id": entry.user_id,
                "extracted_skills": entry.extracted_skills,
                "metadata": entry.metadata
            }
            for entry in entries
        ]
        
        msg.info(f"Retrieved {len(logs)} work log entries")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "logs": logs,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve work log entries: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve work log entries: {str(e)}",
                "logs": [],
                "total_count": 0
            }
        )


@app.put("/api/worklogs/{log_id}")
async def update_worklog(log_id: str, payload: UpdateWorkLogPayload):
    """
    Update an existing work log entry.
    
    Args:
        log_id: UUID of the work log entry to update
        payload: UpdateWorkLogPayload containing updated fields
        
    Returns:
        JSONResponse with updated work log entry or error
    """
    if production == "Demo":
        msg.warn("Can't update work logs when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Work log updates are disabled in Demo mode",
                "worklog": None
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.worklog_manager import WorkLogManager
        worklog_manager = WorkLogManager()
        
        # Verify log_id matches payload
        if payload.log_id != log_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Log ID in URL does not match payload",
                    "worklog": None
                }
            )
        
        entry = await worklog_manager.update_log_entry(
            client=client,
            log_id=log_id,
            content=payload.content,
            extracted_skills=payload.extracted_skills,
            metadata=payload.metadata
        )
        
        msg.good(f"Updated work log entry: {entry.id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "worklog": {
                    "id": entry.id,
                    "content": entry.content,
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": entry.user_id,
                    "extracted_skills": entry.extracted_skills,
                    "metadata": entry.metadata
                }
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to update work log entry: {str(e)}")
        status_code = 404 if "not found" in str(e).lower() else 500
        return JSONResponse(
            status_code=status_code,
            content={
                "error": f"Failed to update work log entry: {str(e)}",
                "worklog": None
            }
        )


@app.delete("/api/worklogs/{log_id}")
async def delete_worklog(log_id: str, payload: DeleteWorkLogPayload):
    """
    Delete a work log entry.
    
    Args:
        log_id: UUID of the work log entry to delete
        payload: DeleteWorkLogPayload containing credentials
        
    Returns:
        JSONResponse with success status or error
    """
    if production == "Demo":
        msg.warn("Can't delete work logs when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Work log deletion is disabled in Demo mode",
                "deleted": False
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.worklog_manager import WorkLogManager
        worklog_manager = WorkLogManager()
        
        # Verify log_id matches payload
        if payload.log_id != log_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Log ID in URL does not match payload",
                    "deleted": False
                }
            )
        
        success = await worklog_manager.delete_log_entry(
            client=client,
            log_id=log_id
        )
        
        msg.good(f"Deleted work log entry: {log_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "deleted": success,
                "log_id": log_id
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to delete work log entry: {str(e)}")
        status_code = 404 if "not found" in str(e).lower() else 500
        return JSONResponse(
            status_code=status_code,
            content={
                "error": f"Failed to delete work log entry: {str(e)}",
                "deleted": False
            }
        )


@app.post("/api/worklogs/{log_id}")
async def get_worklog_by_id(log_id: str, payload: GetWorkLogByIdPayload):
    """
    Retrieve a specific work log entry by ID.
    
    Args:
        log_id: UUID of the work log entry
        payload: GetWorkLogByIdPayload containing credentials
        
    Returns:
        JSONResponse with work log entry or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.worklog_manager import WorkLogManager
        worklog_manager = WorkLogManager()
        
        # Verify log_id matches payload
        if payload.log_id != log_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Log ID in URL does not match payload",
                    "worklog": None
                }
            )
        
        entry = await worklog_manager.get_log_entry_by_id(
            client=client,
            log_id=log_id
        )
        
        if entry is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Work log entry not found: {log_id}",
                    "worklog": None
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "worklog": {
                    "id": entry.id,
                    "content": entry.content,
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": entry.user_id,
                    "extracted_skills": entry.extracted_skills,
                    "metadata": entry.metadata
                }
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve work log entry: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve work log entry: {str(e)}",
                "worklog": None
            }
        )



### SKILLS ANALYSIS ENDPOINTS


@app.post("/api/skills")
async def get_skills(request: Request):
    """
    Retrieve skills breakdown with optional filtering.
    
    Args:
        request: Request containing optional filter criteria and credentials
        
    Returns:
        JSONResponse with skills breakdown or error
    """
    try:
        # Parse request body
        body = await request.json() if request.headers.get("content-length") else {}
        credentials = body.get("credentials", {})
        start_date = body.get("start_date")
        end_date = body.get("end_date")
        category = body.get("category")
        
        # Get client
        if credentials:
            client = await client_manager.connect(Credentials(**credentials))
        else:
            client = await client_manager.get_client()
        
        from goldenverba.components.skills_extractor import SkillsExtractor
        from datetime import datetime, timezone
        
        skills_extractor = SkillsExtractor()
        
        # Parse dates if provided and ensure they're timezone-aware
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            if start_dt.tzinfo is None:
                # Add UTC timezone if naive datetime
                start_dt = start_dt.replace(tzinfo=timezone.utc)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            if end_dt.tzinfo is None:
                # Add UTC timezone if naive datetime
                end_dt = end_dt.replace(tzinfo=timezone.utc)
        
        # Generate skills report with filters
        report = await skills_extractor.aggregate_skills(
            client=client,
            start_date=start_dt,
            end_date=end_dt,
            category_filter=category
        )
        
        msg.info(f"Retrieved skills breakdown with {report.total_skills} total skills")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "skills_by_category": report.to_dict()["skills_by_category"],
                "total_skills": report.total_skills,
                "top_skills": report.to_dict()["top_skills"],
                "recent_skills": report.to_dict()["recent_skills"],
                "generated_at": report.generated_at.isoformat()
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve skills breakdown: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve skills breakdown: {str(e)}",
                "skills_by_category": {},
                "total_skills": 0,
                "top_skills": [],
                "recent_skills": [],
                "generated_at": datetime.now().isoformat()
            }
        )


@app.post("/api/skills/categories")
async def get_skill_categories(payload: GetSkillCategoriesPayload):
    """
    Retrieve list of skill categories.
    
    Args:
        payload: GetSkillCategoriesPayload containing credentials
        
    Returns:
        JSONResponse with skill categories or error
    """
    try:
        # No need to connect to client for static categories
        from goldenverba.components.skills_extractor import SKILL_CATEGORIES
        
        # Format categories with their example skills
        categories = [
            {
                "name": category,
                "display_name": category.replace("_", " ").title(),
                "example_skills": skills[:5]  # First 5 skills as examples
            }
            for category, skills in SKILL_CATEGORIES.items()
        ]
        
        msg.info(f"Retrieved {len(categories)} skill categories")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "categories": categories,
                "total_categories": len(categories)
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve skill categories: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve skill categories: {str(e)}",
                "categories": [],
                "total_categories": 0
            }
        )


@app.post("/api/skills/extract")
async def extract_skills(payload: ExtractSkillsPayload):
    """
    Extract skills from provided text on-demand.
    
    Args:
        payload: ExtractSkillsPayload containing text and credentials
        
    Returns:
        JSONResponse with extracted skills or error
    """
    if production == "Demo":
        msg.warn("Can't extract skills when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Skill extraction is disabled in Demo mode",
                "skills": [],
                "categorized_skills": {}
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.skills_extractor import SkillsExtractor
        
        skills_extractor = SkillsExtractor()
        
        # Get RAG config for generator settings
        rag_config = await manager.load_rag_config(client)
        generator_config = rag_config.get("Generator", {})
        
        # Extract skills from text
        extracted_skills = await skills_extractor.extract_skills(
            client=client,
            text=payload.text,
            generator_config=generator_config,
            use_cache=payload.use_cache
        )
        
        # Categorize the extracted skills
        categorized_skills = skills_extractor.categorize_skills(extracted_skills)
        
        msg.good(f"Extracted {len(extracted_skills)} skills from text")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "skills": extracted_skills,
                "categorized_skills": categorized_skills,
                "total_skills": len(extracted_skills)
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to extract skills: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to extract skills: {str(e)}",
                "skills": [],
                "categorized_skills": {},
                "total_skills": 0
            }
        )



@app.post("/api/skills/extract-from-documents")
async def extract_skills_from_documents(request: Request):
    """
    Extract skills from all existing documents in the database.
    
    This is a utility endpoint to process documents that were uploaded
    before skill extraction was implemented.
    
    Args:
        request: Request containing optional credentials and limit
        
    Returns:
        JSONResponse with extraction results or error
    """
    if production == "Demo":
        msg.warn("Can't extract skills when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Skill extraction is disabled in Demo mode",
                "success": False
            }
        )
    
    try:
        # Parse request body
        body = await request.json() if request.headers.get("content-length") else {}
        credentials = body.get("credentials", {})
        limit = body.get("limit", 100)
        
        # Get client
        if credentials:
            client = await client_manager.connect(Credentials(**credentials))
        else:
            client = await client_manager.get_client()
        
        # Get RAG config for generator settings
        rag_config = await manager.load_rag_config(client)
        generator_config = rag_config.get("Generator", {})
        
        msg.info(f"Starting bulk skill extraction from up to {limit} documents")
        
        # Extract skills from all documents
        result = await manager.extract_skills_from_all_documents(
            client=client,
            generator_config=generator_config,
            limit=limit
        )
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "error": "",
                    **result
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": result.get("message", "Extraction failed"),
                    **result
                }
            )
        
    except Exception as e:
        msg.fail(f"Failed to extract skills from documents: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to extract skills from documents: {str(e)}",
                "success": False,
                "documents_processed": 0,
                "skills_extracted": 0
            }
        )


### RESUME GENERATION AND TRACKING ENDPOINTS


@app.post("/api/resumes/generate")
async def generate_resume(payload: GenerateResumePayload):
    """
    Generate a new resume from a job description.
    
    This endpoint uses the ResumeGenerator to:
    1. Extract job requirements from the description
    2. Retrieve relevant work log entries
    3. Generate a tailored resume using LLM
    4. Store the resume with tracking information
    
    Args:
        payload: GenerateResumePayload containing job description and options
        
    Returns:
        JSONResponse with generated resume or error
    """
    if production == "Demo":
        msg.warn("Can't generate resumes when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Resume generation is disabled in Demo mode",
                "resume": None
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.resume_generator import ResumeOptions
        
        # Use manager's instances
        resume_generator = manager.resume_generator
        resume_tracker = manager.resume_tracker
        
        # Get RAG config for generator and embedder settings
        rag_config = await manager.load_rag_config(client)
        generator_config = rag_config.get("Generator", {})
        embedder_config = rag_config.get("Embedder", {})
        
        # Get generator and embedder instances
        generator = manager.generator_manager.get_generator()
        embedder = manager.embedder_manager.get_embedder()
        
        msg.info(f"Generating resume for role: {payload.target_role or 'unspecified'}")
        
        # Step 1: Extract job requirements
        requirements = await resume_generator.extract_job_requirements(
            job_description=payload.job_description,
            generator=generator,
            generator_config=generator_config
        )
        
        # Step 2: Retrieve relevant experiences using hybrid search
        experiences = await resume_generator.retrieve_relevant_experiences(
            client=client,
            requirements=requirements,
            embedder=embedder,
            embedder_config=embedder_config,
            limit=payload.limit,
            alpha=payload.alpha,
            date_range_days=payload.date_range_days,
            boost_recent=payload.boost_recent
        )
        
        # Step 3: Generate resume
        options = ResumeOptions(
            format=payload.format,
            sections=payload.sections,
            max_length=payload.max_length,
            tone=payload.tone
        )
        
        resume = await resume_generator.generate_resume(
            job_description=payload.job_description,
            experiences=experiences,
            requirements=requirements,
            generator=generator,
            generator_config=generator_config,
            options=options,
            session_id=payload.session_id,
            user_feedback=payload.user_feedback
        )
        
        # Extract source log IDs from experiences
        source_log_ids = [exp.get("id") for exp in experiences if exp.get("source") == resume_generator.worklog_collection]
        
        # Step 4: Save the resume record for tracking
        resume_record = await resume_tracker.save_resume_record(
            client=client,
            resume_content=resume.content,
            job_description=payload.job_description,
            target_role=payload.target_role or "Unspecified",
            format=payload.format,
            source_log_ids=source_log_ids,
            metadata={
                "user_id": payload.user_id,
                "experience_count": len(experiences),
                "requirements": requirements.to_dict()
            }
        )
        
        msg.good(f"Successfully generated resume: {resume_record.id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "error": "",
                "resume": {
                    "id": resume_record.id,
                    "content": resume_record.resume_content,
                    "job_description": resume_record.job_description,
                    "target_role": resume_record.target_role,
                    "format": resume_record.format,
                    "generated_at": resume_record.generated_at.isoformat(),
                    "source_log_ids": resume_record.source_log_ids,
                    "metadata": resume_record.metadata
                }
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to generate resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to generate resume: {str(e)}",
                "resume": None
            }
        )


@app.post("/api/resumes")
async def get_resumes(payload: GetResumesPayload):
    """
    Retrieve resume history with optional filtering.
    
    Args:
        payload: GetResumesPayload containing filter criteria
        
    Returns:
        JSONResponse with list of resume records or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.resume_tracker import ResumeTracker
        from datetime import datetime
        
        resume_tracker = ResumeTracker()
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(payload.start_date) if payload.start_date else None
        end_dt = datetime.fromisoformat(payload.end_date) if payload.end_date else None
        
        # Get resume history with filters
        records = await resume_tracker.get_resume_history(
            client=client,
            target_role=payload.target_role,
            start_date=start_dt,
            end_date=end_dt,
            format=None,
            limit=payload.limit,
            offset=payload.offset
        )
        
        # Get total count
        total_count = await resume_tracker.count_resume_records(
            client=client,
            target_role=payload.target_role
        )
        
        resumes = [
            {
                "id": record.id,
                "content": record.resume_content,
                "job_description": record.job_description,
                "target_role": record.target_role,
                "format": record.format,
                "generated_at": record.generated_at.isoformat(),
                "source_log_ids": record.source_log_ids,
                "metadata": record.metadata
            }
            for record in records
        ]
        
        msg.info(f"Retrieved {len(resumes)} resume records")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "resumes": resumes,
                "total_count": total_count,
                "limit": payload.limit,
                "offset": payload.offset
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve resume history: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve resume history: {str(e)}",
                "resumes": [],
                "total_count": 0
            }
        )


@app.post("/api/resumes/{resume_id}")
async def get_resume_by_id(resume_id: str, payload: GetResumeByIdPayload):
    """
    Retrieve a specific resume by ID.
    
    Args:
        resume_id: UUID of the resume record
        payload: GetResumeByIdPayload containing credentials
        
    Returns:
        JSONResponse with resume record or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.resume_tracker import ResumeTracker
        
        resume_tracker = ResumeTracker()
        
        # Verify resume_id matches payload
        if payload.resume_id != resume_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Resume ID in URL does not match payload",
                    "resume": None
                }
            )
        
        record = await resume_tracker.get_resume_by_id(
            client=client,
            resume_id=resume_id
        )
        
        if record is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Resume not found: {resume_id}",
                    "resume": None
                }
            )
        
        msg.info(f"Retrieved resume: {resume_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "resume": {
                    "id": record.id,
                    "content": record.resume_content,
                    "job_description": record.job_description,
                    "target_role": record.target_role,
                    "format": record.format,
                    "generated_at": record.generated_at.isoformat(),
                    "source_log_ids": record.source_log_ids,
                    "metadata": record.metadata
                }
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve resume: {str(e)}",
                "resume": None
            }
        )


@app.post("/api/resumes/{resume_id}/regenerate")
async def regenerate_resume(resume_id: str, payload: RegenerateResumePayload):
    """
    Regenerate a resume using the same job description with updated work log data.
    
    Args:
        resume_id: UUID of the resume to regenerate
        payload: RegenerateResumePayload containing credentials and options
        
    Returns:
        JSONResponse with regenerated resume or error
    """
    if production == "Demo":
        msg.warn("Can't regenerate resumes when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Resume regeneration is disabled in Demo mode",
                "resume": None
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.resume_generator import ResumeGenerator, ResumeOptions
        from goldenverba.components.resume_tracker import ResumeTracker
        
        resume_generator = ResumeGenerator()
        resume_tracker = ResumeTracker()
        
        # Verify resume_id matches payload
        if payload.resume_id != resume_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Resume ID in URL does not match payload",
                    "resume": None
                }
            )
        
        # Get the original resume record
        original_record = await resume_tracker.get_resume_by_id(
            client=client,
            resume_id=resume_id
        )
        
        if original_record is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Resume not found: {resume_id}",
                    "resume": None
                }
            )
        
        # Get RAG config for generator and embedder settings
        rag_config = await manager.load_rag_config(client)
        generator_config = rag_config.get("Generator", {})
        embedder_config = rag_config.get("Embedder", {})
        
        # Get generator and embedder instances
        generator = manager.generator_manager.get_generator()
        embedder = manager.embedder_manager.get_embedder()
        
        msg.info(f"Regenerating resume: {resume_id}")
        
        # Step 1: Extract job requirements
        requirements = await resume_generator.extract_job_requirements(
            job_description=original_record.job_description,
            generator=generator,
            generator_config=generator_config
        )
        
        # Step 2: Retrieve relevant experiences (with updated data) using hybrid search
        experiences = await resume_generator.retrieve_relevant_experiences(
            client=client,
            requirements=requirements,
            embedder=embedder,
            embedder_config=embedder_config,
            limit=payload.limit,
            alpha=payload.alpha,
            date_range_days=payload.date_range_days,
            boost_recent=payload.boost_recent
        )
        
        # Step 3: Generate resume
        options = ResumeOptions(
            format=original_record.format,
            sections=None,  # Use defaults
            max_length=2000,
            tone="professional"
        )
        
        resume = await resume_generator.generate_resume(
            job_description=original_record.job_description,
            experiences=experiences,
            requirements=requirements,
            generator=generator,
            generator_config=generator_config,
            options=options
        )
        
        # Extract source log IDs from experiences
        source_log_ids = [exp.get("id") for exp in experiences if exp.get("source") == resume_generator.worklog_collection]
        
        # Save the new resume record
        new_record = await resume_tracker.save_resume_record(
            client=client,
            resume_content=resume.content,
            job_description=original_record.job_description,
            target_role=original_record.target_role,
            format=original_record.format,
            source_log_ids=source_log_ids,
            metadata={
                "user_id": original_record.metadata.get("user_id") if original_record.metadata else None,
                "regenerated_from": resume_id,
                "experience_count": len(experiences),
                "requirements": requirements.to_dict()
            }
        )
        
        msg.good(f"Successfully regenerated resume: {new_record.id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "error": "",
                "resume": {
                    "id": new_record.id,
                    "content": new_record.resume_content,
                    "job_description": new_record.job_description,
                    "target_role": new_record.target_role,
                    "format": new_record.format,
                    "generated_at": new_record.generated_at.isoformat(),
                    "source_log_ids": new_record.source_log_ids,
                    "metadata": new_record.metadata
                },
                "original_resume_id": resume_id
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to regenerate resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to regenerate resume: {str(e)}",
                "resume": None
            }
        )


@app.delete("/api/resumes/{resume_id}")
async def delete_resume(resume_id: str, payload: DeleteResumePayload):
    """
    Delete a resume record from history.
    
    Args:
        resume_id: UUID of the resume to delete
        payload: DeleteResumePayload containing credentials
        
    Returns:
        JSONResponse with success status or error
    """
    if production == "Demo":
        msg.warn("Can't delete resumes when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Resume deletion is disabled in Demo mode",
                "deleted": False
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.resume_tracker import ResumeTracker
        
        resume_tracker = ResumeTracker()
        
        # Verify resume_id matches payload
        if payload.resume_id != resume_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Resume ID in URL does not match payload",
                    "deleted": False
                }
            )
        
        success = await resume_tracker.delete_resume_record(
            client=client,
            resume_id=resume_id
        )
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Resume not found: {resume_id}",
                    "deleted": False
                }
            )
        
        msg.good(f"Deleted resume: {resume_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "deleted": True,
                "resume_id": resume_id
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to delete resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to delete resume: {str(e)}",
                "deleted": False
            }
        )


@app.post("/api/resumes/{resume_id}/export")
async def export_resume(resume_id: str, payload: ExportResumePayload):
    """
    Export a resume in the specified format (PDF, DOCX, or Markdown).
    
    Args:
        resume_id: UUID of the resume to export
        payload: ExportResumePayload containing format and credentials
        
    Returns:
        FileResponse with the exported resume file or JSONResponse with error
    """
    if production == "Demo":
        msg.warn("Can't export resumes when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Resume export is disabled in Demo mode"
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.resume_tracker import ResumeTracker
        from goldenverba.components.resume_generator import ResumeGenerator, Resume
        import tempfile
        
        resume_tracker = ResumeTracker()
        resume_generator = ResumeGenerator()
        
        # Verify resume_id matches payload
        if payload.resume_id != resume_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Resume ID in URL does not match payload"
                }
            )
        
        # Get the resume record
        record = await resume_tracker.get_resume_by_id(
            client=client,
            resume_id=resume_id
        )
        
        if record is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Resume not found: {resume_id}"
                }
            )
        
        msg.info(f"Exporting resume {resume_id} as {payload.format}")
        
        # Create Resume object from record
        resume = Resume(
            content=record.resume_content,
            format=record.format,
            generated_at=record.generated_at,
            resume_id=record.id,
            metadata={
                "target_role": record.target_role,
                "job_description": record.job_description
            }
        )
        
        # Format the resume content
        file_bytes = resume_generator.format_resume(
            resume=resume,
            target_format=payload.format,
            title=f"Resume - {record.target_role}",
            author=payload.author
        )
        
        # Determine file extension and media type
        if payload.format == "pdf":
            extension = "pdf"
            media_type = "application/pdf"
        elif payload.format == "docx":
            extension = "docx"
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:  # markdown
            extension = "md"
            media_type = "text/markdown"
        
        # Create a temporary file to store the export
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name
        
        # Generate filename
        safe_role = record.target_role.replace(" ", "_").replace("/", "-")
        filename = f"resume_{safe_role}_{resume_id[:8]}.{extension}"
        
        msg.good(f"Successfully exported resume as {filename}")
        
        return FileResponse(
            path=tmp_file_path,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except NotImplementedError as e:
        msg.warn(f"Export format not yet implemented: {str(e)}")
        return JSONResponse(
            status_code=501,
            content={
                "error": f"Export format not yet implemented: {str(e)}"
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to export resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to export resume: {str(e)}"
            }
        )


# Conversation Session Management Endpoints

@app.post("/api/conversations/sessions")
async def create_conversation_session(payload: CreateConversationSessionPayload):
    """
    Create a new conversation session for resume generation.
    
    Args:
        payload: CreateConversationSessionPayload with optional session_id and metadata
        
    Returns:
        JSONResponse with session_id or error
    """
    try:
        # No need to connect to Weaviate for session creation
        # Sessions are managed in-memory by the ResumeGenerator
        
        # Use the manager's resume_generator instance
        session_id = manager.resume_generator.create_conversation_session(
            session_id=payload.session_id,
            metadata=payload.metadata
        )
        
        msg.good(f"Created conversation session: {session_id}")
        
        return JSONResponse(
            status_code=201,
            content={
                "error": "",
                "session_id": session_id,
                "metadata": payload.metadata or {}
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to create conversation session: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to create conversation session: {str(e)}",
                "session_id": None
            }
        )


@app.post("/api/conversations/sessions/{session_id}/history")
async def get_conversation_history(session_id: str, payload: GetConversationHistoryPayload):
    """
    Get conversation history for a session.
    
    Args:
        session_id: The session ID
        payload: GetConversationHistoryPayload with format preference
        
    Returns:
        JSONResponse with conversation history or error
    """
    try:
        # Verify session_id matches payload
        if payload.session_id != session_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Session ID in URL does not match payload",
                    "history": []
                }
            )
        
        # Get session info
        session_info = manager.resume_generator.get_session_info(session_id)
        
        if session_info is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Session not found: {session_id}",
                    "history": []
                }
            )
        
        # Get conversation history
        history = manager.resume_generator.get_conversation_history(
            session_id=session_id,
            format=payload.format
        )
        
        msg.info(f"Retrieved conversation history for session {session_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "session_id": session_id,
                "history": history,
                "session_info": session_info
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to get conversation history: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to get conversation history: {str(e)}",
                "history": []
            }
        )


@app.post("/api/conversations/sessions/{session_id}/reset")
async def reset_conversation_session(session_id: str, payload: ResetConversationSessionPayload):
    """
    Reset (clear) a conversation session.
    
    Args:
        session_id: The session ID to reset
        payload: ResetConversationSessionPayload with credentials
        
    Returns:
        JSONResponse with success status or error
    """
    try:
        # Verify session_id matches payload
        if payload.session_id != session_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Session ID in URL does not match payload",
                    "success": False
                }
            )
        
        # Reset the session
        success = manager.resume_generator.reset_conversation_context(session_id)
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Session not found: {session_id}",
                    "success": False
                }
            )
        
        msg.good(f"Reset conversation session: {session_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "session_id": session_id,
                "success": True
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to reset conversation session: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to reset conversation session: {str(e)}",
                "success": False
            }
        )


@app.delete("/api/conversations/sessions/{session_id}")
async def delete_conversation_session(session_id: str, payload: DeleteConversationSessionPayload):
    """
    Delete a conversation session.
    
    Args:
        session_id: The session ID to delete
        payload: DeleteConversationSessionPayload with credentials
        
    Returns:
        JSONResponse with success status or error
    """
    try:
        # Verify session_id matches payload
        if payload.session_id != session_id:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Session ID in URL does not match payload",
                    "success": False
                }
            )
        
        # Delete the session
        success = manager.resume_generator.delete_conversation_session(session_id)
        
        if not success:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"Session not found: {session_id}",
                    "success": False
                }
            )
        
        msg.good(f"Deleted conversation session: {session_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "session_id": session_id,
                "success": True
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to delete conversation session: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to delete conversation session: {str(e)}",
                "success": False
            }
        )
