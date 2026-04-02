from dataclasses import dataclass

@dataclass
class LogInformation:
    log_id: str
    user_id: str
    log_message: str
    time: int