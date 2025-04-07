"""
Script to scrape the Individual Test Solutions section of the SHL catalog.
This script will go through all 32 pages of the catalog.
"""
import os
import sys
import pandas as pd
import argparse
import time
import urllib3

# Disable SSL warnings to avoid connection issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import our scraper with error handling
try:
    from utils.crawler import scrape_shl_catalog
except ImportError as e:
    print(f"Error importing crawler module: {e}")
    sys.exit(1)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape SHL Individual Test Solutions')
    parser.add_argument('--no-descriptions', action='store_true', 
                        help='Skip fetching detailed descriptions (faster)')
    parser.add_argument('--max-pages', type=int, default=None,
                        help='Maximum number of pages to scrape (default: all)')
    parser.add_argument('--retry', type=int, default=3,
                        help='Number of retries for network errors')
    parser.add_argument('--delay', type=int, default=0,
                        help='Delay in seconds between retries')
    args = parser.parse_args()
    
    # Scrape all Individual Test Solutions
    print("Starting to scrape all Individual Test Solutions...")
    print("This will process approximately 32 pages of the catalog.")
    
    # Try scraping with retries for network errors
    retries = 0
    max_retries = args.retry
    while retries <= max_retries:
        try:
            # Set the section type to "Individual Test Solutions"
            df = scrape_shl_catalog(
                get_descriptions=not args.no_descriptions,
                section_type="Individual Test Solutions",
                max_pages=args.max_pages
            )
            
            # If we get here, scraping was successful
            break
            
        except Exception as e:
            retries += 1
            if "Max retries exceeded" in str(e) or "connection" in str(e).lower():
                print(f"\nNetwork connection error: {e}")
                if retries <= max_retries:
                    print(f"Retry attempt {retries}/{max_retries} in {args.delay} seconds...")
                    time.sleep(args.delay)
                else:
                    print("Maximum retry attempts reached. Please check your network connection.")
                    print("Try adding --no-descriptions flag to reduce network requests.")
                    sys.exit(1)
            else:
                # For non-connection errors, just propagate the exception
                print(f"Error during scraping: {e}")
                sys.exit(1)
    
    # Print summary
    print("\nScraping complete!")
    print(f"Total Individual Test Solutions scraped: {len(df)}")
    
    # Save as a separate file
    output_path = os.path.join("data", "processed", "shl_individual_tests.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    main()
