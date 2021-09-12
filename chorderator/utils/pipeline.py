import importlib


class Pipeline:

    def __init__(self, pipeline):
        self.pipeline = [importlib.import_module('utils.models.' + module) for module in pipeline]
        assert len(self.pipeline) == 3

    def send_in(self):
        self.__preprocess()
        self.__main_model()
        self.__postprocess()

    def __preprocess(self):
        print(self.pipeline[0])

    def __main_model(self):
        print(self.pipeline[1])

    def __postprocess(self):
        print(self.pipeline[2])

    def send_out(self):
        pass


if __name__ == '__main__':
    pass
