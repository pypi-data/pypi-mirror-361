"""
Anthropic Provider

Provider class for Anthropic Claude models with batch processing.
"""

import json
from textwrap import dedent
from typing import List, Type, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel
from anthropic import Anthropic
from tokencost import calculate_cost_by_tokens
from .base import BaseBatchProvider
from ..citations import Citation


class AnthropicBatchProvider(BaseBatchProvider):
    """Anthropic batch processing provider."""
    
    # Batch limitations from https://docs.anthropic.com/en/docs/build-with-claude/batch-processing#batch-limitations
    MAX_REQUESTS = 100_000      # Max requests per batch
    MAX_TOTAL_SIZE_MB = 256     # Max total batch size in MB
    
    # Batch API offers 50% discount on all usage
    BATCH_DISCOUNT = 0.5
    
    def __init__(self, rate_limits: Dict[str, int] = None):
        super().__init__(rate_limits)
        self.client = Anthropic()  # Automatically reads ANTHROPIC_API_KEY from env
    
    def get_default_rate_limits(self) -> Dict[str, int]:
        """Get default rate limits for Anthropic (basic tier)."""
        return {
            "batches_per_minute": 5,
            "requests_per_minute": 500
        }
    
    def validate_batch(self, messages: List[List[dict]], response_model: Optional[Type[BaseModel]]) -> None:
        if not messages:
            return
            
        if len(messages) > self.MAX_REQUESTS:
            raise ValueError(f"Too many requests: {len(messages)} > {self.MAX_REQUESTS}")
        
        total_size = sum(len(str(msg)) for msg in messages)
        max_size_bytes = self.MAX_TOTAL_SIZE_MB * 1024 * 1024
        if total_size > max_size_bytes:
            raise ValueError(f"Batch too large: ~{total_size/1024/1024:.1f}MB > {self.MAX_TOTAL_SIZE_MB}MB")
        
        # Validate message format
        for i, conversation in enumerate(messages):
            if not isinstance(conversation, list):
                raise ValueError(f"Message {i} must be a list of message objects")
            
            for j, message in enumerate(conversation):
                if not isinstance(message, dict):
                    raise ValueError(f"Message {i}[{j}] must be a dictionary")
                
                if "role" not in message:
                    raise ValueError(f"Message {i}[{j}] missing required 'role' field")
                
                if "content" not in message:
                    raise ValueError(f"Message {i}[{j}] missing required 'content' field")
                
                valid_roles = {"user", "assistant", "system"}
                if message["role"] not in valid_roles:
                    raise ValueError(f"Message {i}[{j}] has invalid role '{message['role']}'. Must be one of: {valid_roles}")
        
        # Check for nested models with citations
        if response_model and self.has_citations_enabled(messages):
            # Check if model has nested Pydantic models
            for field_name, field_info in response_model.model_fields.items():
                field_type = field_info.annotation
                # Check if field type is a BaseModel subclass (nested model)
                if (hasattr(field_type, '__mro__') and 
                    BaseModel in field_type.__mro__ and 
                    field_type != BaseModel):
                    raise ValueError(
                        f"Citations are only supported with flat Pydantic models. "
                        f"Field '{field_name}' contains a nested model '{field_type.__name__}'. "
                        f"Please use a flat model structure when enabling citations."
                    )
    
    def has_citations_enabled(self, messages: List[List[dict]]) -> bool:
        """Check if any message has citations enabled."""
        for conversation in messages:
            for msg in conversation:
                content = msg.get("content", [])
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "document":
                            citations = item.get("citations", {})
                            if isinstance(citations, dict) and citations.get("enabled", False):
                                return True
        return False
    
    def prepare_batch_requests(self, messages: List[List[dict]], response_model: Optional[Type[BaseModel]], **kwargs) -> List[dict]:
        if not messages:
            return []
        
        batch_requests = []
        for i, conversation in enumerate(messages):
            system_messages = [msg["content"] for msg in conversation if msg.get("role") == "system"]
            user_messages = [msg for msg in conversation if msg.get("role") != "system"]
            
            if response_model:
                schema = response_model.model_json_schema()
                system_message = dedent(f"""
                    As a genius expert, your task is to understand the content and provide
                    the parsed objects in json that match the following json_schema:

                    {json.dumps(schema, indent=2, ensure_ascii=False)}

                    Make sure to return an instance of the JSON, not the schema itself
                """).strip()
                
                combined_system = system_message
                if system_messages:
                    original_system = "\n\n".join(system_messages)
                    combined_system = f"{original_system}\n\n{system_message}"
            else:
                combined_system = "\n\n".join(system_messages) if system_messages else None
            
            request = {
                "custom_id": f"request_{i}",
                "params": {
                    "messages": user_messages,
                    **kwargs
                }
            }
            if combined_system:
                request["params"]["system"] = combined_system
                
            batch_requests.append(request)
        
        return batch_requests
    
    def create_batch(self, requests: List[dict]) -> str:
        batch_response = self.client.messages.batches.create(requests=requests)
        return batch_response.id
    
    def get_batch_status(self, batch_id: str) -> str:
        batch_status = self.client.messages.batches.retrieve(batch_id)
        return batch_status.processing_status
    
    def _is_batch_completed(self, status: str) -> bool:
        return status == "ended"
    
    def _is_batch_failed(self, status: str) -> bool:
        return status in ["canceled", "expired"]
    
    def get_results(self, batch_id: str) -> List[Any]:
        return self.client.messages.batches.results(batch_id)
    
    def _parse_content_blocks(self, content_blocks: List[Any]) -> tuple[str, List[Citation]]:
        """Parse content blocks to extract text and citations.
        
        Args:
            content_blocks: List of content blocks from API response
            
        Returns:
            Tuple of (full_text, citations)
        """
        full_text = ""
        all_citations = []
        
        for block in content_blocks:
            if not hasattr(block, 'text'):
                continue
                
            full_text += block.text
            
            if not hasattr(block, 'citations') or not block.citations:
                continue
                
            for cit in block.citations:
                citation_data = {
                    'type': getattr(cit, 'type', ''),
                    'cited_text': getattr(cit, 'cited_text', ''),
                    'document_index': getattr(cit, 'document_index', 0),
                    'document_title': getattr(cit, 'document_title', None),
                }
                
                # Add location fields based on type
                cit_type = getattr(cit, 'type', '')
                if cit_type == 'char_location':
                    citation_data['start_char_index'] = getattr(cit, 'start_char_index', None)
                    citation_data['end_char_index'] = getattr(cit, 'end_char_index', None)
                elif cit_type == 'page_location':
                    citation_data['start_page_number'] = getattr(cit, 'start_page_number', None)
                    citation_data['end_page_number'] = getattr(cit, 'end_page_number', None)
                elif cit_type == 'content_block_location':
                    citation_data['start_block_index'] = getattr(cit, 'start_block_index', None)
                    citation_data['end_block_index'] = getattr(cit, 'end_block_index', None)
                
                all_citations.append(Citation(**citation_data))
        
        return full_text, all_citations
    
    def _extract_json_from_text(self, text: str, response_model: Type[BaseModel]) -> BaseModel:
        """Extract JSON from text and parse into Pydantic model.
        
        Args:
            text: Text containing JSON
            response_model: Pydantic model class
            
        Returns:
            Parsed Pydantic model instance
            
        Raises:
            ValueError: If no valid JSON found
        """
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx == -1 or end_idx <= start_idx:
            raise ValueError(f"No JSON found in response: {text}")
            
        json_str = text[start_idx:end_idx]
        json_data = json.loads(json_str)
        return response_model(**json_data)
    
    def _map_citations_to_fields(self, content_blocks: List[Any], response_model: Type[BaseModel]) -> Dict[str, List[Citation]]:
        """
        Map citations to field names based on JSON structure analysis.
        
        Args:
            content_blocks: List of content blocks from API response
            response_model: Pydantic model for field names
            
        Returns:
            Dict mapping field names to their citations
        """
        field_citations = {}
        current_field = None
        json_buffer = ""
        
        for block in content_blocks:
            text = getattr(block, 'text', '')
            json_buffer += text
            
            # Try to identify field names from JSON structure
            # Look for patterns like '"field_name": ' before a value
            import re
            field_pattern = r'"(\w+)"\s*:\s*$'
            match = re.search(field_pattern, json_buffer)
            if match:
                current_field = match.group(1)
            
            # If this block has citations and we know the current field
            if hasattr(block, 'citations') and block.citations and current_field:
                if current_field not in field_citations:
                    field_citations[current_field] = []
                
                # Convert API citations to our Citation objects
                for cit in block.citations:
                    citation = Citation(
                        type=getattr(cit, 'type', ''),
                        cited_text=getattr(cit, 'cited_text', ''),
                        document_index=getattr(cit, 'document_index', 0),
                        document_title=getattr(cit, 'document_title', None),
                        start_page_number=getattr(cit, 'start_page_number', None),
                        end_page_number=getattr(cit, 'end_page_number', None),
                        start_char_index=getattr(cit, 'start_char_index', None),
                        end_char_index=getattr(cit, 'end_char_index', None),
                        start_content_block_index=getattr(cit, 'start_content_block_index', None),
                        end_content_block_index=getattr(cit, 'end_content_block_index', None)
                    )
                    field_citations[current_field].append(citation)
        
        return field_citations
    
    def parse_results(self, results: List[Any], response_model: Optional[Type[BaseModel]], enable_citations: bool) -> tuple:
        """
        Parse results according to 4 modes:
        1. Plain text (no response_model, no citations)
        2. Structured only (response_model, no citations)
        3. Text + Citations (no response_model, citations)
        4. Structured + Field Citations (response_model + citations)
        """
        if not results:
            return [], None
            
        parsed_results = []
        all_citations = []
        errors = []
        
        for result in results:
            try:
                if result.result.type != "succeeded":
                    errors.append(result.model_dump())
                    continue
                    
                content = result.result.message.content
                
                # Mode 1 & 2: No citations
                if not enable_citations:
                    # Extract text from content
                    if isinstance(content, list):
                        message_content = content[0].text if content else ""
                    else:
                        message_content = content.text if hasattr(content, 'text') else str(content)
                    
                    if response_model:
                        # Mode 2: Structured only
                        model_instance = self._extract_json_from_text(message_content, response_model)
                        parsed_results.append(model_instance)
                    else:
                        # Mode 1: Plain text
                        parsed_results.append(message_content)
                
                # Mode 3 & 4: Citations enabled
                elif enable_citations and isinstance(content, list):
                    # Extract full text and citations
                    full_text, citations = self._parse_content_blocks(content)
                    
                    if response_model:
                        # Mode 4: Structured + Field Citations
                        model_instance = self._extract_json_from_text(full_text, response_model)
                        parsed_results.append(model_instance)
                        
                        # Map citations to fields
                        field_citations = self._map_citations_to_fields(content, response_model)
                        all_citations.append(field_citations)
                    else:
                        # Mode 3: Text + Citations
                        parsed_results.append(full_text)
                        all_citations.extend(citations)
                elif enable_citations and not isinstance(content, list):
                    # Single content block with potential citations
                    message_content = content.text if hasattr(content, 'text') else str(content)
                    
                    if response_model:
                        # Mode 4: Structured + Field Citations (single block)
                        model_instance = self._extract_json_from_text(message_content, response_model)
                        parsed_results.append(model_instance)
                        # Check if single block has citations
                        if hasattr(content, 'citations') and content.citations:
                            field_citations = self._map_citations_to_fields([content], response_model)
                            all_citations.append(field_citations)
                        else:
                            all_citations.append({})
                    else:
                        # Mode 3: Text + Citations (single block)
                        parsed_results.append(message_content)
                        if hasattr(content, 'citations') and content.citations:
                            _, citations = self._parse_content_blocks([content])
                            all_citations.extend(citations)
                else:
                    # Fallback: treat as plain text
                    message_content = str(content)
                    if response_model:
                        model_instance = self._extract_json_from_text(message_content, response_model)
                        parsed_results.append(model_instance)
                    else:
                        parsed_results.append(message_content)
                    
            except Exception as e:
                errors.append({"error": str(e), "result": result.model_dump()})
            
        if errors:
            print(f"\n❌ Batch processing errors ({len(errors)} failed):")
            for i, error in enumerate(errors, 1):
                print(f"\nError {i}:")
                if "error" in error:
                    print(f"  Exception: {error['error']}")
                if "result" in error:
                    result_data = error["result"]
                    if isinstance(result_data, dict):
                        if "result" in result_data and isinstance(result_data["result"], dict):
                            res = result_data["result"]
                            if "type" in res:
                                print(f"  Result type: {res['type']}")
                            if "error" in res:
                                print(f"  API error: {res['error']}")
                        if "custom_id" in result_data:
                            print(f"  Custom ID: {result_data['custom_id']}")
                    else:
                        print(f"  Result data: {result_data}")
                print(f"  Full error: {error}")
            raise RuntimeError(f"Some batch requests failed: {len(errors)} errors")
        
        # Return appropriate citation format based on mode
        if not enable_citations:
            return parsed_results, None
        elif response_model:
            # Mode 4: List of FieldCitations (one per result)
            return parsed_results, all_citations
        else:
            # Mode 3: Flat list of citations
            return parsed_results, all_citations
    
    def _extract_usage_from_result(self, result: Any) -> Dict[str, Any]:
        """
        Extract usage data from API response result.
        
        Args:
            result: API response result object
            
        Returns:
            Dictionary with usage data (input_tokens, output_tokens, service_tier)
        """
        usage_data = {
            "input_tokens": 0,
            "output_tokens": 0,
            "service_tier": "batch"
        }
        
        try:
            if (hasattr(result, 'result') and 
                hasattr(result.result, 'message') and 
                hasattr(result.result.message, 'usage')):
                
                usage = result.result.message.usage
                usage_data["input_tokens"] = getattr(usage, 'input_tokens', 0)
                usage_data["output_tokens"] = getattr(usage, 'output_tokens', 0)
                usage_data["service_tier"] = getattr(usage, 'service_tier', 'standard')
        except Exception:
            # If we can't extract usage, return default values
            pass
            
        return usage_data
    
    def _calculate_token_cost(self, num_tokens: int, model: str, token_type: Literal['input', 'output', 'cached']) -> float:
        """
        Calculate cost for tokens using tokencost library.
        
        Args:
            num_tokens: Number of tokens
            model: Model name
            token_type: Type of token ('input', 'output', or 'cached')
            
        Returns:
            Cost in USD
        """
        if num_tokens == 0:
            return 0.0
            
        try:
            # tokencost expects model names in specific format
            normalized_model = model.lower()
            cost = calculate_cost_by_tokens(num_tokens, normalized_model, token_type)
            return float(cost)
        except Exception:
            # If tokencost fails, return 0 rather than breaking
            return 0.0
    
    def _apply_batch_discount(self, cost: float, service_tier: str) -> float:
        """
        Apply batch discount if service_tier is 'batch'.
        
        Args:
            cost: Original cost
            service_tier: Service tier ('batch' or 'standard')
            
        Returns:
            Discounted cost
        """
        if service_tier == "batch":
            return cost * self.BATCH_DISCOUNT
        return cost
    
    def _aggregate_batch_usage(self, results: List[Any]) -> Dict[str, Any]:
        """
        Aggregate usage data across all results in a batch.
        
        Args:
            results: List of API result objects
            
        Returns:
            Dictionary with aggregated usage data
        """
        total_input_tokens = 0
        total_output_tokens = 0
        service_tier = "batch"
        request_count = 0
        
        for result in results:
            usage_data = self._extract_usage_from_result(result)
            total_input_tokens += usage_data["input_tokens"]
            total_output_tokens += usage_data["output_tokens"]
            service_tier = usage_data["service_tier"]  # Should be same for all in batch
            request_count += 1
            
        return {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "service_tier": service_tier,
            "request_count": request_count
        }
    
    def get_batch_usage_costs(self, batch_id: str, model: str) -> Dict[str, Any]:
        """
        Get usage costs for a completed batch.
        
        Args:
            batch_id: ID of the batch
            model: Model name used for the batch
            
        Returns:
            Dictionary with cost information
        """
        if batch_id == "empty_batch":
            return {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
                "service_tier": "batch",
                "request_count": 0
            }
        
        try:
            # Get raw results to extract usage
            raw_results = self.get_results(batch_id)
            usage_data = self._aggregate_batch_usage(raw_results)
            
            # Calculate costs
            input_cost = self._calculate_token_cost(
                usage_data["total_input_tokens"], 
                model, 
                "input"
            )
            output_cost = self._calculate_token_cost(
                usage_data["total_output_tokens"], 
                model, 
                "output"
            )
            
            # Apply batch discount
            input_cost = self._apply_batch_discount(input_cost, usage_data["service_tier"])
            output_cost = self._apply_batch_discount(output_cost, usage_data["service_tier"])
            
            total_cost = input_cost + output_cost
            
            return {
                "total_input_tokens": usage_data["total_input_tokens"],
                "total_output_tokens": usage_data["total_output_tokens"],
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "service_tier": usage_data["service_tier"],
                "request_count": usage_data["request_count"]
            }
            
        except Exception:
            # If we can't get costs, return zeros
            return {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
                "service_tier": "batch",
                "request_count": 0
            }