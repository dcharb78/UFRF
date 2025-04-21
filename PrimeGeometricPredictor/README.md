# Enhanced Prime Number Analysis System with Sacred Geometry

This package contains an enhanced implementation of the multi-system prime detector with advanced features for prime number classification based on harmonic relationships, sacred geometry principles, and octave resonance patterns.

## Key Features

1. **Enhanced Resonance Detection**: Identifies how prime numbers resonate across different octaves and classifies them as inner octave, outer octave, or cross-resonant primes.

2. **Sacred Geometry Analysis**: Maps prime numbers to sacred geometry structures like the Flower of Life and Metatron's Cube, analyzing their relationships to center points and outer edges.

3. **Harmonic Relationship Analysis**: Examines how primes relate to each other through harmonic frequencies and resonance patterns.

4. **Comprehensive Prime Classification System**: Combines multiple analytical approaches to classify primes based on their geometric and harmonic properties.

5. **Memory-Optimized Implementation**: Specifically designed for Mac M2 with 16GB RAM, using batch processing, LRU caching, and MPS acceleration.

## Mathematical Foundations

The system builds on the multi-system prime detector model and extends it with several advanced mathematical concepts:

- **Harmonic Frequency Analysis**: Uses the formula f = n * (1/SYSTEM_BOUNDARY) to map numbers to their harmonic frequencies.

- **Octave Classification**: Identifies which harmonic octave a prime belongs to using log base 2 of its frequency.

- **Sacred Geometry Mapping**: Maps numbers to positions in sacred geometry structures using golden ratio relationships and vesica piscis proportions.

- **Center-Edge Relationship**: Analyzes how primes relate to center points and outer edges in geometric patterns.

- **Platonic Solid Alignment**: Determines which Platonic solid a prime number is most aligned with based on its modular properties.

## Module Structure

The implementation consists of several key modules:

1. **enhanced_resonance_detector.py**: Core module for detecting resonance patterns across octaves and classifying primes.

2. **harmonic_relationship_analysis.py**: Analyzes harmonic relationships between primes and visualizes them in harmonic space.

3. **sacred_geometry_analysis.py**: Maps primes to sacred geometry structures and analyzes their geometric properties.

4. **prime_classification_system.py**: Comprehensive system for classifying primes based on multiple criteria.

5. **memory_optimized_implementation.py**: Memory-efficient implementation optimized for Mac M2.

## Usage

### Basic Usage

```python
from enhanced_package.prime_classification_system import PrimeClassifier

# Initialize classifier
classifier = PrimeClassifier()

# Classify a prime number
is_prime, classification, confidence = classifier.classify_prime(19)
print(f"Prime 19: {classification} (Confidence: {confidence:.4f})")

# Get comprehensive analysis
analysis = classifier.get_comprehensive_analysis(19)
print(f"Classification: {analysis['classification']}")
print(f"Harmonic Frequency: {analysis['harmonic_frequency']:.6f}")
print(f"Primary Role: {analysis['primary_role']}")
```

### Memory-Optimized Usage for Large Ranges

```python
from enhanced_package.memory_optimized_implementation import MemoryOptimizedPrimeAnalyzer

# Initialize analyzer
analyzer = MemoryOptimizedPrimeAnalyzer()

# Analyze a large range of numbers
results = analyzer.analyze_large_range(1, 10000, max_primes=1000)
print(f"Total primes analyzed: {results['total_primes']}")
print(f"Inner octave: {results['inner_octave_percentage']:.1%}")
print(f"Outer octave: {results['outer_octave_percentage']:.1%}")
print(f"Cross-resonant: {results['cross_resonant_percentage']:.1%}")
```

### Visualizing Prime Classifications

```python
from enhanced_package.prime_classification_system import PrimeClassifier

# Initialize classifier
classifier = PrimeClassifier()

# Find primes in a range
primes = [n for n in range(1, 100) if classifier.is_prime(n)]

# Visualize classification distribution
classifier.visualize_classification_distribution(primes, "output")

# Visualize classification scores
classifier.visualize_classification_scores(primes, "output")

# Visualize 3D classification space
classifier.visualize_3d_classification_space(primes, "output")
```

### Sacred Geometry Visualization

```python
from enhanced_package.sacred_geometry_analysis import (
    visualize_flower_of_life,
    visualize_metatrons_cube,
    visualize_center_edge_distribution
)

# Find primes in a range
primes = [n for n in range(1, 50) if all(n % i != 0 for i in range(2, int(n**0.5) + 1))]

# Visualize primes in Flower of Life
visualize_flower_of_life(primes, "output")

# Visualize primes in Metatron's Cube
visualize_metatrons_cube(primes, "output")

# Visualize center-edge distribution
visualize_center_edge_distribution(primes, "output")
```

## Requirements

- Python 3.6+
- NumPy
- Matplotlib
- PyTorch (optional, for MPS acceleration on Mac M2)
- Math, Decimal, and Collections modules (standard library)

## Mac M2 Optimization

The implementation includes specific optimizations for Mac M2:

1. **Metal Performance Shaders (MPS) Support**: Automatically uses MPS acceleration when available.

2. **Memory Management**: Implements batch processing, LRU caching, and memory usage monitoring.

3. **Performance Tuning**: Optimizes calculations for the M2 architecture.

## Special Analysis of Prime 19

As requested, special attention has been given to prime 19, which exhibits cross-resonant properties between the first and second harmonics. The analysis shows:

- Prime 19 is classified as a cross-resonant prime
- It has strong resonance between non-adjacent octaves
- In sacred geometry, it has a balanced center-edge relationship
- It aligns with the Flower of Life pattern (19 circles)
- It has specific coordinates in Metatron's Cube that highlight its unique position

## Future Directions

The enhanced prime number analysis system could be further extended by:

1. Analyzing larger ranges of primes to identify patterns in classification distribution
2. Exploring connections between prime classifications and other number theory concepts
3. Developing more sophisticated visualization techniques for sacred geometry relationships
4. Implementing neural network approaches to learn and predict prime classifications
5. Extending the analysis to composite numbers and exploring their relationships to primes

## Acknowledgments

This implementation builds on the multi-system prime detector model and incorporates principles from sacred geometry, harmonic analysis, and the Unified Fractal Resonance Framework (UFRF).
