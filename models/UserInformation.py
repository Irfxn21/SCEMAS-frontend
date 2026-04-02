from dataclasses import dataclass
from models import AccountRole

@dataclass
class UserInformation:
    user_id: str
    email: str
    role: AccountRole

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role.value
        }