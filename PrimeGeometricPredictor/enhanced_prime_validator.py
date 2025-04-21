#!/usr/bin/env python3
"""
Enhanced Prime Number Validation Module for Extremely Large Scale Testing

This module validates the primality testing algorithm against known prime numbers
with optimizations for handling extremely large ranges (millions to billions).
"""

import os
import sys
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import gc
import pickle
import math
from datetime import datetime
import multiprocessing as mp
from functools import partial

# Import from other modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from prime_classification_system import PrimeClassifier
except ImportError:
    # Handle relative imports when running as a standalone script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from enhanced_package.prime_classification_system import PrimeClassifier
    except ImportError:
        print("Error: Could not import required modules. Please ensure you're running from the correct directory.")
        sys.exit(1)

class EnhancedPrimeValidator:
    """
    An enhanced validator for prime number detection algorithms that compares results
    against known prime numbers, optimized for extremely large scale testing.
    """
    
    def __init__(self, output_dir='output', low_memory=False):
        """
        Initialize the enhanced prime validator.
        
        Args:
            output_dir: Directory to save output files and visualizations
            low_memory: Whether to use low memory mode
        """
        # Initialize the prime classifier
        self.classifier = PrimeClassifier()
        
        # Set output directory
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output will be saved to: {os.path.abspath(self.output_dir)}")
        
        # Set low memory mode
        self.low_memory = low_memory
        if low_memory:
            print("Low memory mode enabled - optimizing for minimal memory usage")
        
        # Initialize checkpoint data
        self.checkpoint_data = {
            "last_processed": 0,
            "true_positives": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_known_primes_standard(self, limit):
        """
        Generate a list of known prime numbers up to the given limit using
        the standard Sieve of Eratosthenes algorithm.
        
        Args:
            limit: Upper limit for prime generation
            
        Returns:
            Set of prime numbers up to the limit
        """
        print(f"Generating known primes up to {limit} using standard Sieve of Eratosthenes...")
        
        # Initialize the sieve
        sieve = np.ones(limit + 1, dtype=bool)
        sieve[0:2] = False  # 0 and 1 are not prime
        
        # Apply the sieve
        for i in tqdm(range(2, int(np.sqrt(limit)) + 1)):
            if sieve[i]:
                sieve[i*i::i] = False
        
        # Extract the primes
        known_primes = set(np.where(sieve)[0])
        
        print(f"Generated {len(known_primes)} known primes")
        return known_primes
    
    def generate_known_primes_segmented(self, limit, segment_size=10000000):
        """
        Generate a list of known prime numbers up to the given limit using
        the segmented Sieve of Eratosthenes algorithm for memory efficiency.
        
        Args:
            limit: Upper limit for prime generation
            segment_size: Size of each segment to process
            
        Returns:
            Set of prime numbers up to the limit
        """
        print(f"Generating known primes up to {limit} using segmented Sieve of Eratosthenes...")
        
        # Find primes up to sqrt(limit) using standard sieve
        sqrt_limit = int(math.sqrt(limit))
        base_primes = self.generate_known_primes_standard(sqrt_limit)
        
        # Initialize the result set with the base primes
        all_primes = set(base_primes)
        
        # Process segments
        for segment_start in tqdm(range(sqrt_limit + 1, limit + 1, segment_size)):
            segment_end = min(segment_start + segment_size - 1, limit)
            
            # Initialize segment sieve
            segment_size_actual = segment_end - segment_start + 1
            segment_sieve = np.ones(segment_size_actual, dtype=bool)
            
            # Mark multiples of base primes in the segment
            for p in base_primes:
                # Find the first multiple of p in the segment
                start_idx = (segment_start + p - 1) // p * p
                if start_idx < segment_start:
                    start_idx += p
                
                # Mark multiples of p in the segment
                for i in range(start_idx, segment_end + 1, p):
                    segment_sieve[i - segment_start] = False
            
            # Extract primes from the segment
            segment_primes = {i + segment_start for i, is_prime in enumerate(segment_sieve) if is_prime}
            all_primes.update(segment_primes)
            
            # Free memory
            if self.low_memory:
                del segment_sieve
                gc.collect()
        
        print(f"Generated {len(all_primes)} known primes")
        return all_primes
    
    def generate_known_primes_bit_sieve(self, limit):
        """
        Generate a list of known prime numbers up to the given limit using
        a bit-optimized Sieve of Eratosthenes algorithm for memory efficiency.
        
        Args:
            limit: Upper limit for prime generation
            
        Returns:
            Set of prime numbers up to the limit
        """
        print(f"Generating known primes up to {limit} using bit-optimized Sieve of Eratosthenes...")
        
        # We only need to track odd numbers (except 2)
        # This cuts memory usage in half
        sieve_size = (limit - 1) // 2
        sieve = np.ones(sieve_size + 1, dtype=np.uint8)  # Use uint8 instead of bool for better memory usage
        
        # Apply the sieve for odd numbers
        for i in tqdm(range(1, int(np.sqrt(limit)) // 2 + 1)):
            if sieve[i]:
                # Mark multiples of the current prime (2*i + 1)
                p = 2 * i + 1
                # Start from p^2, which is at index (p^2 - 1) // 2
                start_idx = (p * p - 1) // 2
                # Mark every p'th odd number as composite
                sieve[start_idx::p] = 0
        
        # Extract the primes (2 and odd numbers where sieve is True)
        known_primes = {2}  # Start with 2
        known_primes.update({2 * i + 1 for i, is_prime in enumerate(sieve) if is_prime and i > 0})
        
        print(f"Generated {len(known_primes)} known primes")
        return known_primes
    
    def generate_known_primes(self, limit, method='auto'):
        """
        Generate a list of known prime numbers up to the given limit using
        the most appropriate method based on the limit and available memory.
        
        Args:
            limit: Upper limit for prime generation
            method: Method to use ('standard', 'segmented', 'bit', or 'auto')
            
        Returns:
            Set of prime numbers up to the limit
        """
        if method == 'standard' or (method == 'auto' and limit <= 10000000 and not self.low_memory):
            return self.generate_known_primes_standard(limit)
        elif method == 'bit' or (method == 'auto' and limit <= 100000000):
            return self.generate_known_primes_bit_sieve(limit)
        else:  # segmented or auto with large limit
            return self.generate_known_primes_segmented(limit)
    
    def load_known_primes_from_file(self, filepath):
        """
        Load known prime numbers from a file.
        
        Args:
            filepath: Path to the file containing prime numbers
            
        Returns:
            Set of prime numbers from the file
        """
        print(f"Loading known primes from file: {filepath}")
        
        known_primes = set()
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        prime = int(line.strip())
                        known_primes.add(prime)
                    except ValueError:
                        # Skip lines that can't be converted to integers
                        continue
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return set()
        
        print(f"Loaded {len(known_primes)} known primes from file")
        return known_primes
    
    def save_checkpoint(self, checkpoint_data, limit):
        """
        Save checkpoint data to a file.
        
        Args:
            checkpoint_data: Dictionary containing checkpoint data
            limit: Upper limit for validation
        """
        checkpoint_file = os.path.join(self.output_dir, f"checkpoint_{limit}.pkl")
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        print(f"Saved checkpoint to {checkpoint_file}")
    
    def load_checkpoint(self, limit):
        """
        Load checkpoint data from a file.
        
        Args:
            limit: Upper limit for validation
            
        Returns:
            Dictionary containing checkpoint data, or None if no checkpoint exists
        """
        checkpoint_file = os.path.join(self.output_dir, f"checkpoint_{limit}.pkl")
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)
                
                print(f"Loaded checkpoint from {checkpoint_file}")
                print(f"Resuming from {checkpoint_data['last_processed']}")
                return checkpoint_data
            except Exception as e:
                print(f"Error loading checkpoint: {str(e)}")
                return None
        else:
            print("No checkpoint found, starting from scratch")
            return None
    
    def validate_primality_test_batch(self, start, end, known_primes):
        """
        Validate the primality test against known primes for a batch of numbers.
        
        Args:
            start: Start of the batch
            end: End of the batch
            known_primes: Set of known primes
            
        Returns:
            Dictionary with validation results for the batch
        """
        # Initialize counters
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        # Lists to store misclassified numbers
        false_positive_numbers = []
        false_negative_numbers = []
        
        # Validate each number in the batch
        for n in range(start, end + 1):
            # Skip even numbers except 2 for efficiency
            if n > 2 and n % 2 == 0:
                continue
            
            # Check if prime using our classifier
            is_prime = self.classifier.is_prime(n)
            
            # Check against known primes
            is_known_prime = n in known_primes
            
            # Update counters
            if is_prime and is_known_prime:
                true_positives += 1
            elif is_prime and not is_known_prime:
                false_positives += 1
                if len(false_positive_numbers) < 100:  # Limit to avoid memory issues
                    false_positive_numbers.append(n)
            elif not is_prime and is_known_prime:
                false_negatives += 1
                if len(false_negative_numbers) < 100:  # Limit to avoid memory issues
                    false_negative_numbers.append(n)
        
        # Compile results
        results = {
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "false_positive_numbers": false_positive_numbers,
            "false_negative_numbers": false_negative_numbers
        }
        
        return results
    
    def validate_primality_test_distributed(self, limit, known_primes, batch_size=1000000, num_processes=None):
        """
        Validate the primality test against known primes using multiple processes.
        
        Args:
            limit: Upper limit for validation
            known_primes: Set of known primes
            batch_size: Size of each batch to process
            num_processes: Number of processes to use (default: number of CPU cores)
            
        Returns:
            Dictionary with validation results
        """
        print(f"Validating primality test up to {limit} using distributed processing...")
        
        # Determine number of processes
        if num_processes is None:
            num_processes = mp.cpu_count()
        
        print(f"Using {num_processes} processes with batch size {batch_size}")
        
        # Create batches
        batches = []
        for batch_start in range(2, limit + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, limit)
            batches.append((batch_start, batch_end))
        
        # Create a pool of processes
        with mp.Pool(processes=num_processes) as pool:
            # Process batches in parallel
            batch_results = list(tqdm(
                pool.starmap(
                    partial(self.validate_primality_test_batch, known_primes=known_primes),
                    batches
                ),
                total=len(batches)
            ))
        
        # Combine results
        true_positives = sum(result["true_positives"] for result in batch_results)
        false_positives = sum(result["false_positives"] for result in batch_results)
        false_negatives = sum(result["false_negatives"] for result in batch_results)
        
        # Combine misclassified numbers (limited to avoid memory issues)
        false_positive_numbers = []
        false_negative_numbers = []
        
        for result in batch_results:
            false_positive_numbers.extend(result["false_positive_numbers"][:100])
            false_negative_numbers.extend(result["false_negative_numbers"][:100])
            
            if len(false_positive_numbers) >= 1000:
                false_positive_numbers = false_positive_numbers[:1000]
            
            if len(false_negative_numbers) >= 1000:
                false_negative_numbers = false_negative_numbers[:1000]
        
        # Calculate metrics
        total_known_primes = len([p for p in known_primes if p <= limit])
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = true_positives / total_known_primes if total_known_primes > 0 else 0
        
        # Compile results
        results = {
            "limit": limit,
            "total_known_primes": total_known_primes,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
            "false_positive_numbers": false_positive_numbers,
            "false_negative_numbers": false_negative_numbers
        }
        
        return results
    
    def validate_primality_test(self, limit, known_primes=None, use_checkpoint=False, 
                               batch_size=1000000, distributed=False):
        """
        Validate the primality test against known primes with support for checkpointing.
        
        Args:
            limit: Upper limit for validation
            known_primes: Set of known primes (if None, will be generated)
            use_checkpoint: Whether to use checkpointing
            batch_size: Size of each batch to process
            distributed: Whether to use distributed processing
            
        Returns:
            Dictionary with validation results
        """
        print(f"Validating primality test up to {limit}...")
        
        # Get known primes if not provided
        if known_primes is None:
            if self.low_memory:
                known_primes = self.generate_known_primes(limit, method='segmented')
            else:
                known_primes = self.generate_known_primes(limit)
        
        # Use distributed processing if requested
        if distributed:
            return self.validate_primality_test_distributed(limit, known_primes, batch_size)
        
        # Load checkpoint if requested
        start = 2
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        if use_checkpoint:
            checkpoint_data = self.load_checkpoint(limit)
            if checkpoint_data:
                start = checkpoint_data["last_processed"] + 1
                true_positives = checkpoint_data["true_positives"]
                false_positives = checkpoint_data["false_positives"]
                false_negatives = checkpoint_data["false_negatives"]
        
        # Lists to store misclassified numbers
        false_positive_numbers = []
        false_negative_numbers = []
        
        # Process in batches
        for batch_start in range(start, limit + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, limit)
            print(f"Processing batch {batch_start}-{batch_end}...")
            
            # Validate each number in the batch
            for n in tqdm(range(batch_start, batch_end + 1)):
                # Skip even numbers except 2 for efficiency
                if n > 2 and n % 2 == 0:
                    continue
                
                # Check if prime using our classifier
                is_prime = self.classifier.is_prime(n)
                
                # Check against known primes
                is_known_prime = n in known_primes
                
                # Update counters
                if is_prime and is_known_prime:
                    true_positives += 1
                elif is_prime and not is_known_prime:
                    false_positives += 1
                    if len(false_positive_numbers) < 1000:  # Limit to avoid memory issues
                        false_positive_numbers.append(n)
                elif not is_prime and is_known_prime:
                    false_negatives += 1
                    if len(false_negative_numbers) < 1000:  # Limit to avoid memory issues
                        false_negative_numbers.append(n)
            
            # Save checkpoint after each batch if requested
            if use_checkpoint:
                self.checkpoint_data = {
                    "last_processed": batch_end,
                    "true_positives": true_positives,
                    "false_positives": false_positives,
                    "false_negatives": false_negatives,
                    "timestamp": datetime.now().isoformat()
                }
                self.save_checkpoint(self.checkpoint_data, limit)
            
            # Free memory if in low memory mode
            if self.low_memory:
                gc.collect()
        
        # Calculate metrics
        total_known_primes = len([p for p in known_primes if p <= limit])
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = true_positives / total_known_primes if total_known_primes > 0 else 0
        
        # Compile results
        results = {
            "limit": limit,
            "total_known_primes": total_known_primes,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
            "false_positive_numbers": false_positive_numbers,
            "false_negative_numbers": false_negative_numbers
        }
        
        # Save results
        self.save_validation_results(results)
        
        # Create visualizations
        self.visualize_validation_results(results)
        
        return results
    
    def save_validation_results(self, results):
        """
        Save validation results to a text file.
        
        Args:
            results: Dictionary containing validation results
        """
        filepath = os.path.join(self.output_dir, "validation_results.txt")
        with open(filepath, 'w') as f:
            f.write("Prime Number Validation Results\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Validation limit: {results['limit']}\n")
            f.write(f"Total known primes: {results['total_known_primes']}\n\n")
            
            f.write("Performance Metrics:\n")
            f.write(f"  True Positives: {results['true_positives']}\n")
            f.write(f"  False Positives: {results['false_positives']}\n")
            f.write(f"  False Negatives: {results['false_negatives']}\n\n")
            
            f.write(f"  Precision: {results['precision']:.4f}\n")
            f.write(f"  Recall: {results['recall']:.4f}\n")
            f.write(f"  F1 Score: {results['f1_score']:.4f}\n")
            f.write(f"  Accuracy: {results['accuracy']:.4f}\n\n")
            
            if results['false_positive_numbers']:
                f.write("False Positive Numbers (incorrectly identified as prime):\n")
                for i, n in enumerate(results['false_positive_numbers']):
                    f.write(f"  {n}")
                    if (i + 1) % 10 == 0:
                        f.write("\n")
                    else:
                        f.write(", ")
                f.write("\n\n")
            
            if results['false_negative_numbers']:
                f.write("False Negative Numbers (primes missed by our algorithm):\n")
                for i, n in enumerate(results['false_negative_numbers']):
                    f.write(f"  {n}")
                    if (i + 1) % 10 == 0:
                        f.write("\n")
                    else:
                        f.write(", ")
                f.write("\n")
        
        print(f"Saved validation results to {filepath}")
    
    def visualize_validation_results(self, results):
        """
        Create visualizations of validation results.
        
        Args:
            results: Dictionary containing validation results
        """
        # Create performance metrics visualization
        plt.figure(figsize=(10, 6))
        
        # Bar chart of performance metrics
        metrics = ['Precision', 'Recall', 'F1 Score', 'Accuracy']
        values = [results['precision'], results['recall'], results['f1_score'], results['accuracy']]
        colors = ['blue', 'green', 'red', 'purple']
        
        plt.bar(metrics, values, color=colors)
        plt.title('Primality Test Performance Metrics')
        plt.ylabel('Score')
        plt.ylim(0, 1.1)  # Metrics are between 0 and 1
        plt.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Add value labels on top of bars
        for i, v in enumerate(values):
            plt.text(i, v + 0.02, f"{v:.4f}", ha='center')
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'validation_metrics.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved validation metrics visualization to {filepath}")
        
        # Create confusion matrix visualization
        plt.figure(figsize=(8, 8))
        
        # Confusion matrix
        cm = np.array([
            [results['true_positives'], results['false_negatives']],
            [results['false_positives'], 0]  # We don't track true negatives
        ])
        
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar()
        
        # Add labels
        classes = ['Prime', 'Not Prime']
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes)
        plt.yticks(tick_marks, classes)
        
        # Add text annotations
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, format(cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")
        
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'confusion_matrix.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved confusion matrix visualization to {filepath}")
    
    def validate_with_oeis_primes(self, limit=10000):
        """
        Validate using the first primes from OEIS (Online Encyclopedia of Integer Sequences).
        
        Args:
            limit: Maximum number to check
            
        Returns:
            Dictionary with validation results
        """
        # First few primes from OEIS A000040
        oeis_primes = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
            73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
            179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
            283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
            419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541
        ]
        
        # Extend with more primes if needed
        if limit > 541:
            # Generate more primes using the sieve
            extended_primes = self.generate_known_primes(limit)
            known_primes = extended_primes
        else:
            # Filter the OEIS primes up to the limit
            known_primes = set(p for p in oeis_primes if p <= limit)
        
        # Run validation
        return self.validate_primality_test(limit, known_primes)
    
    def run_comprehensive_validation(self, limits=[100, 1000, 10000, 100000]):
        """
        Run validation at multiple limits to assess scaling behavior.
        
        Args:
            limits: List of limits to validate against
            
        Returns:
            Dictionary with validation results for each limit
        """
        print("Running comprehensive validation at multiple limits...")
        
        all_results = {}
        
        for limit in limits:
            print(f"\nValidating up to {limit}...")
            results = self.validate_primality_test(limit)
            all_results[limit] = results
        
        # Create scaling visualization
        self.visualize_scaling_behavior(all_results, limits)
        
        return all_results
    
    def visualize_scaling_behavior(self, all_results, limits):
        """
        Visualize how performance metrics scale with increasing limits.
        
        Args:
            all_results: Dictionary with results for each limit
            limits: List of limits used for validation
        """
        # Extract metrics for each limit
        precisions = [all_results[limit]['precision'] for limit in limits]
        recalls = [all_results[limit]['recall'] for limit in limits]
        f1_scores = [all_results[limit]['f1_score'] for limit in limits]
        accuracies = [all_results[limit]['accuracy'] for limit in limits]
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Plot metrics vs limit
        plt.plot(limits, precisions, 'bo-', label='Precision')
        plt.plot(limits, recalls, 'go-', label='Recall')
        plt.plot(limits, f1_scores, 'ro-', label='F1 Score')
        plt.plot(limits, accuracies, 'mo-', label='Accuracy')
        
        plt.title('Performance Metrics vs. Validation Limit')
        plt.xlabel('Validation Limit')
        plt.ylabel('Score')
        plt.xscale('log')  # Log scale for x-axis
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Save the plot
        filepath = os.path.join(self.output_dir, 'scaling_behavior.png')
        plt.savefig(filepath)
        plt.close()
        
        print(f"Saved scaling behavior visualization to {filepath}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Enhanced Prime Number Validation for Large Scale Testing')
    parser.add_argument('--limit', type=int, default=10000,
                        help='Upper limit for validation')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='Directory to save output files and visualizations')
    parser.add_argument('--comprehensive', action='store_true',
                        help='Run comprehensive validation at multiple limits')
    parser.add_argument('--oeis', action='store_true',
                        help='Validate against OEIS prime numbers')
    parser.add_argument('--segmented-sieve', action='store_true',
                        help='Use segmented Sieve of Eratosthenes for memory efficiency')
    parser.add_argument('--low-memory', action='store_true',
                        help='Optimize for minimal memory usage')
    parser.add_argument('--checkpoint', action='store_true',
                        help='Use checkpointing to save progress')
    parser.add_argument('--distributed', action='store_true',
                        help='Use distributed processing with multiple CPU cores')
    parser.add_argument('--batch-size', type=int, default=1000000,
                        help='Batch size for processing')
    parser.add_argument('--processes', type=int, default=None,
                        help='Number of processes to use for distributed processing')
    return parser.parse_args()

def main():
    """
    Main function to run enhanced prime number validation.
    """
    print("Enhanced Prime Number Validation for Large Scale Testing")
    print("======================================================")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize validator
    validator = EnhancedPrimeValidator(output_dir=args.output_dir, low_memory=args.low_memory)
    
    # Run validation
    if args.comprehensive:
        # Run comprehensive validation at multiple limits
        limits = [100, 1000, 10000, 100000]
        if args.limit > 100000:
            limits.append(args.limit)
        validator.run_comprehensive_validation(limits)
    elif args.oeis:
        # Validate against OEIS prime numbers
        validator.validate_with_oeis_primes(args.limit)
    else:
        # Run standard validation
        sieve_method = 'segmented' if args.segmented_sieve else 'auto'
        known_primes = validator.generate_known_primes(args.limit, method=sieve_method)
        
        validator.validate_primality_test(
            args.limit, 
            known_primes=known_primes,
            use_checkpoint=args.checkpoint,
            batch_size=args.batch_size,
            distributed=args.distributed
        )
    
    print("\nValidation completed successfully.")

if __name__ == "__main__":
    main()
