import yaml
from pathlib import Path

class AnalyzerConfig:
    def __init__(self,
                 config_path=None,
                 allowed_imports=[],
                 blacklist_imports=["os", "sys"],
                 allowed_functions=[],
                 blacklisted_functions=["open"],
                 allowed_statements=[],
                 blacklist_statements=[],
                 allowed_complexity=4
                 ):
        self.config_path=config_path
        self.allowed_imports=allowed_imports
        self.blacklist_imports=blacklist_imports
        self.allowed_functions=allowed_functions
        self.blacklisted_functions=blacklisted_functions
        self.allowed_statements=allowed_statements
        self.blacklist_statements=blacklist_statements
        self.allowed_complexity=allowed_complexity
        
        if self.config_path:
            self._load_from_yaml(self.config_path)
        else:
            # Use defaults
            self._assign_defaults()
        
        self.blacklist = self.blacklist_imports + self.blacklist_statements +self.blacklisted_functions

    def _load_from_yaml(self, config_file_path):
        path = Path(config_file_path)
        if not path:
            raise FileNotFoundError
        
        with open(config_file_path, "r") as config_file:
            config_data = yaml.safe_load(config_file) or {}
        self._assign_attributes(config_data)

    def _assign_attributes(self, config_data, prefix=''):
        for key, value in config_data.items():
            # TODO: make recursive if yaml has nested keys
            print(f"assigning: {key} to {value}")
            setattr(self, key, value)
            print(getattr(self, key, "Did not assign"))

    def _assign_defaults(self):
        self.allowed_imports=[]
        self.blacklist_imports=["os", "sys"]
        self.allowed_functions=[]
        self.blacklisted_functions=[]
        self.allowed_statements=[]
        self.blacklist_statements=[]
        self.allowed_complexity=4


