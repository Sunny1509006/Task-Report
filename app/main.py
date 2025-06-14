from fastapi import FastAPI
from app.routes import task_routes, user_routes
from app.services.scheduler import start_scheduler
from app.routes import report_routes  # Add this import for report APIs
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# List the frontend origins you want to allow
origins = [
    "http://localhost:3000",  # your React dev server
    "http://127.0.0.1:3000",
    # add your deployed frontend URLs here as well
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE etc.
    allow_headers=["*"],
)
# Register your existing routers
app.include_router(task_routes.router)
app.include_router(user_routes.router)

# Register the report router
app.include_router(report_routes.router, prefix="/api")  # prefix optional, but recommended

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

# Start scheduler on app startup event
@app.on_event("startup")
async def startup_event():
    start_scheduler()
