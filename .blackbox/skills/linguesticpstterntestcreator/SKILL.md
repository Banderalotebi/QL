---
name: linguesticpstterntestcreator
description: Linguistic Pattern Test Creator - Detects and tests patterns in Arabic/Quranic text
---

# Linguistic Pattern Test Creator

This skill enables AI agents to discover, test, and validate linguistic patterns in Arabic text, particularly for Muqattaat (lettered Surahs) analysis.

## Capabilities

1. **Pattern Detection**: Detects various types of linguistic patterns:
   - Muqattaat prefixes (الم, الر, طسم, etc.)
   - Letter sequences and transitions
   - Repetition patterns
   - Numerical patterns (Abjad values)

2. **Test Generation**: Automatically generates test cases for discovered patterns

3. **Analysis API**: Provides a comprehensive API for pattern analysis

## Usage Examples

### Basic Pattern Analysis

```python
from src.utils.pattern_detection import PatternAnalyzer, analyze_for_research

# Quick analysis
result = analyze_for_research("الم", surah_id=2)
print(result["patterns_found"])

# Full analyzer with more control
analyzer = PatternAnalyzer()
result = analyzer.analyze(
    text="الحمد لله رب العالمين",
    surah_id=1,
    include_tests=True
)
```

### Working with Specific Detectors

```python
from src.utils.pattern_detection import (
    MuqattaatDetector,
    LetterSequenceDetector,
    RepetitionDetector,
    NumericalPatternDetector
)

# Detect Muqattaat prefixes
matches = MuqattaatDetector().detect_prefix("الم كتاب أنزلناه...")
print(matches[0].pattern_value)  # "الم"

# Find letter sequences
matches = LetterSequenceDetector().find_sequences(text)
for m in matches:
    print(f"Found: {m.pattern_value} at {m.position}")

# Calculate Abjad value
abjad = NumericalPatternDetector().calculate_abjad("الله")  # Returns 66
```

### Creating Custom Tests

```python
from src.utils.pattern_detection import PatternTest, PatternType, PatternAnalyzer

analyzer = PatternAnalyzer()

# Create a custom test case
test = analyzer.create_test_case(
    name="Custom Muqattaat test",
    pattern_type=PatternType.MUQATTAAT_PREFIX,
    test_input="الم",
    expected="الم"
)

# Run the test
print(f"Test: {test.name}")
print(f"Input: {test.test_input}")
print(f"Expected: {test.expected_output}")
```

### Integration with Database

```python
from src.data.db import NeonLabAPI, record_hypothesis
from src.core.state import Hypothesis
from src.utils.pattern_detection import PatternAnalyzer

# Use the API to record findings
api = NeonLabAPI()
api.open_ticket("run_001", "linguistic_scout", "letter_sequence")

# Analyze text and record results
analyzer = PatternAnalyzer()
result = analyzer.analyze("طسم", surah_id=26)

# Create a hypothesis from findings
hyp = Hypothesis(
    source_scout="LinguisticScout",
    goal_link="Detected Muqattaat prefix pattern",
    transformation_steps=1,
    evidence_snippets=[str(result)],
    description="Found letter sequence pattern",
    score=0.5,
    surah_refs=[26]
)

record_hypothesis("run_001", hyp)
```

### Using with Scout Agents

```python
from src.agents.linguistic_scout import LinguisticScout
from src.utils.pattern_detection import PatternAnalyzer

# In a scout's analyze method
def analyze(self, state):
    # Get text to analyze
    text = state.get("current_text", "")
    
    # Use pattern detection
    analyzer = PatternAnalyzer()
    results = analyzer.analyze(text)
    
    # Convert to hypotheses
    hypotheses = []
    for pattern in results["patterns_found"]:
        hypotheses.append(self.make_hypothesis(
            description=f"Found {pattern['pattern_type']}: {pattern['pattern_value']}",
            goal_link="Pattern analysis of Muqattaat text",
            transformation_steps=1,
            evidence_snippets=[str(pattern)],
            surah_refs=[state.get("current_surah")]
        ))
    
    return hypotheses
```

## API Reference

### PatternAnalyzer

Main class for comprehensive pattern analysis.

- `analyze(text, surah_id, include_tests)` - Full analysis with optional test generation
- `create_test_case(name, pattern_type, test_input, expected)` - Create custom test

### Detectors

- `MuqattaatDetector` - Detects Muqattaat prefixes
- `LetterSequenceDetector` - Finds letter sequences and transitions
- `RepetitionDetector` - Finds word/repetition patterns
- `NumericalPatternDetector` - Calculates Abjad values and finds numerical patterns

### Pattern Types

- `PatternType.MUQATTAAT_PREFIX`
- `PatternType.LETTER_SEQUENCE`
- `PatternType.REPETITION`
- `PatternType.NUMERICAL`
- `PatternType.PALINDROME`
- `PatternType.STRUCTURAL`
- `PatternType.SEMANTIC`

### Confidence Levels

- `PatternConfidence.HIGH` - Strong pattern match
- `PatternConfidence.MEDIUM` - Moderate confidence
- `PatternConfidence.LOW` - Weak pattern
- `PatternConfidence.SPECULATIVE` - Hypothesis-level pattern

## Best Practices

1. **Always validate goal_link**: Ensure every hypothesis has a meaningful goal_link explaining Muqattaat relevance

2. **Use proper error handling**: Wrap pattern detection in try/except blocks

3. **Check known_dead_ends**: Before running analysis, check if similar patterns have been tried

4. **Record findings**: Use the database API to persist hypotheses for later review

5. **Generate tests**: Use test generation to validate patterns and create reproducible results

## Integration Points

- **Database**: `src/data/db.py` - `NeonLabAPI`, `record_hypothesis()`
- **State Management**: `src/core/state.py` - `ResearchState`, `Hypothesis`
- **Agents**: `src/agents/base_scout.py` - `BaseScout` class
- **Arabic Utilities**: `src/utils/arabic.py` - Arabic text processing

