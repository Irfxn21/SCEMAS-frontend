from dataclasses import dataclass

@dataclass
class SystemHealth:
    up_time: float
    memory_usage: float
    disk_space: float
    cpu_usage: float