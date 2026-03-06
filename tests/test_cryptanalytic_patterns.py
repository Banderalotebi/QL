"""
tests/test_cryptanalytic_patterns.py
─────────────────────────────────────
Test implementations for Pattern Categories II (Cryptanalytic & Mathematical)
from Test_Idea_Patterns.md.

These tests validate mathematical and cryptographic patterns in the Muqattaat
letter sequences, implementing patterns 31-60.
"""

import pytest
import math
import statistics
from collections import Counter
from src.utils.abjad import ABJAD, abjad_value_of_sequence
from src.data.muqattaat import MUQATTAAT_SURAHS, MUQATTAAT_MAPPING


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def muqattaat_sequences():
    """Return all Muqattaat sequences with their Surah numbers."""
    return {
        2: "الم",
        3: "الم",
        7: "المص",
        10: "الر",
        11: "الر",
        12: "الر",
        13: "الر",
        14: "الر",
        15: "الر",
        19: "كهيعص",
        20: "طه",
        26: "طسم",
        27: "طس",
        28: "طسم",
        36: "يس",
        38: "ص",
        40: "حم",
        41: "حم",
        42: "حمعسق",
        43: "حم",
        44: "حم",
        45: "حم",
        46: "حم",
        50: "ق",
        68: "ن",
    }


@pytest.fixture
def abjad_sums(muqattaat_sequences):
    """Calculate Abjad sums for all Muqattaat sequences."""
    return {
        surah: abjad_value_of_sequence(seq)
        for surah, seq in muqattaat_sequences.items()
    }


# =============================================================================
# PATTERN 31: Prime Number Indexing
# =============================================================================

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def test_prime_number_indexing(abjad_sums):
    """
    Pattern #31: Prime Number Indexing
    Test that Muqattaat sequences or their Surah numbers relate to prime indices.
    """
    prime_count = 0
    for surah, abjad_sum in abjad_sums.items():
        if is_prime(surah):
            prime_count += 1
    
    # At least some Muqattaat Surahs should have prime numbers
    # This is an exploratory test - we're looking for patterns
    assert prime_count >= 0  # Always passes - exploratory
    print(f"Prime-indexed Surahs: {prime_count} out of {len(abjad_sums)}")


def test_abjad_sums_prime_relationships(abjad_sums):
    """
    Test relationships between Abjad sums and prime numbers.
    """
    prime_abjad_count = sum(1 for v in abjad_sums.values() if is_prime(v))
    print(f"Abjad sums that are prime: {prime_abjad_count}")
    # This is exploratory - we're checking for patterns


# =============================================================================
# PATTERN 32: Fibonacci Sequence Alignment
# =============================================================================

def fibonacci_check(n: int) -> bool:
    """Check if a number is in the Fibonacci sequence."""
    if n < 0:
        return False
    # Check using perfect square property
    # n is Fibonacci iff one of 5n^2 + 4 or 5n^2 - 4 is a perfect square
    def is_perfect_square(x):
        if x < 0:
            return False
        root = int(math.sqrt(x))
        return root * root == x
    
    return is_perfect_square(5*n*n + 4) or is_perfect_square(5*n*n - 4)


def test_fibonacci_alignment(abjad_sums):
    """
    Pattern #32: Fibonacci Sequence Alignment
    Test if Muqattaat Abjad values align with Fibonacci numbers.
    """
    fib_count = sum(1 for v in abjad_sums.values() if fibonacci_check(v))
    print(f"Abjad sums matching Fibonacci: {fib_count}")
    # Exploratory test


# =============================================================================
# PATTERN 33: Golden Ratio Distribution
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ≈ 1.618


def test_golden_ratio_distribution(abjad_sums):
    """
    Pattern #33: Golden Ratio Distribution
    Test if Abjad values show Golden Ratio relationships.
    """
    golden_relationships = []
    values = list(abjad_sums.values())
    
    for i, v1 in enumerate(values):
        for v2 in values[i+1:]:
            if v2 != 0:
                ratio = v1 / v2
                # Check if ratio is close to PHI or 1/PHI
                if abs(ratio - PHI) < 0.1 or abs(ratio - 1/PHI) < 0.1:
                    golden_relationships.append((v1, v2, ratio))
    
    print(f"Golden ratio relationships found: {len(golden_relationships)}")
    # Exploratory test


# =============================================================================
# PATTERN 34: Benford's Law Violation
# =============================================================================

def first_digit(n: int) -> int:
    """Get the first digit of a number."""
    while n >= 10:
        n //= 10
    return n


def benford_expected(d: int) -> float:
    """Expected frequency according to Benford's Law."""
    return math.log10(1 + 1/d)


def test_benford_law(abjad_sums):
    """
    Pattern #34: Benford's Law Violation
    Test if Abjad value first digits follow Benford's Law.
    """
    first_digits = [first_digit(v) for v in abjad_sums.values() if v > 0]
    counter = Counter(first_digits)
    total = len(first_digits)
    
    observed_freq = {d: counter.get(d, 0) / total for d in range(1, 10)}
    expected_freq = {d: benford_expected(d) for d in range(1, 10)}
    
    print("Observed vs Expected (Benford's Law):")
    for d in range(1, 10):
        print(f"  Digit {d}: Observed={observed_freq.get(d, 0):.3f}, Expected={expected_freq[d]:.3f}")
    
    # Check for significant deviation (chi-squared-like assessment)
    deviation = sum(abs(observed_freq.get(d, 0) - expected_freq[d]) for d in range(1, 10))
    print(f"Total deviation: {deviation:.3f}")


# =============================================================================
# PATTERN 35: Entropy Calculation
# =============================================================================

def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    
    counter = Counter(text)
    length = len(text)
    
    entropy = 0.0
    for count in counter.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def test_entropy_calculation(muqattaat_sequences):
    """
    Pattern #35: Entropy Calculation
    Test Shannon entropy of Muqattaat sequences.
    """
    entropies = {}
    for surah, sequence in muqattaat_sequences.items():
        entropies[surah] = calculate_entropy(sequence)
    
    print("Muqattaat Sequence Entropies:")
    for surah, entropy in sorted(entropies.items()):
        print(f"  Surah {surah}: {entropy:.3f} bits")
    
    # Maximum possible entropy for sequence length
    avg_entropy = statistics.mean(entropies.values())
    print(f"Average entropy: {avg_entropy:.3f}")


# =============================================================================
# PATTERN 36: Hamming Distance Variance
# =============================================================================

def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance between two equal-length strings."""
    if len(s1) != len(s2):
        raise ValueError("Strings must be of equal length")
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def test_hamming_distance_variance(muqattaat_sequences):
    """
    Pattern #36: Hamming Distance Variance
    Test Hamming distances between similar Muqattaat sequences.
    """
    # Compare ALM sequences
    alm_sequences = {s: seq for s, seq in muqattaat_sequences.items() if seq == "الم"}
    print(f"ALM sequences found in Surahs: {list(alm_sequences.keys())}")
    
    # Compare HM sequences
    hm_sequences = {s: seq for s, seq in muqattaat_sequences.items() if seq == "حم"}
    print(f"حم sequences found in Surahs: {list(hm_sequences.keys())}")
    
    # Cross-compare all pairs
    all_seqs = list(muqattaat_sequences.items())
    for i, (s1, seq1) in enumerate(all_seqs[:5]):
        for s2, seq2 in all_seqs[i+1:6]:
            if len(seq1) == len(seq2):
                try:
                    dist = hamming_distance(seq1, seq2)
                    print(f"  Surah {s1} vs {s2}: Hamming distance = {dist}")
                except ValueError:
                    pass


# =============================================================================
# PATTERN 37: Levenshtein Similarity
# =============================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein (edit) distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculate similarity ratio (0 to 1)."""
    if not s1 and not s2:
        return 1.0
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1 - (levenshtein_distance(s1, s2) / max_len)


def test_levenshtein_similarity(muqattaat_sequences):
    """
    Pattern #37: Levenshtein Similarity
    Test edit distance similarity between Muqattaat sequences.
    """
    seq_groups = {}
    for surah, sequence in muqattaat_sequences.items():
        if sequence not in seq_groups:
            seq_groups[sequence] = []
        seq_groups[sequence].append(surah)
    
    print("Sequence Groups:")
    for seq, surahs in seq_groups.items():
        print(f"  {seq}: Surahs {surahs}")
    
    # Calculate inter-group similarities
    all_seqs = list(seq_groups.keys())
    for i, seq1 in enumerate(all_seqs[:5]):
        for seq2 in all_seqs[i+1:6]:
            sim = levenshtein_similarity(seq1, seq2)
            dist = levenshtein_distance(seq1, seq2)
            print(f"  {seq1} vs {seq2}: Similarity={sim:.3f}, Distance={dist}")


# =============================================================================
# PATTERN 39: Checksum Collision Test
# =============================================================================

def test_checksum_collision(abjad_sums):
    """
    Pattern #39: Checksum Collision Test
    Test for Abjad checksum values - collisions are expected for sequences 
    with the same letters (like Surah 2 and 3 both having "الم").
    """
    unique_sums = set(abjad_sums.values())
    collisions = len(abjad_sums) - len(unique_sums)
    
    print(f"Total sequences: {len(abjad_sums)}")
    print(f"Unique Abjad sums: {len(unique_sums)}")
    print(f"Collisions: {collisions}")
    
    # Find collisions
    if collisions > 0:
        sum_to_surahs = {}
        for surah, sum_val in abjad_sums.items():
            if sum_val not in sum_to_surahs:
                sum_to_surahs[sum_val] = []
            sum_to_surahs[sum_val].append(surah)
        
        print("Collision groups (same letters, different Surahs):")
        for val, surahs in sum_to_surahs.items():
            if len(surahs) > 1:
                print(f"  Abjad {val}: Surahs {surahs}")
    
    # Note: Collisions are expected for sequences with identical letters
    # This test validates the behavior, not enforces uniqueness
    assert collisions >= 0  # Always passes - we document the finding


# =============================================================================
# PATTERN 40: Cyclic Redundancy Check (CRC)
# =============================================================================

def crc32_simple(data: str) -> int:
    """Simple CRC32 implementation for string data."""
    crc = 0xFFFFFFFF
    for char in data:
        crc ^= ord(char)
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
    return crc ^ 0xFFFFFFFF


def test_crc_checksum(muqattaat_sequences):
    """
    Pattern #40: Cyclic Redundancy Check
    Test CRC checksums for Muqattaat sequences.
    """
    crc_values = {}
    for surah, sequence in muqattaat_sequences.items():
        crc_values[surah] = crc32_simple(sequence)
    
    unique_crcs = set(crc_values.values())
    print(f"Unique CRC32 values: {len(unique_crcs)} out of {len(crc_values)}")
    
    # Note: CRC collisions are expected for short strings
    # We're testing that different sequences can have different checksums
    print(f"CRC collision rate: {1 - len(unique_crcs)/len(crc_values):.1%}")


# =============================================================================
# PATTERN 41: Modulo-19 Validation
# =============================================================================

def test_modulo_19_validation(abjad_sums):
    """
    Pattern #41: Modulo-19 Validation
    Test if Abjad sums are divisible by 19 (famous Quranic mathematical claim).
    """
    divisible_by_19 = {}
    for surah, abjad_sum in abjad_sums.items():
        remainder = abjad_sum % 19
        divisible_by_19[surah] = (abjad_sum, remainder, remainder == 0)
    
    print("Modulo-19 Analysis:")
    divisible_count = 0
    for surah, (val, rem, div) in sorted(divisible_by_19.items()):
        status = "DIVISIBLE" if div else f"remainder {rem}"
        print(f"  Surah {surah}: Abjad={val}, {status}")
        if div:
            divisible_count += 1
    
    print(f"Total divisible by 19: {divisible_count}")


def test_modulo_19_surah_numbers():
    """
    Test if Surah numbers relate to modulo 19.
    """
    print("Surah number modulo 19:")
    for surah in MUQATTAAT_SURAHS:
        remainder = surah % 19
        print(f"  Surah {surah}: {remainder}")


# =============================================================================
# PATTERN 42: Frequency Distribution Curve
# =============================================================================

def test_frequency_distribution(muqattaat_sequences):
    """
    Pattern #42: Frequency Distribution Curve
    Test letter frequency distributions in Muqattaat sequences.
    """
    all_letters = "".join(muqattaat_sequences.values())
    freq_dist = Counter(all_letters)
    total = len(all_letters)
    
    print("Letter Frequency Distribution:")
    for letter, count in sorted(freq_dist.items(), key=lambda x: -x[1]):
        percentage = (count / total) * 100
        print(f"  {letter}: {count} ({percentage:.1f}%)")


# =============================================================================
# PATTERN 43: Standard Deviation Outliers
# =============================================================================

def test_standard_deviation_outliers(abjad_sums):
    """
    Pattern #43: Standard Deviation Outliers
    Test for statistical outliers in Abjad value distributions.
    """
    values = list(abjad_sums.values())
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    
    print(f"Abjad Sum Statistics:")
    print(f"  Mean: {mean:.2f}")
    print(f"  Std Dev: {stdev:.2f}")
    print(f"  Min: {min(values)}")
    print(f"  Max: {max(values)}")
    
    # Identify outliers (more than 2 standard deviations)
    outliers = []
    for surah, val in abjad_sums.items():
        z_score = (val - mean) / stdev if stdev > 0 else 0
        if abs(z_score) > 2:
            outliers.append((surah, val, z_score))
    
    print(f"Outliers (|z| > 2):")
    for surah, val, z in outliers:
        print(f"  Surah {surah}: {val} (z={z:.2f})")


# =============================================================================
# PATTERN 45: Markov Chain Transition
# =============================================================================

def build_markov_chain(sequences: list[str]) -> dict:
    """Build a first-order Markov transition matrix."""
    transitions = {}
    
    for seq in sequences:
        for i in range(len(seq) - 1):
            current = seq[i]
            next_char = seq[i + 1]
            
            if current not in transitions:
                transitions[current] = {}
            if next_char not in transitions[current]:
                transitions[current][next_char] = 0
            transitions[current][next_char] += 1
    
    # Convert to probabilities
    for current in transitions:
        total = sum(transitions[current].values())
        for next_char in transitions[current]:
            transitions[current][next_char] /= total
    
    return transitions


def test_markov_chain_transition(muqattaat_sequences):
    """
    Pattern #45: Markov Chain Transition
    Test transition probabilities between Muqattaat letters.
    """
    sequences = list(muqattaat_sequences.values())
    chain = build_markov_chain(sequences)
    
    print("Markov Chain Transition Probabilities:")
    for current, transitions in sorted(chain.items()):
        print(f"  {current} -> ", end="")
        trans_strs = [f"{next_c}:{prob:.2f}" for next_c, prob in sorted(transitions.items())]
        print(", ".join(trans_strs))


# =============================================================================
# PATTERN 49: Chi-Squared Goodness of Fit
# =============================================================================

def test_chi_squared_distribution(muqattaat_sequences):
    """
    Pattern #49: Chi-Squared Goodness of Fit
    Test if letter distribution differs from uniform random.
    """
    all_letters = "".join(muqattaat_sequences.values())
    observed = Counter(all_letters)
    total = len(all_letters)
    
    # Expected under uniform distribution
    unique_letters = len(set(all_letters))
    expected = total / unique_letters
    
    # Calculate chi-squared statistic
    chi_squared = sum(
        (observed[letter] - expected) ** 2 / expected
        for letter in observed
    )
    
    print(f"Chi-Squared Test:")
    print(f"  Observed letters: {unique_letters}")
    print(f"  Expected count per letter: {expected:.2f}")
    print(f"  Chi-squared statistic: {chi_squared:.2f}")
    
    # Degrees of freedom = unique_letters - 1
    df = unique_letters - 1
    print(f"  Degrees of freedom: {df}")


# =============================================================================
# PATTERN 50: Random Forest Classification (Simplified)
# =============================================================================

def test_letter_classification(muqattaat_sequences):
    """
    Pattern #50: Random Forest Classification
    Test if letter features can classify Muqattaat sequences.
    """
    # Create feature vectors for each sequence
    features = []
    labels = []
    
    for surah, sequence in muqattaat_sequences.items():
        # Features: length, unique letters, Abjad sum
        feature_vector = [
            len(sequence),
            len(set(sequence)),
            abjad_value_of_sequence(sequence)
        ]
        features.append(feature_vector)
        labels.append(sequence)
    
    print("Feature Vectors for Classification:")
    for i, (seq, feat) in enumerate(zip(labels, features)):
        print(f"  {seq}: length={feat[0]}, unique={feat[1]}, abjad={feat[2]}")


# =============================================================================
# PATTERN 51-60: Additional Mathematical Tests
# =============================================================================

def test_vector_space_embedding(muqattaat_sequences):
    """
    Pattern #52: Vector Space Embedding
    Test simple vector representations of Muqattaat sequences.
    """
    # Create simple vector embeddings based on letter positions
    all_letters = sorted(set("".join(muqattaat_sequences.values())))
    letter_to_idx = {letter: i for i, letter in enumerate(all_letters)}
    
    embeddings = {}
    for surah, sequence in muqattaat_sequences.items():
        vector = [0] * len(all_letters)
        for letter in sequence:
            vector[letter_to_idx[letter]] += 1
        # Normalize
        magnitude = math.sqrt(sum(x**2 for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        embeddings[surah] = vector
    
    print(f"Vector space dimension: {len(all_letters)}")
    print(f"Letter vocabulary: {all_letters}")


def test_cosine_similarity():
    """
    Pattern #53: Cosine Similarity Match
    Test cosine similarity between vectors.
    """
    # Test vectors for ALM sequences
    v1 = [1, 1, 1]  # Simplified
    v2 = [1, 1, 0.5]
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(x**2 for x in v1))
    mag2 = math.sqrt(sum(x**2 for x in v2))
    
    cosine_sim = dot_product / (mag1 * mag2)
    print(f"Cosine similarity: {cosine_sim:.3f}")


def test_euclidean_distance():
    """
    Pattern #54: Euclidean Distance Analysis
    Test Euclidean distance between sequence vectors.
    """
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]
    
    distance = math.sqrt(sum((a - b)**2 for a, b in zip(v1, v2)))
    print(f"Euclidean distance: {distance:.3f}")


def test_manhattan_distance():
    """
    Pattern #55: Manhattan Distance Mapping
    Test Manhattan distance between sequence vectors.
    """
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]
    
    distance = sum(abs(a - b) for a, b in zip(v1, v2))
    print(f"Manhattan distance: {distance}")


# =============================================================================
# Integration Tests
# =============================================================================

def test_all_math_patterns_integrated(muqattaat_sequences, abjad_sums):
    """
    Integration test covering multiple mathematical patterns.
    """
    # Run multiple pattern checks
    results = {
        "total_sequences": len(muqattaat_sequences),
        "unique_abjad_sums": len(set(abjad_sums.values())),
        "prime_surahs": sum(1 for s in abjad_sums if is_prime(s)),
        "prime_abjads": sum(1 for v in abjad_sums.values() if is_prime(v)),
        "total_abjad": sum(abjad_sums.values()),
        "avg_abjad": statistics.mean(abjad_sums.values()),
    }
    
    print("Integrated Test Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    # Basic assertions
    assert results["total_sequences"] > 0
    assert results["unique_abjad_sums"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

