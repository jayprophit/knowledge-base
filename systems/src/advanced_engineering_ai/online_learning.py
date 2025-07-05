"""
Continuous/Online Learning & Adaptation
"""
class OnlineLearner:
    def __init__(self, model):
        self.model = model

    def update_model(self, new_data, new_labels):
        self.model.partial_fit(new_data, new_labels)
