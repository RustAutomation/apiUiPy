from dataclasses import dataclass


@dataclass
class UserRequest:
    name: str
    job: str

    def to_dict(self):
        return {"name": self.name, "job": self.job}
