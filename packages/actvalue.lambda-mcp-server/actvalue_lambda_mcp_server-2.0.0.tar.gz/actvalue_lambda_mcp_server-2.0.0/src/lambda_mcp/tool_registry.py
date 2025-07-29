import inspect
import functools
from typing import Dict, Callable, Any, get_type_hints, List, Tuple
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Handles tool registration, schema generation, and execution"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self.tool_implementations: Dict[str, Callable] = {}
    
    def _parse_docstring(self, doc: str) -> Tuple[Dict[str, str], str, Dict[str, Any]]:
        """Parse docstring to extract argument descriptions, return info, and annotations.
        
        Returns:
            Tuple of (arg_descriptions, return_description, annotations)
        """
        arg_descriptions = {}
        return_description = ""
        annotations = {}
        
        if not doc:
            return arg_descriptions, return_description, annotations
            
        lines = doc.split('\n')
        in_args = False
        in_returns = False
        
        for line in lines:
            line = line.strip()
            
            # Check for annotations in comments or special markers
            if line.startswith('//') or line.startswith('#'):
                comment_text = line.lstrip('/#').strip()
                if comment_text and 'title' not in annotations:
                    annotations['title'] = comment_text
            
            # Check for specific annotation hints
            line_normalized = line.lower().replace('-', '')
            if 'nonreadonly' in line_normalized:
                annotations['readOnlyHint'] = False
            elif 'readonly' in line_normalized:
                annotations['readOnlyHint'] = True
            if 'nondestructive' in line_normalized:
                annotations['destructiveHint'] = False
            elif 'destructive' in line_normalized:
                annotations['destructiveHint'] = True
            if 'nonidempotent' in line_normalized:
                annotations['idempotentHint'] = False
            elif 'idempotent' in line_normalized:
                annotations['idempotentHint'] = True
            if 'nonopenworld' in line_normalized:
                annotations['openWorldHint'] = False
            elif 'openworld' in line_normalized:
                annotations['openWorldHint'] = True
            
            if line.startswith('Args:'):
                in_args = True
                in_returns = False
                continue
            elif line.startswith('Returns:'):
                in_args = False
                in_returns = True
                continue
            
            if in_args:
                if not line or line.startswith('Returns:'):
                    in_args = False
                    continue
                if ':' in line:
                    arg_name, arg_desc = line.split(':', 1)
                    arg_descriptions[arg_name.strip()] = arg_desc.strip()
            elif in_returns:
                if line and not line.startswith(('Args:', 'Raises:')):
                    if return_description:
                        return_description += " " + line
                    else:
                        return_description = line
        
        return arg_descriptions, return_description, annotations
    
    def _build_input_schema(self, hints: Dict[str, Any], arg_descriptions: Dict[str, str]) -> Tuple[Dict[str, Any], List[str]]:
        """Build input schema from type hints and argument descriptions.
        
        Returns:
            Tuple of (properties, required)
        """
        properties = {}
        required = []
        
        for param_name, param_type in hints.items():
            param_schema = {"type": "string"}  # Default to string
            if param_type == int:
                param_schema["type"] = "integer"
            elif param_type == float:
                param_schema["type"] = "number"
            elif param_type == bool:
                param_schema["type"] = "boolean"
            
            if param_name in arg_descriptions:
                param_schema["description"] = arg_descriptions[param_name]
                
            properties[param_name] = param_schema
            required.append(param_name)
        
        return properties, required
    
    def _build_output_schema(self, return_type: Any, return_description: str) -> Dict[str, Any] | None:
        """Build output schema from return type and description.
        
        Returns:
            Output schema dictionary or None if no schema can be built
        """
        if return_type == Any:
            return None
            
        output_properties = {}
        output_required = []
        
        if return_description:
            if return_type == dict:
                # For dict returns, try to extract property information from description
                desc_lines = return_description.split('.')
                for line in desc_lines:
                    line = line.strip()
                    if ':' in line and not line.startswith('A '):
                        prop_parts = line.split(':', 1)
                        if len(prop_parts) == 2:
                            prop_name = prop_parts[0].strip()
                            prop_desc = prop_parts[1].strip()
                            
                            # Check if field is required first (before parsing type)
                            is_required = False
                            if "required" in prop_desc:
                                is_required = True
                            
                            # Parse type from description if present
                            prop_type = "string"  # default
                            
                            # Look for "type: " anywhere in the description
                            if "type: " in prop_desc:
                                type_start = prop_desc.find("type: ")
                                if type_start != -1:
                                    type_part = prop_desc[type_start + 6:]  # Skip "type: "
                                    # Extract just the type word (stop at comma, period, or space)
                                    type_end = len(type_part)
                                    for delimiter in [',', '.', ' ']:
                                        delimiter_pos = type_part.find(delimiter)
                                        if delimiter_pos != -1 and delimiter_pos < type_end:
                                            type_end = delimiter_pos
                                    
                                    type_value = type_part[:type_end].strip()
                                    if type_value == "boolean":
                                        prop_type = "boolean"
                                    elif type_value == "number":
                                        prop_type = "number"
                                    elif type_value == "integer":
                                        prop_type = "integer"
                                    
                                    # Remove type specification from description
                                    prop_desc = prop_desc[:type_start].strip().rstrip(',').strip()
                            
                            # Clean up required markers from description
                            prop_desc = prop_desc.replace(", required", "").replace(" required", "").replace("required.", "").replace("required", "").strip().rstrip(',').strip()
                            
                            # Add null type for non-required fields
                            if is_required:
                                type_spec = prop_type
                            else:
                                type_spec = [prop_type, "null"]
                            
                            output_properties[prop_name] = {
                                "type": type_spec,
                                "description": prop_desc
                            }
                            
                            if is_required:
                                output_required.append(prop_name)
            
            # If no specific properties found, create a generic description
            if not output_properties:
                if return_type == list:
                    output_properties["items"] = {
                        "type": "array",
                        "description": return_description
                    }
                elif return_type == dict:
                    output_properties["data"] = {
                        "type": "object", 
                        "description": return_description
                    }
                else:
                    prop_type = "string"
                    if return_type == str:
                        prop_type = "string"
                    elif return_type in (int, float):
                        prop_type = "number"
                    elif return_type == bool:
                        prop_type = "boolean"
                    
                    output_properties["result"] = {
                        "type": prop_type,
                        "description": return_description
                    }
                    output_required.append("result")
        
        output_schema = {
            "type": "object",
            "properties": output_properties,
            "required": output_required
        }
        
        # Add overall description if available
        if return_description and not output_properties:
            output_schema["description"] = return_description
            
        return output_schema

    def tool(self):
        """Decorator to register a function as an MCP tool.
        
        Uses function name, docstring, and type hints to generate the MCP tool schema.
        """
        def decorator(func: Callable):
            # Get function name and convert to camelCase for tool name
            func_name = func.__name__
            tool_name = ''.join([func_name.split('_')[0]] + [word.capitalize() for word in func_name.split('_')[1:]])
            
            # Get docstring and parse into description
            doc = inspect.getdoc(func) or ""
            description = doc.split('\n\n')[0]  # First paragraph is description
            
            # Get type hints
            hints = get_type_hints(func)
            return_type = hints.pop('return', Any)
            
            # Parse docstring components
            arg_descriptions, return_description, annotations = self._parse_docstring(doc)
            
            # Build input schema
            properties, required = self._build_input_schema(hints, arg_descriptions)
            
            # Build output schema
            output_schema = self._build_output_schema(return_type, return_description)
            
            # Create tool schema
            tool_schema = {
                "name": tool_name,
                "description": description,
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
            
            # Add output schema if available
            if output_schema:
                tool_schema["outputSchema"] = output_schema
            
            # Add annotations if any were found
            if annotations:
                tool_schema["annotations"] = annotations
            
            # Register the tool
            self.tools[tool_name] = tool_schema
            self.tool_implementations[tool_name] = func
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        
        return decorator
    
    def get_tools(self) -> List[Dict]:
        """Get list of all registered tools"""
        return list(self.tools.values())
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered"""
        return tool_name in self.tools
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any], authorization: str|None = None) -> Any:
        """Execute a registered tool with the given arguments
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments to pass to the tool
            authorization: Optional authorization token
            
        Returns:
            Result of tool execution
            
        Raises:
            KeyError: If tool is not found
            Exception: If tool execution fails
        """
        if tool_name not in self.tool_implementations:
            raise KeyError(f"Tool '{tool_name}' not found")
        
        func = self.tool_implementations[tool_name]
        func_signature = inspect.signature(func)
        
        # Only add authorization if the function accepts it
        if 'authorization' in func_signature.parameters and authorization:
            tool_args["authorization"] = authorization.replace("Bearer ", "").strip()
        
        return func(**tool_args)

# Example docstring with annotations and outputSchema:
#
# def create_record(table: str, data: dict) -> dict:
#     """Create a new record in the database
#     
#     // Create Database Record
#     A non-destructive and idempotent database operation
#     
#     Args:
#         table: The table name to insert into
#         data: The record data as a dictionary
#         
#     Returns:
#         A JSON object containing the created record details.
#         id: The unique identifier of the created record, type: integer, required.
#         name: The name field from the record, required.
#         created_at: Timestamp when the record was created.
#         status: Current status of the record, type: boolean.
#         metadata: Additional record metadata, type: object.
#     """
#     pass
#
# This will generate annotations:
# {
#   "title": "Create Database Record",
#   "destructiveHint": false,
#   "idempotentHint": true
# }
#
# And outputSchema:
# {
#   "type": "object",
#   "properties": {
#     "id": {
#       "type": "integer",
#       "description": "The unique identifier of the created record"
#     },
#     "name": {
#       "type": "string", 
#       "description": "The name field from the record"
#     },
#     "created_at": {
#       "type": ["string", "null"],
#       "description": "Timestamp when the record was created"
#     },
#     "status": {
#       "type": ["boolean" "null"],
#       "description": "Current status of the record"
#     },
#     "metadata": {
#       "type": ["object" "null"],
#       "description": "Additional record metadata"
#     }
#   },
#   "required": ["id", "name"]
# }
