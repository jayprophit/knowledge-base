"""
Tests for the emotional intelligence system.
"""
import pytest
import asyncio
from examples.emotional_intelligence.demo_emotional_ai import (
    EmotionVector,
    EmotionModel,
    SelfAwarenessModule,
    EmpathyModule
)

class TestEmotionVector:
    def test_emotion_vector_validation(self):
        # Test valid values
        ev = EmotionVector(valence=0.5, arousal=0.5, dominance=0.5)
        assert ev.valence == 0.5
        assert ev.arousal == 0.5
        assert ev.dominance == 0.5
        
        # Test boundary values
        ev = EmotionVector(valence=1.0, arousal=1.0, dominance=1.0)
        assert ev.valence == 1.0
        assert ev.arousal == 1.0
        assert ev.dominance == 1.0
        
        # Test clamping of values
        ev = EmotionVector(valence=2.0, arousal=-1.0, dominance=1.5)
        assert -1.0 <= ev.valence <= 1.0
        assert 0.0 <= ev.arousal <= 1.0
        assert 0.0 <= ev.dominance <= 1.0

class TestEmotionModel:
    @pytest.fixture
    def model(self):
        return EmotionModel()
    
    def test_initial_state(self, model):
        assert model.current_emotion.valence == 0.0
        assert model.current_emotion.arousal == 0.5
        assert model.current_emotion.dominance == 0.5
        
    def test_update_emotion(self, model):
        # Test positive stimulus
        new_emotion = model.update_emotion({"valence": 0.8, "arousal": 0.8, "dominance": 0.6})
        assert new_emotion.valence > 0
        assert new_emotion.arousal > 0.5
        assert new_emotion.dominance > 0.5
        
        # Test negative stimulus
        new_emotion = model.update_emotion({"valence": -0.8, "arousal": 0.8, "dominance": 0.4})
        assert new_emotion.valence < 0
        
    def test_emotion_labeling(self, model):
        test_cases = [
            ((0.8, 0.9, 0.7), "excited"),
            ((0.8, 0.4, 0.6), "content"),
            ((-0.8, 0.8, 0.4), "angry"),
            ((-0.8, 0.3, 0.2), "sad"),
            ((0.0, 0.0, 0.5), "neutral")
        ]
        
        for (v, a, d), expected in test_cases:
            model.current_emotion.valence = v
            model.current_emotion.arousal = a
            model.current_emotion.dominance = d
            assert model.get_emotion_label() == expected

class TestSelfAwarenessModule:
    @pytest.fixture
    def module(self):
        return SelfAwarenessModule(EmotionModel())
    
    @pytest.mark.asyncio
    async def test_reflection(self, module):
        # Test with default neutral state
        reflection = await module.reflect()
        assert "neutral" in reflection.lower()
        
        # Test with happy state
        module.emotion_model.current_emotion.valence = 0.8
        reflection = await module.reflect()
        assert any(word in reflection.lower() for word in ["happy", "good", "productive"])

class TestEmpathyModule:
    @pytest.fixture
    def module(self):
        return EmpathyModule(EmotionModel())
    
    @pytest.mark.asyncio
    async def test_empathy_responses(self, module):
        # Test with known emotions
        for emotion in ["happy", "sad", "angry", "anxious"]:
            response = await module.respond_with_empathy(emotion)
            assert isinstance(response, str)
            assert len(response) > 0
            
        # Test with unknown emotion
        response = await module.respond_with_empathy("confused")
        assert response in ["I see.", "Tell me more.", "I understand."]

@pytest.mark.integration
class TestIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end(self):
        # This is a simple integration test
        emotion_model = EmotionModel()
        self_awareness = SelfAwarenessModule(emotion_model)
        empathy = EmpathyModule(emotion_model)
        
        # Update emotion
        emotion_model.update_emotion({"valence": 0.8, "arousal": 0.9, "dominance": 0.7})
        
        # Test reflection
        reflection = await self_awareness.reflect()
        assert reflection
        
        # Test empathy
        response = await empathy.respond_with_empathy("happy")
        assert isinstance(response, str)
        assert len(response) > 0
