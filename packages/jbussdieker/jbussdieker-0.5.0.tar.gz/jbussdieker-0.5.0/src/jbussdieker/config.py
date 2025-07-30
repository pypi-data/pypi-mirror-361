import os
import json
from dataclasses import dataclass, asdict, field

CONFIG_PATH = os.path.expanduser("~/.jbussdieker.json")


@dataclass
class Config:
    username: str = "default_user"
    debug: bool = False
    custom_settings: dict = field(default_factory=dict)
    asdict = asdict

    def save(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.asdict(), f, indent=2)

    @classmethod
    def load(cls):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                data = json.load(f)
            return cls(**data)
        else:
            return cls()
