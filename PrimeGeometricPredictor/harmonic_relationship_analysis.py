#!/usr/bin/env python3
"""
Harmonic Relationship Analysis for Prime Number Classification

This module implements advanced harmonic relationship analysis for prime numbers,
focusing on how primes relate to each other across different systems and octaves.
"""

import numpy as np
import math
import decimal
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Import the enhanced resonance detector
import sys
sys.path.append('/home/ubuntu/fibonacci_prime_project/enhanced_package')
from enhanced_resonance_detector import (
    PHI, SYSTEM_BOUNDARY, DIMENSIONAL_FACTOR, 
    FUNDAMENTAL_FREQUENCY, OCTAVE_RATIO,
    ufrf_dimensional_mapping, calculate_harmonic_frequency,
    identify_harmonic_octave, calculate_cross_octave_resonance,
    classify_prime_by_octave, is_prime_with_enhanced_resonance
)

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

# Define harmonic relationship constants
HARMONIC_SERIES = [1.0, 2.0, 3.0, 5.0, 7.0, 11.0, 13.0]  # Prime-focused harmonic series
RESONANCE_THRESHOLD = 0.85  # Threshold for significant resonance

def calculate_prime_harmonic_series(prime):
    """
    Calculate the harmonic series generated by a prime number.
    
    Args:
        prime: The prime number to analyze
        
    Returns:
        A list of the first 7 harmonics generated by the prime
    """
    return [prime * h for h in HARMONIC_SERIES]

def calculate_harmonic_resonance_between_primes(prime1, prime2):
    """
    Calculate the harmonic resonance between two prime numbers.
    
    Args:
        prime1: First prime number
        prime2: Second prime number
        
    Returns:
        A resonance score between 0 and 1
    """
    # Get harmonic series for both primes
    harmonics1 = calculate_prime_harmonic_series(prime1)
    harmonics2 = calculate_prime_harmonic_series(prime2)
    
    # Calculate normalized frequencies
    normalized1 = [h * FUNDAMENTAL_FREQUENCY % 1.0 for h in harmonics1]
    normalized2 = [h * FUNDAMENTAL_FREQUENCY % 1.0 for h in harmonics2]
    
    # Find closest matches between harmonics
    min_distances = []
    for freq1 in normalized1:
        distances = [min(abs(freq1 - freq2), 1.0 - abs(freq1 - freq2)) for freq2 in normalized2]
        min_distances.append(min(distances))
    
    # Calculate average minimum distance (lower is better)
    avg_min_distance = sum(min_distances) / len(min_distances)
    
    # Convert to resonance score (higher is better)
    resonance_score = 1.0 - avg_min_distance
    
    return resonance_score

def find_harmonic_prime_clusters(primes):
    """
    Find clusters of primes that have strong harmonic relationships with each other.
    
    Args:
        primes: List of prime numbers to analyze
        
    Returns:
        A list of prime clusters
    """
    # Calculate resonance between all pairs of primes
    resonance_matrix = {}
    for i, prime1 in enumerate(primes):
        for j, prime2 in enumerate(primes[i+1:], i+1):
            resonance = calculate_harmonic_resonance_between_primes(prime1, prime2)
            resonance_matrix[(prime1, prime2)] = resonance
    
    # Find clusters based on resonance threshold
    clusters = []
    remaining_primes = set(primes)
    
    while remaining_primes:
        # Start a new cluster with the first remaining prime
        current_prime = next(iter(remaining_primes))
        current_cluster = {current_prime}
        remaining_primes.remove(current_prime)
        
        # Find all primes that resonate with the current cluster
        added = True
        while added:
            added = False
            for prime in list(remaining_primes):
                # Check if prime resonates with any prime in the current cluster
                for cluster_prime in current_cluster:
                    key = (min(prime, cluster_prime), max(prime, cluster_prime))
                    if resonance_matrix.get(key, 0) >= RESONANCE_THRESHOLD:
                        current_cluster.add(prime)
                        remaining_primes.remove(prime)
                        added = True
                        break
        
        # Add the cluster if it has more than one prime
        if len(current_cluster) > 1:
            clusters.append(sorted(current_cluster))
    
    return clusters

def analyze_prime_harmonic_field(start, end, resolution=10):
    """
    Analyze the harmonic field created by prime numbers in a range.
    
    Args:
        start: Starting number
        end: Ending number
        resolution: Resolution of the field analysis
        
    Returns:
        A dictionary mapping regions to harmonic field strength
    """
    # Find primes in the range
    primes = []
    for n in range(start, end + 1):
        if n > 1 and all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1)):
            primes.append(n)
    
    # Initialize harmonic field
    harmonic_field = defaultdict(float)
    
    # Calculate field strength across the frequency space
    frequency_space = np.linspace(0, 1, resolution, endpoint=False)
    
    for prime in primes:
        # Get harmonic series for this prime
        harmonics = calculate_prime_harmonic_series(prime)
        
        # Calculate normalized frequencies
        normalized = [h * FUNDAMENTAL_FREQUENCY % 1.0 for h in harmonics]
        
        # Add field strength around each harmonic frequency
        for freq in normalized:
            # Add field strength with a Gaussian distribution around the frequency
            for i, f in enumerate(frequency_space):
                distance = min(abs(freq - f), 1.0 - abs(freq - f))
                # Gaussian falloff with distance
                field_strength = math.exp(-10 * distance**2)
                harmonic_field[i] += field_strength
    
    # Normalize field strength
    max_strength = max(harmonic_field.values()) if harmonic_field else 1.0
    for key in harmonic_field:
        harmonic_field[key] /= max_strength
    
    return harmonic_field, frequency_space

def visualize_harmonic_field(harmonic_field, frequency_space, output_dir='.'):
    """
    Visualize the harmonic field created by prime numbers.
    
    Args:
        harmonic_field: Dictionary mapping regions to field strength
        frequency_space: Array of frequency values
        output_dir: Directory to save the visualization
    """
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Convert dictionary to arrays for plotting
    field_strength = [harmonic_field[i] for i in range(len(frequency_space))]
    
    # Plot the harmonic field
    plt.plot(frequency_space, field_strength, 'b-', linewidth=2)
    
    # Add markers for key frequencies
    for i, freq in enumerate(frequency_space):
        if harmonic_field[i] > 0.7:  # Highlight strong resonance points
            plt.plot(freq, harmonic_field[i], 'ro', markersize=8)
    
    plt.title('Prime Number Harmonic Field')
    plt.xlabel('Normalized Frequency')
    plt.ylabel('Field Strength')
    plt.grid(True)
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'prime_harmonic_field.png'))
    plt.close()

def calculate_harmonic_coordinates(prime):
    """
    Calculate 3D coordinates for a prime based on its harmonic properties.
    
    Args:
        prime: The prime number to map
        
    Returns:
        A tuple (x, y, z) representing the prime in harmonic space
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(prime)
    
    # Calculate harmonic frequency
    frequency = calculate_harmonic_frequency(prime)
    
    # Calculate octave
    octave = identify_harmonic_octave(prime)
    
    # Calculate cross-octave resonance
    resonance_map = calculate_cross_octave_resonance(prime)
    max_resonance = max(resonance_map.values())
    
    # Calculate coordinates in harmonic space
    
    # X-coordinate: Based on frequency and golden ratio
    x = math.cos(2 * math.pi * frequency) * (1 + (position / DIMENSIONAL_FACTOR))
    
    # Y-coordinate: Based on frequency and golden ratio
    y = math.sin(2 * math.pi * frequency) * (1 + (position / DIMENSIONAL_FACTOR))
    
    # Z-coordinate: Based on octave and resonance
    z = octave + max_resonance
    
    return (x, y, z)

def visualize_harmonic_prime_space(primes, output_dir='.'):
    """
    Visualize primes in 3D harmonic space.
    
    Args:
        primes: List of prime numbers to visualize
        output_dir: Directory to save the visualization
    """
    # Calculate classifications and coordinates for each prime
    classifications = {}
    coordinates = {}
    
    for prime in primes:
        # Get classification
        _, classification, _ = is_prime_with_enhanced_resonance(prime)
        classifications[prime] = classification
        
        # Calculate coordinates
        coordinates[prime] = calculate_harmonic_coordinates(prime)
    
    # Separate primes by classification
    inner_octave_primes = [p for p in primes if classifications[p] == 'inner_octave']
    outer_octave_primes = [p for p in primes if classifications[p] == 'outer_octave']
    cross_resonant_primes = [p for p in primes if classifications[p] == 'cross_resonant']
    
    # Create the plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot primes by classification
    if inner_octave_primes:
        x, y, z = zip(*[coordinates[p] for p in inner_octave_primes])
        ax.scatter(x, y, z, c='blue', s=50, label='Inner Octave Primes')
    
    if outer_octave_primes:
        x, y, z = zip(*[coordinates[p] for p in outer_octave_primes])
        ax.scatter(x, y, z, c='green', s=50, label='Outer Octave Primes')
    
    if cross_resonant_primes:
        x, y, z = zip(*[coordinates[p] for p in cross_resonant_primes])
        ax.scatter(x, y, z, c='red', s=80, label='Cross-Resonant Primes')
    
    # Add prime labels
    for prime in primes:
        x, y, z = coordinates[prime]
        ax.text(x, y, z, str(prime), fontsize=8)
    
    ax.set_title('Prime Numbers in Harmonic Space')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.legend()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'harmonic_prime_space.png'))
    plt.close()

def analyze_prime_19_harmonic_relationships():
    """
    Perform detailed analysis of prime 19's harmonic relationships with other primes.
    
    Returns:
        A dictionary of analysis results
    """
    # Define a range of primes to check against
    test_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    # Calculate resonance between 19 and other primes
    resonance_scores = {}
    for prime in test_primes:
        if prime != 19:
            resonance = calculate_harmonic_resonance_between_primes(19, prime)
            resonance_scores[prime] = resonance
    
    # Sort by resonance score
    sorted_resonance = sorted(resonance_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate harmonic series for 19
    harmonics_19 = calculate_prime_harmonic_series(19)
    normalized_19 = [h * FUNDAMENTAL_FREQUENCY % 1.0 for h in harmonics_19]
    
    # Calculate octave classification for 19
    _, classification, _ = is_prime_with_enhanced_resonance(19)
    
    # Calculate cross-octave resonance for 19
    resonance_map = calculate_cross_octave_resonance(19)
    
    # Compile results
    results = {
        "prime": 19,
        "classification": classification,
        "harmonic_series": harmonics_19,
        "normalized_frequencies": normalized_19,
        "cross_octave_resonance": resonance_map,
        "resonance_with_other_primes": dict(sorted_resonance)
    }
    
    return results

def main():
    """
    Main function to demonstrate harmonic relationship analysis.
    """
    print("Harmonic Relationship Analysis for Prime Number Classification")
    print("===========================================================")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Analyze prime 19's harmonic relationships
    print("\nAnalyzing prime 19's harmonic relationships:")
    results = analyze_prime_19_harmonic_relationships()
    
    print(f"Prime 19 Classification: {results['classification']}")
    print("Harmonic Series:", [f"{h:.1f}" for h in results['harmonic_series']])
    print("Normalized Frequencies:", [f"{f:.6f}" for f in results['normalized_frequencies']])
    
    print("\nCross-Octave Resonance:")
    for octave_pair, resonance in results['cross_octave_resonance'].items():
        print(f"  Octaves {octave_pair}: {resonance:.4f}")
    
    print("\nResonance with Other Primes:")
    for prime, resonance in results['resonance_with_other_primes'].items():
        print(f"  Prime {prime}: {resonance:.4f}")
    
    # Find primes in a small range
    print("\nFinding primes in range 1-50:")
    primes = []
    for n in range(1, 51):
        if n > 1 and all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1)):
            primes.append(n)
    
    print(f"Found {len(primes)} primes: {primes}")
    
    # Find harmonic prime clusters
    print("\nFinding harmonic prime clusters:")
    clusters = find_harmonic_prime_clusters(primes)
    
    print(f"Found {len(clusters)} clusters:")
    for i, cluster in enumerate(clusters):
        print(f"  Cluster {i+1}: {cluster}")
    
    # Analyze harmonic field
    print("\nAnalyzing harmonic field for primes 1-50:")
    harmonic_field, frequency_space = analyze_prime_harmonic_field(1, 50)
    
    # Visualize harmonic field
    print("Visualizing harmonic field...")
    visualize_harmonic_field(harmonic_field, frequency_space, "output")
    
    # Visualize primes in harmonic space
    print("Visualizing primes in harmonic space...")
    visualize_harmonic_prime_space(primes, "output")
    
    print("\nHarmonic relationship analysis completed successfully.")

if __name__ == "__main__":
    main()
