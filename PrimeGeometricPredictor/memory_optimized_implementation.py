#!/usr/bin/env python3
"""
Memory-Optimized Implementation for Mac M2

This module provides memory optimization techniques for running the enhanced prime
detection and classification system on Mac M2 with 16GB RAM constraints.
"""

import numpy as np
import math
import os
import gc
import time
import argparse
from functools import lru_cache
import matplotlib.pyplot as plt

# Import from other modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from enhanced_resonance_detector import (
        PHI, SYSTEM_BOUNDARY, DIMENSIONAL_FACTOR, 
        FUNDAMENTAL_FREQUENCY, OCTAVE_RATIO,
        ufrf_dimensional_mapping, calculate_harmonic_frequency
    )
    from prime_classification_system import PrimeClassifier
except ImportError:
    # Handle relative imports when running as a standalone script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from enhanced_package.enhanced_resonance_detector import (
            PHI, SYSTEM_BOUNDARY, DIMENSIONAL_FACTOR, 
            FUNDAMENTAL_FREQUENCY, OCTAVE_RATIO,
            ufrf_dimensional_mapping, calculate_harmonic_frequency
        )
        from enhanced_package.prime_classification_system import PrimeClassifier
    except ImportError:
        print("Error: Could not import required modules. Please ensure you're running from the correct directory.")
        sys.exit(1)

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

# Memory optimization constants
MAX_BATCH_SIZE = 1000  # Maximum number of primes to process at once
CACHE_SIZE = 10000     # Size of LRU cache for function results
MEMORY_CHECK_INTERVAL = 100  # How often to check memory usage (in iterations)
MEMORY_THRESHOLD = 0.8  # Threshold for memory usage (0.8 = 80% of available memory)

class MemoryOptimizedPrimeAnalyzer:
    """
    A memory-optimized analyzer for prime numbers that works efficiently on Mac M2 with 16GB RAM.
    """
    
    def __init__(self, output_dir='output'):
        """
        Initialize the memory-optimized analyzer.
        
        Args:
            output_dir: Directory to save output files and visualizations
        """
        # Initialize the prime classifier
        self.classifier = PrimeClassifier()
        
        # Set up memory monitoring
        self.memory_usage = []
        self.last_memory_check = time.time()
        
        # Set output directory
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output will be saved to: {os.path.abspath(self.output_dir)}")
        
        # Apply LRU cache to expensive functions
        self.apply_caching()
    
    def apply_caching(self):
        """Apply LRU caching to expensive functions to improve performance."""
        # Cache the dimensional mapping function
        self.cached_dimensional_mapping = lru_cache(maxsize=CACHE_SIZE)(ufrf_dimensional_mapping)
        
        # Cache the harmonic frequency calculation
        self.cached_harmonic_frequency = lru_cache(maxsize=CACHE_SIZE)(calculate_harmonic_frequency)
        
        # Cache the prime classification
        self.cached_classify_prime = lru_cache(maxsize=CACHE_SIZE)(self.classifier.classify_prime)
    
    def check_memory_usage(self):
        """
        Check current memory usage and trigger garbage collection if needed.
        
        Returns:
            Current memory usage as a fraction of available memory
        """
        # Only check memory periodically to avoid performance impact
        current_time = time.time()
        if current_time - self.last_memory_check < 1.0:  # Check at most once per second
            return 0.0
        
        self.last_memory_check = current_time
        
        try:
            # Try to get memory usage using psutil if available
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage = memory_info.rss / psutil.virtual_memory().total
        except ImportError:
            # Fallback to a simple estimate based on garbage collector
            gc.collect()
            memory_usage = 0.5  # Dummy value when we can't measure
        
        # Record memory usage
        self.memory_usage.append(memory_usage)
        
        # Trigger garbage collection if memory usage is high
        if memory_usage > MEMORY_THRESHOLD:
            print(f"High memory usage detected ({memory_usage:.2%}), triggering garbage collection...")
            gc.collect()
        
        return memory_usage
    
    def optimize_torch_for_m2(self):
        """
        Apply optimizations specific to PyTorch on Mac M2.
        """
        if not USE_MPS:
            return
        
        # Empty MPS cache to free up memory
        # Note: torch.backends.mps.enable_mps() doesn't exist, so we use empty_cache instead
        if hasattr(torch.mps, 'empty_cache'):
            torch.mps.empty_cache()
        
        print("Applied PyTorch optimizations for Mac M2")
    
    def batch_process_primes(self, start, end, process_func, batch_size=MAX_BATCH_SIZE):
        """
        Process a range of primes in batches to manage memory usage.
        
        Args:
            start: Starting number
            end: Ending number
            process_func: Function to apply to each prime
            batch_size: Maximum batch size
            
        Returns:
            Combined results from all batches
        """
        all_results = []
        
        # Process in batches
        current_start = start
        while current_start <= end:
            # Determine batch end
            current_end = min(current_start + batch_size - 1, end)
            
            # Process this batch
            print(f"Processing batch {current_start}-{current_end}...")
            batch_results = []
            
            # Find primes in this batch
            batch_primes = []
            for n in range(current_start, current_end + 1):
                if self.classifier.is_prime(n):
                    batch_primes.append(n)
            
            # Apply the process function to each prime
            for prime in batch_primes:
                result = process_func(prime)
                batch_results.append(result)
            
            # Add batch results to all results
            all_results.extend(batch_results)
            
            # Check memory usage
            memory_usage = self.check_memory_usage()
            if memory_usage > MEMORY_THRESHOLD:
                # If memory usage is high, reduce batch size for next batch
                batch_size = max(10, batch_size // 2)
                print(f"Reduced batch size to {batch_size} due to high memory usage")
            
            # Move to next batch
            current_start = current_end + 1
        
        return all_results
    
    def find_primes_by_classification_optimized(self, classification, start, end, max_count=100):
        """
        Find prime numbers of a specific classification with memory optimization.
        
        Args:
            classification: The classification to search for
            start: Starting number
            end: Ending number
            max_count: Maximum number of primes to find
            
        Returns:
            A list of prime numbers with the specified classification
        """
        matching_primes = []
        count = 0
        
        # Process in batches
        batch_size = MAX_BATCH_SIZE
        current_start = start
        
        while current_start <= end and count < max_count:
            # Determine batch end
            current_end = min(current_start + batch_size - 1, end)
            
            # Process this batch
            batch_matching = []
            
            for n in range(current_start, current_end + 1):
                # Skip even numbers except 2
                if n > 2 and n % 2 == 0:
                    continue
                
                # Check if prime and classify
                is_prime, prime_class, confidence = self.cached_classify_prime(n)
                
                if is_prime and prime_class == classification:
                    # Add to results
                    batch_matching.append({
                        "number": n,
                        "classification": classification,
                        "confidence": confidence
                    })
                    
                    count += 1
                    
                    # Check if we've reached the maximum count
                    if count >= max_count:
                        break
                
                # Check memory usage periodically
                if n % MEMORY_CHECK_INTERVAL == 0:
                    self.check_memory_usage()
            
            # Add batch results to all results
            matching_primes.extend(batch_matching)
            
            # Move to next batch
            current_start = current_end + 1
        
        # Save results to file
        self.save_classification_results(matching_primes, f"{classification}_primes.txt")
        
        return matching_primes
    
    def save_classification_results(self, primes_data, filename):
        """
        Save classification results to a text file.
        
        Args:
            primes_data: List of dictionaries with prime classification data
            filename: Name of the file to save
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Classification Results - {len(primes_data)} primes\n")
            f.write("=" * 50 + "\n\n")
            
            for data in primes_data:
                f.write(f"Prime: {data['number']}\n")
                f.write(f"Classification: {data['classification']}\n")
                f.write(f"Confidence: {data['confidence']:.4f}\n")
                f.write("-" * 30 + "\n")
        
        print(f"Saved classification results to {filepath}")
    
    def analyze_large_range(self, start, end, max_primes=1000):
        """
        Analyze a large range of numbers for prime classification with memory optimization.
        
        Args:
            start: Starting number
            end: Ending number
            max_primes: Maximum number of primes to analyze
            
        Returns:
            A dictionary of classification results and statistics
        """
        # Initialize counters
        total_primes = 0
        inner_count = 0
        outer_count = 0
        cross_count = 0
        
        # Initialize lists for each classification
        inner_primes = []
        outer_primes = []
        cross_primes = []
        
        # Initialize lists for visualization data
        all_primes = []
        all_classifications = []
        all_confidences = []
        
        # Process in batches
        batch_size = MAX_BATCH_SIZE
        current_start = start
        
        while current_start <= end and total_primes < max_primes:
            # Determine batch end
            current_end = min(current_start + batch_size - 1, end)
            
            # Process this batch
            print(f"Analyzing batch {current_start}-{current_end}...")
            
            for n in range(current_start, current_end + 1):
                # Skip even numbers except 2
                if n > 2 and n % 2 == 0:
                    continue
                
                # Check if prime and classify
                is_prime, classification, confidence = self.cached_classify_prime(n)
                
                if is_prime:
                    # Add to visualization data
                    all_primes.append(n)
                    all_classifications.append(classification)
                    all_confidences.append(confidence)
                    
                    total_primes += 1
                    
                    # Categorize by classification
                    if classification == "inner_octave":
                        inner_count += 1
                        if len(inner_primes) < 10:  # Keep only a few examples
                            inner_primes.append(n)
                    elif classification == "outer_octave":
                        outer_count += 1
                        if len(outer_primes) < 10:  # Keep only a few examples
                            outer_primes.append(n)
                    else:  # cross_resonant
                        cross_count += 1
                        if len(cross_primes) < 10:  # Keep only a few examples
                            cross_primes.append(n)
                    
                    # Check if we've reached the maximum count
                    if total_primes >= max_primes:
                        break
                
                # Check memory usage periodically
                if n % MEMORY_CHECK_INTERVAL == 0:
                    self.check_memory_usage()
            
            # Move to next batch
            current_start = current_end + 1
        
        # Calculate percentages
        inner_percentage = inner_count / total_primes if total_primes > 0 else 0
        outer_percentage = outer_count / total_primes if total_primes > 0 else 0
        cross_percentage = cross_count / total_primes if total_primes > 0 else 0
        
        # Compile results
        results = {
            "total_primes": total_primes,
            "inner_octave_count": inner_count,
            "outer_octave_count": outer_count,
            "cross_resonant_count": cross_count,
            "inner_octave_percentage": inner_percentage,
            "outer_octave_percentage": outer_percentage,
            "cross_resonant_percentage": cross_percentage,
            "inner_octave_examples": inner_primes,
            "outer_octave_examples": outer_primes,
            "cross_resonant_examples": cross_primes
        }
        
        # Create visualizations
        if all_primes:
            self.visualize_classification_distribution(all_primes, all_classifications)
            self.visualize_classification_confidence(all_primes, all_classifications, all_confidences)
        
        # Save results to file
        self.save_analysis_results(results)
        
        return results
    
    def save_analysis_results(self, results):
        """
        Save analysis results to a text file.
        
        Args:
            results: Dictionary containing analysis results
        """
        filepath = os.path.join(self.output_dir, "analysis_results.txt")
        with open(filepath, 'w') as f:
            f.write("Prime Number Analysis Results\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Total primes analyzed: {results['total_primes']}\n\n")
            
            f.write("Classification Distribution:\n")
            f.write(f"  Inner Octave: {results['inner_octave_count']} ({results['inner_octave_percentage']:.1%})\n")
            f.write(f"  Outer Octave: {results['outer_octave_count']} ({results['outer_octave_percentage']:.1%})\n")
            f.write(f"  Cross-Resonant: {results['cross_resonant_count']} ({results['cross_resonant_percentage']:.1%})\n\n")
            
            f.write("Example Primes by Classification:\n")
            
            f.write("Inner Octave Examples:\n")
            for prime in results['inner_octave_examples']:
                f.write(f"  {prime}\n")
            
            f.write("\nOuter Octave Examples:\n")
            for prime in results['outer_octave_examples']:
                f.write(f"  {prime}\n")
            
            f.write("\nCross-Resonant Examples:\n")
            for prime in results['cross_resonant_examples']:
                f.write(f"  {prime}\n")
        
        print(f"Saved analysis results to {filepath}")
    
    def visualize_memory_usage(self):
        """
        Visualize memory usage during processing.
        """
        if not self.memory_usage:
            print("No memory usage data available")
            return
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Plot memory usage
        plt.plot(self.memory_usage, 'b-', linewidth=2)
        
        # Add threshold line
        plt.axhline(y=MEMORY_THRESHOLD, color='r', linestyle='--', label=f'Threshold ({MEMORY_THRESHOLD:.0%})')
        
        plt.title('Memory Usage During Processing')
        plt.xlabel('Check Point')
        plt.ylabel('Memory Usage (fraction of total)')
        plt.grid(True)
        plt.legend()
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'memory_usage.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved memory usage visualization to {filepath}")
    
    def visualize_classification_distribution(self, primes, classifications):
        """
        Visualize the distribution of prime classifications.
        
        Args:
            primes: List of prime numbers
            classifications: List of classifications for each prime
        """
        # Count primes by classification
        inner_count = classifications.count('inner_octave')
        outer_count = classifications.count('outer_octave')
        cross_count = classifications.count('cross_resonant')
        
        # Create the plot
        plt.figure(figsize=(10, 8))
        
        # Pie chart of classifications
        labels = ['Inner Octave', 'Outer Octave', 'Cross-Resonant']
        sizes = [inner_count, outer_count, cross_count]
        colors = ['blue', 'green', 'red']
        explode = (0.1, 0, 0)  # explode the 1st slice (Inner Octave)
        
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Distribution of Prime Classifications')
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'classification_distribution.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved classification distribution visualization to {filepath}")
    
    def visualize_classification_confidence(self, primes, classifications, confidences):
        """
        Visualize the confidence scores for each classification.
        
        Args:
            primes: List of prime numbers
            classifications: List of classifications for each prime
            confidences: List of confidence scores for each prime
        """
        # Separate by classification
        inner_indices = [i for i, c in enumerate(classifications) if c == 'inner_octave']
        outer_indices = [i for i, c in enumerate(classifications) if c == 'outer_octave']
        cross_indices = [i for i, c in enumerate(classifications) if c == 'cross_resonant']
        
        inner_conf = [confidences[i] for i in inner_indices]
        outer_conf = [confidences[i] for i in outer_indices]
        cross_conf = [confidences[i] for i in cross_indices]
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Box plot of confidence scores
        data = [inner_conf, outer_conf, cross_conf]
        labels = ['Inner Octave', 'Outer Octave', 'Cross-Resonant']
        
        plt.boxplot(data, labels=labels, patch_artist=True,
                   boxprops=dict(facecolor='lightblue'),
                   flierprops=dict(marker='o', markerfacecolor='red', markersize=8))
        
        plt.title('Confidence Scores by Classification')
        plt.ylabel('Confidence Score')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'classification_confidence.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved classification confidence visualization to {filepath}")
    
    def run_small_test(self):
        """
        Run a small test to verify functionality and measure performance.
        
        Returns:
            Test results and performance metrics
        """
        print("Running small test to verify functionality...")
        
        # Record start time
        start_time = time.time()
        
        # Test range
        test_start = 1
        test_end = 100
        
        # Find primes in the range
        primes = []
        for n in range(test_start, test_end + 1):
            if self.classifier.is_prime(n):
                primes.append(n)
        
        # Classify each prime
        classifications = {}
        for prime in primes:
            _, classification, confidence = self.cached_classify_prime(prime)
            classifications[prime] = (classification, confidence)
        
        # Count by classification
        inner_count = sum(1 for p in primes if classifications[p][0] == 'inner_octave')
        outer_count = sum(1 for p in primes if classifications[p][0] == 'outer_octave')
        cross_count = sum(1 for p in primes if classifications[p][0] == 'cross_resonant')
        
        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Calculate performance metrics
        primes_per_second = len(primes) / elapsed_time if elapsed_time > 0 else 0
        
        # Compile results
        results = {
            "test_range": (test_start, test_end),
            "primes_found": len(primes),
            "inner_octave_count": inner_count,
            "outer_octave_count": outer_count,
            "cross_resonant_count": cross_count,
            "elapsed_time": elapsed_time,
            "primes_per_second": primes_per_second
        }
        
        # Print results
        print(f"Test completed in {elapsed_time:.2f} seconds")
        print(f"Found {len(primes)} primes in range {test_start}-{test_end}")
        print(f"Classification breakdown: {inner_count} inner octave, {outer_count} outer octave, {cross_count} cross-resonant")
        print(f"Performance: {primes_per_second:.2f} primes processed per second")
        
        # Save test results
        self.save_test_results(results)
        
        # Create a simple visualization of the test results
        self.visualize_test_results(results)
        
        return results
    
    def save_test_results(self, results):
        """
        Save test results to a text file.
        
        Args:
            results: Dictionary containing test results
        """
        filepath = os.path.join(self.output_dir, "test_results.txt")
        with open(filepath, 'w') as f:
            f.write("Small Test Results\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Test range: {results['test_range'][0]}-{results['test_range'][1]}\n")
            f.write(f"Primes found: {results['primes_found']}\n")
            f.write(f"Classification breakdown:\n")
            f.write(f"  Inner Octave: {results['inner_octave_count']}\n")
            f.write(f"  Outer Octave: {results['outer_octave_count']}\n")
            f.write(f"  Cross-Resonant: {results['cross_resonant_count']}\n\n")
            f.write(f"Elapsed time: {results['elapsed_time']:.2f} seconds\n")
            f.write(f"Performance: {results['primes_per_second']:.2f} primes/second\n")
        
        print(f"Saved test results to {filepath}")
    
    def visualize_test_results(self, results):
        """
        Create a simple visualization of the test results.
        
        Args:
            results: Dictionary containing test results
        """
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Bar chart of classification counts
        labels = ['Inner Octave', 'Outer Octave', 'Cross-Resonant']
        counts = [results['inner_octave_count'], results['outer_octave_count'], results['cross_resonant_count']]
        colors = ['blue', 'green', 'red']
        
        plt.bar(labels, counts, color=colors)
        plt.title('Prime Classification Distribution (Test Results)')
        plt.ylabel('Number of Primes')
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Add count labels on top of bars
        for i, count in enumerate(counts):
            plt.text(i, count + 0.5, str(count), ha='center')
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'test_results.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved test results visualization to {filepath}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Memory-Optimized Prime Number Analysis')
    parser.add_argument('--range', nargs=2, type=int, default=[1, 1000000],
                        help='Range of numbers to analyze (start end)')
    parser.add_argument('--max_primes', type=int, default=10000,
                        help='Maximum number of primes to analyze')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='Directory to save output files and visualizations')
    return parser.parse_args()

def main():
    """
    Main function to demonstrate memory-optimized implementation.
    """
    print("Memory-Optimized Implementation for Mac M2")
    print("=========================================")
    
    # Parse command line arguments
    args = parse_arguments()
    start_range, end_range = args.range
    max_primes = args.max_primes
    output_dir = args.output_dir
    
    # Initialize memory-optimized analyzer
    analyzer = MemoryOptimizedPrimeAnalyzer(output_dir=output_dir)
    
    # Apply Mac M2 specific optimizations
    analyzer.optimize_torch_for_m2()
    
    # Run small test
    test_results = analyzer.run_small_test()
    
    # Find inner octave primes with memory optimization
    print("\nFinding inner octave primes with memory optimization:")
    inner_primes = analyzer.find_primes_by_classification_optimized("inner_octave", 1, 200, 10)
    print(f"Found {len(inner_primes)} inner octave primes:")
    for p in inner_primes:
        print(f"  {p['number']} (Confidence: {p['confidence']:.4f})")
    
    # Analyze a larger range with memory optimization
    print(f"\nAnalyzing range {start_range}-{end_range} with memory optimization (max {max_primes} primes):")
    large_range_results = analyzer.analyze_large_range(start_range, end_range, max_primes)
    
    print(f"Total primes analyzed: {large_range_results['total_primes']}")
    print(f"Inner octave: {large_range_results['inner_octave_count']} ({large_range_results['inner_octave_percentage']:.1%})")
    print(f"Outer octave: {large_range_results['outer_octave_count']} ({large_range_results['outer_octave_percentage']:.1%})")
    print(f"Cross-resonant: {large_range_results['cross_resonant_count']} ({large_range_results['cross_resonant_percentage']:.1%})")
    
    # Visualize memory usage
    analyzer.visualize_memory_usage()
    
    print(f"\nAll results have been saved to the {output_dir} directory.")
    print("\nMemory-optimized implementation completed successfully.")

if __name__ == "__main__":
    main()
