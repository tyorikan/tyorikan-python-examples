# API Guidelines

## RESTful Design
*   Use standard HTTP methods (GET, POST, PUT, DELETE).
*   Use standard HTTP status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error).
*   URL Naming: Kebab-case, Plural nouns (e.g., `/api/v1/products`).

## Request/Response
*   JSON is the standard format.
*   Snake_case for JSON keys.
*   Dates must be ISO 8601 UTC.
