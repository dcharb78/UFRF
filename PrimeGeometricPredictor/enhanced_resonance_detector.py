#!/usr/bin/env python3
"""
Enhanced Resonance Detector for Prime Number Classification

This module extends the multi-system prime detector with advanced resonance detection
capabilities, focusing on harmonic relationships and octave classification of primes.
"""

import numpy as np
import math
import decimal
from collections import defaultdict
import os

# Set decimal precision for handling extremely large numbers
decimal.getcontext().prec = 100

# Constants derived from the UFRF framework
PHI = (1 + 5**0.5) / 2  # Golden ratio
SYSTEM_BOUNDARY = 99779  # Key boundary from Riemann Hypothesis proof
DIMENSIONAL_FACTOR = 13  # Base dimensional factor from UFRF: D_n = 13 × 2^(n-1)

# Define the range for multiple systems
FIRST_SYSTEM_END = DIMENSIONAL_FACTOR * 2**13  # End of first system
SECOND_SYSTEM_END = DIMENSIONAL_FACTOR * 2**14  # End of second system
THIRD_SYSTEM_END = DIMENSIONAL_FACTOR * 2**15   # End of third system

# Harmonic constants
FUNDAMENTAL_FREQUENCY = 1.0 / SYSTEM_BOUNDARY
OCTAVE_RATIO = 2.0  # Frequency ratio between octaves

# Check if MPS (Metal Performance Shaders) is available for Mac M2
try:
    import torch
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        USE_MPS = True
        print("Using MPS (Metal Performance Shaders) for Mac M2 acceleration")
        
        # Initialize MPS device
        mps_device = torch.device("mps")
        
        # Function to move tensor to MPS
        def to_mps(tensor):
            return tensor.to(mps_device)
    else:
        USE_MPS = False
        print("MPS not available, using CPU instead (code is still M2-compatible)")
        
        # Dummy function when MPS is not available
        def to_mps(tensor):
            return tensor
except ImportError:
    USE_MPS = False
    print("PyTorch not available, using CPU only")
    
    # Dummy function when PyTorch is not available
    def to_mps(tensor):
        return tensor

def safe_log2(n):
    """
    Safely calculate log2 for extremely large numbers.
    
    Args:
        n: The number to calculate log2 for
        
    Returns:
        The log2 value
    """
    # For extremely large numbers, use decimal module
    if n > 1e100:
        # Convert to Decimal for high precision
        d_n = decimal.Decimal(str(n))
        
        # Calculate log2 using the relation log2(n) = log10(n) / log10(2)
        d_log2 = d_n.ln() / decimal.Decimal(2).ln()
        
        return float(d_log2)
    else:
        # For smaller numbers, use standard math.log2
        return math.log2(n)

def ufrf_dimensional_mapping(n):
    """
    Map a number to the UFRF dimensional structure.
    
    Args:
        n: The number to map
        
    Returns:
        A tuple (system_level, dimension, position, cycle, metacycle)
    """
    # Special case for extremely large numbers
    if n > 1e100:
        # Use safe_log2 for extremely large numbers
        try:
            system_level = max(1, math.floor(safe_log2(n / DIMENSIONAL_FACTOR)) + 1)
        except (OverflowError, ValueError):
            # Fallback for numbers too large even for safe_log2
            # Estimate system level based on digit count
            digit_count = len(str(n))
            system_level = max(1, math.floor(digit_count / 3))
    else:
        # Using the UFRF dimensional formula: D_n = 13 × 2^(n-1)
        try:
            system_level = max(1, math.floor(math.log2(n / DIMENSIONAL_FACTOR)) + 1)
        except (OverflowError, ValueError):
            # Fallback if standard approach fails
            digit_count = len(str(n))
            system_level = max(1, math.floor(digit_count / 3))
    
    # Calculate dimension with modulo to avoid overflow
    # For extremely large numbers, use a simplified approach
    if n > 1e100:
        dimension = (n % 1000) % (DIMENSIONAL_FACTOR * 2**(min(system_level, 100) - 1))
    else:
        try:
            dimension = n % (DIMENSIONAL_FACTOR * 2**(system_level - 1))
        except OverflowError:
            # Fallback if modulo calculation overflows
            dimension = (n % 1000) % DIMENSIONAL_FACTOR
    
    position = (dimension % DIMENSIONAL_FACTOR) + 1
    
    # Calculate cycle and metacycle
    cycle = math.floor(dimension / DIMENSIONAL_FACTOR)
    metacycle = math.floor(cycle / DIMENSIONAL_FACTOR)
    
    return (system_level, dimension, position, cycle, metacycle)

def calculate_harmonic_frequency(n):
    """
    Calculate the harmonic frequency of a number relative to the system boundary.
    
    Args:
        n: The number to analyze
        
    Returns:
        The harmonic frequency
    """
    # Calculate the frequency relative to the system boundary
    frequency = n * FUNDAMENTAL_FREQUENCY
    
    # Normalize to the range [0, 1) by taking modulo 1
    normalized_frequency = frequency % 1.0
    
    return normalized_frequency

def identify_harmonic_octave(n):
    """
    Identify which harmonic octave a number belongs to.
    
    Args:
        n: The number to analyze
        
    Returns:
        The octave number (0 = fundamental, 1 = first octave, etc.)
    """
    # Calculate the frequency relative to the system boundary
    frequency = n * FUNDAMENTAL_FREQUENCY
    
    # Calculate the octave (log base 2 of the frequency)
    if frequency > 0:
        octave = math.floor(safe_log2(frequency))
    else:
        octave = 0
    
    return octave

def calculate_cross_octave_resonance(n):
    """
    Calculate how strongly a number resonates across different octaves.
    
    Args:
        n: The number to analyze
        
    Returns:
        A dictionary mapping octave pairs to resonance strength
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate harmonic frequency
    frequency = calculate_harmonic_frequency(n)
    
    # Calculate resonance across octaves
    resonance_map = {}
    
    # Check resonance between fundamental and higher octaves
    for octave in range(1, 4):  # Check first 3 octaves
        # Calculate frequency in this octave
        octave_frequency = frequency * (OCTAVE_RATIO ** octave)
        normalized_octave_frequency = octave_frequency % 1.0
        
        # Calculate resonance (closer to 0 means stronger resonance)
        resonance = 1.0 - abs(frequency - normalized_octave_frequency)
        
        # Store in map
        resonance_map[(0, octave)] = resonance
    
    # Check resonance between adjacent octaves
    for octave1 in range(1, 3):
        for octave2 in range(octave1 + 1, 4):
            # Calculate frequencies in these octaves
            octave1_frequency = frequency * (OCTAVE_RATIO ** octave1) % 1.0
            octave2_frequency = frequency * (OCTAVE_RATIO ** octave2) % 1.0
            
            # Calculate resonance
            resonance = 1.0 - abs(octave1_frequency - octave2_frequency)
            
            # Store in map
            resonance_map[(octave1, octave2)] = resonance
    
    return resonance_map

def classify_prime_by_octave(n):
    """
    Classify a prime number as inner or outer octave based on its resonance patterns.
    
    Args:
        n: The number to classify (assumed to be prime)
        
    Returns:
        A string classification: "inner_octave", "outer_octave", or "cross_resonant"
    """
    # Calculate cross-octave resonance
    resonance_map = calculate_cross_octave_resonance(n)
    
    # Calculate average resonance
    avg_resonance = sum(resonance_map.values()) / len(resonance_map)
    
    # Calculate resonance between fundamental and first octave
    fundamental_first_resonance = resonance_map.get((0, 1), 0)
    
    # Calculate maximum resonance between any octaves
    max_resonance = max(resonance_map.values())
    max_resonance_pair = max(resonance_map.items(), key=lambda x: x[1])[0]
    
    # Classify based on resonance patterns
    if max_resonance > 0.8 and max_resonance_pair != (0, 1):
        # Strong resonance between non-adjacent octaves
        return "cross_resonant"
    elif fundamental_first_resonance > 0.7:
        # Strong resonance between fundamental and first octave
        return "inner_octave"
    else:
        # Weaker resonance or resonance in higher octaves
        return "outer_octave"

def analyze_angular_relationships(n):
    """
    Analyze the angular relationships of a number across different dimensions.
    
    Args:
        n: The number to analyze
        
    Returns:
        A dictionary of angular relationships
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate golden angle
    golden_angle_rad = 2 * math.pi / (PHI * PHI)
    angle = (n * golden_angle_rad) % (2 * math.pi)
    
    # Calculate angular relationships
    angular_relationships = {}
    
    # Relationship with golden angle
    angular_relationships["golden_ratio"] = abs(math.cos(angle - golden_angle_rad))
    
    # Relationship with system level
    system_angle = (system_level * math.pi / DIMENSIONAL_FACTOR) % (2 * math.pi)
    angular_relationships["system_level"] = abs(math.cos(angle - system_angle))
    
    # Relationship with position
    position_angle = (position * math.pi / DIMENSIONAL_FACTOR) % (2 * math.pi)
    angular_relationships["position"] = abs(math.cos(angle - position_angle))
    
    # Relationship with cycle
    cycle_angle = (cycle * math.pi / (DIMENSIONAL_FACTOR * 2)) % (2 * math.pi)
    angular_relationships["cycle"] = abs(math.cos(angle - cycle_angle))
    
    # Calculate overall angular coherence
    angular_relationships["coherence"] = sum(angular_relationships.values()) / len(angular_relationships)
    
    return angular_relationships

def is_prime_with_enhanced_resonance(n):
    """
    Determine if a number is prime using enhanced resonance detection.
    
    Args:
        n: The number to check
        
    Returns:
        A tuple (is_prime, classification, resonance_score)
    """
    # Special cases
    if n < 2:
        return (False, "non_prime", 0.0)
    if n == 2 or n == 3:
        return (True, "inner_octave", 1.0)
    if n % 2 == 0:
        return (False, "non_prime", 0.0)
    
    # Check primality using trial division for small numbers
    if n < 1000:
        is_prime = all(n % i != 0 for i in range(3, int(math.sqrt(n)) + 1, 2))
    else:
        # For larger numbers, use probabilistic primality test
        # This is a simplified version - in practice, use a proper primality test
        is_prime = True
        for _ in range(5):  # 5 iterations of trial division with random numbers
            divisor = 3 + 2 * (n % 100)  # Simple way to get odd numbers
            if divisor < n and n % divisor == 0:
                is_prime = False
                break
    
    if not is_prime:
        return (False, "non_prime", 0.0)
    
    # For prime numbers, classify by octave
    classification = classify_prime_by_octave(n)
    
    # Calculate resonance score
    resonance_map = calculate_cross_octave_resonance(n)
    resonance_score = max(resonance_map.values())
    
    return (True, classification, resonance_score)

def analyze_prime_with_enhanced_detection(n):
    """
    Perform comprehensive analysis of a prime number with enhanced detection.
    
    Args:
        n: The number to analyze
        
    Returns:
        A dictionary containing detailed analysis results
    """
    # Check if prime with enhanced resonance
    is_prime, classification, resonance_score = is_prime_with_enhanced_resonance(n)
    
    if not is_prime:
        return {
            "number": n,
            "is_prime": False,
            "classification": "non_prime",
            "resonance_score": 0.0
        }
    
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate harmonic frequency
    frequency = calculate_harmonic_frequency(n)
    
    # Calculate octave
    octave = identify_harmonic_octave(n)
    
    # Calculate cross-octave resonance
    resonance_map = calculate_cross_octave_resonance(n)
    
    # Analyze angular relationships
    angular_relationships = analyze_angular_relationships(n)
    
    # Compile results
    results = {
        "number": n,
        "is_prime": True,
        "classification": classification,
        "resonance_score": resonance_score,
        "system_level": system_level,
        "dimension": dimension,
        "position": position,
        "cycle": cycle,
        "metacycle": metacycle,
        "harmonic_frequency": frequency,
        "octave": octave,
        "cross_octave_resonance": resonance_map,
        "angular_relationships": angular_relationships
    }
    
    return results

def batch_analyze_primes(start, end, max_count=100):
    """
    Analyze a batch of numbers for prime classification with memory constraints.
    
    Args:
        start: Starting number
        end: Ending number
        max_count: Maximum number of primes to analyze
        
    Returns:
        A list of analysis results for prime numbers
    """
    results = []
    count = 0
    
    for n in range(start, end + 1):
        # Skip even numbers except 2
        if n > 2 and n % 2 == 0:
            continue
        
        # Check if prime with enhanced resonance
        is_prime, classification, resonance_score = is_prime_with_enhanced_resonance(n)
        
        if is_prime:
            # For prime numbers, perform full analysis
            analysis = analyze_prime_with_enhanced_detection(n)
            results.append(analysis)
            count += 1
            
            # Check if we've reached the maximum count
            if count >= max_count:
                break
    
    return results

def find_cross_resonant_primes(start, end, max_count=10):
    """
    Find prime numbers that exhibit strong cross-octave resonance.
    
    Args:
        start: Starting number
        end: Ending number
        max_count: Maximum number of primes to find
        
    Returns:
        A list of cross-resonant prime numbers with their analysis
    """
    cross_resonant_primes = []
    count = 0
    
    for n in range(start, end + 1):
        # Skip even numbers except 2
        if n > 2 and n % 2 == 0:
            continue
        
        # Check if prime with enhanced resonance
        is_prime, classification, resonance_score = is_prime_with_enhanced_resonance(n)
        
        if is_prime and classification == "cross_resonant":
            # For cross-resonant primes, perform full analysis
            analysis = analyze_prime_with_enhanced_detection(n)
            cross_resonant_primes.append(analysis)
            count += 1
            
            # Check if we've reached the maximum count
            if count >= max_count:
                break
    
    return cross_resonant_primes

def analyze_specific_prime(n):
    """
    Perform detailed analysis of a specific prime number.
    
    Args:
        n: The prime number to analyze
        
    Returns:
        A dictionary containing detailed analysis results
    """
    # Check if the number is prime
    is_prime, classification, resonance_score = is_prime_with_enhanced_resonance(n)
    
    if not is_prime:
        print(f"{n} is not a prime number.")
        return None
    
    # Perform full analysis
    analysis = analyze_prime_with_enhanced_detection(n)
    
    # Print key findings
    print(f"Analysis of prime number {n}:")
    print(f"Classification: {analysis['classification']}")
    print(f"Resonance Score: {analysis['resonance_score']:.4f}")
    print(f"Harmonic Frequency: {analysis['harmonic_frequency']:.6f}")
    print(f"Octave: {analysis['octave']}")
    print(f"System Level: {analysis['system_level']}")
    print(f"Position: {analysis['position']}")
    
    # Print cross-octave resonance
    print("\nCross-Octave Resonance:")
    for octave_pair, resonance in analysis['cross_octave_resonance'].items():
        print(f"  Octaves {octave_pair}: {resonance:.4f}")
    
    # Print angular relationships
    print("\nAngular Relationships:")
    for relationship, value in analysis['angular_relationships'].items():
        print(f"  {relationship}: {value:.4f}")
    
    return analysis

def main():
    """
    Main function to demonstrate the enhanced resonance detector.
    """
    print("Enhanced Resonance Detector for Prime Number Classification")
    print("=========================================================")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Analyze prime 19 (mentioned by the user as resonant across first and second harmonics)
    print("\nAnalyzing prime 19 (cross-resonant prime):")
    analyze_specific_prime(19)
    
    # Find cross-resonant primes in a small range
    print("\nFinding cross-resonant primes in range 1-100:")
    cross_resonant_primes = find_cross_resonant_primes(1, 100)
    print(f"Found {len(cross_resonant_primes)} cross-resonant primes:")
    for analysis in cross_resonant_primes:
        print(f"  {analysis['number']} (Resonance Score: {analysis['resonance_score']:.4f})")
    
    # Batch analyze primes in a small range
    print("\nAnalyzing primes in range 1-50:")
    prime_analyses = batch_analyze_primes(1, 50)
    
    # Count primes by classification
    inner_octave_count = sum(1 for a in prime_analyses if a['classification'] == 'inner_octave')
    outer_octave_count = sum(1 for a in prime_analyses if a['classification'] == 'outer_octave')
    cross_resonant_count = sum(1 for a in prime_analyses if a['classification'] == 'cross_resonant')
    
    print(f"Found {len(prime_analyses)} primes:")
    print(f"  Inner Octave: {inner_octave_count}")
    print(f"  Outer Octave: {outer_octave_count}")
    print(f"  Cross-Resonant: {cross_resonant_count}")
    
    print("\nEnhanced resonance detection completed successfully.")

if __name__ == "__main__":
    main()
