import os
from typing import Any, Dict, List

OTH_DEFAULT_CONFIG: Dict[str, Any] = {}


class Config:
    def __init__(self):
        # shallow copy ok if we only have strings in the default config
        self._config: Dict[str, Any] = OTH_DEFAULT_CONFIG.copy()
        self._load_from_env()

    def __str__(self):
        return str(self._config)

    def _load_from_env(self) -> None:
        for key, value in os.environ.items():
            prefix: str = key[:4].lower()
            if prefix == "oth_" or prefix == "rgt_":
                namespace: str = key[4:].lower().strip("_").replace("__", ":")
                self.set(namespace, value)

    def set(self, namespace: str, value: Any) -> None:
        if namespace == "":
            raise AttributeError("you cannot set the root config node")

        parts: List[str] = namespace.split(":")

        set_point: dict = self._config
        for p in parts[:-1]:
            print(p)
            if not p.isidentifier():
                raise ValueError(f"config key '{p}' is not a valid Python identifier")

            if p in set_point and not isinstance(set_point[p], dict):
                raise KeyError(f"config namespace '{namespace}' would overwrite data")

            if p not in set_point:
                set_point[p] = {}

            set_point = set_point[p]

        if not parts[-1].isidentifier():
            raise ValueError(f"config key '{p}' is not a valid Python identifier")
        else:
            set_point[parts[-1]] = value

    def get(self, namespace: str, none_on_miss: bool = True) -> Any:
        if namespace == "":
            return self._config

        parts: List[str] = namespace.split(":")

        ret_value: Any = self._config
        for p in parts:
            if not p.isidentifier():
                raise ValueError(f"config key '{p}' is not a valid Python identifier")

            if p not in ret_value:
                if not none_on_miss:
                    raise KeyError(f"config namespace '{namespace}' does not exist")
                else:
                    return None

            ret_value = ret_value[p]

        return ret_value


oth_config: Config = Config()
