#!/usr/bin/env python3
"""
Prime Classification System for Inner vs. Outer Octave Primes

This module implements a comprehensive classification system for prime numbers,
distinguishing between inner octave, outer octave, and cross-resonant primes
based on their geometric and harmonic properties.
"""

import numpy as np
import math
import decimal
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

# Import from other modules
import sys
sys.path.append('/home/ubuntu/fibonacci_prime_project/enhanced_package')
from enhanced_resonance_detector import (
    PHI, SYSTEM_BOUNDARY, DIMENSIONAL_FACTOR, 
    FUNDAMENTAL_FREQUENCY, OCTAVE_RATIO,
    ufrf_dimensional_mapping, calculate_harmonic_frequency,
    identify_harmonic_octave, calculate_cross_octave_resonance,
    classify_prime_by_octave, is_prime_with_enhanced_resonance
)
from harmonic_relationship_analysis import (
    calculate_prime_harmonic_series,
    calculate_harmonic_resonance_between_primes,
    calculate_harmonic_coordinates
)
from sacred_geometry_analysis import (
    calculate_sacred_angle,
    map_to_flower_of_life,
    map_to_metatrons_cube,
    analyze_center_edge_relationship,
    calculate_platonic_solid_mapping
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

# Classification Constants
INNER_OCTAVE_THRESHOLD = 0.7
OUTER_OCTAVE_THRESHOLD = 0.6
CROSS_RESONANT_THRESHOLD = 0.8
CENTER_EDGE_WEIGHT = 0.3
HARMONIC_WEIGHT = 0.4
SACRED_GEOMETRY_WEIGHT = 0.3

class PrimeClassifier:
    """
    A comprehensive classifier for prime numbers based on their geometric and harmonic properties.
    """
    
    def __init__(self):
        """Initialize the classifier."""
        # Cache for classification results
        self.classification_cache = {}
        
        # Cache for prime verification
        self.prime_cache = {}
        
        # Create custom colormaps for visualization
        self.create_custom_colormaps()
    
    def create_custom_colormaps(self):
        """Create custom colormaps for visualizing prime classifications."""
        # Inner Octave colormap (blues)
        inner_colors = [(0.9, 0.9, 1.0), (0.0, 0.0, 0.8)]
        self.inner_cmap = LinearSegmentedColormap.from_list('inner_octave', inner_colors)
        
        # Outer Octave colormap (greens)
        outer_colors = [(0.9, 1.0, 0.9), (0.0, 0.6, 0.0)]
        self.outer_cmap = LinearSegmentedColormap.from_list('outer_octave', outer_colors)
        
        # Cross-Resonant colormap (reds)
        cross_colors = [(1.0, 0.9, 0.9), (0.8, 0.0, 0.0)]
        self.cross_cmap = LinearSegmentedColormap.from_list('cross_resonant', cross_colors)
    
    def is_prime(self, n):
        """
        Check if a number is prime using cached results or primality test.
        
        Args:
            n: The number to check
            
        Returns:
            Boolean indicating if the number is prime
        """
        # Check cache first
        if n in self.prime_cache:
            return self.prime_cache[n]
        
        # Special cases
        if n < 2:
            self.prime_cache[n] = False
            return False
        if n == 2 or n == 3:
            self.prime_cache[n] = True
            return True
        if n % 2 == 0:
            self.prime_cache[n] = False
            return False
        
        # Check primality using trial division
        is_prime = all(n % i != 0 for i in range(3, int(math.sqrt(n)) + 1, 2))
        
        # Cache the result
        self.prime_cache[n] = is_prime
        
        return is_prime
    
    def calculate_inner_octave_score(self, n):
        """
        Calculate how strongly a number aligns with inner octave characteristics.
        
        Args:
            n: The number to analyze
            
        Returns:
            A score between 0 and 1 (higher = stronger inner octave alignment)
        """
        # Get dimensional mapping
        system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
        
        # Calculate harmonic frequency
        frequency = calculate_harmonic_frequency(n)
        
        # Calculate cross-octave resonance
        resonance_map = calculate_cross_octave_resonance(n)
        
        # Inner octave primes typically have strong resonance between fundamental and first octave
        fundamental_first_resonance = resonance_map.get((0, 1), 0)
        
        # Inner octave primes typically have positions 2, 3, 5, 7, 11, 13
        prime_positions = {2, 3, 5, 7, 11, 13}
        position_score = 1.0 if position in prime_positions else 0.0
        
        # Inner octave primes typically have low system levels
        system_level_score = 1.0 / (1.0 + system_level / 5.0)
        
        # Inner octave primes typically have center point characteristics in sacred geometry
        center_edge = analyze_center_edge_relationship(n)
        center_score = center_edge['center_score']
        
        # Calculate weighted score
        inner_score = (
            0.4 * fundamental_first_resonance +
            0.2 * position_score +
            0.2 * system_level_score +
            0.2 * center_score
        )
        
        return inner_score
    
    def calculate_outer_octave_score(self, n):
        """
        Calculate how strongly a number aligns with outer octave characteristics.
        
        Args:
            n: The number to analyze
            
        Returns:
            A score between 0 and 1 (higher = stronger outer octave alignment)
        """
        # Get dimensional mapping
        system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
        
        # Calculate harmonic frequency
        frequency = calculate_harmonic_frequency(n)
        
        # Calculate cross-octave resonance
        resonance_map = calculate_cross_octave_resonance(n)
        
        # Outer octave primes typically have weaker resonance between fundamental and first octave
        fundamental_first_resonance = resonance_map.get((0, 1), 0)
        inverse_fundamental_first = 1.0 - fundamental_first_resonance
        
        # Outer octave primes typically have positions 1, 4, 6, 8, 9, 10, 12
        outer_positions = {1, 4, 6, 8, 9, 10, 12}
        position_score = 1.0 if position in outer_positions else 0.0
        
        # Outer octave primes typically have higher system levels
        system_level_score = min(system_level / 10.0, 1.0)
        
        # Outer octave primes typically have edge point characteristics in sacred geometry
        center_edge = analyze_center_edge_relationship(n)
        edge_score = center_edge['edge_score']
        
        # Calculate weighted score
        outer_score = (
            0.4 * inverse_fundamental_first +
            0.2 * position_score +
            0.2 * system_level_score +
            0.2 * edge_score
        )
        
        return outer_score
    
    def calculate_cross_resonant_score(self, n):
        """
        Calculate how strongly a number aligns with cross-resonant characteristics.
        
        Args:
            n: The number to analyze
            
        Returns:
            A score between 0 and 1 (higher = stronger cross-resonant alignment)
        """
        # Calculate cross-octave resonance
        resonance_map = calculate_cross_octave_resonance(n)
        
        # Cross-resonant primes typically have strong resonance between non-adjacent octaves
        cross_octave_pairs = [(0, 2), (0, 3), (1, 3)]
        cross_octave_resonances = [resonance_map.get(pair, 0) for pair in cross_octave_pairs]
        max_cross_resonance = max(cross_octave_resonances) if cross_octave_resonances else 0
        
        # Cross-resonant primes typically have balanced center and edge characteristics
        center_edge = analyze_center_edge_relationship(n)
        balance_score = 1.0 - abs(center_edge['center_score'] - center_edge['edge_score'])
        
        # Cross-resonant primes typically align with specific Platonic solids
        platonic_solid, platonic_score = calculate_platonic_solid_mapping(n)
        dodecahedron_alignment = platonic_score if platonic_solid == 'dodecahedron' else 0.0
        
        # Calculate weighted score
        cross_score = (
            0.5 * max_cross_resonance +
            0.3 * balance_score +
            0.2 * dodecahedron_alignment
        )
        
        return cross_score
    
    def classify_prime(self, n):
        """
        Classify a prime number as inner octave, outer octave, or cross-resonant.
        
        Args:
            n: The number to classify
            
        Returns:
            A tuple (is_prime, classification, confidence_score)
        """
        # Check if already classified
        if n in self.classification_cache:
            return self.classification_cache[n]
        
        # Check if prime
        if not self.is_prime(n):
            result = (False, "non_prime", 0.0)
            self.classification_cache[n] = result
            return result
        
        # Calculate scores for each classification
        inner_score = self.calculate_inner_octave_score(n)
        outer_score = self.calculate_outer_octave_score(n)
        cross_score = self.calculate_cross_resonant_score(n)
        
        # Determine classification based on highest score
        scores = {
            "inner_octave": inner_score,
            "outer_octave": outer_score,
            "cross_resonant": cross_score
        }
        
        classification = max(scores.items(), key=lambda x: x[1])
        class_name = classification[0]
        confidence = classification[1]
        
        # Store result in cache
        result = (True, class_name, confidence)
        self.classification_cache[n] = result
        
        return result
    
    def get_comprehensive_analysis(self, n):
        """
        Perform comprehensive analysis of a number, combining all aspects.
        
        Args:
            n: The number to analyze
            
        Returns:
            A dictionary containing detailed analysis results
        """
        # Check if prime
        is_prime = self.is_prime(n)
        
        if not is_prime:
            return {
                "number": n,
                "is_prime": False,
                "classification": "non_prime",
                "confidence": 0.0
            }
        
        # Get classification
        _, classification, confidence = self.classify_prime(n)
        
        # Get dimensional mapping
        system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
        
        # Calculate harmonic frequency
        frequency = calculate_harmonic_frequency(n)
        
        # Calculate octave
        octave = identify_harmonic_octave(n)
        
        # Calculate cross-octave resonance
        resonance_map = calculate_cross_octave_resonance(n)
        
        # Calculate harmonic coordinates
        harmonic_coords = calculate_harmonic_coordinates(n)
        
        # Calculate sacred geometry mapping
        sacred_angle = calculate_sacred_angle(n)
        flower_coords = map_to_flower_of_life(n)
        metatron_coords = map_to_metatrons_cube(n)
        
        # Analyze center-edge relationship
        center_edge = analyze_center_edge_relationship(n)
        
        # Get Platonic solid alignment
        platonic_solid, platonic_score = calculate_platonic_solid_mapping(n)
        
        # Calculate classification scores
        inner_score = self.calculate_inner_octave_score(n)
        outer_score = self.calculate_outer_octave_score(n)
        cross_score = self.calculate_cross_resonant_score(n)
        
        # Compile results
        results = {
            "number": n,
            "is_prime": True,
            "classification": classification,
            "confidence": confidence,
            "system_level": system_level,
            "dimension": dimension,
            "position": position,
            "cycle": cycle,
            "metacycle": metacycle,
            "harmonic_frequency": frequency,
            "octave": octave,
            "cross_octave_resonance": dict(resonance_map),
            "harmonic_coordinates": harmonic_coords,
            "sacred_angle": sacred_angle,
            "flower_of_life_coordinates": flower_coords,
            "metatrons_cube_coordinates": metatron_coords,
            "center_score": center_edge['center_score'],
            "edge_score": center_edge['edge_score'],
            "primary_role": center_edge['primary_role'],
            "platonic_solid": platonic_solid,
            "platonic_score": platonic_score,
            "inner_octave_score": inner_score,
            "outer_octave_score": outer_score,
            "cross_resonant_score": cross_score
        }
        
        return results
    
    def batch_classify_primes(self, start, end, max_count=100):
        """
        Classify a batch of prime numbers with memory constraints.
        
        Args:
            start: Starting number
            end: Ending number
            max_count: Maximum number of primes to classify
            
        Returns:
            A list of classification results for prime numbers
        """
        results = []
        count = 0
        
        for n in range(start, end + 1):
            # Skip even numbers except 2
            if n > 2 and n % 2 == 0:
                continue
            
            # Check if prime
            if self.is_prime(n):
                # Classify the prime
                _, classification, confidence = self.classify_prime(n)
                
                # Add to results
                results.append({
                    "number": n,
                    "classification": classification,
                    "confidence": confidence
                })
                
                count += 1
                
                # Check if we've reached the maximum count
                if count >= max_count:
                    break
        
        return results
    
    def find_primes_by_classification(self, classification, start, end, max_count=10):
        """
        Find prime numbers of a specific classification.
        
        Args:
            classification: The classification to search for ("inner_octave", "outer_octave", or "cross_resonant")
            start: Starting number
            end: Ending number
            max_count: Maximum number of primes to find
            
        Returns:
            A list of prime numbers with the specified classification
        """
        matching_primes = []
        count = 0
        
        for n in range(start, end + 1):
            # Skip even numbers except 2
            if n > 2 and n % 2 == 0:
                continue
            
            # Check if prime and classify
            is_prime, prime_class, confidence = self.classify_prime(n)
            
            if is_prime and prime_class == classification:
                # Add to results
                matching_primes.append({
                    "number": n,
                    "classification": classification,
                    "confidence": confidence
                })
                
                count += 1
                
                # Check if we've reached the maximum count
                if count >= max_count:
                    break
        
        return matching_primes
    
    def visualize_classification_distribution(self, primes, output_dir='.'):
        """
        Visualize the distribution of prime classifications.
        
        Args:
            primes: List of prime numbers to visualize
            output_dir: Directory to save the visualization
        """
        # Classify each prime
        classifications = {}
        confidences = {}
        
        for prime in primes:
            _, classification, confidence = self.classify_prime(prime)
            classifications[prime] = classification
            confidences[prime] = confidence
        
        # Count primes by classification
        inner_count = sum(1 for p in primes if classifications[p] == 'inner_octave')
        outer_count = sum(1 for p in primes if classifications[p] == 'outer_octave')
        cross_count = sum(1 for p in primes if classifications[p] == 'cross_resonant')
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Pie chart of classifications
        labels = ['Inner Octave', 'Outer Octave', 'Cross-Resonant']
        sizes = [inner_count, outer_count, cross_count]
        colors = ['blue', 'green', 'red']
        explode = (0.1, 0, 0)  # explode the 1st slice (Inner Octave)
        
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax1.set_title('Distribution of Prime Classifications')
        
        # Bar chart of confidence by classification
        inner_primes = [p for p in primes if classifications[p] == 'inner_octave']
        outer_primes = [p for p in primes if classifications[p] == 'outer_octave']
        cross_primes = [p for p in primes if classifications[p] == 'cross_resonant']
        
        inner_conf = [confidences[p] for p in inner_primes] if inner_primes else [0]
        outer_conf = [confidences[p] for p in outer_primes] if outer_primes else [0]
        cross_conf = [confidences[p] for p in cross_primes] if cross_primes else [0]
        
        ax2.boxplot([inner_conf, outer_conf, cross_conf], labels=labels)
        ax2.set_title('Confidence Scores by Classification')
        ax2.set_ylabel('Confidence Score')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Save the plot
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, 'classification_distribution.png'))
        plt.close()
    
    def visualize_classification_scores(self, primes, output_dir='.'):
        """
        Visualize the classification scores for each prime.
        
        Args:
            primes: List of prime numbers to visualize
            output_dir: Directory to save the visualization
        """
        # Calculate scores for each prime
        inner_scores = []
        outer_scores = []
        cross_scores = []
        
        for prime in primes:
            inner_scores.append(self.calculate_inner_octave_score(prime))
            outer_scores.append(self.calculate_outer_octave_score(prime))
            cross_scores.append(self.calculate_cross_resonant_score(prime))
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Set up bar positions
        bar_width = 0.25
        index = np.arange(len(primes))
        
        # Create bars
        bar1 = ax.bar(index, inner_scores, bar_width, label='Inner Octave Score', color='blue', alpha=0.7)
        bar2 = ax.bar(index + bar_width, outer_scores, bar_width, label='Outer Octave Score', color='green', alpha=0.7)
        bar3 = ax.bar(index + 2*bar_width, cross_scores, bar_width, label='Cross-Resonant Score', color='red', alpha=0.7)
        
        # Add labels and title
        ax.set_xlabel('Prime Number')
        ax.set_ylabel('Classification Score')
        ax.set_title('Classification Scores for Prime Numbers')
        ax.set_xticks(index + bar_width)
        ax.set_xticklabels([str(p) for p in primes])
        ax.legend()
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Save the plot
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, 'classification_scores.png'))
        plt.close()
    
    def visualize_3d_classification_space(self, primes, output_dir='.'):
        """
        Visualize primes in 3D classification space.
        
        Args:
            primes: List of prime numbers to visualize
            output_dir: Directory to save the visualization
        """
        # Calculate scores for each prime
        inner_scores = []
        outer_scores = []
        cross_scores = []
        classifications = []
        
        for prime in primes:
            inner_scores.append(self.calculate_inner_octave_score(prime))
            outer_scores.append(self.calculate_outer_octave_score(prime))
            cross_scores.append(self.calculate_cross_resonant_score(prime))
            _, classification, _ = self.classify_prime(prime)
            classifications.append(classification)
        
        # Create the plot
        fig = plt.figure(figsize=(14, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create scatter plot with color based on classification
        colors = []
        for c in classifications:
            if c == 'inner_octave':
                colors.append('blue')
            elif c == 'outer_octave':
                colors.append('green')
            else:  # cross_resonant
                colors.append('red')
        
        scatter = ax.scatter(inner_scores, outer_scores, cross_scores, c=colors, s=100)
        
        # Add labels for each point
        for i, prime in enumerate(primes):
            ax.text(inner_scores[i], outer_scores[i], cross_scores[i], str(prime), fontsize=8)
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Inner Octave'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Outer Octave'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Cross-Resonant')
        ]
        ax.legend(handles=legend_elements)
        
        # Add labels and title
        ax.set_xlabel('Inner Octave Score')
        ax.set_ylabel('Outer Octave Score')
        ax.set_zlabel('Cross-Resonant Score')
        ax.set_title('Prime Numbers in 3D Classification Space')
        
        # Save the plot
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(os.path.join(output_dir, 'classification_3d_space.png'))
        plt.close()

def main():
    """
    Main function to demonstrate the prime classification system.
    """
    print("Prime Classification System for Inner vs. Outer Octave Primes")
    print("===========================================================")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Initialize classifier
    classifier = PrimeClassifier()
    
    # Analyze prime 19 (mentioned by the user as resonant across first and second harmonics)
    print("\nComprehensive Analysis of Prime 19:")
    analysis = classifier.get_comprehensive_analysis(19)
    
    print(f"Classification: {analysis['classification']} (Confidence: {analysis['confidence']:.4f})")
    print(f"Inner Octave Score: {analysis['inner_octave_score']:.4f}")
    print(f"Outer Octave Score: {analysis['outer_octave_score']:.4f}")
    print(f"Cross-Resonant Score: {analysis['cross_resonant_score']:.4f}")
    print(f"Primary Role in Sacred Geometry: {analysis['primary_role']}")
    print(f"Platonic Solid Alignment: {analysis['platonic_solid']} (Score: {analysis['platonic_score']:.4f})")
    
    # Find primes in a small range
    print("\nFinding primes in range 1-50:")
    primes = []
    for n in range(1, 51):
        if classifier.is_prime(n):
            primes.append(n)
    
    print(f"Found {len(primes)} primes: {primes}")
    
    # Classify all primes
    print("\nClassifying all primes:")
    for prime in primes:
        _, classification, confidence = classifier.classify_prime(prime)
        print(f"Prime {prime}: {classification} (Confidence: {confidence:.4f})")
    
    # Find primes by classification
    print("\nFinding inner octave primes in range 1-100:")
    inner_primes = classifier.find_primes_by_classification("inner_octave", 1, 100)
    print(f"Found {len(inner_primes)} inner octave primes:")
    for p in inner_primes:
        print(f"  {p['number']} (Confidence: {p['confidence']:.4f})")
    
    print("\nFinding outer octave primes in range 1-100:")
    outer_primes = classifier.find_primes_by_classification("outer_octave", 1, 100)
    print(f"Found {len(outer_primes)} outer octave primes:")
    for p in outer_primes:
        print(f"  {p['number']} (Confidence: {p['confidence']:.4f})")
    
    print("\nFinding cross-resonant primes in range 1-100:")
    cross_primes = classifier.find_primes_by_classification("cross_resonant", 1, 100)
    print(f"Found {len(cross_primes)} cross-resonant primes:")
    for p in cross_primes:
        print(f"  {p['number']} (Confidence: {p['confidence']:.4f})")
    
    # Visualize classification distribution
    print("\nVisualizing classification distribution...")
    classifier.visualize_classification_distribution(primes, "output")
    
    # Visualize classification scores
    print("Visualizing classification scores...")
    classifier.visualize_classification_scores(primes, "output")
    
    # Visualize 3D classification space
    print("Visualizing 3D classification space...")
    classifier.visualize_3d_classification_space(primes, "output")
    
    print("\nPrime classification system completed successfully.")

if __name__ == "__main__":
    main()
