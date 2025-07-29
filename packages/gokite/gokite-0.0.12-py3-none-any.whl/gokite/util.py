import json
from typing import Dict, Tuple, Optional, Any

def to_json_dict(schema: Any) -> dict:
    if isinstance(schema, str):
        return json.loads(schema)
    return schema

def path_join(path1: str, path2: str) -> str:
    """
    Join two paths, ensuring there is no double slash between them.
    """
    return path1.rstrip('/') + '/' + path2.lstrip('/')

def openapi_to_description(schema: dict) -> str:
    """
    Convert OpenAPI schema to a human-readable description.
    """
    schema = to_json_dict(schema)
    info_parts = []
    info_parts.append("\nAPI Endpoints:")
    # Parse OpenAPI schema for endpoints
    paths = schema.get("paths", {})
    if paths:
        for path, path_item in paths.items():
            for method, operation in paths[path].items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    # Get operation summary and description
                    summary = operation.get("summary", "No summary")
                    op_description = operation.get("description", "")

                    info_parts.append(f"\n  {method.upper()} {path}")
                    info_parts.append(f"    Summary: {summary}")
                    if op_description:
                        info_parts.append(f"    Description: {op_description}")

                    # Request body information
                    request_body = operation.get("requestBody", {})
                    if request_body:
                        info_parts.append("    Request Body:")
                        content = request_body.get("content", {})

                        for content_type, content_info in content.items():
                            info_parts.append(f"      Content-Type: {content_type}")
                            json_schema = content_info.get("schema", {})

                            # Required fields
                            required_fields = json_schema.get("required", [])
                            if required_fields:
                                info_parts.append(f"      Required fields: {', '.join(required_fields)}")

                            # Properties
                            properties = json_schema.get("properties", {})
                            if properties:
                                info_parts.append("      Fields:")
                                for field_name, field_schema in properties.items():
                                    field_type = field_schema.get("type", "unknown")
                                    field_description = field_schema.get("description", "")
                                    is_required = field_name in required_fields

                                    field_info = f"        - {field_name} ({field_type})"
                                    if is_required:
                                        field_info += " [required]"
                                    if field_description:
                                        field_info += f": {field_description}"

                                    info_parts.append(field_info)

                    # Response information
                    responses = operation.get("responses", {})
                    if responses:
                        info_parts.append("    Responses:")
                        for status_code, response_info in responses.items():
                            response_description = response_info.get("description", "No description")
                            info_parts.append(f"      {status_code}: {response_description}")

                            # Response schema
                            response_content = response_info.get("content", {})
                            for content_type, content_info in response_content.items():
                                response_schema = content_info.get("schema", {})
                                if response_schema:
                                    response_properties = response_schema.get("properties", {})
                                    if response_properties:
                                        info_parts.append("        Response fields:")
                                        for field_name, field_schema in response_properties.items():
                                            field_type = field_schema.get("type", "unknown")
                                            field_description = field_schema.get("description", "")

                                            field_info = f"          - {field_name} ({field_type})"
                                            if field_description:
                                                field_info += f": {field_description}"

                                            info_parts.append(field_info)
    else:
        info_parts.append("  No endpoints defined in schema")
    return "\n".join(info_parts)

def find_matching_endpoint(service_url: str, schema: dict) -> Tuple[Optional[str], Optional[str]]:
    """
    Find the matching endpoint and HTTP method from the OpenAPI schema.

    Args:
        service_url: The service URL to match
        schema: OpenAPI schema definition

    Returns:
        Tuple of (path, method) or (None, None) if no match found
    """
    schema = to_json_dict(schema)
    # Normalize the path (remove trailing slash if present)
    service_url = service_url.rstrip('/')

    # Extract path from server URL
    server_url = schema.get("servers", [{}])[0].get("url", "")

    paths = schema.get("paths", {})

    # Check if key in paths + server_path matches service_path
    for path_key in paths:
        # Combine server path with the path key from schema
        full_url = path_join(server_url, path_key).rstrip('/')
        if full_url == service_url:
            # Find the method that supports request body (POST, PUT, PATCH)
            for method in ["post", "put", "patch", "get"]:
                if method in paths[path_key]:
                    return path_key, method

    return None, None

def extract_input_fields_from_schema(schema: dict, service_url: str) -> Dict[str, str]:
    """
    Extract input fields from OpenAPI schema for a given service URL.

    Args:
        schema: OpenAPI schema definition
        service_url: The service URL to match

    Returns:
        Dictionary mapping parameter names to their data types.
        For GET methods, returns empty dict.
        For POST/PUT/PATCH methods, returns dict of request body parameters.
    """
    schema = to_json_dict(schema)
    path, method = find_matching_endpoint(service_url, schema)

    if not path or not method:
        return {}

    # For GET methods, return empty dict
    if method.lower() == "get":
        return {}

    # For POST/PUT/PATCH methods, extract request body parameters
    paths = schema.get("paths", {})
    if path not in paths or method not in paths[path]:
        return {}

    operation = paths[path][method]
    request_body = operation.get("requestBody", {})

    if not request_body:
        return {}

    content = request_body.get("content", {})
    if "application/json" not in content:
        return {}

    json_schema = content["application/json"].get("schema", {})
    properties = json_schema.get("properties", {})

    # Extract parameter names and their types
    input_fields = {}
    for param_name, param_schema in properties.items():
        param_type = param_schema.get("type", "string")
        input_fields[param_name] = param_type

    return input_fields

def extract_response_fields_from_schema(schema: dict, service_url: str) -> Dict[str, str]:
    """
    Extract response fields from OpenAPI schema for a given service URL.

    Args:
        schema: OpenAPI schema definition
        service_url: The service URL to match

    Returns:
        Dictionary mapping parameter names to their data types.
    """
    schema = to_json_dict(schema)
    path, method = find_matching_endpoint(service_url, schema)

    if not path or not method:
        return {}

    paths = schema.get("paths", {})
    if path not in paths or method not in paths[path]:
        return {}

    operation = paths[path][method]
    responses = operation.get("responses", {})

    # Look for 200 response first, then fallback to any success response
    response_schema = None
    for status_code in ["200", "201", "202"]:
        if status_code in responses:
            response_content = responses[status_code].get("content", {})
            if "application/json" in response_content:
                response_schema = response_content["application/json"].get("schema", {})
                break

    # If no specific success response found, try to find any response with content
    if not response_schema:
        for status_code, response in responses.items():
            response_content = response.get("content", {})
            if "application/json" in response_content:
                response_schema = response_content["application/json"].get("schema", {})
                break

    if not response_schema:
        return {}

    # Handle different response schema structures
    properties = {}

    # Direct properties
    if "properties" in response_schema:
        properties = response_schema["properties"]
    # Reference to another schema
    elif "$ref" in response_schema:
        ref_path = response_schema["$ref"]
        if ref_path.startswith("#/components/schemas/"):
            schema_name = ref_path.split("/")[-1]
            components = schema.get("components", {}).get("schemas", {})
            if schema_name in components:
                properties = components[schema_name].get("properties", {})
    # Array response
    elif response_schema.get("type") == "array":
        items_schema = response_schema.get("items", {})
        if "properties" in items_schema:
            properties = items_schema["properties"]
        elif "$ref" in items_schema:
            ref_path = items_schema["$ref"]
            if ref_path.startswith("#/components/schemas/"):
                schema_name = ref_path.split("/")[-1]
                components = schema.get("components", {}).get("schemas", {})
                if schema_name in components:
                    properties = components[schema_name].get("properties", {})

    # Extract parameter names and their types
    response_fields = {}
    for param_name, param_schema in properties.items():
        param_type = param_schema.get("type", "string")
        response_fields[param_name] = param_type

    return response_fields

def validate_payload_against_openapi(payload: dict, schema: dict, path: str, method: str) -> bool:
    """
    Validate payload against OpenAPI schema for a specific endpoint.

    Args:
        payload: The payload to validate
        schema: OpenAPI schema definition
        path: The path to validate against
        method: The HTTP method to validate against

    Returns:
        True if payload is valid, raises KiteError if not
    """
    from .exceptions import KiteError

    schema = to_json_dict(schema)

    try:
        paths = schema.get("paths", {})
        if path not in paths or method not in paths[path]:
            raise KiteError(f"Endpoint {method.upper()} {path} not found in schema")

        operation = paths[path][method]

        # For GET requests, validate query parameters
        if method.lower() == "get":
            parameters = operation.get("parameters", [])
            for param in parameters:
                if param.get("required", False):
                    param_name = param["name"]
                    if param_name not in payload:
                        raise KiteError(f"Missing required query parameter: {param_name}")
        else:
            # For other methods, validate request body
            request_body = operation.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})

                # Check application/json content
                if "application/json" in content:
                    json_schema = content["application/json"].get("schema", {})

                    # Validate required fields
                    required_fields = json_schema.get("required", [])
                    for field in required_fields:
                        if field not in payload:
                            raise KiteError(f"Missing required field: {field}")

                    # Validate field types (basic validation)
                    properties = json_schema.get("properties", {})
                    for field, value in payload.items():
                        if field in properties:
                            field_schema = properties[field]
                            field_type = field_schema.get("type")

                            if field_type == "string" and not isinstance(value, str):
                                raise KiteError(f"Field '{field}' must be a string")
                            elif field_type == "number" and not isinstance(value, (int, float)):
                                raise KiteError(f"Field '{field}' must be a number")
                            elif field_type == "integer" and not isinstance(value, int):
                                raise KiteError(f"Field '{field}' must be an integer")
                            elif field_type == "boolean" and not isinstance(value, bool):
                                raise KiteError(f"Field '{field}' must be a boolean")
                            elif field_type == "array" and not isinstance(value, list):
                                raise KiteError(f"Field '{field}' must be an array")
                            elif field_type == "object" and not isinstance(value, dict):
                                raise KiteError(f"Field '{field}' must be an object")

        return True

    except KiteError:
        raise
    except Exception as e:
        raise KiteError(f"Schema validation error: {str(e)}")
