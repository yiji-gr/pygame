import yaml


class Game:
    def __init__(self, config_path):
        self.config_path = config_path
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self._read_cfg()

    def _read_cfg(self):
        raise NotImplementedError

    def start(self):
        self._init_state()
        self._run()

    def _init_state(self):
        raise NotImplementedError

    def _run(self):
        raise NotImplementedError
