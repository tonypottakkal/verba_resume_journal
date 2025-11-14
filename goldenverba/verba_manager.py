import os
import importlib
import math
import json
from datetime import datetime

from dotenv import load_dotenv
from wasabi import msg
import asyncio

from copy import deepcopy
import hashlib

from goldenverba.server.helpers import LoggerManager
from weaviate.client import WeaviateAsyncClient

from goldenverba.components.document import Document
from goldenverba.server.types import (
    FileConfig,
    FileStatus,
    ChunkScore,
    Credentials,
)

from goldenverba.components.managers import (
    ReaderManager,
    ChunkerManager,
    EmbeddingManager,
    RetrieverManager,
    GeneratorManager,
    WeaviateManager,
)
from goldenverba.components.schema_extensions import SchemaExtensions
from goldenverba.components.worklog_manager import WorkLogManager
from goldenverba.components.skills_extractor import SkillsExtractor
from goldenverba.components.resume_generator import ResumeGenerator
from goldenverba.components.resume_tracker import ResumeTracker

load_dotenv()


class VerbaManager:
    """Manages all Verba Components."""

    def __init__(self) -> None:
        self.reader_manager = ReaderManager()
        self.chunker_manager = ChunkerManager()
        self.embedder_manager = EmbeddingManager()
        self.retriever_manager = RetrieverManager()
        self.generator_manager = GeneratorManager()
        self.weaviate_manager = WeaviateManager()
        self.schema_extensions = SchemaExtensions()
        
        # Initialize new resume-specific managers
        self.worklog_manager = WorkLogManager()
        self.skills_extractor = SkillsExtractor()
        self.resume_generator = ResumeGenerator()
        self.resume_tracker = ResumeTracker()
        
        self.rag_config_uuid = "e0adcc12-9bad-4588-8a1e-bab0af6ed485"
        self.theme_config_uuid = "baab38a7-cb51-4108-acd8-6edeca222820"
        self.user_config_uuid = "f53f7738-08be-4d5a-b003-13eb4bf03ac7"
        self.resume_config_uuid = "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6"
        self.environment_variables = {}
        self.installed_libraries = {}

        self.verify_installed_libraries()
        self.verify_variables()

    async def connect(self, credentials: Credentials, port: str = "8080"):
        start_time = asyncio.get_event_loop().time()
        try:
            client = await self.weaviate_manager.connect(
                credentials.deployment, credentials.url, credentials.key, port
            )
        except Exception as e:
            raise e
        if client:
            initialized = await self.weaviate_manager.verify_collection(
                client, self.weaviate_manager.config_collection_name
            )
            if initialized:
                # Initialize resume-specific collections
                await self.schema_extensions.initialize_all_collections(client)
                end_time = asyncio.get_event_loop().time()
                msg.info(f"Connection time: {end_time - start_time:.2f} seconds")
                return client

    async def disconnect(self, client):
        start_time = asyncio.get_event_loop().time()
        result = await self.weaviate_manager.disconnect(client)
        end_time = asyncio.get_event_loop().time()
        msg.info(f"Disconnection time: {end_time - start_time:.2f} seconds")
        return result

    async def get_deployments(self):
        deployments = {
            "WEAVIATE_URL_VERBA": (
                os.getenv("WEAVIATE_URL_VERBA")
                if os.getenv("WEAVIATE_URL_VERBA")
                else ""
            ),
            "WEAVIATE_API_KEY_VERBA": (
                os.getenv("WEAVIATE_API_KEY_VERBA")
                if os.getenv("WEAVIATE_API_KEY_VERBA")
                else ""
            ),
        }
        return deployments

    # Import

    async def import_document(
        self, client, fileConfig: FileConfig, logger: LoggerManager = LoggerManager()
    ):
        try:
            loop = asyncio.get_running_loop()
            start_time = loop.time()

            duplicate_uuid = await self.weaviate_manager.exist_document_name(
                client, fileConfig.filename
            )
            if duplicate_uuid is not None and not fileConfig.overwrite:
                raise Exception(f"{fileConfig.filename} already exists in Verba")
            elif duplicate_uuid is not None and fileConfig.overwrite:
                await self.weaviate_manager.delete_document(client, duplicate_uuid)
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.STARTING,
                    message=f"Overwriting {fileConfig.filename}",
                    took=0,
                )
            else:
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.STARTING,
                    message="Starting Import",
                    took=0,
                )

            documents = await self.reader_manager.load(
                fileConfig.rag_config["Reader"].selected, fileConfig, logger
            )

            tasks = [
                self.process_single_document(client, doc, fileConfig, logger)
                for doc in documents
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_tasks = sum(
                1 for result in results if not isinstance(result, Exception)
            )

            if successful_tasks > 1:
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.INGESTING,
                    message=f"Imported {fileConfig.filename} and it's {successful_tasks} documents into Weaviate",
                    took=round(loop.time() - start_time, 2),
                )
            elif successful_tasks == 1:
                await logger.send_report(
                    fileConfig.fileID,
                    status=FileStatus.INGESTING,
                    message=f"Imported {fileConfig.filename} and {len(documents[0].chunks)} chunks into Weaviate",
                    took=round(loop.time() - start_time, 2),
                )
            elif (
                successful_tasks == 0
                and len(results) == 1
                and isinstance(results[0], Exception)
            ):
                msg.fail(
                    f"No documents imported {successful_tasks} of {len(results)} succesful tasks"
                )
                raise results[0]
            else:
                raise Exception(
                    f"No documents imported {successful_tasks} of {len(results)} succesful tasks"
                )

            await logger.send_report(
                fileConfig.fileID,
                status=FileStatus.DONE,
                message=f"Import for {fileConfig.filename} completed successfully",
                took=round(loop.time() - start_time, 2),
            )

        except Exception as e:
            await logger.send_report(
                fileConfig.fileID,
                status=FileStatus.ERROR,
                message=f"Import for {fileConfig.filename} failed: {str(e)}",
                took=0,
            )
            return

    async def process_single_document(
        self,
        client,
        document: Document,
        fileConfig: FileConfig,
        logger: LoggerManager,
    ):
        loop = asyncio.get_running_loop()
        start_time = loop.time()

        if fileConfig.isURL:
            currentFileConfig = deepcopy(fileConfig)
            currentFileConfig.fileID = fileConfig.fileID + document.title
            currentFileConfig.isURL = False
            currentFileConfig.filename = document.title
            await logger.create_new_document(
                fileConfig.fileID + document.title,
                document.title,
                fileConfig.fileID,
            )
        else:
            currentFileConfig = fileConfig

        try:
            duplicate_uuid = await self.weaviate_manager.exist_document_name(
                client, document.title
            )
            if duplicate_uuid is not None and not currentFileConfig.overwrite:
                raise Exception(f"{document.title} already exists in Verba")
            elif duplicate_uuid is not None and currentFileConfig.overwrite:
                await self.weaviate_manager.delete_document(client, duplicate_uuid)

            chunk_task = asyncio.create_task(
                self.chunker_manager.chunk(
                    currentFileConfig.rag_config["Chunker"].selected,
                    currentFileConfig,
                    [document],
                    self.embedder_manager.embedders[
                        currentFileConfig.rag_config["Embedder"].selected
                    ],
                    logger,
                )
            )
            chunked_documents = await chunk_task

            embedding_task = asyncio.create_task(
                self.embedder_manager.vectorize(
                    currentFileConfig.rag_config["Embedder"].selected,
                    currentFileConfig,
                    chunked_documents,
                    logger,
                )
            )
            vectorized_documents = await embedding_task

            for document in vectorized_documents:
                ingesting_task = asyncio.create_task(
                    self.weaviate_manager.import_document(
                        client,
                        document,
                        currentFileConfig.rag_config["Embedder"]
                        .components[fileConfig.rag_config["Embedder"].selected]
                        .config["Model"]
                        .value,
                    )
                )
                await ingesting_task
                
                # Post-processing: Extract skills from ingested document
                await self._extract_skills_from_document(
                    client, document, currentFileConfig, logger
                )

            await logger.send_report(
                currentFileConfig.fileID,
                status=FileStatus.INGESTING,
                message=f"Imported {currentFileConfig.filename} into Weaviate",
                took=round(loop.time() - start_time, 2),
            )

            await logger.send_report(
                currentFileConfig.fileID,
                status=FileStatus.DONE,
                message=f"Import for {currentFileConfig.filename} completed successfully",
                took=round(loop.time() - start_time, 2),
            )
        except Exception as e:
            await logger.send_report(
                currentFileConfig.fileID,
                status=FileStatus.ERROR,
                message=f"Import for {fileConfig.filename} failed: {str(e)}",
                took=round(loop.time() - start_time, 2),
            )
            raise Exception(f"Import for {fileConfig.filename} failed: {str(e)}")

    async def _extract_skills_from_document(
        self,
        client: WeaviateAsyncClient,
        document: Document,
        fileConfig: FileConfig,
        logger: LoggerManager,
    ):
        """
        Extract skills from an ingested document and store them in the Skill collection.
        
        This is a post-processing hook that runs after document ingestion to automatically
        extract and categorize skills from the document content.
        
        Args:
            client: Weaviate async client instance
            document: The ingested document
            fileConfig: File configuration containing RAG settings
            logger: Logger for status updates
        """
        try:
            # Check if skill extraction is enabled
            skill_extraction_enabled = os.getenv("ENABLE_SKILL_EXTRACTION", "true").lower() == "true"
            if not skill_extraction_enabled:
                msg.info(f"Skill extraction disabled, skipping for {document.title}")
                return
            
            msg.info(f"Extracting skills from document: {document.title}")
            
            # Combine document content from all chunks
            document_text = document.metadata + "\n\n" + "\n\n".join(
                [chunk.content for chunk in document.chunks]
            )
            
            # Limit text length to avoid token limits (use first 10000 characters)
            if len(document_text) > 10000:
                document_text = document_text[:10000]
                msg.info(f"Truncated document text to 10000 characters for skill extraction")
            
            # Get generator config for LLM calls
            generator_config = fileConfig.rag_config.get("Generator", {})
            if not generator_config or not generator_config.get("selected"):
                msg.warn(f"No generator configured, skipping skill extraction for {document.title}")
                return
            
            selected_generator = generator_config["selected"]
            generator_component = generator_config.get("components", {}).get(selected_generator, {})
            generator_settings = generator_component.get("config", {})
            
            # Extract skills using the SkillsExtractor
            extracted_skills = await self.skills_extractor.extract_skills(
                client=client,
                text=document_text,
                generator_config=generator_settings,
                use_cache=True
            )
            
            if not extracted_skills:
                msg.info(f"No skills extracted from {document.title}")
                return
            
            msg.good(f"Extracted {len(extracted_skills)} skills from {document.title}")
            
            # Categorize the extracted skills
            categorized_skills = self.skills_extractor.categorize_skills(extracted_skills)
            
            # Get the document UUID from Weaviate (it was just imported)
            document_uuid = await self.weaviate_manager.exist_document_name(
                client, document.title
            )
            
            if not document_uuid:
                msg.warn(f"Could not find document UUID for {document.title}, using title as fallback")
                document_uuid = document.title
            
            for category, skills in categorized_skills.items():
                for skill_name in skills:
                    try:
                        await self.skills_extractor.store_or_update_skill(
                            client=client,
                            skill_name=skill_name,
                            category=category,
                            source_document_id=document_uuid
                        )
                    except Exception as skill_error:
                        msg.warn(f"Failed to store skill '{skill_name}': {str(skill_error)}")
            
            msg.good(f"Successfully stored skills from {document.title}")
            
        except Exception as e:
            # Don't fail the entire import if skill extraction fails
            msg.warn(f"Skill extraction failed for {document.title}: {str(e)}")

    # Configuration

    def create_config(self) -> dict:
        """Creates the RAG Configuration and returns the full Verba Config with also Settings"""

        available_environments = self.environment_variables
        available_libraries = self.installed_libraries

        readers = self.reader_manager.readers
        reader_config = {
            "components": {
                reader: readers[reader].get_meta(
                    available_environments, available_libraries
                )
                for reader in readers
            },
            "selected": list(readers.values())[0].name,
        }

        chunkers = self.chunker_manager.chunkers
        chunkers_config = {
            "components": {
                chunker: chunkers[chunker].get_meta(
                    available_environments, available_libraries
                )
                for chunker in chunkers
            },
            "selected": list(chunkers.values())[0].name,
        }

        embedders = self.embedder_manager.embedders
        embedder_config = {
            "components": {
                embedder: embedders[embedder].get_meta(
                    available_environments, available_libraries
                )
                for embedder in embedders
            },
            "selected": list(embedders.values())[0].name,
        }

        retrievers = self.retriever_manager.retrievers
        retrievers_config = {
            "components": {
                retriever: retrievers[retriever].get_meta(
                    available_environments, available_libraries
                )
                for retriever in retrievers
            },
            "selected": list(retrievers.values())[0].name,
        }

        generators = self.generator_manager.generators
        generator_config = {
            "components": {
                generator: generators[generator].get_meta(
                    available_environments, available_libraries
                )
                for generator in generators
            },
            "selected": list(generators.values())[0].name,
        }

        return {
            "Reader": reader_config,
            "Chunker": chunkers_config,
            "Embedder": embedder_config,
            "Retriever": retrievers_config,
            "Generator": generator_config,
        }

    def create_user_config(self) -> dict:
        return {"getting_started": False}
    
    def create_resume_config(self) -> dict:
        """Creates the Resume Configuration for new features"""
        return {
            "skill_extraction": {
                "enabled": True,
                "model": os.getenv("SKILL_EXTRACTION_MODEL", "gpt-4"),
                "use_cache": True,
                "auto_extract_on_import": False
            },
            "resume_generation": {
                "enabled": True,
                "model": os.getenv("RESUME_GENERATION_MODEL", "gpt-4"),
                "default_format": "markdown",
                "default_sections": ["summary", "experience", "skills", "education"],
                "default_tone": "professional",
                "max_length": 2000,
                "max_work_logs_per_resume": int(os.getenv("MAX_WORK_LOGS_PER_RESUME", "50"))
            },
            "resume_tracking": {
                "enabled": True,
                "enable_pdf_export": os.getenv("ENABLE_PDF_EXPORT", "false").lower() == "true",
                "enable_docx_export": os.getenv("ENABLE_DOCX_EXPORT", "false").lower() == "true"
            },
            "hybrid_search": {
                "alpha": 0.5,  # Balance between semantic (0.0) and keyword (1.0) search
                "limit": 20
            }
        }

    async def set_theme_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.theme_config_uuid, config)

    async def set_rag_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.rag_config_uuid, config)

    async def set_user_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.user_config_uuid, config)
    
    async def set_resume_config(self, client, config: dict):
        await self.weaviate_manager.set_config(client, self.resume_config_uuid, config)

    async def load_rag_config(self, client):
        """Check if a Configuration File exists in the database, if yes, check if corrupted. Returns a valid configuration file"""
        loaded_config = await self.weaviate_manager.get_config(
            client, self.rag_config_uuid
        )
        new_config = self.create_config()
        if loaded_config is not None:
            if self.verify_config(loaded_config, new_config):
                msg.info("Using Existing RAG Configuration")
                return loaded_config
            else:
                msg.info("Using New RAG Configuration")
                await self.set_rag_config(client, new_config)
                return new_config
        else:
            msg.info("Using New RAG Configuration")
            return new_config

    async def load_theme_config(self, client):
        loaded_config = await self.weaviate_manager.get_config(
            client, self.theme_config_uuid
        )

        if loaded_config is None:
            return None, None

        return loaded_config["theme"], loaded_config["themes"]

    async def load_user_config(self, client):
        loaded_config = await self.weaviate_manager.get_config(
            client, self.user_config_uuid
        )

        if loaded_config is None:
            return self.create_user_config()

        return loaded_config
    
    async def load_resume_config(self, client):
        """Load resume configuration from database or create new one"""
        loaded_config = await self.weaviate_manager.get_config(
            client, self.resume_config_uuid
        )
        
        if loaded_config is None:
            msg.info("Using New Resume Configuration")
            new_config = self.create_resume_config()
            await self.set_resume_config(client, new_config)
            return new_config
        
        msg.info("Using Existing Resume Configuration")
        return loaded_config

    def verify_config(self, a: dict, b: dict) -> bool:
        # Check Settings ( RAG & Settings )
        try:
            if os.getenv("VERBA_PRODUCTION") == "Demo":
                return True
            for a_component_key, b_component_key in zip(a, b):
                if a_component_key != b_component_key:
                    msg.fail(
                        f"Config Validation Failed, component name mismatch: {a_component_key} != {b_component_key}"
                    )
                    return False

                a_component = a[a_component_key]["components"]
                b_component = b[b_component_key]["components"]

                if len(a_component) != len(b_component):
                    msg.fail(
                        f"Config Validation Failed, {a_component_key} component count mismatch: {len(a_component)} != {len(b_component)}"
                    )
                    return False

                for a_rag_component_key, b_rag_component_key in zip(
                    a_component, b_component
                ):
                    if a_rag_component_key != b_rag_component_key:
                        msg.fail(
                            f"Config Validation Failed, component name mismatch: {a_rag_component_key} != {b_rag_component_key}"
                        )
                        return False
                    a_rag_component = a_component[a_rag_component_key]
                    b_rag_component = b_component[b_rag_component_key]

                    a_config = a_rag_component["config"]
                    b_config = b_rag_component["config"]

                    if len(a_config) != len(b_config):
                        msg.fail(
                            f"Config Validation Failed, component config count mismatch: {len(a_config)} != {len(b_config)}"
                        )
                        return False

                    for a_config_key, b_config_key in zip(a_config, b_config):
                        if a_config_key != b_config_key:
                            msg.fail(
                                f"Config Validation Failed, component name mismatch: {a_config_key} != {b_config_key}"
                            )
                            return False

                        a_setting = a_config[a_config_key]
                        b_setting = b_config[b_config_key]

                        if a_setting["description"] != b_setting["description"]:
                            msg.fail(
                                f"Config Validation Failed, description mismatch: {a_setting['description']} != {b_setting['description']}"
                            )
                            return False

                        if sorted(a_setting["values"]) != sorted(b_setting["values"]):
                            msg.fail(
                                f"Config Validation Failed, values mismatch: {a_setting['values']} != {b_setting['values']}"
                            )
                            return False

            return True

        except Exception as e:
            msg.fail(f"Config Validation failed: {str(e)}")
            return False

    async def reset_rag_config(self, client):
        msg.info("Resetting RAG Configuration")
        await self.weaviate_manager.reset_config(client, self.rag_config_uuid)

    async def reset_theme_config(self, client):
        msg.info("Resetting Theme Configuration")
        await self.weaviate_manager.reset_config(client, self.theme_config_uuid)

    async def reset_user_config(self, client):
        msg.info("Resetting User Configuration")
        await self.weaviate_manager.reset_config(client, self.user_config_uuid)
    
    async def reset_resume_config(self, client):
        msg.info("Resetting Resume Configuration")
        await self.weaviate_manager.reset_config(client, self.resume_config_uuid)

    # Environment and Libraries

    def verify_installed_libraries(self) -> None:
        """
        Checks which libraries are installed and fills out the self.installed_libraries dictionary for the frontend to access, this will be displayed in the status page.
        """
        reader = [
            lib
            for reader in self.reader_manager.readers
            for lib in self.reader_manager.readers[reader].requires_library
        ]
        chunker = [
            lib
            for chunker in self.chunker_manager.chunkers
            for lib in self.chunker_manager.chunkers[chunker].requires_library
        ]
        embedder = [
            lib
            for embedder in self.embedder_manager.embedders
            for lib in self.embedder_manager.embedders[embedder].requires_library
        ]
        retriever = [
            lib
            for retriever in self.retriever_manager.retrievers
            for lib in self.retriever_manager.retrievers[retriever].requires_library
        ]
        generator = [
            lib
            for generator in self.generator_manager.generators
            for lib in self.generator_manager.generators[generator].requires_library
        ]

        required_libraries = reader + chunker + embedder + retriever + generator
        unique_libraries = set(required_libraries)

        for lib in unique_libraries:
            try:
                importlib.import_module(lib)
                self.installed_libraries[lib] = True
            except Exception:
                self.installed_libraries[lib] = False

    def verify_variables(self) -> None:
        """
        Checks which environment variables are installed and fills out the self.environment_variables dictionary for the frontend to access.
        """
        reader = [
            lib
            for reader in self.reader_manager.readers
            for lib in self.reader_manager.readers[reader].requires_env
        ]
        chunker = [
            lib
            for chunker in self.chunker_manager.chunkers
            for lib in self.chunker_manager.chunkers[chunker].requires_env
        ]
        embedder = [
            lib
            for embedder in self.embedder_manager.embedders
            for lib in self.embedder_manager.embedders[embedder].requires_env
        ]
        retriever = [
            lib
            for retriever in self.retriever_manager.retrievers
            for lib in self.retriever_manager.retrievers[retriever].requires_env
        ]
        generator = [
            lib
            for generator in self.generator_manager.generators
            for lib in self.generator_manager.generators[generator].requires_env
        ]

        required_envs = reader + chunker + embedder + retriever + generator
        unique_envs = set(required_envs)

        for env in unique_envs:
            if os.environ.get(env) is not None:
                self.environment_variables[env] = True
            else:
                self.environment_variables[env] = False

    # Document Content Retrieval

    async def get_content(
        self,
        client,
        uuid: str,
        page: int,
        chunkScores: list[ChunkScore],
    ):
        chunks_per_page = 10
        content_pieces = []
        total_batches = 0

        # Return Chunks with surrounding context
        if len(chunkScores) > 0:
            if page > len(chunkScores):
                page = 0

            total_batches = len(chunkScores)
            chunk = await self.weaviate_manager.get_chunk(
                client, chunkScores[page].uuid, chunkScores[page].embedder
            )

            before_ids = [
                i
                for i in range(
                    max(0, chunkScores[page].chunk_id - int(chunks_per_page / 2)),
                    chunkScores[page].chunk_id,
                )
            ]
            if before_ids:
                chunks_before_chunk = await self.weaviate_manager.get_chunk_by_ids(
                    client,
                    chunkScores[page].embedder,
                    uuid,
                    ids=[
                        i
                        for i in range(
                            max(
                                0, chunkScores[page].chunk_id - int(chunks_per_page / 2)
                            ),
                            chunkScores[page].chunk_id,
                        )
                    ],
                )
                before_content = "".join(
                    [
                        chunk.properties["content_without_overlap"]
                        for chunk in chunks_before_chunk
                    ]
                )
            else:
                before_content = ""

            after_ids = [
                i
                for i in range(
                    chunkScores[page].chunk_id + 1,
                    chunkScores[page].chunk_id + int(chunks_per_page / 2),
                )
            ]
            if after_ids:
                chunks_after_chunk = await self.weaviate_manager.get_chunk_by_ids(
                    client,
                    chunkScores[page].embedder,
                    uuid,
                    ids=[
                        i
                        for i in range(
                            chunkScores[page].chunk_id + 1,
                            chunkScores[page].chunk_id + int(chunks_per_page / 2),
                        )
                    ],
                )
                after_content = "".join(
                    [
                        chunk.properties["content_without_overlap"]
                        for chunk in chunks_after_chunk
                    ]
                )
            else:
                after_content = ""

            content_pieces.append(
                {
                    "content": before_content,
                    "chunk_id": 0,
                    "score": 0,
                    "type": "text",
                }
            )
            content_pieces.append(
                {
                    "content": chunk["content_without_overlap"],
                    "chunk_id": chunkScores[page].chunk_id,
                    "score": chunkScores[page].score,
                    "type": "extract",
                }
            )
            content_pieces.append(
                {
                    "content": after_content,
                    "chunk_id": 0,
                    "score": 0,
                    "type": "text",
                }
            )

        # Return Content based on Page
        else:
            document = await self.weaviate_manager.get_document(
                client, uuid, properties=["meta"]
            )
            config = json.loads(document["meta"])
            embedder = config["Embedder"]["config"]["Model"]["value"]
            request_chunk_ids = [
                i
                for i in range(
                    chunks_per_page * (page + 1) - chunks_per_page,
                    chunks_per_page * (page + 1),
                )
            ]

            chunks = await self.weaviate_manager.get_chunk_by_ids(
                client, embedder, uuid, request_chunk_ids
            )

            total_chunks = await self.weaviate_manager.get_chunk_count(
                client, embedder, uuid
            )
            total_batches = int(math.ceil(total_chunks / chunks_per_page))

            content = "".join(
                [chunk.properties["content_without_overlap"] for chunk in chunks]
            )

            content_pieces.append(
                {
                    "content": content,
                    "chunk_id": 0,
                    "score": 0,
                    "type": "text",
                }
            )

        return (content_pieces, total_batches)

    # Retrieval Augmented Generation

    async def retrieve_chunks(
        self,
        client,
        query: str,
        rag_config: dict,
        labels: list[str] = [],
        document_uuids: list[str] = [],
    ):
        retriever = rag_config["Retriever"].selected
        embedder = rag_config["Embedder"].selected

        await self.weaviate_manager.add_suggestion(client, query)

        vector = await self.embedder_manager.vectorize_query(
            embedder, query, rag_config
        )
        documents, context = await self.retriever_manager.retrieve(
            client,
            retriever,
            query,
            vector,
            rag_config,
            self.weaviate_manager,
            labels,
            document_uuids,
        )

        return (documents, context)

    async def generate_stream_answer(
        self,
        rag_config: dict,
        query: str,
        context: str,
        conversation: list[dict],
    ):

        full_text = ""
        async for result in self.generator_manager.generate_stream(
            rag_config, query, context, conversation
        ):
            full_text += result["message"]
            yield result


class ClientManager:
    def __init__(self) -> None:
        self.clients: dict[str, dict] = {}
        self.manager: VerbaManager = VerbaManager()
        self.max_time: int = 10
        self.locks: dict[str, asyncio.Lock] = {}

    def hash_credentials(self, credentials: Credentials) -> str:
        cred_string = f"{credentials.deployment}:{credentials.url}:{credentials.key}"
        return hashlib.sha256(cred_string.encode()).hexdigest()

    def get_or_create_lock(self, cred_hash: str) -> asyncio.Lock:
        if cred_hash not in self.locks:
            self.locks[cred_hash] = asyncio.Lock()
        return self.locks[cred_hash]

    def heartbeat(self):
        msg.info(f"{len(self.clients)} clients connected")
        for cred_hash, client in self.clients.items():
            msg.info(f"Client {cred_hash} connected at {client['timestamp']}")

    async def get_client(self) -> WeaviateAsyncClient:
        """Get or create a client with default credentials"""
        default_credentials = Credentials(
            url=os.environ.get("WEAVIATE_URL_VERBA", ""),
            key=os.environ.get("WEAVIATE_API_KEY_VERBA", ""),
            deployment="Local"
        )
        return await self.connect(default_credentials)

    async def connect(
        self, credentials: Credentials, port: str = "8080"
    ) -> WeaviateAsyncClient:

        _credentials = credentials

        if not _credentials.url and not _credentials.key:
            _credentials.url = os.environ.get("WEAVIATE_URL_VERBA", "")
            _credentials.key = os.environ.get("WEAVIATE_API_KEY_VERBA", "")

        cred_hash = self.hash_credentials(_credentials)

        lock = self.get_or_create_lock(cred_hash)
        async with lock:
            if cred_hash in self.clients:
                msg.info("Found existing Client")
                return self.clients[cred_hash]["client"]
            else:
                msg.warn("Connecting new Client")
                try:
                    client = await self.manager.connect(_credentials, port)
                    if client:
                        self.clients[cred_hash] = {
                            "client": client,
                            "timestamp": datetime.now(),
                        }
                        return client
                    else:
                        raise Exception("Client not created")
                except Exception as e:
                    raise e

    async def disconnect(self):
        msg.warn("Disconnecting Clients!")
        for cred_hash, client in self.clients.items():
            await self.manager.disconnect(client["client"])

    async def clean_up(self):
        msg.info("Cleaning Clients Cache")
        current_time = datetime.now()
        clients_to_remove = []

        for cred_hash, client_data in self.clients.items():
            time_difference = current_time - client_data["timestamp"]
            if time_difference.total_seconds() / 60 > self.max_time:
                clients_to_remove.append(cred_hash)
            client: WeaviateAsyncClient = client_data["client"]
            if not await client.is_ready():
                clients_to_remove.append(cred_hash)

        for cred_hash in clients_to_remove:
            await self.manager.disconnect(self.clients[cred_hash]["client"])
            del self.clients[cred_hash]
            msg.warn(f"Removed client: {cred_hash}")

        msg.info(f"Cleaned up {len(clients_to_remove)} clients")
        self.heartbeat()
