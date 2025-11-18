import psutil


def get_cpu_usage() -> float:
    process = psutil.Process()
    return process.cpu_percent(interval=None)


def get_ram_usage() -> float:
    process = psutil.Process()
    mem = process.memory_info().rss
    return mem / (1024 * 1024)  # MB
