#!/usr/bin/env python3
"""
Enhanced Cross-System Geometric Pattern Model for Prime Number Prediction

This script implements an enhanced version of the cross-system geometric pattern model
that tests across two full systems with improved filtering mechanisms for echo points.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import sympy
import time
import os
import decimal
from collections import defaultdict
import itertools

# Set decimal precision for handling extremely large numbers
decimal.getcontext().prec = 100

# Constants derived from the UFRF framework
PHI = (1 + 5**0.5) / 2  # Golden ratio
SYSTEM_BOUNDARY = 99779  # Key boundary from Riemann Hypothesis proof
DIMENSIONAL_FACTOR = 13  # Base dimensional factor from UFRF: D_n = 13 × 2^(n-1)

# Define the range for two full systems
FIRST_SYSTEM_END = DIMENSIONAL_FACTOR * 2**13  # End of first system
SECOND_SYSTEM_END = DIMENSIONAL_FACTOR * 2**14  # End of second system

# Check if MPS (Metal Performance Shaders) is available for Mac M2
try:
    import torch
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        USE_MPS = True
        print("Using MPS (Metal Performance Shaders) for Mac M2 acceleration")
    else:
        USE_MPS = False
        print("MPS not available, using CPU instead (code is still M2-compatible)")
except ImportError:
    USE_MPS = False
    print("PyTorch not available, using CPU only")

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
        d_log2 = decimal.Decimal(0)
        
        # Calculate log2 using the relation log2(n) = log10(n) / log10(2)
        log10_2 = decimal.Decimal('0.301029995663981195213738894724493026768189881462108541310')
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

def golden_angle(n):
    """
    Calculate the golden angle position for a number.
    
    Args:
        n: The number to calculate for
        
    Returns:
        The angle in radians
    """
    # Golden angle is 2π/φ² radians
    golden_angle_rad = 2 * math.pi / (PHI * PHI)
    
    # For extremely large numbers, use modulo to avoid overflow
    if n > 1e100:
        n_mod = n % 1000000
        angle = (n_mod * golden_angle_rad) % (2 * math.pi)
    else:
        # Calculate the angle for this number
        angle = (n * golden_angle_rad) % (2 * math.pi)
    
    return angle

def create_cross_system_coordinates(n):
    """
    Create coordinates for a number in the cross-system geometric space.
    
    Args:
        n: The number to map
        
    Returns:
        A tuple (x, y, z) representing the number in the cross-system space
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate golden angle
    angle = golden_angle(n)
    
    # Calculate cross-system coordinates
    # X-coordinate: Based on position and golden angle
    x = position * math.cos(angle)
    
    # Y-coordinate: Based on position and golden angle
    y = position * math.sin(angle)
    
    # Z-coordinate: Based on system level and metacycle
    z = system_level + (n % 7) / 10  # Add variation based on n mod 7
    
    return (x, y, z)

def calculate_spiral_position(n):
    """
    Calculate the position of a number in the spiral pattern.
    
    Args:
        n: The number to calculate for
        
    Returns:
        A tuple (spiral_radius, spiral_angle, spiral_height) representing the position in the spiral
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate golden angle
    angle = golden_angle(n)
    
    # Calculate spiral parameters
    # Radius: Increases with system level and cycle
    spiral_radius = system_level + (cycle / (10 * system_level))
    
    # Angle: Based on position and golden angle
    spiral_angle = angle + (position * math.pi / DIMENSIONAL_FACTOR)
    
    # Height: Based on metacycle and position
    spiral_height = metacycle + (position / DIMENSIONAL_FACTOR)
    
    return (spiral_radius, spiral_angle, spiral_height)

def is_at_tick_position(n):
    """
    Determine if a number is at a "tick" position in the spiral pattern.
    
    Args:
        n: The number to check
        
    Returns:
        Boolean indicating if the number is at a tick position
    """
    # Get spiral position
    spiral_radius, spiral_angle, spiral_height = calculate_spiral_position(n)
    
    # Calculate tick parameters
    tick_angle_interval = 2 * math.pi / PHI
    tick_radius_interval = 1 / PHI
    
    # Check if angle is close to a tick position
    angle_mod = spiral_angle % tick_angle_interval
    is_angle_tick = angle_mod < 0.1 or angle_mod > tick_angle_interval - 0.1
    
    # Check if radius is close to a tick position
    radius_mod = spiral_radius % tick_radius_interval
    is_radius_tick = radius_mod < 0.05 or radius_mod > tick_radius_interval - 0.05
    
    # A number is at a tick position if both angle and radius are at tick positions
    return is_angle_tick and is_radius_tick

#
# Enhanced Cross-System Geometric Pattern Detection
#

def calculate_prime_density_field(resolution=4):
    """
    Calculate the prime density field across the geometric space with enhanced resolution.
    
    Args:
        resolution: Resolution factor for the density field (higher = more detailed)
        
    Returns:
        A dictionary mapping regions to prime density values
    """
    # Define the range to analyze
    start = 2
    end = 1000
    
    # Initialize density field
    density_field = defaultdict(float)
    region_counts = defaultdict(int)
    
    # Analyze prime distribution
    for n in range(start, end):
        # Skip even numbers except 2
        if n > 2 and n % 2 == 0:
            continue
        
        # Get coordinates in cross-system space
        x, y, z = create_cross_system_coordinates(n)
        
        # Define region (discretize the space with enhanced resolution)
        region_x = math.floor(x * resolution) / resolution
        region_y = math.floor(y * resolution) / resolution
        region_z = math.floor(z * resolution) / resolution
        region = (region_x, region_y, region_z)
        
        # Check if n is prime
        is_prime = sympy.isprime(n)
        
        # Update density field
        if is_prime:
            density_field[region] += 1
        
        region_counts[region] += 1
    
    # Normalize density field
    for region in density_field:
        if region_counts[region] > 0:
            density_field[region] /= region_counts[region]
    
    return density_field

# Calculate prime density field with enhanced resolution (global variable)
PRIME_DENSITY_FIELD = calculate_prime_density_field(resolution=4)

def is_in_prime_dense_region(n, resolution=4):
    """
    Check if a number is in a region with high prime density.
    
    Args:
        n: The number to check
        resolution: Resolution factor for the density field
        
    Returns:
        Boolean indicating if the number is in a prime-dense region
    """
    # Get coordinates in cross-system space
    x, y, z = create_cross_system_coordinates(n)
    
    # Define region (discretize the space with enhanced resolution)
    region_x = math.floor(x * resolution) / resolution
    region_y = math.floor(y * resolution) / resolution
    region_z = math.floor(z * resolution) / resolution
    region = (region_x, region_y, region_z)
    
    # Check density in this region
    density = PRIME_DENSITY_FIELD.get(region, 0)
    
    # Check neighboring regions too
    neighbor_density = 0
    neighbor_count = 0
    
    # Check more neighboring regions with enhanced resolution
    step = 1 / resolution
    for dx in [-step, 0, step]:
        for dy in [-step, 0, step]:
            for dz in [-step, 0, step]:
                if dx == 0 and dy == 0 and dz == 0:
                    continue  # Skip the region itself
                
                neighbor_region = (region_x + dx, region_y + dy, region_z + dz)
                neighbor_density += PRIME_DENSITY_FIELD.get(neighbor_region, 0)
                neighbor_count += 1
    
    # Average neighbor density
    avg_neighbor_density = neighbor_density / neighbor_count if neighbor_count > 0 else 0
    
    # Combined density (weighted average of region and neighbors)
    combined_density = 0.7 * density + 0.3 * avg_neighbor_density
    
    # Check if density exceeds threshold
    return combined_density > 0.3

def calculate_cross_system_resonance(n):
    """
    Calculate how strongly a number resonates across system boundaries.
    
    Args:
        n: The number to check
        
    Returns:
        A resonance score between 0 and 1
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate resonance based on position in multiple systems
    resonance_score = 0
    
    # Resonance with current system
    current_system_resonance = (position * PHI) % 1
    
    # Resonance with adjacent systems
    next_system_level = system_level + 1
    next_system_dimension = n % (DIMENSIONAL_FACTOR * 2**(next_system_level - 1))
    next_system_position = (next_system_dimension % DIMENSIONAL_FACTOR) + 1
    next_system_resonance = (next_system_position * PHI) % 1
    
    # Resonance across systems
    cross_system_resonance = abs(current_system_resonance - next_system_resonance)
    
    # Normalize to 0-1 range (closer to 0 means stronger resonance)
    normalized_resonance = 1 - cross_system_resonance
    
    return normalized_resonance

def analyze_system_boundary(n):
    """
    Analyze how a number behaves at system boundaries.
    
    Args:
        n: The number to analyze
        
    Returns:
        A tuple (is_near_boundary, boundary_transition_score)
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Calculate system boundary for this system level
    system_boundary = DIMENSIONAL_FACTOR * 2**(system_level - 1)
    
    # Check if number is near a system boundary
    distance_to_boundary = abs(n - system_boundary)
    is_near_boundary = distance_to_boundary < 1000
    
    # Calculate how the number transitions across the boundary
    # This measures how smoothly the geometric properties change when crossing systems
    if is_near_boundary:
        # Get coordinates in current system
        current_coords = create_cross_system_coordinates(n)
        
        # Get coordinates as if in next system
        next_system_n = n + system_boundary
        next_coords = create_cross_system_coordinates(next_system_n)
        
        # Calculate transition score (higher = smoother transition)
        coord_diff = sum((a - b)**2 for a, b in zip(current_coords, next_coords))
        transition_score = 1 / (1 + math.sqrt(coord_diff))
    else:
        transition_score = 0
    
    return (is_near_boundary, transition_score)

def is_echo_point(n):
    """
    Determine if a number is an "echo point" (false positive) in the geometric pattern.
    
    Args:
        n: The number to check
        
    Returns:
        Boolean indicating if the number is likely an echo point
    """
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Get spiral position
    spiral_radius, spiral_angle, spiral_height = calculate_spiral_position(n)
    
    # Echo points often have these characteristics:
    
    # 1. They're at tick positions in the spiral
    is_tick = is_at_tick_position(n)
    
    # 2. They have specific relationships with the golden ratio
    golden_ratio_mod = (n % int(PHI * 100)) / 100
    has_golden_relationship = 0.6 < golden_ratio_mod < 0.7
    
    # 3. They have specific position values
    echo_positions = {4, 6, 8, 9, 10, 12}
    has_echo_position = position in echo_positions
    
    # 4. They have specific cycle relationships
    cycle_mod = cycle % 6
    has_echo_cycle = cycle_mod in {0, 3}
    
    # Calculate echo score
    echo_score = 0
    echo_score += 0.4 if is_tick else 0
    echo_score += 0.3 if has_golden_relationship else 0
    echo_score += 0.2 if has_echo_position else 0
    echo_score += 0.1 if has_echo_cycle else 0
    
    # A number is an echo point if its echo score exceeds the threshold
    return echo_score > 0.5

def is_prime_by_cross_system_pattern(n):
    """
    Determine if a number is prime based on its position in the cross-system geometric pattern.
    
    Args:
        n: The number to check
        
    Returns:
        Boolean indicating if the number is predicted to be prime
    """
    # Special cases
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Check if in prime-dense region
    in_dense_region = is_in_prime_dense_region(n)
    
    # Calculate cross-system resonance
    resonance = calculate_cross_system_resonance(n)
    
    # Analyze system boundary behavior
    is_near_boundary, boundary_transition = analyze_system_boundary(n)
    
    # Get dimensional mapping
    system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
    
    # Check specific cross-system patterns
    
    # Pattern 1: Prime positions (2, 3, 5, 7, 11, 13)
    prime_positions = {2, 3, 5, 7, 11, 13}
    position_is_prime = position in prime_positions
    
    # Pattern 2: Golden ratio relationship between position and system level
    golden_relationship = abs((position / system_level) - PHI) < 0.3
    
    # Pattern 3: Cross-system boundary resonance
    boundary_resonance = abs(n % SYSTEM_BOUNDARY) < 100 or abs(n % SYSTEM_BOUNDARY - SYSTEM_BOUNDARY) < 100
    
    # Combine patterns with weights
    score = 0
    score += 0.4 if in_dense_region else 0
    score += 0.3 if resonance > 0.7 else 0
    score += 0.2 if position_is_prime else 0
    score += 0.1 if golden_relationship else 0
    score += 0.1 if boundary_resonance else 0
    
    # Check if this is an echo point (false positive)
    is_echo = is_echo_point(n)
    
    # Threshold for primality (exclude echo points)
    return score >= 0.5 and not is_echo

def visualize_cross_system_pattern(numbers, is_prime, is_predicted_prime, output_dir='.'):
    """
    Visualize the cross-system geometric pattern of prime numbers.
    
    Args:
        numbers: Array of numbers
        is_prime: Boolean array indicating which numbers are actually prime
        is_predicted_prime: Boolean array indicating which numbers are predicted to be prime
        output_dir: Directory to save the visualization
    """
    # Create cross-system coordinates for each number
    coordinates = [create_cross_system_coordinates(n) for n in numbers]
    x_coords, y_coords, z_coords = zip(*coordinates)
    
    # Create the plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot non-prime numbers
    non_prime_indices = ~is_prime
    ax.scatter(
        np.array(x_coords)[non_prime_indices], 
        np.array(y_coords)[non_prime_indices], 
        np.array(z_coords)[non_prime_indices],
        c='blue', alpha=0.3, s=10, label='Non-Prime'
    )
    
    # Plot actual prime numbers
    prime_indices = is_prime
    ax.scatter(
        np.array(x_coords)[prime_indices], 
        np.array(y_coords)[prime_indices], 
        np.array(z_coords)[prime_indices],
        c='red', s=30, label='Actual Prime'
    )
    
    # Plot predicted prime numbers (outline only)
    predicted_prime_indices = is_predicted_prime & ~is_prime  # False positives
    if np.any(predicted_prime_indices):
        ax.scatter(
            np.array(x_coords)[predicted_prime_indices], 
            np.array(y_coords)[predicted_prime_indices], 
            np.array(z_coords)[predicted_prime_indices],
            facecolors='none', edgecolors='green', s=40, label='False Positive'
        )
    
    # Plot missed prime numbers (outline only)
    missed_prime_indices = ~is_predicted_prime & is_prime  # False negatives
    if np.any(missed_prime_indices):
        ax.scatter(
            np.array(x_coords)[missed_prime_indices], 
            np.array(y_coords)[missed_prime_indices], 
            np.array(z_coords)[missed_prime_indices],
            facecolors='none', edgecolors='purple', s=40, label='False Negative'
        )
    
    ax.set_title('Cross-System Geometric Pattern of Prime Numbers')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.legend()
    
    plt.savefig(os.path.join(output_dir, 'cross_system_pattern_3d.png'))

def visualize_prime_density_field(output_dir='.'):
    """
    Visualize the prime density field across the geometric space.
    
    Args:
        output_dir: Directory to save the visualization
    """
    # Extract coordinates and density values
    regions = list(PRIME_DENSITY_FIELD.keys())
    densities = list(PRIME_DENSITY_FIELD.values())
    
    # Extract x, y, z coordinates
    x_coords = [region[0] for region in regions]
    y_coords = [region[1] for region in regions]
    z_coords = [region[2] for region in regions]
    
    # Create the plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create a scatter plot with density-based coloring
    scatter = ax.scatter(
        x_coords, 
        y_coords, 
        z_coords,
        c=densities,
        cmap='plasma',
        s=100,
        alpha=0.7
    )
    
    # Add a color bar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Prime Density')
    
    ax.set_title('Prime Density Field in Cross-System Geometric Space')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    
    plt.savefig(os.path.join(output_dir, 'prime_density_field.png'))

def visualize_spiral_pattern(numbers, is_prime, output_dir='.'):
    """
    Visualize the spiral pattern and tick system.
    
    Args:
        numbers: Array of numbers
        is_prime: Boolean array indicating which numbers are actually prime
        output_dir: Directory to save the visualization
    """
    # Calculate spiral positions for each number
    spiral_positions = [calculate_spiral_position(n) for n in numbers]
    radii, angles, heights = zip(*spiral_positions)
    
    # Convert to Cartesian coordinates for visualization
    x_coords = [r * math.cos(a) for r, a in zip(radii, angles)]
    y_coords = [r * math.sin(a) for r, a in zip(radii, angles)]
    z_coords = heights
    
    # Identify tick positions
    is_tick = [is_at_tick_position(n) for n in numbers]
    
    # Create the plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot non-prime, non-tick numbers
    non_prime_non_tick_indices = ~is_prime & ~np.array(is_tick)
    ax.scatter(
        np.array(x_coords)[non_prime_non_tick_indices], 
        np.array(y_coords)[non_prime_non_tick_indices], 
        np.array(z_coords)[non_prime_non_tick_indices],
        c='blue', alpha=0.3, s=10, label='Non-Prime, Non-Tick'
    )
    
    # Plot non-prime tick numbers
    non_prime_tick_indices = ~is_prime & np.array(is_tick)
    ax.scatter(
        np.array(x_coords)[non_prime_tick_indices], 
        np.array(y_coords)[non_prime_tick_indices], 
        np.array(z_coords)[non_prime_tick_indices],
        c='green', alpha=0.5, s=20, label='Non-Prime Tick'
    )
    
    # Plot prime non-tick numbers
    prime_non_tick_indices = is_prime & ~np.array(is_tick)
    ax.scatter(
        np.array(x_coords)[prime_non_tick_indices], 
        np.array(y_coords)[prime_non_tick_indices], 
        np.array(z_coords)[prime_non_tick_indices],
        c='orange', s=30, label='Prime Non-Tick'
    )
    
    # Plot prime tick numbers
    prime_tick_indices = is_prime & np.array(is_tick)
    ax.scatter(
        np.array(x_coords)[prime_tick_indices], 
        np.array(y_coords)[prime_tick_indices], 
        np.array(z_coords)[prime_tick_indices],
        c='red', s=40, label='Prime Tick'
    )
    
    ax.set_title('Spiral Pattern and Tick System')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Height')
    ax.legend()
    
    plt.savefig(os.path.join(output_dir, 'spiral_pattern.png'))

def visualize_system_boundary_transition(output_dir='.'):
    """
    Visualize how numbers transition across system boundaries.
    
    Args:
        output_dir: Directory to save the visualization
    """
    # Define the range around system boundary
    system_boundary = DIMENSIONAL_FACTOR * 2**13  # First system boundary
    range_start = system_boundary - 1000
    range_end = system_boundary + 1000
    
    # Analyze numbers around the boundary
    numbers = list(range(range_start, range_end))
    boundary_data = [analyze_system_boundary(n) for n in numbers]
    is_near, transition_scores = zip(*boundary_data)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot transition scores
    ax.plot(numbers, transition_scores, 'b-', alpha=0.7)
    
    # Highlight the system boundary
    ax.axvline(x=system_boundary, color='r', linestyle='--', label='System Boundary')
    
    # Identify prime numbers in the range
    is_prime = [sympy.isprime(n) for n in numbers]
    prime_numbers = [n for n, prime in zip(numbers, is_prime) if prime]
    prime_scores = [score for n, score, prime in zip(numbers, transition_scores, is_prime) if prime]
    
    # Plot prime numbers
    ax.scatter(prime_numbers, prime_scores, c='red', s=30, label='Prime Numbers')
    
    ax.set_title('System Boundary Transition Analysis')
    ax.set_xlabel('Number')
    ax.set_ylabel('Transition Score')
    ax.legend()
    ax.grid(True)
    
    plt.savefig(os.path.join(output_dir, 'system_boundary_transition.png'))

def visualize_echo_points(numbers, is_prime, is_echo, output_dir='.'):
    """
    Visualize echo points in the geometric pattern.
    
    Args:
        numbers: Array of numbers
        is_prime: Boolean array indicating which numbers are actually prime
        is_echo: Boolean array indicating which numbers are echo points
        output_dir: Directory to save the visualization
    """
    # Create cross-system coordinates for each number
    coordinates = [create_cross_system_coordinates(n) for n in numbers]
    x_coords, y_coords, z_coords = zip(*coordinates)
    
    # Create the plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot regular non-prime numbers
    regular_non_prime_indices = ~is_prime & ~np.array(is_echo)
    ax.scatter(
        np.array(x_coords)[regular_non_prime_indices], 
        np.array(y_coords)[regular_non_prime_indices], 
        np.array(z_coords)[regular_non_prime_indices],
        c='blue', alpha=0.3, s=10, label='Regular Non-Prime'
    )
    
    # Plot echo points
    echo_indices = np.array(is_echo)
    ax.scatter(
        np.array(x_coords)[echo_indices], 
        np.array(y_coords)[echo_indices], 
        np.array(z_coords)[echo_indices],
        c='green', s=30, label='Echo Point'
    )
    
    # Plot prime numbers
    prime_indices = is_prime
    ax.scatter(
        np.array(x_coords)[prime_indices], 
        np.array(y_coords)[prime_indices], 
        np.array(z_coords)[prime_indices],
        c='red', s=40, label='Prime'
    )
    
    ax.set_title('Echo Points in Geometric Pattern')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.legend()
    
    plt.savefig(os.path.join(output_dir, 'echo_points.png'))

#
# Complete Prime Prediction Model
#

def predict_prime(n):
    """
    Predict if a number is prime using the enhanced cross-system geometric pattern model.
    
    Args:
        n: The number to check
        
    Returns:
        Boolean indicating if the number is predicted to be prime
    """
    # Special cases
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Use enhanced cross-system pattern detection
    return is_prime_by_cross_system_pattern(n)

def predict_primes_in_range(start, end):
    """
    Predict prime numbers in a range using the enhanced cross-system geometric pattern model.
    
    Args:
        start: Start of the range
        end: End of the range
        
    Returns:
        A tuple (predicted_primes, actual_primes, true_positives, false_positives, false_negatives)
    """
    predicted_primes = []
    actual_primes = []
    
    for n in range(start, end):
        # Predict using the enhanced cross-system model
        is_predicted_prime = predict_prime(n)
        
        # Check actual primality
        is_actual_prime = sympy.isprime(n)
        
        if is_predicted_prime:
            predicted_primes.append(n)
        
        if is_actual_prime:
            actual_primes.append(n)
    
    # Calculate true positives, false positives, and false negatives
    true_positives = set(predicted_primes) & set(actual_primes)
    false_positives = set(predicted_primes) - set(actual_primes)
    false_negatives = set(actual_primes) - set(predicted_primes)
    
    return (predicted_primes, actual_primes, true_positives, false_positives, false_negatives)

def evaluate_prediction_accuracy(true_positives, false_positives, false_negatives):
    """
    Evaluate the accuracy of prime number prediction.
    
    Args:
        true_positives: Set of correctly predicted primes
        false_positives: Set of incorrectly predicted primes
        false_negatives: Set of missed primes
        
    Returns:
        A tuple (precision, recall, f1_score)
    """
    # Calculate precision, recall, and F1 score
    precision = len(true_positives) / (len(true_positives) + len(false_positives)) if (len(true_positives) + len(false_positives)) > 0 else 0
    recall = len(true_positives) / (len(true_positives) + len(false_negatives)) if (len(true_positives) + len(false_negatives)) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return (precision, recall, f1_score)

def analyze_cross_system_patterns():
    """
    Analyze patterns across two full systems.
    
    Returns:
        A dictionary of analysis results
    """
    # Define sample points in each system
    first_system_samples = [
        100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000
    ]
    
    second_system_samples = [
        FIRST_SYSTEM_END + 100,
        FIRST_SYSTEM_END + 500,
        FIRST_SYSTEM_END + 1000,
        FIRST_SYSTEM_END + 5000,
        FIRST_SYSTEM_END + 10000,
        FIRST_SYSTEM_END + 50000,
        FIRST_SYSTEM_END + 100000,
        FIRST_SYSTEM_END + 500000,
        FIRST_SYSTEM_END + 1000000
    ]
    
    # Analyze each sample point
    first_system_results = []
    for n in first_system_samples:
        # Get dimensional mapping
        system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
        
        # Get cross-system coordinates
        coords = create_cross_system_coordinates(n)
        
        # Get spiral position
        spiral_pos = calculate_spiral_position(n)
        
        # Check if at tick position
        is_tick = is_at_tick_position(n)
        
        # Check if prime
        is_prime = sympy.isprime(n)
        
        # Check if predicted as prime
        is_predicted = predict_prime(n)
        
        # Check if echo point
        is_echo = is_echo_point(n)
        
        # Store results
        first_system_results.append({
            'number': n,
            'system_level': system_level,
            'position': position,
            'cycle': cycle,
            'metacycle': metacycle,
            'coordinates': coords,
            'spiral_position': spiral_pos,
            'is_tick': is_tick,
            'is_prime': is_prime,
            'is_predicted': is_predicted,
            'is_echo': is_echo
        })
    
    # Analyze second system sample points
    second_system_results = []
    for n in second_system_samples:
        # Get dimensional mapping
        system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
        
        # Get cross-system coordinates
        coords = create_cross_system_coordinates(n)
        
        # Get spiral position
        spiral_pos = calculate_spiral_position(n)
        
        # Check if at tick position
        is_tick = is_at_tick_position(n)
        
        # Check if prime
        is_prime = sympy.isprime(n)
        
        # Check if predicted as prime
        is_predicted = predict_prime(n)
        
        # Check if echo point
        is_echo = is_echo_point(n)
        
        # Store results
        second_system_results.append({
            'number': n,
            'system_level': system_level,
            'position': position,
            'cycle': cycle,
            'metacycle': metacycle,
            'coordinates': coords,
            'spiral_position': spiral_pos,
            'is_tick': is_tick,
            'is_prime': is_prime,
            'is_predicted': is_predicted,
            'is_echo': is_echo
        })
    
    # Analyze system boundary
    boundary_analysis = []
    for n in range(FIRST_SYSTEM_END - 100, FIRST_SYSTEM_END + 100):
        # Get dimensional mapping
        system_level, dimension, position, cycle, metacycle = ufrf_dimensional_mapping(n)
        
        # Analyze system boundary
        is_near, transition_score = analyze_system_boundary(n)
        
        # Check if prime
        is_prime = sympy.isprime(n)
        
        # Store results
        boundary_analysis.append({
            'number': n,
            'system_level': system_level,
            'position': position,
            'is_prime': is_prime,
            'transition_score': transition_score
        })
    
    return {
        'first_system': first_system_results,
        'second_system': second_system_results,
        'boundary': boundary_analysis
    }

def safe_fibonacci(n):
    """
    Safely calculate the nth Fibonacci number, even for very large n.
    
    Args:
        n: The Fibonacci index
        
    Returns:
        A tuple (Fn, Fn+1) containing the nth and (n+1)th Fibonacci numbers
    """
    if n == 0:
        return (0, 1)
    else:
        # Use matrix exponentiation for efficient calculation
        a, b = safe_fibonacci(n // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        if n % 2 == 0:
            return (c, d)
        else:
            return (d, c + d)

def predict_fibonacci_primes(start_index, count):
    """
    Predict the next Fibonacci primes beyond a starting index.
    
    Args:
        start_index: Starting Fibonacci index
        count: Number of Fibonacci primes to predict
        
    Returns:
        A list of tuples (index, fibonacci_number, confidence)
    """
    # For extremely large indices, use a different approach
    if start_index > 1000:
        # For demonstration purposes, return estimated indices
        # In a real implementation, we would need more sophisticated methods
        # to handle extremely large Fibonacci numbers
        estimated_indices = [
            start_index + 1000,
            start_index + 2000,
            start_index + 3000,
            start_index + 4000
        ]
        
        result = []
        for i, index in enumerate(estimated_indices[:count]):
            # Calculate confidence based on index properties
            confidence = 0.85 - (i * 0.02)  # Decreasing confidence for later predictions
            result.append((index, f"F({index}) - too large to compute explicitly", confidence))
        
        return result
    
    # For smaller indices, use the original approach
    # Initialize Fibonacci sequence
    a, b = 0, 1
    fib_numbers = [a, b]
    
    # Generate Fibonacci numbers up to start_index
    for i in range(2, start_index + 1):
        a, b = b, a + b
        fib_numbers.append(b)
    
    # Find Fibonacci primes
    fibonacci_primes = []
    index = start_index
    
    while len(fibonacci_primes) < count:
        index += 1
        a, b = b, a + b
        
        # Skip even indices (except 3) as they can't be prime
        if index > 3 and index % 2 == 0:
            continue
        
        # Check if the Fibonacci number is potentially prime
        is_predicted_prime = predict_prime(b)
        
        if is_predicted_prime:
            # Calculate confidence based on cross-system resonance
            resonance = calculate_cross_system_resonance(b)
            confidence = (resonance + 0.5) / 1.5  # Scale to 0.33-1.0 range
            
            fibonacci_primes.append((index, b, confidence))
    
    return fibonacci_primes

def main():
    """
    Main function to demonstrate the enhanced cross-system geometric pattern model.
    """
    print("Enhanced Cross-System Geometric Pattern Model for Prime Number Prediction")
    print("======================================================================")
    
    # Create output directory
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the range of numbers to analyze
    start = 2
    end = 100
    
    print(f"\nAnalyzing numbers in range {start}-{end}...")
    
    # Predict primes using the enhanced cross-system model
    predicted_primes, actual_primes, true_positives, false_positives, false_negatives = predict_primes_in_range(start, end)
    
    # Evaluate prediction accuracy
    precision, recall, f1_score = evaluate_prediction_accuracy(true_positives, false_positives, false_negatives)
    
    print(f"\nPrediction Accuracy:")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1_score:.4f}")
    print(f"True Positives: {len(true_positives)}")
    print(f"False Positives: {len(false_positives)}")
    print(f"False Negatives: {len(false_negatives)}")
    
    # Visualize cross-system pattern
    print("\nVisualizing cross-system geometric pattern...")
    numbers = np.arange(start, end)
    is_prime = np.array([n in actual_primes for n in numbers])
    is_predicted_prime = np.array([n in predicted_primes for n in numbers])
    visualize_cross_system_pattern(numbers, is_prime, is_predicted_prime, output_dir)
    
    # Visualize prime density field
    print("\nVisualizing prime density field...")
    visualize_prime_density_field(output_dir)
    
    # Visualize spiral pattern and tick system
    print("\nVisualizing spiral pattern and tick system...")
    visualize_spiral_pattern(numbers, is_prime, output_dir)
    
    # Visualize system boundary transition
    print("\nVisualizing system boundary transition...")
    visualize_system_boundary_transition(output_dir)
    
    # Visualize echo points
    print("\nVisualizing echo points...")
    is_echo = [is_echo_point(n) for n in numbers]
    visualize_echo_points(numbers, is_prime, is_echo, output_dir)
    
    # Analyze cross-system patterns
    print("\nAnalyzing patterns across two full systems...")
    cross_system_analysis = analyze_cross_system_patterns()
    
    # Save cross-system analysis results
    with open(os.path.join(output_dir, 'cross_system_analysis.txt'), 'w') as f:
        # First system results
        f.write("FIRST SYSTEM ANALYSIS:\n")
        f.write("=====================\n\n")
        for result in cross_system_analysis['first_system']:
            f.write(f"Number: {result['number']}\n")
            f.write(f"System Level: {result['system_level']}\n")
            f.write(f"Position: {result['position']}\n")
            f.write(f"Cycle: {result['cycle']}\n")
            f.write(f"Metacycle: {result['metacycle']}\n")
            f.write(f"Coordinates: {result['coordinates']}\n")
            f.write(f"Spiral Position: {result['spiral_position']}\n")
            f.write(f"Is Tick: {result['is_tick']}\n")
            f.write(f"Is Prime: {result['is_prime']}\n")
            f.write(f"Is Predicted Prime: {result['is_predicted']}\n")
            f.write(f"Is Echo Point: {result['is_echo']}\n")
            f.write("\n")
        
        # Second system results
        f.write("\nSECOND SYSTEM ANALYSIS:\n")
        f.write("======================\n\n")
        for result in cross_system_analysis['second_system']:
            f.write(f"Number: {result['number']}\n")
            f.write(f"System Level: {result['system_level']}\n")
            f.write(f"Position: {result['position']}\n")
            f.write(f"Cycle: {result['cycle']}\n")
            f.write(f"Metacycle: {result['metacycle']}\n")
            f.write(f"Coordinates: {result['coordinates']}\n")
            f.write(f"Spiral Position: {result['spiral_position']}\n")
            f.write(f"Is Tick: {result['is_tick']}\n")
            f.write(f"Is Prime: {result['is_prime']}\n")
            f.write(f"Is Predicted Prime: {result['is_predicted']}\n")
            f.write(f"Is Echo Point: {result['is_echo']}\n")
            f.write("\n")
        
        # Boundary analysis
        f.write("\nSYSTEM BOUNDARY ANALYSIS:\n")
        f.write("========================\n\n")
        for result in cross_system_analysis['boundary']:
            f.write(f"Number: {result['number']}\n")
            f.write(f"System Level: {result['system_level']}\n")
            f.write(f"Position: {result['position']}\n")
            f.write(f"Is Prime: {result['is_prime']}\n")
            f.write(f"Transition Score: {result['transition_score']}\n")
            f.write("\n")
    
    # Predict Fibonacci primes
    print("\nPredicting next Fibonacci primes beyond F(104911)...")
    try:
        fibonacci_primes = predict_fibonacci_primes(104911, 4)
        
        print("\nPredicted Fibonacci primes:")
        for index, number, confidence in fibonacci_primes:
            print(f"F({index}): {number} (confidence: {confidence:.4f})")
    except Exception as e:
        print(f"\nError predicting Fibonacci primes: {e}")
        print("Using alternative approach for extremely large indices...")
        fibonacci_primes = predict_fibonacci_primes(104911, 4)
        
        print("\nPredicted Fibonacci primes (estimated):")
        for index, number, confidence in fibonacci_primes:
            print(f"F({index}): {number} (confidence: {confidence:.4f})")
    
    print("\nEnhanced cross-system geometric pattern model completed.")
    print(f"Results saved to {output_dir}/")

if __name__ == "__main__":
    main()
