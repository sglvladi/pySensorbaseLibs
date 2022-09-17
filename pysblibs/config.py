import json
from pathlib import Path
from typing import Union, Sequence


class ConfigManager:
    def __init__(self, config_file: Union[str, Path] = Path('config.json')):
        self.config_file = config_file if isinstance(config_file, Path) else Path(config_file)

        if not self.config_file.exists():
            self.config_file.touch()
            self.config = {}
        else:
            with open(self.config_file) as configfile:
                self.config = json.load(configfile)

    def get(self, option: Union[str, Sequence[str]]):
        if isinstance(option, str):
            return self.config.get(option)
        else:
            value = self.config
            for i, key in enumerate(option):
                value = value[key]
            return value

    def set(self, option: Union[str, Sequence[str]], value):
        if isinstance(option, str):
            self.config[option] = value
        else:
            current_dict = self.config
            for i, key in enumerate(option[:-1]):
                try:
                    current_dict = current_dict[key]
                except KeyError:
                    current_dict[key] = {}
                    current_dict = current_dict[key]
            current_dict[option[-1]] = value
        with open(self.config_file, 'w') as configfile:
            configfile.write(json.dumps(self.config, indent=4))

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

