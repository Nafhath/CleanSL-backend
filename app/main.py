from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers.addresses import router as addresses_router
from app.routers.complaints import router as complaints_router
from app.routers.collection_tasks import router as tasks_router
from app.routers.drivers import router as drivers_router
from app.routers.analytics import router as analytics_router
from app.routers.violations import router as violations_router
from app.routers.trucks import router as trucks_router
from app.routers.users import router as users_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CleanSL backend API for waste management operations"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "CleanSL backend is running"}


app.include_router(addresses_router)
app.include_router(complaints_router)
app.include_router(tasks_router)
app.include_router(drivers_router)
app.include_router(analytics_router)
app.include_router(violations_router)
app.include_router(trucks_router)
app.include_router(users_router)