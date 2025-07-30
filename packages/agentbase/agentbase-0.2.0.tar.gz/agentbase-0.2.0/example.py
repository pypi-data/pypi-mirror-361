#!/usr/bin/env python3
"""
Example usage of AgentBase - Open Source AI Agent Storage with Learning and Adaptation

This script demonstrates the key features of AgentBase including:
- Memory caching
- Experience replay
- Mistake recording and correction
- Model update tracking
- Concept drift detection
"""

import time
import numpy as np
from agentbase import AgentBase, AgentConfig
from agentbase.memory.lifelong_learning import UpdateType, MistakeType
from agentbase.logging.metadata_logger import LogLevel


def main():
    """Demonstrate AgentBase functionality."""
    print("🤖 AgentBase Example - Learning and Adaptation Demo")
    print("=" * 50)
    
    # Create agent configuration
    config = AgentConfig(
        agent_id="example_agent",
        name="Example Learning Agent",
        description="Demonstration agent for AgentBase features",
        cache_size=1000,
        replay_buffer_capacity=10000,
        drift_detection_enabled=True,
        enable_console_logging=True,
        log_level="INFO"
    )
    
    # Initialize AgentBase
    with AgentBase(config) as agent:
        print(f"✅ Agent initialized: {agent.config.name}")
        print(f"   Agent ID: {agent.config.agent_id}")
        print()
        
        # Demonstrate memory caching
        print("📦 Memory Caching Demo")
        print("-" * 30)
        agent.cache_set("user_preference", {"theme": "dark", "language": "en"})
        agent.cache_set("model_weights", np.random.random(100), ttl=300)
        
        preference = agent.cache_get("user_preference")
        print(f"Retrieved preference: {preference}")
        
        cache_stats = agent.cache.get_stats()
        print(f"Cache hit rate: {cache_stats['hit_rate']:.2f}%")
        print()
        
        # Demonstrate experience replay
        print("🎯 Experience Replay Demo")
        print("-" * 30)
        
        # Simulate some learning experiences
        for episode in range(5):
            episode_id = f"episode_{episode}"
            total_reward = 0
            
            for step in range(10):
                # Simulate environment interaction
                state = np.random.random(4)
                action = np.random.randint(0, 2)
                reward = np.random.random() - 0.5  # Random reward between -0.5 and 0.5
                next_state = np.random.random(4)
                done = step == 9
                
                # Store experience
                agent.store_experience(
                    state=state,
                    action=action,
                    reward=reward,
                    next_state=next_state,
                    done=done,
                    episode_id=episode_id
                )
                
                total_reward += reward
            
            print(f"Episode {episode}: Total reward = {total_reward:.3f}")
        
        # Sample experiences for training
        if agent.replay_buffer.is_ready():
            sample_batch = agent.sample_experiences(batch_size=32)
            print(f"Sampled {len(sample_batch)} experiences for training")
        
        replay_stats = agent.replay_buffer.get_stats()
        print(f"Replay buffer: {replay_stats['current_size']} experiences stored")
        print()
        
        # Demonstrate mistake recording and correction
        print("🔧 Mistake Recording and Correction Demo")
        print("-" * 30)
        
        # Simulate some mistakes
        for i in range(3):
            mistake_id = agent.record_mistake(
                mistake_type=MistakeType.PREDICTION_ERROR,
                context={"input": f"test_input_{i}", "model_version": "v1.0"},
                expected_output=1.0,
                actual_output=0.5 + i * 0.1,
                error_magnitude=abs(1.0 - (0.5 + i * 0.1)),
                severity="medium"
            )
            
            # Apply correction
            correction_id = agent.apply_correction(
                mistake_id=mistake_id,
                correction_type="parameter_adjustment",
                correction_data={"parameter": "learning_rate", "adjustment": -0.01},
                success_rate=0.8 + i * 0.05,
                validation_results={"accuracy": 0.85 + i * 0.02}
            )
            
            print(f"Mistake {i+1}: ID={mistake_id[:8]}..., Correction={correction_id[:8]}...")
        
        learning_stats = agent.lifelong_learning.get_statistics()
        print(f"Learning stats: {learning_stats['total_mistakes']} mistakes, {learning_stats['total_corrections']} corrections")
        print()
        
        # Demonstrate model update tracking
        print("📈 Model Update Tracking Demo")
        print("-" * 30)
        
        # Simulate model updates
        for update_num in range(3):
            update_id = agent.record_model_update(
                update_type=UpdateType.PARAMETER_UPDATE,
                description=f"Gradient update #{update_num + 1}",
                parameters_changed=["layer1.weights", "layer2.bias"],
                performance_before={"accuracy": 0.80 + update_num * 0.02, "loss": 0.5 - update_num * 0.05},
                performance_after={"accuracy": 0.82 + update_num * 0.02, "loss": 0.45 - update_num * 0.05},
                update_data={"learning_rate": 0.001, "batch_size": 32}
            )
            
            print(f"Update {update_num + 1}: ID={update_id[:8]}..., Accuracy improved by {0.02:.3f}")
        
        print()
        
        # Demonstrate concept drift detection
        print("📊 Concept Drift Detection Demo")
        print("-" * 30)
        
        if agent.drift_detector:
            # Simulate reference data (stable period)
            for i in range(100):
                value = np.random.normal(0, 1)  # Normal distribution
                agent.drift_detector.add_sample("feature_1", value, is_reference=True)
            
            # Simulate drift (distribution change)
            print("Simulating concept drift...")
            for i in range(50):
                # Gradually shift the distribution
                drift_factor = i / 50.0
                value = np.random.normal(drift_factor * 2, 1)  # Shifting mean
                agent.drift_detector.add_sample("feature_1", value, is_reference=False)
            
            # Check for drift alerts
            alerts = agent.drift_detector.get_alerts(limit=5)
            if alerts:
                print(f"🚨 Drift detected! {len(alerts)} alerts generated")
                for alert in alerts[:2]:  # Show first 2 alerts
                    print(f"   - {alert.feature_name}: {alert.severity.value} severity (score: {alert.drift_score:.3f})")
            else:
                print("No drift detected in this simulation")
        
        print()
        
        # Show comprehensive statistics
        print("📊 Comprehensive Statistics")
        print("-" * 30)
        
        stats = agent.get_statistics()
        print(f"Uptime: {stats['uptime']:.1f} seconds")
        print(f"Operations performed: {stats['operations_performed']}")
        print(f"Performance score: {stats['performance_score']:.3f}")
        print(f"Cache hit rate: {stats['cache_stats']['hit_rate']:.2f}%")
        print(f"Experiences stored: {stats['experiences_stored']}")
        print(f"Mistakes recorded: {stats['mistakes_recorded']}")
        print(f"Corrections applied: {stats['corrections_applied']}")
        if agent.drift_detector:
            print(f"Drift alerts: {stats['drift_alerts']}")
        
        print()
        
        # Save agent state
        print("💾 Saving Agent State")
        print("-" * 30)
        agent.save_state()
        print("Agent state saved successfully!")
        
        print()
        print("✅ Demo completed successfully!")
        print("🎉 AgentBase is ready for your AI agent projects!")


if __name__ == "__main__":
    main() 