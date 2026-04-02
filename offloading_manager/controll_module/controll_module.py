from offloading_manager.core.state import  get_state
from offloading_manager.type import ModuleType, Stats
from offloading_manager.core.decision import stats_valutation
import aiodocker

docker_name: dict[str, ModuleType] = {
    "project-emerge-aruco-detector": ModuleType.ARUCO,
    "project-emerge-aggregate-runtime": ModuleType.AGGREGATE,
    "project-emerge-neighborhood-system": ModuleType.NEIGHBOR,
}

def cpu_percent(stats: dict) -> float:
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

def mem_percent(stats: dict) -> float:
    usage = stats["memory_stats"]["usage"]
    cache = stats["memory_stats"].get("stats", {}).get("cache", 0)
    limit = stats["memory_stats"]["limit"]
    return ((usage - cache) / limit) * 100

async def get_containers(client):
    containers = await client.containers.list()
    return [
        c for c in containers()
        if "project-emerge-network" in [
            n for n in c.attrs["NetworkSettings"]["Networks"]
        ]
    ]

async def get_stats(container):
    stats = await container.stats(stream=False)
    cpu_percentage = cpu_percent(stats)
    mem_percentage = mem_percent(stats)
    return Stats(cpu_usage=cpu_percentage, memory_usage=mem_percentage)
 
async def module_controll():
    
    '''state = get_state()
    async with aiodocker.Docker() as client:
        while True:
            containers = await get_containers(client)
            for container in containers:
                name = container.attrs["Name"].lstrip("/")
                if name in docker_name:
                    state.update_module_stats(docker_name[name], await get_stats(container))
            await stats_valutation(state)'''
                