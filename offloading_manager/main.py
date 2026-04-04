from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from offloading_manager.routers.module.router import modules_router
from offloading_manager.routers.robot.router import robots_router
from offloading_manager.routers.state.router import state_router
from offloading_manager.routers.system.router import system_router
from offloading_manager.control_module.control_module import DockerMonitor
from offloading_manager.core.state import get_state
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    docker_monitor = DockerMonitor(get_state())
    task = asyncio.create_task(docker_monitor.start())
    yield
    docker_monitor.stop()
    task.cancel()

app = FastAPI(lifespan=lifespan)

#just for testing, to be removed later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modules_router)
app.include_router(robots_router)
app.include_router(state_router)
app.include_router(system_router)