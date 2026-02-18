from app import app
from fastapi.routing import APIRoute

print("Dumping FastAPI Routes:")
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"Path: {route.path} | Methods: {route.methods} | Name: {route.name}")
