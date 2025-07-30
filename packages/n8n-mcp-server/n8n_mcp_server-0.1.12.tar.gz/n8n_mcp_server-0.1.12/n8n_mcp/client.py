"""Custom HTTP client for n8n API that converts JSON strings back to objects.

This middleware handles the MCP limitation where certain fields must be defined as
'string | object' in the schema, but the n8n API expects them as objects.
"""
import json
from typing import Any, Union
import httpx


class CustomResponse(httpx.Response):
    """Custom response class that processes JSON responses to handle None values"""
    
    def json(self, **kwargs):
        """Override json() to process the response and handle None values"""
        data = super().json(**kwargs)
        return self._process_response_data(data)
    
    def _process_response_data(self, data: Any) -> Any:
        """Process response data to handle None values that don't match schema"""
        if isinstance(data, dict):
            # Create a new dict, replacing None with appropriate defaults
            result = {}
            for key, value in data.items():
                if value is None:
                    # Skip None values in responses - they cause schema validation errors
                    continue
                else:
                    result[key] = self._process_response_data(value)
            return result
        elif isinstance(data, list):
            # Process each item in the list
            return [self._process_response_data(item) for item in data if item is not None]
        else:
            return data


class N8nHTTPXClient(httpx.AsyncClient):
    """Custom HTTPX client that fixes JSON string serialization issues"""
    
    def _fix_json_strings(self, data: Any) -> Any:
        """Convert JSON strings to objects for n8n API compatibility
        
        MCP sends these fields as JSON strings, but n8n API expects them as objects.
        This middleware converts them back to objects before sending to the API.
        """
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Known fields that MCP sends as JSON strings but n8n expects as objects
                if key in ['settings', 'staticData', 'connections', 'meta', 'pinData']:
                    if value is not None and isinstance(value, str):
                        try:
                            # Try to parse the JSON string
                            parsed = json.loads(value)
                            # Use the parsed object
                            result[key] = parsed
                        except (json.JSONDecodeError, TypeError):
                            # Not valid JSON, keep as is
                            result[key] = value
                    else:
                        # Not a string or is None, keep as is
                        result[key] = value
                else:
                    # Recursively process nested structures
                    result[key] = self._fix_json_strings(value)
            return result
        elif isinstance(data, list):
            return [self._fix_json_strings(item) for item in data]
        else:
            return data
    
    async def request(self, method: str, url: Union[httpx.URL, str], **kwargs) -> httpx.Response:
        """Override request to fix JSON string issues and None values before sending"""
        # Check if there's JSON content in the request
        if 'json' in kwargs:
            kwargs['json'] = self._fix_json_strings(kwargs['json'])
            # Also remove None values from the JSON body
            kwargs['json'] = self._remove_none_values(kwargs['json'])
        
        # Check if there are query parameters and remove None values
        if 'params' in kwargs and kwargs['params']:
            kwargs['params'] = self._remove_none_from_params(kwargs['params'])
        
        # Call the parent request method
        response = await super().request(method, url, **kwargs)
        
        # Wrap the response in our custom response class
        response.__class__ = CustomResponse
        return response
    
    def _remove_none_values(self, data: Any) -> Any:
        """Remove None values from dictionaries recursively"""
        if isinstance(data, dict):
            return {k: self._remove_none_values(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            # For lists, we keep the structure but process nested dicts/lists
            # We don't remove None from arrays as that would change indices
            return [self._remove_none_values(item) if isinstance(item, (dict, list)) else item for item in data]
        else:
            return data
    
    def _remove_none_from_params(self, params: Union[dict, Any]) -> Union[dict, Any]:
        """Remove None values from query parameters"""
        if isinstance(params, dict):
            return {k: v for k, v in params.items() if v is not None}
        return params