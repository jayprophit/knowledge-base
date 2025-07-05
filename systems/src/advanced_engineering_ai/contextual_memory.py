"""
Contextual Memory: Maintain context across interactions
"""
class ContextualMemory:
    def __init__(self):
        self.context_history = []

    def add_context(self, context):
        self.context_history.append(context)
        if len(self.context_history) > 10:
            self.context_history.pop(0)

    def get_context(self):
        return self.context_history
