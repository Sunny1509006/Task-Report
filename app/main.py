from fastapi import FastAPI
from app.routes import task_routes, user_routes
from app.services.scheduler import start_scheduler
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Register your routers
app.include_router(task_routes.router)
app.include_router(user_routes.router)

# Custom OpenAPI for Swagger Bearer Auth support
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Task Manager API",
        version="1.0.0",
        description="API for managing tasks and users",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
