"""
Ethics & Governance: Ethical Decision Framework, Transparency
"""
class EthicalAI:
    def __init__(self):
        self.ethical_guidelines = {
            "minimize_harm": True,
            "promote_wellbeing": True,
        }

    def evaluate_decision(self, decision):
        if self.ethical_guidelines["minimize_harm"] and hasattr(decision, 'harms_others') and decision.harms_others():
            return "This decision is not ethical."
        return "This decision is ethical."
