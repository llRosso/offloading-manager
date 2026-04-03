import asyncio
import aiodocker
from offloading_manager.type import ModuleType, Stats
from offloading_manager.core.decision import stats_valutation
from offloading_manager.core.state import State

DOCKER_NAME: dict[str, ModuleType] = {
    "project-emerge-aruco-detector": ModuleType.ARUCO,
    "project-emerge-aggregate-runtime": ModuleType.AGGREGATE,
    "project-emerge-neighborhood-system": ModuleType.NEIGHBOR,
}

class DockerMonitor:
    def __init__(self, state: State, network: str = "project-emerge-network", interval: float = 5.0):
        self.state = state
        self.network = network
        self.interval = interval
        self._running = False
        self._client: aiodocker.Docker 

    async def start(self):
        self._running = True
        async with aiodocker.Docker() as client:
            self._client = client
            while self._running:
                await self._tick()
                await asyncio.sleep(self.interval)

    def stop(self):
        self._running = False

    async def _get_containers(self):
        containers = await self._client.containers.list()
        result = []
        for c in containers:
            info = await c.show()  
            if self.network in info["NetworkSettings"]["Networks"]:
                result.append((c, info)) 
        return result

    async def _tick(self):
        containers = await self._get_containers()
        for container, info in containers: 
            name = info["Name"].lstrip("/")
            if name in DOCKER_NAME:
                stats = await self._get_stats(container)
                self.state.update_module_stats(DOCKER_NAME[name], stats)
        await stats_valutation(self.state)

    async def _get_stats(self, container) -> Stats:
        raw = await container.stats(stream=False)
        return Stats(
            cpu_usage=self._cpu_percent(raw),
            memory_usage=self._mem_percent(raw),
        )

    @staticmethod
    def _cpu_percent(stats: dict) -> float:
        cpu_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"]
            - stats["precpu_stats"]["system_cpu_usage"]
        )
        num_cpus = stats["cpu_stats"]["online_cpus"]
        if system_delta == 0:
            return 0.0
        return (cpu_delta / system_delta) * num_cpus * 100

    @staticmethod
    def _mem_percent(stats: dict) -> float:
        usage = stats["memory_stats"]["usage"]
        cache = stats["memory_stats"].get("stats", {}).get("cache", 0)
        limit = stats["memory_stats"]["limit"]
        return ((usage - cache) / limit) * 100