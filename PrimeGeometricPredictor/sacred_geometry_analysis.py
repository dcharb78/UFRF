#!/usr/bin/env python3
"""
Angular Relationship Analysis with Sacred Geometry Principles

This module implements advanced angular relationship analysis for prime numbers,
incorporating sacred geometry principles to understand how primes relate across dimensions.
"""

import numpy as np
import math
import decimal
from collections import defaultdict
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

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

# Sacred Geometry Constants
VESICA_PISCIS_RATIO = math.sqrt(3) / 2  # Ratio in Vesica Piscis
SEED_OF_LIFE_POINTS = 7  # Number of circles in Seed of Life
FLOWER_OF_LIFE_POINTS = 19  # Number of circles in Flower of Life
METATRONS_CUBE_VERTICES = 13  # Number of vertices in Metatron's Cube
PLATONIC_SOLIDS = {
    "tetrahedron": 4,  # Vertices in a tetrahedron
    "hexahedron": 8,   # Vertices in a cube/hexahedron
    "octahedron": 6,   # Vertices in an octahedron
    "dodecahedron": 20, # Vertices in a dodecahedron
    "icosahedron": 12  # Vertices in an icosahedron
}

def calculate_sacred_angle(n):
    """
    Calculate the sacred angle of a number based on sacred geometry principles.
    
    Args:
        n: The number to analyze
        
    Returns:
        The sacred angle in radians
    """
    # Golden angle (based on golden ratio)
    golden_angle_rad = 2 * math.pi / (PHI * PHI)
    
    # Vesica Piscis angle (based on the intersection of two circles)
    vesica_angle_rad = 2 * math.asin(1/3)
    
    # Calculate a weighted angle based on the number's properties
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Weight factors based on position in dimensional structure
    golden_weight = (position / DIMENSIONAL_FACTOR)
    vesica_weight = 1 - golden_weight
    
    # Calculate weighted angle
    weighted_angle = (golden_weight * (n * golden_angle_rad) + 
                      vesica_weight * (n * vesica_angle_rad)) % (2 * math.pi)
    
    return weighted_angle

def map_to_flower_of_life(n):
    """
    Map a number to a position in the Flower of Life pattern.
    
    Args:
        n: The number to map
        
    Returns:
        A tuple (x, y) representing coordinates in the Flower of Life
    """
    # Calculate sacred angle
    angle = calculate_sacred_angle(n)
    
    # Calculate radius based on position in dimensional structure
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # In Flower of Life, points are arranged in concentric circles
    # The radius is determined by the system level and position
    base_radius = 1.0
    radius_step = 0.5
    
    # Calculate which circle this number belongs to (based on position)
    circle_index = (position - 1) % 6  # 6 circles around the center in Flower of Life
    
    # Calculate radius
    radius = base_radius + (circle_index * radius_step)
    
    # Calculate coordinates
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    return (x, y)

def map_to_metatrons_cube(n):
    """
    Map a number to a vertex in Metatron's Cube.
    
    Args:
        n: The number to map
        
    Returns:
        A tuple (x, y, z) representing coordinates in Metatron's Cube
    """
    # Metatron's Cube has 13 vertices (center + 12 vertices of an icosahedron)
    # We'll map the number to one of these vertices based on its properties
    
    # Calculate which vertex this number maps to
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    vertex_index = (position - 1) % METATRONS_CUBE_VERTICES
    
    # Define the 13 vertices of Metatron's Cube
    # Center point
    if vertex_index == 0:
        return (0, 0, 0)
    
    # The 12 vertices of the icosahedron
    # These are arranged in 3 orthogonal golden rectangles
    vertex_index -= 1  # Adjust to 0-11 range
    
    # Calculate which golden rectangle this vertex belongs to
    rectangle_index = vertex_index // 4
    position_in_rectangle = vertex_index % 4
    
    # Define the coordinates based on golden ratio
    if rectangle_index == 0:  # XY plane
        if position_in_rectangle == 0:
            return (0, 1, PHI)
        elif position_in_rectangle == 1:
            return (0, -1, PHI)
        elif position_in_rectangle == 2:
            return (0, 1, -PHI)
        else:
            return (0, -1, -PHI)
    elif rectangle_index == 1:  # YZ plane
        if position_in_rectangle == 0:
            return (PHI, 0, 1)
        elif position_in_rectangle == 1:
            return (PHI, 0, -1)
        elif position_in_rectangle == 2:
            return (-PHI, 0, 1)
        else:
            return (-PHI, 0, -1)
    else:  # XZ plane
        if position_in_rectangle == 0:
            return (1, PHI, 0)
        elif position_in_rectangle == 1:
            return (-1, PHI, 0)
        elif position_in_rectangle == 2:
            return (1, -PHI, 0)
        else:
            return (-1, -PHI, 0)

def calculate_platonic_solid_mapping(n):
    """
    Determine which Platonic solid a number is most aligned with.
    
    Args:
        n: The number to analyze
        
    Returns:
        A tuple (solid_name, alignment_score)
    """
    # Calculate properties of the number
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate alignment scores for each Platonic solid
    alignment_scores = {}
    
    # Tetrahedron (Fire) - associated with primes of form 4n+1
    tetrahedron_score = 1 - abs(((n % 4) - 1) / 4)
    alignment_scores["tetrahedron"] = tetrahedron_score
    
    # Hexahedron/Cube (Earth) - associated with primes of form 4n+3
    hexahedron_score = 1 - abs(((n % 4) - 3) / 4)
    alignment_scores["hexahedron"] = hexahedron_score
    
    # Octahedron (Air) - associated with primes of form 6n+1
    octahedron_score = 1 - abs(((n % 6) - 1) / 6)
    alignment_scores["octahedron"] = octahedron_score
    
    # Dodecahedron (Ether/Universe) - associated with primes of form 10n±1
    dodecahedron_score = max(1 - abs(((n % 10) - 1) / 10), 1 - abs(((n % 10) - 9) / 10))
    alignment_scores["dodecahedron"] = dodecahedron_score
    
    # Icosahedron (Water) - associated with primes of form 10n±3
    icosahedron_score = max(1 - abs(((n % 10) - 3) / 10), 1 - abs(((n % 10) - 7) / 10))
    alignment_scores["icosahedron"] = icosahedron_score
    
    # Find the Platonic solid with the highest alignment score
    best_solid = max(alignment_scores.items(), key=lambda x: x[1])
    
    return best_solid

def analyze_center_edge_relationship(n):
    """
    Analyze how a number relates to center points and outer edges in sacred geometry.
    
    Args:
        n: The number to analyze
        
    Returns:
        A dictionary with center and edge relationship scores
    """
    # Calculate properties of the number
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate sacred angle
    angle = calculate_sacred_angle(n)
    
    # Map to Flower of Life
    flower_coords = map_to_flower_of_life(n)
    
    # Map to Metatron's Cube
    metatron_coords = map_to_metatrons_cube(n)
    
    # Calculate distance from center in Flower of Life
    flower_distance_from_center = math.sqrt(flower_coords[0]**2 + flower_coords[1]**2)
    
    # Calculate distance from center in Metatron's Cube
    metatron_distance_from_center = math.sqrt(sum(c**2 for c in metatron_coords))
    
    # Calculate center relationship score (higher = closer to center)
    center_score = 1 / (1 + flower_distance_from_center)
    
    # Calculate edge relationship score (higher = closer to edge)
    # Maximum distance in standard Flower of Life is about 3.5
    max_distance = 3.5
    edge_score = flower_distance_from_center / max_distance
    
    # Calculate angular position (0 = aligned with axes, 1 = between axes)
    angular_position = min(angle % (math.pi/2), math.pi/2 - (angle % (math.pi/2))) / (math.pi/4)
    
    # Determine if the number is more of a center point or edge point
    if center_score > edge_score:
        primary_role = "center_point"
    else:
        primary_role = "edge_point"
    
    # Calculate overall sacred geometry alignment
    sacred_alignment = (center_score + edge_score + angular_position) / 3
    
    # Get Platonic solid alignment
    platonic_solid, platonic_score = calculate_platonic_solid_mapping(n)
    
    return {
        "center_score": center_score,
        "edge_score": edge_score,
        "angular_position": angular_position,
        "primary_role": primary_role,
        "sacred_alignment": sacred_alignment,
        "platonic_solid": platonic_solid,
        "platonic_score": platonic_score,
        "flower_of_life_coords": flower_coords,
        "metatrons_cube_coords": metatron_coords
    }

def visualize_flower_of_life(primes, output_dir='.'):
    """
    Visualize prime numbers mapped to the Flower of Life pattern.
    
    Args:
        primes: List of prime numbers to visualize
        output_dir: Directory to save the visualization
    """
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # Draw the Flower of Life pattern
    center = (0, 0)
    radius = 1.0
    
    # Draw center circle
    circle = plt.Circle(center, radius, fill=False, color='lightgray')
    ax.add_patch(circle)
    
    # Draw the six circles around the center
    for i in range(6):
        angle = i * math.pi / 3
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        circle = plt.Circle((x, y), radius, fill=False, color='lightgray')
        ax.add_patch(circle)
    
    # Draw the outer circles to complete the Flower of Life
    for i in range(6):
        angle1 = i * math.pi / 3
        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        
        angle2 = ((i + 1) % 6) * math.pi / 3
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        
        # Draw circle at the intersection point
        circle = plt.Circle((x1 + x2)/2, radius, fill=False, color='lightgray')
        ax.add_patch(circle)
    
    # Calculate classifications for each prime
    classifications = {}
    flower_coords = {}
    
    for prime in primes:
        # Get classification
        _, classification, _ = is_prime_with_enhanced_resonance(prime)
        classifications[prime] = classification
        
        # Map to Flower of Life
        flower_coords[prime] = map_to_flower_of_life(prime)
    
    # Separate primes by classification
    inner_octave_primes = [p for p in primes if classifications[p] == 'inner_octave']
    outer_octave_primes = [p for p in primes if classifications[p] == 'outer_octave']
    cross_resonant_primes = [p for p in primes if classifications[p] == 'cross_resonant']
    
    # Plot primes by classification
    for prime in inner_octave_primes:
        x, y = flower_coords[prime]
        ax.plot(x, y, 'bo', markersize=8)
        ax.text(x, y, str(prime), fontsize=8, ha='center', va='center')
    
    for prime in outer_octave_primes:
        x, y = flower_coords[prime]
        ax.plot(x, y, 'go', markersize=8)
        ax.text(x, y, str(prime), fontsize=8, ha='center', va='center')
    
    for prime in cross_resonant_primes:
        x, y = flower_coords[prime]
        ax.plot(x, y, 'ro', markersize=10)
        ax.text(x, y, str(prime), fontsize=8, ha='center', va='center')
    
    # Add legend
    ax.plot([], [], 'bo', label='Inner Octave Primes')
    ax.plot([], [], 'go', label='Outer Octave Primes')
    ax.plot([], [], 'ro', label='Cross-Resonant Primes')
    
    ax.set_title('Prime Numbers in the Flower of Life Pattern')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    ax.set_aspect('equal')
    ax.legend()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'primes_flower_of_life.png'))
    plt.close()

def visualize_metatrons_cube(primes, output_dir='.'):
    """
    Visualize prime numbers mapped to Metatron's Cube.
    
    Args:
        primes: List of prime numbers to visualize
        output_dir: Directory to save the visualization
    """
    # Create the plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Define the vertices of Metatron's Cube
    vertices = []
    
    # Center point
    vertices.append((0, 0, 0))
    
    # The 12 vertices of the icosahedron
    # These are arranged in 3 orthogonal golden rectangles
    for rectangle_index in range(3):
        for position_in_rectangle in range(4):
            if rectangle_index == 0:  # XY plane
                if position_in_rectangle == 0:
                    vertices.append((0, 1, PHI))
                elif position_in_rectangle == 1:
                    vertices.append((0, -1, PHI))
                elif position_in_rectangle == 2:
                    vertices.append((0, 1, -PHI))
                else:
                    vertices.append((0, -1, -PHI))
            elif rectangle_index == 1:  # YZ plane
                if position_in_rectangle == 0:
                    vertices.append((PHI, 0, 1))
                elif position_in_rectangle == 1:
                    vertices.append((PHI, 0, -1))
                elif position_in_rectangle == 2:
                    vertices.append((-PHI, 0, 1))
                else:
                    vertices.append((-PHI, 0, -1))
            else:  # XZ plane
                if position_in_rectangle == 0:
                    vertices.append((1, PHI, 0))
                elif position_in_rectangle == 1:
                    vertices.append((-1, PHI, 0))
                elif position_in_rectangle == 2:
                    vertices.append((1, -PHI, 0))
                else:
                    vertices.append((-1, -PHI, 0))
    
    # Draw the edges of Metatron's Cube
    # This is a simplified version - a complete Metatron's Cube would have more edges
    for i in range(1, len(vertices)):
        # Connect each vertex to the center
        ax.plot([vertices[0][0], vertices[i][0]],
                [vertices[0][1], vertices[i][1]],
                [vertices[0][2], vertices[i][2]], 'k-', alpha=0.3)
        
        # Connect to adjacent vertices
        for j in range(i+1, len(vertices)):
            # Calculate distance between vertices
            dist = math.sqrt(sum((vertices[i][k] - vertices[j][k])**2 for k in range(3)))
            
            # Connect if they're close enough (part of the same face)
            if dist < 2.5:
                ax.plot([vertices[i][0], vertices[j][0]],
                        [vertices[i][1], vertices[j][1]],
                        [vertices[i][2], vertices[j][2]], 'k-', alpha=0.3)
    
    # Calculate classifications for each prime
    classifications = {}
    metatron_coords = {}
    
    for prime in primes:
        # Get classification
        _, classification, _ = is_prime_with_enhanced_resonance(prime)
        classifications[prime] = classification
        
        # Map to Metatron's Cube
        metatron_coords[prime] = map_to_metatrons_cube(prime)
    
    # Separate primes by classification
    inner_octave_primes = [p for p in primes if classifications[p] == 'inner_octave']
    outer_octave_primes = [p for p in primes if classifications[p] == 'outer_octave']
    cross_resonant_primes = [p for p in primes if classifications[p] == 'cross_resonant']
    
    # Plot primes by classification
    if inner_octave_primes:
        x, y, z = zip(*[metatron_coords[p] for p in inner_octave_primes])
        ax.scatter(x, y, z, c='blue', s=100, label='Inner Octave Primes')
        for prime in inner_octave_primes:
            x, y, z = metatron_coords[prime]
            ax.text(x, y, z, str(prime), fontsize=8)
    
    if outer_octave_primes:
        x, y, z = zip(*[metatron_coords[p] for p in outer_octave_primes])
        ax.scatter(x, y, z, c='green', s=100, label='Outer Octave Primes')
        for prime in outer_octave_primes:
            x, y, z = metatron_coords[prime]
            ax.text(x, y, z, str(prime), fontsize=8)
    
    if cross_resonant_primes:
        x, y, z = zip(*[metatron_coords[p] for p in cross_resonant_primes])
        ax.scatter(x, y, z, c='red', s=150, label='Cross-Resonant Primes')
        for prime in cross_resonant_primes:
            x, y, z = metatron_coords[prime]
            ax.text(x, y, z, str(prime), fontsize=8)
    
    ax.set_title("Prime Numbers in Metatron's Cube")
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.legend()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'primes_metatrons_cube.png'))
    plt.close()

def visualize_center_edge_distribution(primes, output_dir='.'):
    """
    Visualize the distribution of primes between center points and edge points.
    
    Args:
        primes: List of prime numbers to visualize
        output_dir: Directory to save the visualization
    """
    # Analyze center-edge relationship for each prime
    center_scores = []
    edge_scores = []
    labels = []
    
    for prime in primes:
        analysis = analyze_center_edge_relationship(prime)
        center_scores.append(analysis['center_score'])
        edge_scores.append(analysis['edge_score'])
        labels.append(str(prime))
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot each prime as a point
    scatter = ax.scatter(center_scores, edge_scores, c=range(len(primes)), cmap='viridis', s=100)
    
    # Add labels for each point
    for i, label in enumerate(labels):
        ax.annotate(label, (center_scores[i], edge_scores[i]), fontsize=8)
    
    # Add diagonal line representing equal center and edge scores
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    
    # Add regions for center points and edge points
    ax.fill_between([0, 1], [0, 0], [1, 1], color='blue', alpha=0.1, label='Center Points Dominant')
    ax.fill_between([0, 1], [0, 0], [0, 1], color='red', alpha=0.1, label='Edge Points Dominant')
    
    ax.set_title('Center vs. Edge Distribution of Prime Numbers')
    ax.set_xlabel('Center Point Score')
    ax.set_ylabel('Edge Point Score')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'center_edge_distribution.png'))
    plt.close()

def analyze_prime_19_sacred_geometry():
    """
    Perform detailed sacred geometry analysis of prime 19.
    
    Returns:
        A dictionary of analysis results
    """
    # Analyze center-edge relationship
    center_edge_analysis = analyze_center_edge_relationship(19)
    
    # Map to Flower of Life
    flower_coords = map_to_flower_of_life(19)
    
    # Map to Metatron's Cube
    metatron_coords = map_to_metatrons_cube(19)
    
    # Calculate sacred angle
    sacred_angle = calculate_sacred_angle(19)
    
    # Get Platonic solid alignment
    platonic_solid, platonic_score = calculate_platonic_solid_mapping(19)
    
    # Get octave classification
    _, classification, _ = is_prime_with_enhanced_resonance(19)
    
    # Compile results
    results = {
        "prime": 19,
        "classification": classification,
        "sacred_angle": sacred_angle,
        "flower_of_life_coords": flower_coords,
        "metatrons_cube_coords": metatron_coords,
        "center_score": center_edge_analysis['center_score'],
        "edge_score": center_edge_analysis['edge_score'],
        "primary_role": center_edge_analysis['primary_role'],
        "platonic_solid": platonic_solid,
        "platonic_score": platonic_score
    }
    
    return results

def main():
    """
    Main function to demonstrate angular relationship analysis with sacred geometry.
    """
    print("Angular Relationship Analysis with Sacred Geometry Principles")
    print("===========================================================")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Analyze prime 19 with sacred geometry
    print("\nAnalyzing prime 19 with sacred geometry principles:")
    results = analyze_prime_19_sacred_geometry()
    
    print(f"Prime 19 Classification: {results['classification']}")
    print(f"Sacred Angle: {results['sacred_angle']:.4f} radians")
    print(f"Flower of Life Coordinates: ({results['flower_of_life_coords'][0]:.4f}, {results['flower_of_life_coords'][1]:.4f})")
    print(f"Metatron's Cube Coordinates: ({results['metatrons_cube_coords'][0]:.4f}, {results['metatrons_cube_coords'][1]:.4f}, {results['metatrons_cube_coords'][2]:.4f})")
    print(f"Center Score: {results['center_score']:.4f}")
    print(f"Edge Score: {results['edge_score']:.4f}")
    print(f"Primary Role: {results['primary_role']}")
    print(f"Platonic Solid Alignment: {results['platonic_solid']} (Score: {results['platonic_score']:.4f})")
    
    # Find primes in a small range
    print("\nFinding primes in range 1-50:")
    primes = []
    for n in range(1, 51):
        if n > 1 and all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1)):
            primes.append(n)
    
    print(f"Found {len(primes)} primes: {primes}")
    
    # Visualize primes in Flower of Life
    print("\nVisualizing primes in Flower of Life pattern...")
    visualize_flower_of_life(primes, "output")
    
    # Visualize primes in Metatron's Cube
    print("Visualizing primes in Metatron's Cube...")
    visualize_metatrons_cube(primes, "output")
    
    # Visualize center-edge distribution
    print("Visualizing center-edge distribution of primes...")
    visualize_center_edge_distribution(primes, "output")
    
    # Analyze center-edge relationship for each prime
    print("\nCenter-Edge Analysis of Prime Numbers:")
    for prime in primes:
        analysis = analyze_center_edge_relationship(prime)
        print(f"Prime {prime}: {analysis['primary_role']} (Center: {analysis['center_score']:.4f}, Edge: {analysis['edge_score']:.4f})")
    
    print("\nAngular relationship analysis with sacred geometry completed successfully.")

if __name__ == "__main__":
    main()
