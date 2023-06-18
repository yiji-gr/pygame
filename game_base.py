class Game:
    def __init__(self, config_path):
        self.config_path = config_path
        self._read_cfg()

    def start(self):
        self._init_state()
        self._run()

    def _run(self):
        raise NotImplementedError

    def _init_state(self):
        raise NotImplementedError

    def _read_cfg(self):
        raise NotImplementedError
