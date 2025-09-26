import os
import secrets
import warnings
from typing import Annotated, Any, Literal, List

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    # Document processing parameters
    FULL_SCAN_DOCUMENT_CHUNK_SIZE: int = 100000
    FULL_SCAN_DOCUMENT_CHUNK_OVERLAP: int = 200
    RAG_DOCUMENT_CHUNK_SIZE: int = 1000
    RAG_DOCUMENT_CHUNK_OVERLAP: int = 200
    RAG_NUM_CHUNKS: int = 20  # Number of chunks to retrieve for RAG search

    # Content filtering settings for improved RAG quality
    RAG_FILTER_BIBLIOGRAPHY: bool = True  # Filter bibliography content from RAG results
    RAG_MIN_QUALITY_SCORE: float = 0.3  # Minimum quality score for content chunks
    RAG_MAX_BIBLIOGRAPHY_CHUNKS: int = 0  # Maximum bibliography chunks to include

    # Embedding processing parameters
    EMBEDDING_MAX_TOKENS_PER_REQUEST: int = (
        250000  # Maximum tokens per embedding API request (safe limit below OpenAI's 300k token limit)
    )

    # Knowledge Base settings
    KB_PROGRESS_UPDATE_INTERVAL: int = (
        10  # How often to update progress during processing
    )
    KB_MIN_BATCH_SIZE: int = 1
    KB_MAX_BATCH_SIZE: int = 50
    KB_MEMORY_THRESHOLD_MB: float = 1000  # Memory threshold for warnings

    # Memory management settings for large files
    KB_MAX_IN_MEMORY_SIZE_MB: int = 100  # Files larger than this use streaming
    KB_STREAM_CHUNK_SIZE_MB: int = 8  # Chunk size for streaming (8MB)
    KB_MAX_DB_SIZE_MB: int = (
        200  # Maximum size for database storage (reduced to prevent crashes)
    )
    KB_MEMORY_SAFETY_THRESHOLD: float = (
        0.2  # Use chunked reading if file > 20% of available memory
    )
    KB_HIGH_MEMORY_USAGE_THRESHOLD: float = (
        60.0  # Memory usage % that triggers chunked reading
    )

    # File-based storage settings for large knowledge bases
    KB_USE_FILE_STORAGE_ABOVE_MB: int = (
        200  # Store files on disk instead of DB if larger than this
    )
    KB_FILE_STORAGE_PATH: str = (
        "/app/data/knowledge_bases"  # Path for file-based storage
    )

    # FormConnect processing parameters
    FORMCONNECT_MAX_TOKENS_PER_REQUEST: int = 3000  # Token limit for full text mode
    FORMCONNECT_VECTOR_SEARCH_CHUNKS: int = 5  # Number of chunks to retrieve per field
    FORMCONNECT_CHUNK_OVERLAP: int = 200  # Overlap for document chunking

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # ENABLED_LLM_PROVIDERS: str = "huggingface,openai,ollama,replicate,aws"
    # ENABLED_EMBEDDING_PROVIDERS: str = "huggingface,openai,ollama,replicate,aws"
    ENABLED_LLM_PROVIDERS: str = "openai,aws"
    ENABLED_EMBEDDING_PROVIDERS: str = "openai,aws"

    # Supported Languages for Translation
    SUPPORTED_LANGUAGES: dict[str, str] = {
        # Major European Languages
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "pt": "Português",
        "ru": "Русский",
        "uk": "Українська",
        "pl": "Polski",
        "nl": "Nederlands",
        "sv": "Svenska",
        "no": "Norsk",
        "da": "Dansk",
        "fi": "Suomi",
        "cs": "Čeština",
        "sk": "Slovenčina",
        "hu": "Magyar",
        "ro": "Română",
        "bg": "Български",
        "hr": "Hrvatski",
        "sr": "Српски",
        "sl": "Slovenščina",
        "et": "Eesti",
        "lv": "Latviešu",
        "lt": "Lietuvių",
        "el": "Ελληνικά",
        # Asian Languages
        "zh": "中文 (简体)",
        "zh-TW": "中文 (繁體)",
        "ja": "日本語",
        "ko": "한국어",
        "hi": "हिन्दी",
        "th": "ไทย",
        "vi": "Tiếng Việt",
        "id": "Bahasa Indonesia",
        "ms": "Bahasa Melayu",
        "tl": "Filipino",
        # Middle Eastern & African Languages
        "ar": "العربية",
        "he": "עברית",
        "fa": "فارسی",
        "tr": "Türkçe",
        "sw": "Kiswahili",
        # Regional Variants
        "pt-BR": "Português (Brasil)",
        "es-LATAM": "Español (Latinoamérica)",
    }

    # OpenAI API Configuration
    OPENAI_TIMEOUT: int = 3600  # 60 minutes timeout for OpenAI API calls

    # Usage Quota Configuration
    QUOTA_PERIOD_START_DAY: int = 1  # Day of month when quota period starts (1-28)
    QUOTA_PERIOD_MAX_TOKENS: int = 50_000_000  # Maximum tokens per quota period

    # Model Selection Configuration
    ENABLE_MODEL_SELECTION: bool = True  # Set to False to disable model selection UI
    FORCE_DEFAULT_LLM: str = (
        "gpt-4o-mini"  # Default LLM when model selection is disabled
    )
    FORCE_DEFAULT_EMBEDDING: str = (
        "text-embedding-3-small"  # Default embedding when disabled
    )

    @computed_field
    @property
    def llm_providers(self) -> list[str]:
        """Return list of enabled LLM providers"""
        return [provider.strip() for provider in self.ENABLED_LLM_PROVIDERS.split(",")]

    @computed_field
    @property
    def embedding_providers(self) -> list[str]:
        """Return list of enabled embedding model providers"""
        return [
            provider.strip() for provider in self.ENABLED_EMBEDDING_PROVIDERS.split(",")
        ]

    # LLM Templates
    REPORT_GENIE_PROMPT_TEMPLATE: str = """
    You are drafting a document.
    
    DRAFT OF REPORT SO FAR:
    {report_draft}

    TASK:
    You will be shown some reference information and then asked to write a clear and comprehensive section of this document based on the description below. 
    
    The section to create is: {question}

    REFERENCE INFORMATION:
    {context}

    TASK:
    
    The content should:
    1. Be written in plain language (8th-grade reading level)
    2. Be concise yet thorough
    3. Be limited to the specific section requested -- don't keep adding unnecessary/unrequested language like "Your participation is important, and we appreciate your commitment to this investigation."
    4. Use second-person perspective (addressing "you" - the participant)
    5. Should not make any claims that are not supported by the provided reference information
    6. Keep in mind what has already been generated in the report, and don't be redundant when writing the new section.

    {custom_instructions}

    SECTION CONTENT:
    """

    VERADOC_CONTEXT_PROMPT_TEMPLATE: str = """
    INSTRUCTION: 
    You are an AI assistant that helps answer questions about documents that are under review based on specific policy regulations.
    You are answering a certain question about a document, but you need to check the policy regulations to make sure that you are taking into account the full policy context.

    What necessary information from the context below should be kept in mind when answering the following question? {question} 

    SOURCE POLICY CITATIONS:
    {context}
    
    CRITICAL INSTRUCTIONS:
    1. ONLY include policy information that is EXPLICITLY stated in the provided SOURCE POLICY CITATIONS above
    2. Do NOT make assumptions or infer requirements that are not directly written in the source material
    3. Do NOT add general knowledge about policies or regulations that is not contained in the citations
    4. If the provided citations do not contain information relevant to the question, state "No relevant policy information found in the provided citations"
    5. Quote or directly reference specific sections from the citations when possible
    6. ONLY include policy information that would be SPECIFICALLY pertinent to the question -- do NOT repeat general requirements
    7. If you cannot find specific, relevant policy information in the citations, it is better to say so than to make up requirements
    
    ANSWER:
    Based strictly on the provided policy citations, the following should be kept in mind when answering the question:
    """

    VERADOC_QA_PROMPT_TEMPLATE: str = """
        INSTRUCTION: 
        You are an AI assistant that helps answer questions about documents based on specific policy regulations.
        Read the following document and answer the question below clearly and concisely in 100 words or less.
        If the document does not contain sufficient detail to confirm that a requirement is met, state that the information is insufficient, even if the requirement is mentioned.
        You will also be provided with some policy context to help you in your determination.

        SAMPLE DOCUMENT:
        {document_text}

        QUESTION:
        {question}

        RELEVANT REQUIREMENTS:
        {question_context}

        Additional instructions for answering the question:
        {custom_instructions_section}

        Now begin your answer with either YES or NO.
        ANSWER:
    """

    VERADOC_FINAL_PROMPT_TEMPLATE: str = """
    INSTRUCTION: 
    You are an AI assistant that helps answer questions about documents based on specific policy regulations.
    According to policy, an acceptable document must have all of the elements described in the following questions.
    Read the following question-and-answer pairs about a certain proposal and determine whether or not it conforms to the policy.
    
    Remember: if any single element is missing from the proposal, it automatically means that the entire proposal does NOT conform to policy.
    If the plan does not conform to policy, explain why not.
    
    {qa_pairs}
    
    Based on the question-and-answer pairs above, does the plan follow policy?
    """

    VERADOC_OPTIMIZE_PROMPT_TEMPLATE: str = """
    INSTRUCTION: 
    You are an AI assistant that helps optimize review checklist questions to be more appropriate for document evaluation.

    You have been given a checklist question and the answer that was generated when evaluating a document that SHOULD meet all requirements. If the answer indicates the requirement was not met (starts with NO rather than YES), you need to suggest a revised question that is less stringent but still meaningful.

    ORIGINAL QUESTION:
    {original_question}

    GENERATED ANSWER:
    {generated_answer}

    DOCUMENT CONTEXT:
    {document_context}

    TASK:
    If the answer begins with NO and suggests the requirement was not met, provide a revised question that would be more likely to result in a "yes" answer for similar documents, while still maintaining the intent of the original requirement.

    If the answer begins with YES and indicates the requirement was met, return the original question unchanged.

    FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
    REVISED_QUESTION: [your revised question here]
    REASON: [brief explanation of why you made this change]
    NEEDS_REVISION: [yes/no]
    """

    FORMCONNECT_DIGITIZED_PROMPT_TEMPLATE: str = """
    Here is a template of the fields that I want you to extract from this document: {template}
    Here is the full text of a document: {document_text}
    Fill out the template based on the fields you can find.
    """

    FORMCONNECT_COMPARISON_PROMPT_TEMPLATE: str = """
    I am going to show you information extracted from multiple documents:

    {documents_str}

    Please analyze all the documents and identify any fields that have different values across documents.

    Create a markdown table with the following format:
    1. First column should be titled "FIELD" and contain the field name
    2. Each additional column should have the document name as header (e.g., "Document 1", "Document 2")
    3. Include ONLY fields where there are discrepancies between documents

    After the table, please:
    1. For each discrepancy, suggest which value is most likely correct and why
    2. Provide a summary of how consistent the documents are overall

    Example format:
    ```markdown
    | FIELD | Document 1 | Document 2 | ... |
    |-------|------------|------------|-----|
    | Name  | John Smith | J. Smith   | ... |
    | Date  | 2023-01-01 | 2023-01-15 | ... |
    ```

    ONLY return the Markdown table -- do NOT return any other text. 
    Also, do NOT add tick marks like ``` and the label 'markdown': just give the actual markdown table content as raw text.
    However, if there are no discrepancies, please state that all fields match across documents.
    IF A FIELD ENTRY WASN'T FOUND FOR A GIVEN DOCUMENT, SAY SO EXPLICITLY.
    """

    FORMCONNECT_SINGLE_DOCUMENT_PROMPT_TEMPLATE: str = """
    I have extracted the following field values from a document:

    Document: {document_name}
    Extracted Data: {extracted_data}

    Please create a clear, well-formatted presentation of the extracted field values from this document.

    Create a markdown table with the following format:
    1. First column should be titled "FIELD" 
    2. Second column should be titled "VALUE"
    3. Include ALL fields from the template, even if no value was found

    Example format:
    ```markdown
    | FIELD | VALUE |
    |-------|-------|
    | Name  | John Smith |
    | Date  | 2023-01-01 |
    | Address | Not found |
    ```

    After the table, provide a brief summary of:
    1. How many fields were successfully extracted
    2. Which fields had missing or unclear values
    3. Overall data quality assessment

    ONLY return the Markdown table and summary -- do NOT return any other text.
    Also, do NOT add tick marks like ``` and the label 'markdown': just give the actual markdown table content as raw text.
    IF A FIELD VALUE WASN'T FOUND, CLEARLY STATE "Not found" OR "Not detected" in the VALUE column.
    """

    FORMCONNECT_GENERATE_FIELDS_PROMPT_TEMPLATE: str = """
    Generate a list of form fields for data extraction based on the following description:

    DESCRIPTION: {description}

    {knowledge_base_instruction}
    {knowledge_base_content}
    {example_instruction}

    Please generate form field names that would be relevant for extracting structured data from documents that match this description.

    Guidelines:
    1. Focus on creating field names that would commonly appear in forms or documents of this type
    2. Use clear, descriptive field names (e.g., "First Name", "Date of Birth", "Address Line 1")
    3. Include both required and optional fields that might be found
    4. Consider standard fields for this type of document/form
    5. Generate between 5-20 fields unless a specific number is requested
    6. Make field names practical for data entry and extraction
    7. Avoid overly specific or technical jargon in field names
    8. Use title case for field names (e.g., "Social Security Number" not "social_security_number")
    9. Include common variations that might be needed (e.g., both "Phone Number" and "Email Address" for contact info)
    10. Consider fields that would help with validation and verification
    {analysis_instruction}

    Output format:
    FIELDS:
    1. [Field Name 1]
    2. [Field Name 2]
    3. [Field Name 3]
    ...

    ANALYSIS:
    [Brief explanation of why these fields were selected and how they relate to the description{analysis_note}]
    """

    CHATBOT_REPHRASING_PROMPT_TEMPLATE: str = """
    You are an AI that rephrases the user's latest question to incorporate relevant context from the conversation history.
    
    CONVERSATION HISTORY:
    {chat_history}
    
    CURRENT QUESTION: {question}
    
    INSTRUCTIONS:
    1. Analyze the conversation history and the current question.
    2. Rewrite the current question to be self-contained, incorporating any relevant context.
    3. The rephrased question should be answerable without needing to see the conversation history.
    4. Return ONLY the rephrased question, nothing else.
    5. If the current question is already self-contained and doesn't reference anything from the history, return it unchanged.
    
    REPHRASED QUESTION:
    """

    CHATBOT_KB_QA_PROMPT_TEMPLATE: str = """
    You are a helpful assistant that answers questions based on the provided context.
    
    CONTEXT:
    {context}
    
    QUESTION: {question}
    
    INSTRUCTIONS:
    1. Answer the question based ONLY on the information provided in the CONTEXT.
    2. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question."
    3. Be concise and to the point.
    4. Don't make up information or use knowledge outside the provided context.
    
    ANSWER:
    """

    CHATBOT_GENERAL_QA_PROMPT_TEMPLATE: str = """
    You are a helpful AI assistant. Answer the following question to the best of your knowledge.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    QUESTION: {question}

    ANSWER:
    """

    # TwinCheck prompt templates
    TWINCHECK_ANALYSIS_PROMPT_TEMPLATE: str = """
    You are an expert document analyst comparing two documents:
    - Document 1: {doc1_name}
    - Document 2: {doc2_name}
    
    Based on your analysis of the content below:
    - Lines starting with '- ' represent content unique to Document 1
    - Lines starting with '+ ' represent content unique to Document 2
    - Lines starting with '? ' indicate formatting or minor textual variations
    - Lines with no prefix represent shared content between both documents
    
    Document comparison data:
    {diff_text}
    {knowledge_base_context}
    
    Please analyze how these documents differ specifically regarding: "{topic}"
    
    Provide a clear, detailed analysis of the differences between the two documents regarding this topic.
    Refer to specific sections of the documents where relevant differences exist.
    If there are no differences related to this topic, state that clearly.
    If reference context was provided, use it to inform your analysis and provide additional insights.
    """

    TWINCHECK_SUMMARY_PROMPT_TEMPLATE: str = """
    You are an expert document analyst comparing two documents:
    - Document 1: {doc1_name}
    - Document 2: {doc2_name}
    
    Based on your analysis of the content below:
    - Lines starting with '- ' represent content unique to Document 1
    - Lines starting with '+ ' represent content unique to Document 2
    - Lines starting with '? ' indicate formatting or minor textual variations
    - Lines with no prefix represent shared content between both documents
    
    Document comparison data:
    {diff_text}
    
    The user is particularly interested in these topics:
    {topics}
    
    Please provide a comprehensive analysis of all significant differences between the two documents. 
    Focus on structural, content, and semantic variations. 
    Highlight the most important distinctions and explain their potential implications.
    Be clear, concise, and informative.
    """

    # TwinCheck chunk processing settings
    # Reduced to accommodate 128K token limit with generous reserves for prompt template
    TWINCHECK_MAX_TOKENS_PER_CHUNK: int = 100000  # Reduced from 150K to 100K
    TWINCHECK_PROMPT_RESERVE_TOKENS: int = 20000  # Increased from 5K to 20K for safety

    REPLICATE_API_TOKEN: str | None = os.getenv("REPLICATE_API_TOKEN")

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    REPORT_GENIE_SYNTHESIS_PROMPT_TEMPLATE: str = """
    You are an AI assistant synthesizing analysis from multiple text chunks to answer a question.

    QUESTION: {question}

    ANALYSIS FROM CHUNKS:
    {chunk_analyses}

    INSTRUCTIONS:
    1. Review the analysis from all text chunks.
    2. Combine the information to form a comprehensive and coherent answer to the original QUESTION.
    3. Do not include information that is not supported by the provided analysis.
    4. If the combined analysis does not provide a clear answer, state that the information could not be fully determined from the text.
    5. Synthesize the information, do not just list the findings from each chunk.

    SYNTHESIZED ANSWER:
    """

    # Full text scan template for chat functionality
    CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE: str = """
    You are an AI assistant analyzing a text chunk to answer a specific question.

    TEXT CHUNK:
    {chunk}

    QUESTION: {question}

    INSTRUCTIONS:
    1. Analyze the text chunk to find information relevant to the question.
    2. If the chunk contains relevant information, provide a clear and concise answer based only on that information.
    3. If the chunk does not contain relevant information, respond with "No relevant information found in this chunk."
    4. Do not make assumptions or add information not present in the text chunk.

    ANALYSIS:
    """

    CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE: str = """
    You are an AI assistant synthesizing analysis from multiple text chunks to answer a question.

    QUESTION: {question}

    ANALYSIS FROM TEXT CHUNKS:
    {chunk_analyses}

    INSTRUCTIONS:
    1. Review the analysis from all text chunks.
    2. Combine the information to form a comprehensive and coherent answer to the original QUESTION.
    3. Only include information that is supported by the provided chunk analyses.
    4. If the combined analysis does not provide sufficient information to answer the question, state that clearly.
    5. Synthesize the information, do not just list the findings from each chunk.
    6. Provide a well-structured, coherent response.

    SYNTHESIZED ANSWER:
    """

    VERADOC_GENERATE_QUESTIONS_PROMPT_TEMPLATE: str = """
INSTRUCTION: 
You are an AI assistant that helps generate comprehensive checklist questions based on a given description.
Your task is to create specific, actionable questions that would help evaluate documents or processes according to the described requirements.

DESCRIPTION:
{description}

CHECKLIST TYPE: {checklist_type}

{reference_documents_instruction}

{reference_documents_content}

INSTRUCTIONS:
1. Generate as many specific, clear, and actionable questions as needed to comprehensively cover the description
2. Each question should be evaluable with a yes/no or specific answer
3. Questions should be comprehensive and cover all aspects mentioned in the description
4. Make questions specific enough to be useful for document review or compliance checking
5. Avoid vague or overly general questions
6. Focus on what can be verified or assessed in a document or process
7. Use clear, professional language suitable for a checklist
8. Generate between 5-25 questions depending on the complexity of the requirements
9. For complex regulatory or compliance requirements, generate more detailed questions
10. For simple processes, fewer but comprehensive questions are sufficient
{additional_instructions}

FORMAT YOUR RESPONSE AS:
QUESTIONS:
1. [First question]
2. [Second question]
3. [Third question]
... (continue with as many questions as needed to comprehensively cover the requirements)

ANALYSIS:
[Brief explanation of why these questions comprehensively cover the described requirements and how many questions were needed]
"""

    TWINCHECK_GENERATE_TOPICS_PROMPT_TEMPLATE: str = """
INSTRUCTION: 
You are an AI assistant that helps generate comprehensive comparison topics for document analysis based on a given description.
Your task is to create specific, actionable topics that would help compare two documents effectively according to the described comparison requirements.

DESCRIPTION:
{description}

COMPARISON TYPE: {comparison_type}

{example_document}

{knowledge_base_content}

INSTRUCTIONS:
1. Generate as many specific, clear, and actionable comparison topics as needed to comprehensively cover the description
2. Each topic should represent a distinct area of comparison between two documents
3. Topics should be comprehensive and cover all aspects mentioned in the description
4. Make topics specific enough to be useful for meaningful document comparison
5. Avoid vague or overly general topics
6. Focus on what can be compared, contrasted, or analyzed between documents
7. Use clear, professional language suitable for document comparison analysis
8. Generate between 3-15 topics depending on the complexity of the comparison requirements
9. For complex regulatory or compliance comparisons, generate more detailed topics
10. For simple comparisons, fewer but comprehensive topics are sufficient
11. Consider both content-based comparisons (what is included/excluded) and structural comparisons (how information is organized)
12. Include topics that would reveal differences in approach, methodology, compliance, or implementation{example_instruction}{knowledge_base_instruction}

FORMAT YOUR RESPONSE AS:
TOPICS:
1. [First topic for comparison]
2. [Second topic for comparison]
3. [Third topic for comparison]
... (continue with as many topics as needed to comprehensively cover the comparison requirements)

ANALYSIS:
[Brief explanation of why these topics comprehensively cover the described comparison requirements and how they would help identify meaningful differences between documents{example_analysis_instruction}]
"""

    REPORTGENIE_GENERATE_OUTLINE_PROMPT_TEMPLATE: str = """
INSTRUCTION: 
You are an AI assistant that helps generate comprehensive section outlines for reports based on a given description.
Your task is to create specific, meaningful section descriptions that would help structure a comprehensive report according to the outlined requirements.

OUTLINE DESCRIPTION:
{description}

REPORT TYPE: {report_type}

{example_document}

{knowledge_base_content}

INSTRUCTIONS:
1. Generate as many specific, clear, and meaningful sections as needed to comprehensively cover the outline description
2. Each section should represent a distinct topic or area that would be covered in the report
3. Sections should be comprehensive and cover all aspects mentioned in the outline description
4. Make section descriptions specific enough to be useful for report generation
5. Avoid vague or overly general section descriptions
6. Focus on what would be meaningful content areas for a structured report
7. Use clear, professional language suitable for report sections
8. If an example document is provided, generate approximately the same number of sections as shown in the example document structure to match its format and depth
9. For each section, provide not just a title but also a detailed description that includes:
   - The specific topics and subtopics that should be covered in that section
   - The general scope and depth of content expected
   - Approximate length or detail level (e.g., brief overview, detailed analysis, comprehensive review)
10. Each section description should be substantive (3-5 sentences) explaining what content would be included{example_instruction}{knowledge_base_instruction}

FORMAT YOUR RESPONSE AS:
SECTIONS:
1. [Section Title]: [Detailed description of what this section should cover, including specific topics, scope, and expected depth/length of content]
2. [Section Title]: [Detailed description of what this section should cover, including specific topics, scope, and expected depth/length of content]
3. [Section Title]: [Detailed description of what this section should cover, including specific topics, scope, and expected depth/length of content]
... (continue with as many sections as needed to comprehensively cover the outline)

ANALYSIS:
[Brief explanation of why these sections comprehensively cover the outlined requirements and how the sections work together to form a complete report structure{example_analysis_instruction}]
"""

    REPORTGENIE_OPTIMIZE_OUTLINE_PROMPT_TEMPLATE: str = """
INSTRUCTION:
You are an expert at analyzing content quality and suggesting improvements to report outline sections by comparing generated report content to a ground-truth reference document.

ORIGINAL SECTION: {original_section}

GENERATED CONTENT FOR THIS SECTION:
{generated_content}

RELEVANT CONTENT FROM GROUND-TRUTH DOCUMENT:
{ground_truth_content}

{custom_instructions}

ANALYSIS GUIDELINES:
Compare the generated content to the ground truth and determine if revision is needed.

ONLY set NEEDS_REVISION to YES if there are SIGNIFICANT issues:
- Major information gaps (missing key points from ground truth)
- Substantially different scope or focus that makes content less useful
- Quality issues that would materially impact report effectiveness
- Clear misalignment with the intended purpose of the section
- Generated content covers fundamentally different topics than ground truth

DO NOT revise for minor differences:
- Small wording variations or stylistic differences
- Different but equivalent phrasing that conveys the same information
- Minor detail variations if core information is adequately covered
- Reorganized content that still addresses the same key points
- Acceptable alternative approaches to the same topic

THRESHOLD: Be conservative - only suggest revisions for substantial improvements that would meaningfully enhance the report quality.

INSTRUCTIONS:
1. Compare the generated content to the relevant ground-truth content
2. Assess whether there are significant gaps, deficiencies, or scope misalignments
3. Only suggest a revision if the improvement would be substantial and meaningful
4. If suggesting a revision, provide a specific improved section description
5. Focus on what content should be included to better match the ground-truth scope and quality
6. If the generated content adequately covers the key points, indicate no revision is needed

FORMAT YOUR RESPONSE AS:
NEEDS_REVISION: [Yes/No]
SUGGESTED_SECTION: [Improved section description if revision needed, otherwise same as original]
REASON: [Specific explanation of significant gaps requiring revision, or why current content is adequate]
QUALITY_GAP_SEVERITY: [none/minor/moderate/significant]
"""

    # Vision-related settings for multimodal document analysis
    VISION_ENABLED_MODELS: List[str] = [
        "gpt-4-vision-preview",
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
        "claude-3-5-sonnet",
    ]

    MAX_IMAGES_PER_DOCUMENT: int = 50
    MAX_IMAGE_SIZE_MB: int = 5

    # Vision prompt templates for different functionalities
    CHATBOT_VISION_PROMPT_TEMPLATE: str = """
You are an AI assistant analyzing visual content to answer questions.

Images provided: {image_count} from files: {source_files}

Question: {question}

Context from previous conversation:
{context}

Analyze the visual elements in the images and provide a comprehensive answer based on what you can see. Focus on:
1. Text content visible in images
2. Charts, diagrams, and visual data
3. Layout and formatting
4. Any relevant visual information

Answer:
"""

    TWINCHECK_VISION_COMPARISON_PROMPT_TEMPLATE: str = """
Analyze and compare the visual content in these images from two documents.

Topic to analyze: {topic}

Document 1 Images: {doc1_image_count} images
Document 2 Images: {doc2_image_count} images

Focus on:
1. Visual elements, charts, diagrams, tables
2. Layout and formatting differences
3. Any visual information that differs between documents
4. Text content and annotations

Provide a detailed comparison focusing on the topic: {topic}
"""

    FORMCONNECT_VISION_PROMPT_TEMPLATE: str = """
Extract information from these images to fill the form template.

Template fields to fill:
{template_fields}

Images provided: {image_count}

Analyze the visual content and extract relevant information for each template field. Look for:
1. Text content in images
2. Form fields and their values
3. Tables and structured data
4. Text content and annotations
5. Signatures and checkboxes

Return the extracted information in JSON format matching the template structure.
"""

    VERADOC_VISION_PROMPT_TEMPLATE: str = """
Analyze the visual content in these images to answer the checklist question.

Question: {question}

Images provided: {image_count} from document: {filename}

Look for visual evidence that helps answer the question, including:
1. Charts, graphs, and diagrams
2. Tables and structured data
3. Images and photographs
4. Layout and formatting
5. Visual indicators or symbols

Provide a detailed answer based on the visual analysis:
"""


settings = Settings()  # type: ignore
