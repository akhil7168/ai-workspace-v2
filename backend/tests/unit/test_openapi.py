import json
import re
from pathlib import Path

from fastapi.routing import APIRoute

from app.main import app


def test_openapi_covers_registered_routes_and_documents_contracts():
    schema = app.openapi()
    assert schema["openapi"].startswith("3.")
    json.dumps(schema)

    routes = []
    pending = list(app.routes)
    while pending:
        route = pending.pop()
        if isinstance(route, APIRoute):
            if route.include_in_schema:
                routes.append(route)
            continue

        included_router = getattr(route, "original_router", None)
        if included_router is not None:
            pending.extend(included_router.routes)

    operations = {
        (method.lower(), route.path): route
        for route in routes
        for method in route.methods or ()
        if method not in {"HEAD", "OPTIONS"}
    }

    assert len(operations) == len(routes)
    openapi_operations = {
        (method, path): operation
        for path, path_item in schema["paths"].items()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    }
    assert openapi_operations.keys() == operations.keys()
    assert len(openapi_operations) == len(operations)

    public_paths = {
        "/",
        "/health/",
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/logout",
    }
    operation_ids = []
    for key, route in operations.items():
        operation = openapi_operations[key]
        assert operation.get("summary", "").strip()
        assert operation.get("summary") != route.name.replace("_", " ").title()
        operation_ids.append(operation["operationId"])

        success_code = str(route.status_code or 200)
        success_response = operation["responses"][success_code]
        assert success_response["content"]["application/json"]["schema"]

        has_request_contract = bool(operation.get("parameters") or operation.get("requestBody"))
        if has_request_contract:
            assert "422" in operation["responses"]

        for status_code in {"400", "401", "403", "404", "409"}:
            response = operation["responses"].get(status_code)
            if response:
                schema_ref = response["content"]["application/json"]["schema"]["$ref"]
                assert schema_ref == "#/components/schemas/ErrorResponse"

        if key[0] in {"post", "put", "patch"} and key[1] not in {
            "/auth/logout-all",
            "/projects/{project_id}/archive",
        }:
            assert operation.get("requestBody", {}).get("content")

        if key[1] in public_paths:
            assert not operation.get("security")
        else:
            assert operation.get("security")
            assert "401" in operation["responses"]
            assert operation["security"] == [{"OAuth2PasswordBearer": []}]

    assert len(operation_ids) == len(set(operation_ids))
    assert schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] == {
        "type": "oauth2",
        "flows": {
            "password": {
                "scopes": {},
                "tokenUrl": "/auth/login",
            }
        },
    }

    api_doc = Path(__file__).resolve().parents[3] / "docs" / "API.md"
    documented_operations = {
        (match.group(1).lower(), match.group(2))
        for line in api_doc.read_text(encoding="utf-8").splitlines()
        if (match := re.match(r"^\| (GET|POST|PUT|PATCH|DELETE) \| `([^`]+)` \|", line))
    }
    assert documented_operations == openapi_operations.keys()

    assert {
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/auth/logout",
        "/auth/logout-all",
        "/auth/me",
        "/users/me",
        "/users/profile",
        "/users/password",
        "/users/admin-only",
        "/users/all",
        "/workspaces",
        "/workspaces/{workspace_id}",
        "/projects/workspace/{workspace_id}",
        "/projects/{project_id}",
        "/projects/{project_id}/members",
        "/projects/{project_id}/members/{user_id}",
        "/memberships/{workspace_id}",
        "/memberships/{workspace_id}/{user_id}",
        "/health/",
        "/",
    }.issubset(schema["paths"])

    assert {
        "ErrorResponse",
        "HTTPValidationError",
        "UserResponse",
        "WorkspaceResponse",
        "ProjectResponse",
        "MembershipResponse",
        "ProjectMemberResponse",
    }.issubset(schema["components"]["schemas"])

    user_list = schema["paths"]["/users/all"]["get"]["responses"]["200"]
    assert user_list["content"]["application/json"]["schema"]["type"] == "array"
    assert "password_hash" not in str(user_list)

    login_body = schema["paths"]["/auth/login"]["post"]["requestBody"]["content"]
    assert {"application/json", "application/x-www-form-urlencoded"} <= login_body.keys()

    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"
