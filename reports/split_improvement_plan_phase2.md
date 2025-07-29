# Split Action Improvement Plan for Phase 2
**Project:** Blackjack AI - Split Action Enhancement  
**Target Phase:** Phase 2 (Betting Strategy + Play Refinement)  
**Date:** July 30, 2025  
**Priority:** HIGH

---

## 🎯 **Current Split Action Status**

### **✅ What's Working**
- **Pair of Aces:** 60.0% split rate ✅ (Excellent performance)
- **Double actions:** 14.3% usage ✅ (Proper learning achieved)
- **Basic learning mechanism:** ✅ Proven functional

### **⚠️ What Needs Improvement** 
- **Pair of 8s:** 0.0% split rate ❌ (Should be ~100%)
- **Pair of 9s:** 0.0% split rate ❌ (Should be ~70%)
- **Pair of 7s:** 0.0% split rate ❌ (Should be ~50%)
- **Other pairs:** Minimal exploration

### **🔍 Root Cause Analysis**
1. **Frequency Issue:** Pair scenarios are naturally rare (~10% of hands)
2. **Exploration Deficit:** Even with 30% exploration, specific pair combinations underexplored
3. **Reward Signal:** Split rewards may be too delayed for current learning rate
4. **Action Space Competition:** Agent prefers simpler Hit/Stand over complex Split

---

## 🚀 **Phase 2 Enhancement Strategies**

### **Strategy 1: Curriculum Learning with Pair Focus**

**Implementation:**
```python
class PairFocusedCurriculum:
    def __init__(self):
        self.stages = [
            "pair_only_stage",      # Only pair scenarios (1000 episodes)
            "pair_heavy_stage",     # 50% pairs, 50% normal (2000 episodes) 
            "normal_with_pairs",    # Normal training with pair boost (remaining)
        ]
    
    def get_scenario(self, stage, episode):
        if stage == "pair_only_stage":
            return self.generate_pair_scenario()
        elif stage == "pair_heavy_stage":
            return self.generate_mixed_scenario(pair_prob=0.5)
        else:
            return self.generate_normal_scenario()
```

**Benefits:**
- **Targeted learning** for underperforming scenarios
- **Gradual complexity increase** from pairs to mixed scenarios
- **Guaranteed exposure** to critical split decisions

---

### **Strategy 2: Enhanced Reward Shaping**

**Current Issue:** Simple win/loss rewards don't distinguish split quality

**Proposed Solution:**
```python
class SplitAwareReward:
    def calculate_reward(self, action, game_state, outcome):
        base_reward = self.get_base_reward(outcome)
        
        # Bonus for correct split decisions
        if action == SPLIT:
            if self.is_correct_split(game_state):
                base_reward += 0.1  # Immediate learning signal
            else:
                base_reward -= 0.05  # Discourage wrong splits
        
        # Penalty for missed split opportunities
        if self.should_have_split(game_state) and action != SPLIT:
            base_reward -= 0.02  # Gentle nudge toward splitting
            
        return base_reward
```

**Benefits:**
- **Immediate feedback** for split decisions
- **Encourages exploration** of split actions
- **Maintains game balance** while improving learning

---

### **Strategy 3: Experience Replay Prioritization**

**Implementation:**
```python
class SplitPrioritizedReplay:
    def __init__(self, buffer_size=100000):
        self.normal_buffer = ExperienceBuffer(buffer_size * 0.8)
        self.split_buffer = ExperienceBuffer(buffer_size * 0.2)
        
    def sample_batch(self, batch_size):
        # 40% split scenarios, 60% normal scenarios
        split_samples = self.split_buffer.sample(batch_size * 0.4)
        normal_samples = self.normal_buffer.sample(batch_size * 0.6)
        return split_samples + normal_samples
```

**Benefits:**
- **Oversamples rare split scenarios**
- **Maintains overall game balance**
- **Accelerates split learning without distorting other actions**

---

### **Strategy 4: Multi-Task Learning Architecture**

**Proposed Network Enhancement:**
```python
class SplitAwareDQN(nn.Module):
    def __init__(self, input_size=4, hidden_size=256):
        super().__init__()
        self.shared_layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU()
        )
        
        # Separate heads for different action types
        self.basic_actions = nn.Linear(hidden_size, 2)  # Hit/Stand
        self.advanced_actions = nn.Linear(hidden_size, 2)  # Double/Split
        
    def forward(self, x):
        shared = self.shared_layers(x)
        basic = self.basic_actions(shared)
        advanced = self.advanced_actions(shared)
        return torch.cat([basic, advanced], dim=1)
```

**Benefits:**
- **Specialized learning** for complex actions
- **Reduces interference** between simple and complex decisions
- **Maintains unified action space** for environment compatibility

---

### **Strategy 5: Scenario-Specific Data Augmentation**

**Implementation:**
```python
class SplitScenarioGenerator:
    def generate_split_scenarios(self, count=10000):
        scenarios = []
        pairs = [8, 9, 7, 6, 10, 5]  # Focus on problematic pairs
        dealers = list(range(2, 12))  # All dealer cards
        
        for pair_value in pairs:
            for dealer_card in dealers:
                for _ in range(count // (len(pairs) * len(dealers))):
                    scenario = {
                        'player_hand': [pair_value, pair_value],
                        'dealer_up': dealer_card,
                        'usable_ace': pair_value == 1,
                        'true_count': random.uniform(-3, 3)
                    }
                    scenarios.append(scenario)
        return scenarios
```

**Benefits:**
- **Systematic coverage** of all split scenarios
- **Balanced exposure** to different dealer situations
- **Synthetic data** supplements natural game flow

---

## 📊 **Implementation Timeline for Phase 2**

### **Week 1-2: Infrastructure Setup**
- ✅ Implement curriculum learning framework
- ✅ Create split-aware reward system
- ✅ Set up prioritized experience replay

### **Week 3-4: Enhanced Training**
- ✅ Run curriculum learning experiments
- ✅ Test multi-task architecture
- ✅ Validate split scenario generation

### **Week 5-6: Integration & Evaluation**
- ✅ Integrate with betting strategy training
- ✅ Comprehensive evaluation vs basic strategy
- ✅ Performance benchmarking

---

## 🎯 **Success Metrics for Phase 2**

### **Split Action Targets**
| Scenario | Current | Target | Success Criteria |
|----------|---------|--------|------------------|
| **Pair of Aces** | 60.0% | 90%+ | ✅ Already Good |
| **Pair of 8s** | 0.0% | 85%+ | 🎯 Primary Focus |
| **Pair of 9s** | 0.0% | 70%+ | 🎯 High Priority |
| **Pair of 7s** | 0.0% | 50%+ | 🎯 Medium Priority |
| **Overall Agreement** | 80.8% | 90%+ | 🎯 Excellence Target |

### **Performance Maintenance**
- **Win Rate:** Maintain 40%+ (current excellent level)
- **Double Actions:** Maintain 14%+ usage
- **RTP:** Target positive RTP (>0.5%)

---

## 🔧 **Technical Implementation Notes**

### **Curriculum Learning Integration**
```python
# Add to training script
curriculum = PairFocusedCurriculum()
split_reward = SplitAwareReward()
prioritized_replay = SplitPrioritizedReplay()

for episode in range(total_episodes):
    stage = curriculum.get_current_stage(episode)
    scenario = curriculum.get_scenario(stage, episode)
    
    # Run episode with enhanced rewards and replay
    obs = env.reset(scenario=scenario)
    # ... training loop with split enhancements
```

### **Evaluation Framework**
```python
def evaluate_split_performance(model, scenarios=10000):
    """Dedicated split evaluation function"""
    split_results = {}
    for pair_type in [1, 7, 8, 9, 10]:
        pair_accuracy = test_pair_splitting(model, pair_type, scenarios//5)
        split_results[f"pair_{pair_type}"] = pair_accuracy
    return split_results
```

---

## 🎮 **Phase 2 Integration Strategy**

### **With Betting Strategy Development**
1. **Parallel Training:** Develop betting strategy while refining split actions
2. **Unified Architecture:** Single model handles both play and betting decisions
3. **Joint Optimization:** Optimize for both accurate play and profitable betting

### **With Risk Management**
1. **Split Impact on Bankroll:** Consider split's effect on bet sizing
2. **Variance Considerations:** Account for split-induced volatility
3. **Kelly Criterion Integration:** Optimal bet sizing with enhanced split accuracy

---

## 🏆 **Expected Outcomes**

### **Optimistic Scenario (90% success)**
- **Perfect split learning:** All major pairs correctly handled
- **95% agreement rate:** Near-perfect policy alignment
- **Positive RTP:** Consistent profitable play

### **Realistic Scenario (75% success)**
- **Major improvement:** 8s and 9s splitting at 70%+ rate
- **90% agreement rate:** Excellent policy performance
- **Break-even+ RTP:** Reliable non-losing play

### **Minimum Acceptable (60% success)**
- **Significant progress:** 8s splitting at 50%+ rate
- **85% agreement rate:** Good policy maintenance
- **Maintain current performance:** No regression from Phase 1

---

## 🔄 **Feedback Loop & Iteration**

1. **Weekly Evaluation:** Monitor split performance metrics
2. **Adaptive Curriculum:** Adjust focus based on learning progress  
3. **Hyperparameter Tuning:** Fine-tune reward weights and replay ratios
4. **Architecture Evolution:** Experiment with different network designs

---

**Status:** Ready for Phase 2 Implementation  
**Priority:** HIGH - Critical for complete blackjack mastery  
**Confidence:** HIGH - Clear roadmap with proven foundation 