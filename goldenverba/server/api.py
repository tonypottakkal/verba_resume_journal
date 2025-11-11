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
    if origin == str(request.base_url).rstrip("/") or (
        origin
        and origin.startswith("http://localhost:")
        and request.base_url.hostname == "localhost"
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
                        "request_headers": dict(request.headers),
                        "expected_header": "Origin header matching the server's base URL or localhost",
                    },
                },
            )

        # Allow non-API routes to pass through
        return await call_next(request)


BASE_DIR = Path(__file__).resolve().parent

# Serve the assets (JS, CSS, images, etc.)
app.mount(
    "/static/_next",
    StaticFiles(directory=BASE_DIR / "frontend/out/_next"),
    name="next-assets",
)

# Serve the main page and other static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend/out"), name="app")


@app.get("/")
@app.head("/")
async def serve_frontend():
    return FileResponse(os.path.join(BASE_DIR, "frontend/out/index.html"))


### INITIAL ENDPOINTS


# Define health check endpoint
@app.get("/api/health")
async def health_check():

    await client_manager.clean_up()

    if production == "Local":
        deployments = await manager.get_deployments()
    else:
        deployments = {"WEAVIATE_URL_VERBA": "", "WEAVIATE_API_KEY_VERBA": ""}

    return JSONResponse(
        content={
            "message": "Alive!",
            "production": production,
            "gtag": tag,
            "deployments": deployments,
            "default_deployment": os.getenv("DEFAULT_DEPLOYMENT", ""),
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
async def create_worklog(payload: CreateWorkLogPayload):
    """
    Create a new work log entry.
    
    Args:
        payload: CreateWorkLogPayload containing work log content and metadata
        
    Returns:
        JSONResponse with created work log entry or error
    """
    if production == "Demo":
        msg.warn("Can't create work logs when in Production Mode")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Work log creation is disabled in Demo mode",
                "worklog": None
            }
        )
    
    try:
        client = await client_manager.connect(payload.credentials)
        
        # Create work log entry using WorkLogManager
        from goldenverba.components.worklog_manager import WorkLogManager
        worklog_manager = WorkLogManager()
        
        entry = await worklog_manager.create_log_entry(
            client=client,
            content=payload.content,
            user_id=payload.user_id,
            extracted_skills=payload.extracted_skills,
            metadata=payload.metadata
        )
        
        msg.good(f"Created work log entry: {entry.id}")
        
        return JSONResponse(
            status_code=201,
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
        msg.fail(f"Failed to create work log entry: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to create work log entry: {str(e)}",
                "worklog": None
            }
        )


@app.post("/api/get_worklogs")
async def get_worklogs(payload: GetWorkLogsPayload):
    """
    Retrieve work log entries with optional filtering.
    
    Args:
        payload: GetWorkLogsPayload containing filter criteria and credentials
        
    Returns:
        JSONResponse with list of work log entries or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.worklog_manager import WorkLogManager
        from datetime import datetime
        
        worklog_manager = WorkLogManager()
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(payload.start_date) if payload.start_date else None
        end_dt = datetime.fromisoformat(payload.end_date) if payload.end_date else None
        
        entries = await worklog_manager.get_log_entries(
            client=client,
            user_id=payload.user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=payload.limit,
            offset=payload.offset
        )
        
        # Get total count
        total_count = await worklog_manager.count_log_entries(
            client=client,
            user_id=payload.user_id
        )
        
        worklogs = [
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
        
        msg.info(f"Retrieved {len(worklogs)} work log entries")
        
        return JSONResponse(
            status_code=200,
            content={
                "error": "",
                "worklogs": worklogs,
                "total_count": total_count,
                "limit": payload.limit,
                "offset": payload.offset
            }
        )
        
    except Exception as e:
        msg.fail(f"Failed to retrieve work log entries: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to retrieve work log entries: {str(e)}",
                "worklogs": [],
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
async def get_skills(payload: GetSkillsPayload):
    """
    Retrieve skills breakdown with optional filtering.
    
    Args:
        payload: GetSkillsPayload containing filter criteria and credentials
        
    Returns:
        JSONResponse with skills breakdown or error
    """
    try:
        client = await client_manager.connect(payload.credentials)
        
        from goldenverba.components.skills_extractor import SkillsExtractor
        from datetime import datetime
        
        skills_extractor = SkillsExtractor()
        
        # Parse dates if provided
        start_dt = datetime.fromisoformat(payload.start_date) if payload.start_date else None
        end_dt = datetime.fromisoformat(payload.end_date) if payload.end_date else None
        
        # Generate skills report with filters
        report = await skills_extractor.aggregate_skills(
            client=client,
            start_date=start_dt,
            end_date=end_dt,
            category_filter=payload.category
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
