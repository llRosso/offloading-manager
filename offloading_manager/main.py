from fastapi import FastAPI
from contextlib import asynccontextmanager
from offloading_manager.routers.module.router import modules_router
from offloading_manager.routers.robot.router import robots_router
from offloading_manager.routers.state.router import state_router
from offloading_manager.routers.system.router import system_router
from offloading_manager.controll_module import controll_module

@asynccontextmanager
async def lifespan(app: FastAPI):
    await controll_module.module_controll()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(modules_router)
app.include_router(robots_router)
app.include_router(state_router)
app.include_router(system_router)