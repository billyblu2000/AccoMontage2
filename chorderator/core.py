class Core:

    def __init__(self):
        self.pipeline = []

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Core, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_core(cls):
        core = Core()
        return core

    def _verify_pipeline(self):
        pass

    def run(self):
        pass
