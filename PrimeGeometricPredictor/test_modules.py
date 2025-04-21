#!/usr/bin/env python3
"""
Test script to verify the availability of required modules and basic functionality.
"""

import sys
import os

def test_module_imports():
    """Test if required modules can be imported."""
    print(f"Python version: {sys.version}")
    print("Testing import of required modules...")
    
    modules = {
        "numpy": "NumPy",
        "matplotlib": "Matplotlib",
        "matplotlib.pyplot": "Matplotlib.pyplot",
        "torch": "PyTorch",
        "math": "Math",
        "decimal": "Decimal",
        "collections": "Collections"
    }
    
    all_ok = True
    
    for module_name, display_name in modules.items():
        try:
            __import__(module_name)
            print(f"{display_name}: OK")
        except ImportError as e:
            print(f"{display_name}: Missing - {str(e)}")
            all_ok = False
    
    return all_ok

def test_basic_prime_functions():
    """Test basic prime number functions."""
    print("\nTesting basic prime number functions...")
    
    # Simple primality test function
    def is_prime(n):
        """Check if a number is prime."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        
        # Check odd divisors up to sqrt(n)
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        
        return True
    
    # Test cases
    test_cases = [
        (2, True),
        (3, True),
        (4, False),
        (17, True),
        (19, True),
        (21, False),
        (97, True)
    ]
    
    all_passed = True
    
    for num, expected in test_cases:
        result = is_prime(num)
        if result == expected:
            print(f"is_prime({num}) = {result}: PASS")
        else:
            print(f"is_prime({num}) = {result}, expected {expected}: FAIL")
            all_passed = False
    
    return all_passed

def test_enhanced_resonance_detector():
    """Test if the enhanced resonance detector module can be imported and used."""
    print("\nTesting enhanced resonance detector module...")
    
    try:
        sys.path.append('/home/ubuntu/fibonacci_prime_project/enhanced_package')
        from enhanced_resonance_detector import (
            PHI, SYSTEM_BOUNDARY, calculate_harmonic_frequency,
            identify_harmonic_octave, classify_prime_by_octave
        )
        
        print(f"PHI = {PHI}")
        print(f"SYSTEM_BOUNDARY = {SYSTEM_BOUNDARY}")
        
        # Test harmonic frequency calculation for prime 19
        freq_19 = calculate_harmonic_frequency(19)
        print(f"Harmonic frequency of 19: {freq_19}")
        
        # Test octave identification for prime 19
        octave_19 = identify_harmonic_octave(19)
        print(f"Harmonic octave of 19: {octave_19}")
        
        # Test classification for prime 19
        classification_19 = classify_prime_by_octave(19)
        print(f"Classification of 19: {classification_19}")
        
        return True
    except Exception as e:
        print(f"Error testing enhanced resonance detector: {str(e)}")
        return False

def test_sacred_geometry_analysis():
    """Test if the sacred geometry analysis module can be imported and used."""
    print("\nTesting sacred geometry analysis module...")
    
    try:
        sys.path.append('/home/ubuntu/fibonacci_prime_project/enhanced_package')
        from sacred_geometry_analysis import (
            calculate_sacred_angle,
            map_to_flower_of_life,
            analyze_center_edge_relationship
        )
        
        # Test sacred angle calculation for prime 19
        angle_19 = calculate_sacred_angle(19)
        print(f"Sacred angle of 19: {angle_19}")
        
        # Test mapping to Flower of Life for prime 19
        flower_coords_19 = map_to_flower_of_life(19)
        print(f"Flower of Life coordinates of 19: {flower_coords_19}")
        
        # Test center-edge relationship for prime 19
        center_edge_19 = analyze_center_edge_relationship(19)
        print(f"Center score of 19: {center_edge_19['center_score']}")
        print(f"Edge score of 19: {center_edge_19['edge_score']}")
        print(f"Primary role of 19: {center_edge_19['primary_role']}")
        
        return True
    except Exception as e:
        print(f"Error testing sacred geometry analysis: {str(e)}")
        return False

def test_prime_classification_system():
    """Test if the prime classification system can be imported and used."""
    print("\nTesting prime classification system...")
    
    try:
        sys.path.append('/home/ubuntu/fibonacci_prime_project/enhanced_package')
        from prime_classification_system import PrimeClassifier
        
        # Initialize classifier
        classifier = PrimeClassifier()
        
        # Test classification for a few primes
        test_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        
        for prime in test_primes:
            is_prime, classification, confidence = classifier.classify_prime(prime)
            print(f"Prime {prime}: {classification} (Confidence: {confidence:.4f})")
        
        return True
    except Exception as e:
        print(f"Error testing prime classification system: {str(e)}")
        return False

def test_memory_optimized_implementation():
    """Test if the memory optimized implementation can be imported and used."""
    print("\nTesting memory optimized implementation...")
    
    try:
        sys.path.append('/home/ubuntu/fibonacci_prime_project/enhanced_package')
        from memory_optimized_implementation import MemoryOptimizedPrimeAnalyzer
        
        # Initialize analyzer
        analyzer = MemoryOptimizedPrimeAnalyzer()
        
        # Run small test
        test_results = analyzer.run_small_test()
        
        print(f"Test range: {test_results['test_range']}")
        print(f"Primes found: {test_results['primes_found']}")
        print(f"Classification breakdown: {test_results['inner_octave_count']} inner octave, "
              f"{test_results['outer_octave_count']} outer octave, "
              f"{test_results['cross_resonant_count']} cross-resonant")
        print(f"Performance: {test_results['primes_per_second']:.2f} primes/second")
        
        return True
    except Exception as e:
        print(f"Error testing memory optimized implementation: {str(e)}")
        return False

def main():
    """Main function to run all tests."""
    print("Running tests to verify functionality of enhanced prime number analysis...")
    print("=" * 80)
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run tests
    module_imports_ok = test_module_imports()
    basic_functions_ok = test_basic_prime_functions()
    
    # Only run advanced tests if basic imports and functions work
    if module_imports_ok and basic_functions_ok:
        resonance_detector_ok = test_enhanced_resonance_detector()
        sacred_geometry_ok = test_sacred_geometry_analysis()
        classification_system_ok = test_prime_classification_system()
        memory_optimized_ok = test_memory_optimized_implementation()
        
        # Summarize results
        print("\nTest Summary:")
        print(f"Module imports: {'PASS' if module_imports_ok else 'FAIL'}")
        print(f"Basic prime functions: {'PASS' if basic_functions_ok else 'FAIL'}")
        print(f"Enhanced resonance detector: {'PASS' if resonance_detector_ok else 'FAIL'}")
        print(f"Sacred geometry analysis: {'PASS' if sacred_geometry_ok else 'FAIL'}")
        print(f"Prime classification system: {'PASS' if classification_system_ok else 'FAIL'}")
        print(f"Memory optimized implementation: {'PASS' if memory_optimized_ok else 'FAIL'}")
        
        all_passed = (module_imports_ok and basic_functions_ok and 
                      resonance_detector_ok and sacred_geometry_ok and 
                      classification_system_ok and memory_optimized_ok)
        
        if all_passed:
            print("\nAll tests PASSED! The enhanced prime number analysis system is functioning correctly.")
        else:
            print("\nSome tests FAILED. Please check the output for details.")
    else:
        print("\nBasic tests failed. Skipping advanced tests.")
        print("\nTest Summary:")
        print(f"Module imports: {'PASS' if module_imports_ok else 'FAIL'}")
        print(f"Basic prime functions: {'PASS' if basic_functions_ok else 'FAIL'}")
        print("\nPlease fix the basic issues before running advanced tests.")

if __name__ == "__main__":
    main()
