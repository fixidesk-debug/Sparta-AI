"""
AI Code Generator - Main Orchestration
Generates Python data analysis code from natural language queries
"""
from typing import Optional, Dict, Any, List, AsyncGenerator
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.services.ai_providers import AIProvider, AIProviderFactory, AIProviderBase
from app.services.prompt_templates import AnalysisType, PromptTemplates
from app.services.code_validator import CodeValidator
from app.services.data_context import DataContext, data_context_manager
from app.services.conversation_memory import ConversationMemory, conversation_memory_manager
from app.db.models import File
from app.core.config import settings

logger = logging.getLogger(__name__)


class CodeGenerationResult:
    """Result of code generation"""
    
    def __init__(
        self,
        code: str,
        is_valid: bool,
        error: Optional[str] = None,
        explanation: Optional[str] = None,
        analysis_type: Optional[AnalysisType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize code generation result
        
        Args:
            code: Generated code
            is_valid: Whether code passed validation
            error: Error message if validation failed
            explanation: Optional explanation of the code
            analysis_type: Type of analysis performed
            metadata: Additional metadata
        """
        self.code = code
        self.is_valid = is_valid
        self.error = error
        self.explanation = explanation
        self.analysis_type = analysis_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'code': self.code,
            'is_valid': self.is_valid,
            'error': self.error,
            'explanation': self.explanation,
            'analysis_type': self.analysis_type.value if self.analysis_type else None,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class AICodeGenerator:
    """Main AI code generation orchestrator"""
    
    def __init__(
        self,
        provider: AIProvider = AIProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Initialize AI code generator
        
        Args:
            provider: AI provider to use
            api_key: API key (uses settings if not provided)
            model: Model name (uses default if not provided)
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens to generate
        """
        self.provider_type = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Get API key from settings if not provided
        if api_key is None:
            if provider == AIProvider.OPENAI:
                api_key = settings.OPENAI_API_KEY
            elif provider == AIProvider.ANTHROPIC:
                api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        
        if not api_key:
            raise ValueError(f"API key not provided for {provider.value}")
        
        # Create provider
        self.provider: AIProviderBase = AIProviderFactory.create_provider(
            provider=provider,
            api_key=api_key,
            model=model
        )
        
        # Initialize utilities
        self.validator = CodeValidator()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.logger.info(
            f"Initialized AICodeGenerator with {provider.value} "
            f"(temp={temperature}, max_tokens={max_tokens})"
        )
    
    async def generate_code(
        self,
        query: str,
        file_id: int,
        user_id: int,
        db: Session,
        session_id: Optional[str] = None,
        analysis_type: Optional[AnalysisType] = None
    ) -> CodeGenerationResult:
        """
        Generate Python code from natural language query
        
        Args:
            query: User's natural language query
            file_id: ID of the file to analyze
            user_id: User ID
            db: Database session
            session_id: Optional conversation session ID
            analysis_type: Optional analysis type (auto-detected if not provided)
            
        Returns:
            CodeGenerationResult
        """
        try:
            self.logger.info(f"Generating code for query: {query[:100]}...")
            
            # Get or create conversation memory
            if session_id:
                memory = conversation_memory_manager.get_or_create(session_id)
            else:
                memory = ConversationMemory(max_history=20)
            
            # Get data context
            data_context = self._get_data_context(file_id, db)
            if not data_context:
                return CodeGenerationResult(
                    code="",
                    is_valid=False,
                    error="Failed to load data context"
                )
            
            # Detect analysis type if not provided
            if not analysis_type:
                analysis_type = PromptTemplates.detect_analysis_type(query)
                self.logger.info(f"Detected analysis type: {analysis_type.value}")
            
            # Build prompt
            prompt = self._build_prompt(
                query=query,
                data_context=data_context,
                memory=memory,
                analysis_type=analysis_type
            )
            
            # Generate completion
            response = await self.provider.generate_completion(
                messages=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and validate code
            code, explanation = self._parse_response(response)
            sanitized_code, is_valid, error = self.validator.validate_and_sanitize(code)
            
            if not is_valid:
                self.logger.warning(f"Code validation failed: {error}")
            else:
                self.logger.info(f"Successfully generated and validated code ({len(sanitized_code)} chars)")
            
            # Update conversation memory
            memory.add_user_message(query, metadata={'file_id': file_id})
            memory.add_assistant_message(
                explanation or "Generated code for your query",
                metadata={
                    'code': sanitized_code,
                    'analysis_type': analysis_type.value,
                    'is_valid': is_valid
                }
            )
            
            # Create result
            result = CodeGenerationResult(
                code=sanitized_code,
                is_valid=is_valid,
                error=error,
                explanation=explanation,
                analysis_type=analysis_type,
                metadata={
                    'file_id': file_id,
                    'user_id': user_id,
                    'provider': self.provider_type.value,
                    'raw_response_length': len(response)
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Error generating code: {e}")
            return CodeGenerationResult(
                code="",
                is_valid=False,
                error=f"Code generation failed: {str(e)}"
            )
    
    async def generate_code_streaming(
        self,
        query: str,
        file_id: int,
        user_id: int,
        db: Session,
        session_id: Optional[str] = None,
        analysis_type: Optional[AnalysisType] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate code with streaming response
        
        Args:
            query: User's natural language query
            file_id: ID of the file to analyze
            user_id: User ID
            db: Database session
            session_id: Optional conversation session ID
            analysis_type: Optional analysis type
            
        Yields:
            Response chunks as they arrive
        """
        try:
            self.logger.info(f"Generating streaming code for query: {query[:100]}...")
            
            # Get or create conversation memory
            if session_id:
                memory = conversation_memory_manager.get_or_create(session_id)
            else:
                memory = ConversationMemory(max_history=20)
            
            # Get data context
            data_context = self._get_data_context(file_id, db)
            if not data_context:
                yield "Error: Failed to load data context"
                return
            
            # Detect analysis type if not provided
            if not analysis_type:
                analysis_type = PromptTemplates.detect_analysis_type(query)
            
            # Build prompt
            prompt = self._build_prompt(
                query=query,
                data_context=data_context,
                memory=memory,
                analysis_type=analysis_type
            )
            
            # Stream completion
            full_response = ""
            stream_generator = await self.provider.generate_streaming_completion(
                messages=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            if stream_generator is not None:
                async for chunk in stream_generator:  # type: ignore
                    full_response += chunk
                    yield chunk
            
            # Update conversation memory with final response
            code, explanation = self._parse_response(full_response)
            sanitized_code, is_valid, error = self.validator.validate_and_sanitize(code)
            
            memory.add_user_message(query, metadata={'file_id': file_id})
            memory.add_assistant_message(
                explanation or full_response,
                metadata={
                    'code': sanitized_code,
                    'analysis_type': analysis_type.value,
                    'is_valid': is_valid
                }
            )
            
        except Exception as e:
            self.logger.exception(f"Error in streaming generation: {e}")
            yield f"\n\nError: {str(e)}"
    
    def _get_data_context(self, file_id: int, db: Session) -> Optional[DataContext]:
        """
        Get data context for a file
        
        Args:
            file_id: File ID
            db: Database session
            
        Returns:
            DataContext or None
        """
        try:
            # Check if context already exists
            context = data_context_manager.get_context(file_id)
            if context:
                return context
            
            # Get file from database
            file = db.query(File).filter(File.id == file_id).first()
            if not file:
                self.logger.error(f"File not found: {file_id}")
                return None
            
            # Create new context
            context = data_context_manager.create_context(
                file_id=file_id,
                file_path=str(file.file_path),
                filename=str(file.filename)
            )
            
            return context
            
        except Exception as e:
            self.logger.exception(f"Error getting data context: {e}")
            return None
    
    def _build_prompt(
        self,
        query: str,
        data_context: DataContext,
        memory: ConversationMemory,
        analysis_type: AnalysisType
    ) -> List[Dict[str, str]]:
        """
        Build prompt for code generation
        
        Args:
            query: User query
            data_context: Data context
            memory: Conversation memory
            analysis_type: Analysis type
            
        Returns:
            List of message dicts
        """
        # Set system message if not already set
        if not memory.system_message:
            memory.set_system_message(PromptTemplates.SYSTEM_PROMPT)
        
        # Build data context string
        context_str = PromptTemplates.build_data_context(
            filename=data_context.filename,
            rows=data_context.metadata.get('rows', 0) if data_context.metadata else 0,
            columns=data_context.metadata.get('columns', 0) if data_context.metadata else 0,
            column_names=data_context.metadata.get('column_names', []) if data_context.metadata else [],
            dtypes=data_context.metadata.get('dtypes', {}) if data_context.metadata else {},
            missing_values=data_context.metadata.get('missing_values', {}) if data_context.metadata else {},
            sample_data=data_context.get_sample_data(n=3) if data_context.df is not None else "No data available",
            statistical_summary=data_context.get_statistical_summary() if data_context.df is not None else "No data available"
        )
        
        # Build conversation history
        conversation_history = memory.get_history_text(limit=5)
        last_code = memory.get_last_code()
        last_results = memory.get_last_results()
        
        # Build full prompt
        prompt_text = PromptTemplates.build_prompt(
            analysis_type=analysis_type,
            user_query=query,
            data_context=context_str,
            conversation_history=conversation_history if len(memory.messages) > 0 else None,
            previous_code=last_code,
            previous_results=last_results
        )
        
        # Return messages in chat format, adding the new user prompt
        messages = memory.get_chat_format(limit=10, include_system=True)
        messages.append({"role": "user", "content": prompt_text})
        return messages
    
    def _parse_response(self, response: str) -> tuple[str, Optional[str]]:
        """
        Parse AI response to extract code and explanation
        
        Args:
            response: Raw AI response
            
        Returns:
            Tuple of (code, explanation)
        """
        # Try to extract code blocks
        code_blocks = self.validator.extract_code_blocks(response)
        
        if code_blocks:
            # Use the first code block
            code = code_blocks[0]
            
            # Try to extract explanation (text before first code block)
            code_marker = "```python" if "```python" in response else "```"
            parts = response.split(code_marker, 1)
            explanation = parts[0].strip() if len(parts) > 1 else None
            
            return code, explanation
        else:
            # No code blocks found, treat entire response as code
            # This handles cases where AI returns code without markdown
            return response.strip(), None
    
    def validate_code(self, code: str) -> tuple[str, bool, Optional[str]]:
        """
        Validate code without generating
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (sanitized_code, is_valid, error)
        """
        return self.validator.validate_and_sanitize(code)
    
    def get_safety_wrapped_code(self, code: str) -> str:
        """
        Get code wrapped with safety error handling
        
        Args:
            code: Python code
            
        Returns:
            Code wrapped with try/except
        """
        return self.validator.add_safety_wrapper(code)


# Helper functions for easy usage
async def generate_analysis_code(
    query: str,
    file_id: int,
    user_id: int,
    db: Session,
    provider: AIProvider = AIProvider.OPENAI,
    session_id: Optional[str] = None
) -> CodeGenerationResult:
    """
    Convenience function to generate analysis code
    
    Args:
        query: Natural language query
        file_id: File ID
        user_id: User ID
        db: Database session
        provider: AI provider to use
        session_id: Optional session ID for conversation memory
        
    Returns:
        CodeGenerationResult
    """
    generator = AICodeGenerator(provider=provider, temperature=0.3)
    return await generator.generate_code(
        query=query,
        file_id=file_id,
        user_id=user_id,
        db=db,
        session_id=session_id
    )
