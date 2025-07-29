"""
HACS Anthropic Integration

This package provides Anthropic Claude integration for HACS (Healthcare Agent
Communication Standard). It enables seamless integration between HACS clinical
data models and Anthropic's Claude models for structured healthcare AI applications.
"""

import json
import os
from collections.abc import Callable
from typing import Any, List, Union

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None

from pydantic import BaseModel

if not anthropic:
    raise ImportError("anthropic not available. Install with: pip install anthropic")

try:
    import instructor
except ImportError:
    instructor = None

# Import HACS models for type hints
try:
    from hacs_models import Patient, Observation, Encounter, AgentMessage
    from hacs_core import MemoryBlock, Evidence
except ImportError:
    # Fallback for type hints when packages aren't available
    Patient = Observation = Encounter = AgentMessage = MemoryBlock = Evidence = Any


class AnthropicClient:
    """Enhanced Anthropic client with HACS integration."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int = 3,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        top_k: int | None = None,
    ):
        """Initialize Anthropic client with configurable parameters."""
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k

        self.client = Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    def analyze_patient(
        self,
        query: str,
        patient_data: Union[List[Union[Patient, Observation, Encounter, AgentMessage, MemoryBlock, Evidence]], 
                           Patient, Observation, Encounter, AgentMessage, MemoryBlock, Evidence],
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> str:
        """
        Analyze patient data using natural language query.
        
        Args:
            query: Natural language query about the patient data
            patient_data: Single resource or list of HACS resources
            model: Override model for this request
            max_tokens: Override max tokens for this request
            temperature: Override temperature for this request
            
        Returns:
            Analysis result as a string
        """
        # Convert single resource to list
        if not isinstance(patient_data, list):
            patient_data = [patient_data]
        
        # Serialize patient data to JSON for context
        try:
            data_context = []
            for item in patient_data:
                if hasattr(item, 'model_dump'):
                    # Pydantic model
                    data_context.append(item.model_dump())
                elif hasattr(item, 'dict'):
                    # Older Pydantic models
                    data_context.append(item.dict())
                else:
                    # Fallback to string representation
                    data_context.append(str(item))
            
            context_str = json.dumps(data_context, indent=2, default=str)
        except Exception as e:
            context_str = f"Error serializing patient data: {e}"
        
        # Create system prompt for healthcare analysis
        system_prompt = """You are a healthcare AI assistant with deep knowledge of clinical data analysis, 
        FHIR standards, and medical terminology. You provide thoughtful, evidence-based analysis of patient data.
        
        When analyzing patient data:
        - Use proper medical terminology
        - Consider clinical context and relationships between data points
        - Identify potential clinical insights and patterns
        - Highlight any concerning findings that may need attention
        - Be precise and professional in your analysis
        
        Always base your analysis on the provided patient data and avoid speculation beyond what the data supports."""
        
        # Create user message with context
        user_message = f"""
        Patient Data Context:
        {context_str}
        
        Query: {query}
        
        Please provide a comprehensive analysis based on the patient data provided.
        """
        
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.chat(
                messages=messages,
                system=system_prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract text content from response
            if response.content:
                content = ""
                for block in response.content:
                    if block.type == "text":
                        content += block.text
                return content
            return "No response generated"
            
        except Exception as e:
            return f"Error analyzing patient data: {e}"

    def generate_clinical_summary(
        self,
        patient_data: Union[List[Union[Patient, Observation, Encounter, AgentMessage, MemoryBlock, Evidence]], 
                           Patient, Observation, Encounter, AgentMessage, MemoryBlock, Evidence],
        summary_type: str = "comprehensive",
        **kwargs
    ) -> str:
        """
        Generate a clinical summary of patient data.
        
        Args:
            patient_data: Single resource or list of HACS resources
            summary_type: Type of summary (comprehensive, brief, problem-focused)
            
        Returns:
            Clinical summary as a string
        """
        summary_prompts = {
            "comprehensive": "Generate a comprehensive clinical summary including patient demographics, medical history, current observations, and clinical insights.",
            "brief": "Generate a brief clinical summary highlighting the most important findings and current status.",
            "problem-focused": "Generate a problem-focused summary identifying key clinical issues and concerns."
        }
        
        query = summary_prompts.get(summary_type, summary_prompts["comprehensive"])
        
        return self.analyze_patient(
            query=query,
            patient_data=patient_data,
            temperature=0.3,  # Lower temperature for more consistent summaries
            **kwargs
        )

    def extract_clinical_insights(
        self,
        patient_data: Union[List[Union[Patient, Observation, Encounter, AgentMessage, MemoryBlock, Evidence]], 
                           Patient, Observation, Encounter, AgentMessage, MemoryBlock, Evidence],
        **kwargs
    ) -> dict[str, Any]:
        """
        Extract structured clinical insights from patient data.
        
        Args:
            patient_data: Single resource or list of HACS resources
            
        Returns:
            Dictionary with clinical insights
        """
        query = """
        Extract key clinical insights from this patient data and provide them in a structured format.
        Focus on:
        - Key findings and observations
        - Potential clinical concerns
        - Trends or patterns in the data
        - Recommendations for further care
        """
        
        try:
            analysis = self.analyze_patient(
                query=query,
                patient_data=patient_data,
                temperature=0.2,  # Lower temperature for structured output
                **kwargs
            )
            
            # Try to parse as JSON if possible, otherwise return as text
            try:
                return json.loads(analysis)
            except:
                return {"analysis": analysis}
                
        except Exception as e:
            return {"error": f"Error extracting insights: {e}"}

    def chat(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: dict[str, Any] | None = None,
        **kwargs,
    ) -> anthropic.types.Message:
        """Standard message completion."""

        return self.client.messages.create(
            model=model or self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature or self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            system=system,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )

    def structured_output(
        self,
        messages: list[dict[str, str]],
        response_model: type[BaseModel],
        system: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        max_retries: int = 3,
        **kwargs,
    ) -> BaseModel:
        """Generate structured output by using tool calling."""

        # Create tool schema from Pydantic model
        tool_schema = {
            "name": "generate_structured_response",
            "description": f"Generate a structured response using the {response_model.__name__} model",
            "input_schema": response_model.model_json_schema(),
        }

        # Add instruction to use the tool
        if system:
            system += (
                " You must use the generate_structured_response tool to provide your response."
            )
        else:
            system = "You must use the generate_structured_response tool to provide your response."

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=model or self.model,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=temperature or self.temperature,
                    top_p=self.top_p,
                    top_k=self.top_k,
                    system=system,
                    messages=messages,
                    tools=[tool_schema],
                    tool_choice={"type": "tool", "name": "generate_structured_response"},
                    **kwargs,
                )

                # Extract tool use from response
                for content in response.content:
                    if content.type == "tool_use":
                        return response_model(**content.input)

                raise ValueError("No tool use found in response")

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                continue

        raise RuntimeError(f"Failed to generate structured output after {max_retries} attempts")

    def tool_call(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]],
        system: str | None = None,
        tool_choice: dict[str, Any] | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs,
    ) -> anthropic.types.Message:
        """Tool calling."""

        return self.client.messages.create(
            model=model or self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature or self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            system=system,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs,
        )


class AnthropicStructuredGenerator:
    """Specialized class for generating HACS models with Anthropic Claude."""

    def __init__(
        self,
        client: AnthropicClient | None = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.3,  # Lower temperature for structured output
        system_prompt: str | None = None,
    ):
        """Initialize structured generator."""
        self.client = client or AnthropicClient(model=model, temperature=temperature)
        self.system_prompt = system_prompt or self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        """Default system prompt for healthcare AI."""
        return """You are a healthcare AI assistant that generates structured,
        FHIR-compliant healthcare data. Always use proper medical terminology
        and follow healthcare data standards. Ensure all generated data is
        realistic and clinically appropriate. You have extensive knowledge of
        medical terminology, clinical workflows, and healthcare standards."""

    def generate_hacs_resource(
        self,
        resource_type: type[BaseModel],
        user_prompt: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> BaseModel:
        """Generate a HACS resource from natural language."""

        messages = [{"role": "user", "content": user_prompt}]

        return self.client.structured_output(
            messages=messages,
            response_model=resource_type,
            system=system_prompt or self.system_prompt,
            **kwargs,
        )

    def generate_batch_resources(
        self,
        resource_type: type[BaseModel],
        prompts: list[str],
        system_prompt: str | None = None,
        **kwargs,
    ) -> list[BaseModel]:
        """Generate multiple HACS resources."""

        results = []
        for prompt in prompts:
            try:
                resource = self.generate_hacs_resource(
                    resource_type=resource_type,
                    user_prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs,
                )
                results.append(resource)
            except Exception as e:
                print(f"Error generating resource for prompt '{prompt}': {e}")
                results.append(None)

        return results

    def generate_with_context(
        self,
        resource_type: type[BaseModel],
        user_prompt: str,
        context_data: dict[str, Any],
        system_prompt: str | None = None,
        **kwargs,
    ) -> BaseModel:
        """Generate HACS resource with additional context."""

        context_str = json.dumps(context_data, indent=2)
        enhanced_prompt = f"""
        Context information:
        {context_str}

        User request: {user_prompt}

        Please generate the requested resource using the provided context.
        """

        return self.generate_hacs_resource(
            resource_type=resource_type,
            user_prompt=enhanced_prompt,
            system_prompt=system_prompt,
            **kwargs,
        )


class AnthropicToolRegistry:
    """Registry for Anthropic tools and functions."""

    def __init__(self):
        self.tools = {}
        self.functions = {}

    def register_tool(
        self, name: str, function: Callable, description: str, input_schema: dict[str, Any]
    ):
        """Register a tool for Anthropic tool calling."""

        self.tools[name] = {"name": name, "description": description, "input_schema": input_schema}
        self.functions[name] = function

    def register_hacs_tool(
        self, name: str, function: Callable, description: str, input_model: type[BaseModel]
    ):
        """Register a tool using a HACS/Pydantic model for input schema."""

        self.register_tool(
            name=name,
            function=function,
            description=description,
            input_schema=input_model.model_json_schema(),
        )

    def get_tools(self) -> list[dict[str, Any]]:
        """Get all registered tools."""
        return list(self.tools.values())

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a registered tool/function."""

        if name in self.functions:
            return self.functions[name](**arguments)

        raise ValueError(f"Tool/function '{name}' not found")

    def create_tool_choice(self, tool_name: str) -> dict[str, Any]:
        """Create tool choice for specific tool."""
        return {"type": "tool", "name": tool_name}


class AnthropicConversationManager:
    """Manages multi-turn conversations with context and memory."""

    def __init__(
        self,
        client: AnthropicClient | None = None,
        system_prompt: str | None = None,
        max_context_length: int = 100000,  # Claude's context window
    ):
        """Initialize conversation manager."""
        self.client = client or AnthropicClient()
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.max_context_length = max_context_length
        self.conversation_history: list[dict[str, str]] = []
        self.context_data: dict[str, Any] = {}

    def _default_system_prompt(self) -> str:
        """Default system prompt for healthcare conversations."""
        return """You are a healthcare AI assistant specializing in clinical data
        and workflows. You help healthcare professionals with tasks like patient
        data analysis, clinical documentation, and decision support. Always maintain
        patient privacy and follow healthcare best practices."""

    def add_context(self, key: str, value: Any):
        """Add context data to the conversation."""
        self.context_data[key] = value

    def clear_context(self):
        """Clear all context data."""
        self.context_data.clear()

    def send_message(
        self,
        message: str,
        include_context: bool = True,
        tools: list[dict[str, Any]] | None = None,
        **kwargs,
    ) -> anthropic.types.Message:
        """Send a message and get response."""

        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})

        # Prepare system prompt with context
        system_prompt = self.system_prompt
        if include_context and self.context_data:
            context_str = json.dumps(self.context_data, indent=2)
            system_prompt += f"\n\nContext data:\n{context_str}"

        # Get response
        response = self.client.chat(
            messages=self.conversation_history, system=system_prompt, tools=tools, **kwargs
        )

        # Add assistant response to history
        if response.content:
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    content += f"[Tool used: {block.name}]"

            self.conversation_history.append({"role": "assistant", "content": content})

        return response

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()

    def get_history(self) -> list[dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()


# Convenience functions for creating common instances
def create_anthropic_client(
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
    base_url: str | None = None,
    **kwargs,
) -> AnthropicClient:
    """Create an Anthropic client with default configuration."""
    return AnthropicClient(model=model, api_key=api_key, base_url=base_url, **kwargs)


def create_structured_generator(
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.3,
    api_key: str | None = None,
    base_url: str | None = None,
    **kwargs,
) -> AnthropicStructuredGenerator:
    """Create a structured generator with default configuration."""
    client = create_anthropic_client(
        model=model, api_key=api_key, base_url=base_url, temperature=temperature, **kwargs
    )
    return AnthropicStructuredGenerator(client=client)


def create_conversation_manager(
    model: str = "claude-3-5-sonnet-20241022",
    api_key: str | None = None,
    base_url: str | None = None,
    system_prompt: str | None = None,
    **kwargs,
) -> AnthropicConversationManager:
    """Create a conversation manager with default configuration."""
    client = create_anthropic_client(model=model, api_key=api_key, base_url=base_url, **kwargs)
    return AnthropicConversationManager(client=client, system_prompt=system_prompt)


__all__ = [
    "AnthropicClient",
    "AnthropicStructuredGenerator",
    "AnthropicToolRegistry",
    "AnthropicConversationManager",
    "create_anthropic_client",
    "create_structured_generator",
    "create_conversation_manager",
]
