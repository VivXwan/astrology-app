#!/usr/bin/env python3
# test_dasha.py - Test script for the enhanced and optimized dasha calculations

import time
from datetime import datetime
from models import BirthData
from services.dasha import calculate_vimshottari_dasha

def test_dasha_calculation(max_level=2):
    """
    Test the enhanced dasha calculation implementation.
    
    Args:
        max_level (int): Maximum level of sub-dashas to calculate (0-5)
    """
    # Sample birth data
    birth_data = BirthData(
        year=1990, 
        month=5, 
        day=15, 
        hour=12, 
        minute=30, 
        second=0, 
        latitude=13.0827, 
        longitude=80.2707  # Chennai, India
    )
    
    # Mock Moon data (simplified for testing)
    moon_data = {
        "planet": "Moon",
        "longitude": 85.5,  # Sample longitude in Pushya Nakshatra
        "latitude": 5.0,
        "house": 3
    }
    
    # Calculate dasha with specified level and measure performance
    print(f"Calculating Vimshottari Dasha with max_level={max_level}...")
    start_time = time.time()
    dasha_timeline = calculate_vimshottari_dasha(birth_data, moon_data, max_level=max_level)
    end_time = time.time()
    
    # Performance metrics
    calc_time = end_time - start_time
    print(f"Calculation time: {calc_time:.6f} seconds")
    
    # Verify structure
    print(f"\nGenerated {len(dasha_timeline)} Mahadasha periods")
    
    # Check first Mahadasha for structure
    if dasha_timeline and len(dasha_timeline) > 0:
        md = dasha_timeline[0]
        print(f"\nFirst Mahadasha: {md['planet']} ({md['start_date']} to {md['end_date']})")
        
        # Check first Antardasha if level >= 1
        if max_level >= 1 and 'antardashas' in md and len(md['antardashas']) > 0:
            ad = md['antardashas'][0]
            print(f"  First Antardasha: {ad['planet']} ({ad['start_date']} to {ad['end_date']})")
            
            # Check first Pratyantar if level >= 2
            if max_level >= 2 and 'pratyantar_dashas' in ad and len(ad['pratyantar_dashas']) > 0:
                pd = ad['pratyantar_dashas'][0]
                print(f"    First Pratyantar: {pd['planet']} ({pd['start_date']} to {pd['end_date']})")
                
                # Check first Sookshma if level >= 3
                if max_level >= 3 and 'sookshma_dashas' in pd and len(pd['sookshma_dashas']) > 0:
                    sd = pd['sookshma_dashas'][0]
                    print(f"      First Sookshma: {sd['planet']} ({sd['start_date']} to {sd['end_date']})")
                    
                    # Check first Prana if level >= 4
                    if max_level >= 4 and 'prana_dashas' in sd and len(sd['prana_dashas']) > 0:
                        prd = sd['prana_dashas'][0]
                        print(f"        First Prana: {prd['planet']} ({prd['start_date']} to {prd['end_date']})")
                        
                        # Check first Deha if level >= 5
                        if max_level >= 5 and 'deha_dashas' in prd and len(prd['deha_dashas']) > 0:
                            dd = prd['deha_dashas'][0]
                            print(f"          First Deha: {dd['planet']} ({dd['start_date']} to {dd['end_date']})")
                
    print("\nDasha structure verification complete!")

def benchmark_caching():
    """Test the effectiveness of caching by running the same calculation twice"""
    birth_data = BirthData(
        year=1985, 
        month=10, 
        day=15, 
        hour=14, 
        minute=30, 
        second=0, 
        latitude=20.5937, 
        longitude=78.9629  # India
    )
    
    moon_data = {
        "planet": "Moon",
        "longitude": 120.5,
        "latitude": 3.0,
        "house": 4
    }
    
    # First run (cache miss)
    print("\n===== CACHING BENCHMARK =====")
    print("First run (cache miss):")
    start_time = time.time()
    calculate_vimshottari_dasha(birth_data, moon_data, max_level=3)
    end_time = time.time()
    first_run_time = end_time - start_time
    print(f"Time: {first_run_time:.6f} seconds")
    
    # Second run (cache hit)
    print("\nSecond run (cache hit):")
    start_time = time.time()
    calculate_vimshottari_dasha(birth_data, moon_data, max_level=3)
    end_time = time.time()
    second_run_time = end_time - start_time
    print(f"Time: {second_run_time:.6f} seconds")
    
    # Calculate speedup
    if first_run_time > 0:
        speedup = first_run_time / second_run_time if second_run_time > 0 else float('inf')
        print(f"\nCache speedup: {speedup:.2f}x faster")
    
if __name__ == "__main__":
    # Test with different levels
    for level in range(6):
        print(f"\n{'='*50}")
        print(f"TESTING DASHA CALCULATION WITH MAX_LEVEL = {level}")
        print(f"{'='*50}")
        test_dasha_calculation(level)
    
    # Test caching
    benchmark_caching() 