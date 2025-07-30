from abc import abstractmethod

class BaseAIModel:
    @abstractmethod
    def update_model(self, data, label):
        pass

    @abstractmethod
    def load_model(self, model_path = None):
        pass

    @abstractmethod
    def predict(self, data):
        pass