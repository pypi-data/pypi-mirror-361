from enum import Enum

class Status(str, Enum):
    RUNNING = "running"
    NOT_RUNNING = "not_running"
    SUCCESS = "success"
    FAILED = "failed"
