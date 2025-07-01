"""
Integration tests for the emotional intelligence system.
"""
import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta
from examples.emotional_intelligence.demo_emotional_ai import (
    EmotionVector,
    EmotionModel,
    SelfAwarenessModule,
    EmpathyModule
)

class TestEmotionalSystemIntegration:
    """Integration tests for the emotional intelligence system."""
    
    @pytest.fixture
    def setup_components(self):
        """Set up test components."""
        emotion_model = EmotionModel()
        self_awareness = SelfAwarenessModule(emotion_model)
        empathy = EmpathyModule(emotion_model)
        return emotion_model, self_awareness, empathy
    
    @pytest.mark.asyncio
    async def test_emotion_flow(self, setup_components):
        """Test the complete emotion processing flow."""
        emotion_model, self_awareness, empathy = setup_components
        
        # Test initial state
        assert emotion_model.get_emotion_label() == "neutral"
        
        # Process positive stimulus
        emotion_model.update_emotion({"valence": 0.8, "arousal": 0.9, "dominance": 0.7})
        assert emotion_model.get_emotion_label() == "excited"
        
        # Test self-awareness
        reflection = await self_awareness.reflect()
        assert "productive" in reflection.lower() or "happy" in reflection.lower()
        
        # Test empathy
        response = await empathy.respond_with_empathy("happy")
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Process negative stimulus
        emotion_model.update_emotion({"valence": -0.8, "arousal": 0.8, "dominance": 0.4})
        assert emotion_model.get_emotion_label() == "angry"
        
        # Test updated self-awareness
        reflection = await self_awareness.reflect()
        assert "calm" in reflection.lower() or "upset" in reflection.lower()
    
    @pytest.mark.asyncio
    async def test_emotion_persistence(self, setup_components):
        """Test that emotional state persists and evolves over time."""
        emotion_model, _, _ = setup_components
        
        # Initial state
        assert emotion_model.get_emotion_label() == "neutral"
        
        # Apply stimulus
        emotion_model.update_emotion({"valence": 0.6, "arousal": 0.7, "dominance": 0.5})
        assert emotion_model.get_emotion_label() in ["excited", "happy"]
        
        # Let it decay
        for _ in range(5):
            emotion_model.update_emotion({"valence": 0.0, "arousal": 0.0, "dominance": 0.0})
        
        # Should be returning to neutral
        assert abs(emotion_model.current_emotion.valence) < 0.3
        assert abs(emotion_model.current_emotion.arousal - 0.5) < 0.3
    
    @pytest.mark.asyncio
    async def test_empathy_variability(self, setup_components):
        """Test that empathy responses vary appropriately."""
        _, _, empathy = setup_components
        
        # Test multiple responses to ensure variability
        responses = set()
        for _ in range(10):
            response = await empathy.respond_with_empathy("happy")
            responses.add(response)
            
        # Should have at least 2 different responses
        assert len(responses) >= 2
    
    @pytest.mark.asyncio
    async def test_self_awareness_adaptation(self, setup_components):
        """Test that self-awareness adapts to emotional state."""
        emotion_model, self_awareness, _ = setup_components
        
        # Test with happy state
        emotion_model.update_emotion({"valence": 0.8, "arousal": 0.7, "dominance": 0.6})
        happy_reflection = await self_awareness.reflect()
        
        # Test with sad state
        emotion_model.update_emotion({"valence": -0.8, "arousal": 0.2, "dominance": 0.3})
        sad_reflection = await self_awareness.reflect()
        
        # Reflections should be different
        assert happy_reflection != sad_reflection
        
        # Should contain appropriate emotional words
        assert any(word in happy_reflection.lower() for word in ["happy", "good", "great"])
        assert any(word in sad_reflection.lower() for word in ["sad", "down", "low"])

class TestPerformance:
    """Performance tests for the emotional intelligence system."""
    
    @pytest.mark.parametrize("iterations", [10, 100, 1000])
    def test_emotion_update_performance(self, benchmark, iterations):
        """Test the performance of emotion updates."""
        model = EmotionModel()
        
        def run_updates():
            for _ in range(iterations):
                model.update_emotion({
                    "valence": np.random.uniform(-1, 1),
                    "arousal": np.random.uniform(0, 1),
                    "dominance": np.random.uniform(0, 1)
                })
        
        benchmark(run_updates)
        
        # Assert we're processing at least 1000 updates per second
        stats = benchmark.stats
        if hasattr(stats, 'data'):
            ops_per_second = iterations / (stats.data[-1] / 1e9)  # Convert ns to s
            print(f"\nPerformance: {ops_per_second:.2f} emotion updates per second")
            assert ops_per_second > 1000, "Performance below expected threshold"
