#!/usr/bin/env python3
"""
Prime Number Validation Module

This module validates the primality testing algorithm against known prime numbers
to measure accuracy, false positives, and false negatives.
"""

import os
import sys
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

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

class PrimeValidator:
    """
    A validator for prime number detection algorithms that compares results
    against known prime numbers.
    """
    
    def __init__(self, output_dir='output'):
        """
        Initialize the prime validator.
        
        Args:
            output_dir: Directory to save output files and visualizations
        """
        # Initialize the prime classifier
        self.classifier = PrimeClassifier()
        
        # Set output directory
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output will be saved to: {os.path.abspath(self.output_dir)}")
    
    def generate_known_primes(self, limit):
        """
        Generate a list of known prime numbers up to the given limit using
        the Sieve of Eratosthenes algorithm.
        
        Args:
            limit: Upper limit for prime generation
            
        Returns:
            Set of prime numbers up to the limit
        """
        print(f"Generating known primes up to {limit} using Sieve of Eratosthenes...")
        
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
    
    def validate_primality_test(self, limit, known_primes=None):
        """
        Validate the primality test against known primes.
        
        Args:
            limit: Upper limit for validation
            known_primes: Set of known primes (if None, will be generated)
            
        Returns:
            Dictionary with validation results
        """
        print(f"Validating primality test up to {limit}...")
        
        # Get known primes if not provided
        if known_primes is None:
            known_primes = self.generate_known_primes(limit)
        
        # Initialize counters
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        # Lists to store misclassified numbers
        false_positive_numbers = []
        false_negative_numbers = []
        
        # Validate each number
        for n in tqdm(range(2, limit + 1)):
            # Check if prime using our classifier
            is_prime = self.classifier.is_prime(n)
            
            # Check against known primes
            is_known_prime = n in known_primes
            
            # Update counters
            if is_prime and is_known_prime:
                true_positives += 1
            elif is_prime and not is_known_prime:
                false_positives += 1
                false_positive_numbers.append(n)
            elif not is_prime and is_known_prime:
                false_negatives += 1
                false_negative_numbers.append(n)
        
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
    
    def run_comprehensive_validation(self, limits=[100, 1000, 10000]):
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
    parser = argparse.ArgumentParser(description='Prime Number Validation')
    parser.add_argument('--limit', type=int, default=10000,
                        help='Upper limit for validation')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='Directory to save output files and visualizations')
    parser.add_argument('--comprehensive', action='store_true',
                        help='Run comprehensive validation at multiple limits')
    parser.add_argument('--oeis', action='store_true',
                        help='Validate against OEIS prime numbers')
    return parser.parse_args()

def main():
    """
    Main function to run prime number validation.
    """
    print("Prime Number Validation")
    print("======================")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize validator
    validator = PrimeValidator(output_dir=args.output_dir)
    
    # Run validation
    if args.comprehensive:
        # Run comprehensive validation at multiple limits
        limits = [100, 1000, 10000]
        if args.limit > 10000:
            limits.append(args.limit)
        validator.run_comprehensive_validation(limits)
    elif args.oeis:
        # Validate against OEIS prime numbers
        validator.validate_with_oeis_primes(args.limit)
    else:
        # Run standard validation
        validator.validate_primality_test(args.limit)
    
    print("\nValidation completed successfully.")

if __name__ == "__main__":
    main()
