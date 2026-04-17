from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.core.decision_module import OnlyDeleteDecisionModule
from src.core.model import Model
from src.routers.module.router import ModuleRouter
from src.routers.robot.router import RobotRouter
from src.routers.state.router import StateRouter
from src.routers.system.router import SystemRouter
from src.module_monitor.module_monitor import ModuleMonitor
import asyncio


model = Model(OnlyDeleteDecisionModule)


@asynccontextmanager
async def lifespan(app: FastAPI):
    docker_monitor = ModuleMonitor(model)
    task = asyncio.create_task(docker_monitor.start())
    yield
    docker_monitor.stop()
    task.cancel()


app = FastAPI(lifespan=lifespan)

# just for testing, to be removed later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ModuleRouter(model).router)
app.include_router(RobotRouter(model).router)
app.include_router(StateRouter(model).router)
app.include_router(SystemRouter(model).router)
