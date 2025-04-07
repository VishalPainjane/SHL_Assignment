"""Web scraper for the SHL Product Catalog."""
import os
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SHL_CATALOG_URL, RAW_DATA_DIR, PROCESSED_DATA_DIR

def scrape_shl_catalog(get_descriptions=True, section_type="Pre-packaged Job Solutions", max_pages=None):
    """
    Scrapes the SHL product catalog website and extracts assessment information.
    
    Args:
        get_descriptions: Whether to fetch descriptions from detail pages
        section_type: Which section to scrape ("Pre-packaged Job Solutions" or "Individual Test Solutions")
        max_pages: Maximum number of pages to scrape (None for all)
        
    Returns:
        DataFrame of assessments with their details.
    """
    print(f"Fetching SHL catalog from {SHL_CATALOG_URL}...")
    
    try:
        # Set up Selenium WebDriver
        chrome_options = Options()
        # Uncomment the line below for headless mode in production
        # chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)  # Increase page load timeout
        
        # Navigate to the catalog page with correct URL parameters
        # Use the first URL from observed patterns
        if section_type == "Pre-packaged Job Solutions":
            initial_url = f"{SHL_CATALOG_URL}?start=0&type=2&type=2"
        else:
            initial_url = f"{SHL_CATALOG_URL}?start=0&type=1&type=1"
            
        driver.get(initial_url)
        time.sleep(5)  # Give more time for the page to fully load
        
        # Wait for the tables to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
        except TimeoutException:
            print("Warning: Tables took too long to load, but continuing anyway...")
        
        # Create list to store all assessments
        all_assessments = []
        
        # Extract test type legend (descriptions of A, B, C, etc.)
        test_type_legend = extract_test_type_legend(driver)
        
        # Process pages until we reach the end or hit max_pages
        page_num = 1
        has_more_pages = True
        processed_urls = set()  # Track URLs we've already processed to avoid loops
        processed_urls.add(driver.current_url)
        
        while has_more_pages and (max_pages is None or page_num <= max_pages):
            print(f"Processing {section_type} - Page {page_num}")
            
            # Find all products on current page
            products = scrape_products_from_page(driver, section_type, test_type_legend)
            
            if get_descriptions and products:
                # Get detailed information for each product
                for product in tqdm(products, desc=f"Extracting details for page {page_num}"):
                    product_details = extract_product_details(driver, product["url"])
                    product.update(product_details)
                    all_assessments.append(product)
            elif products:
                all_assessments.extend(products)
            
            # Check if there's a next page and navigate to it
            next_url = find_next_page_url(driver)
            
            if next_url and next_url not in processed_urls and (max_pages is None or page_num < max_pages):
                try:
                    print(f"Navigating to next page: {next_url}")
                    driver.get(next_url)
                    processed_urls.add(next_url)
                    time.sleep(5)  # Allow page to load
                    
                    # Verify page loaded successfully
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                        )
                    except TimeoutException:
                        print("Page may not have loaded properly. Attempting to continue...")
                        
                    page_num += 1
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    # Try one more time with a refresh
                    try:
                        driver.refresh()
                        time.sleep(5)
                        has_more_pages = (find_next_page_url(driver) is not None)
                    except:
                        has_more_pages = False
            else:
                has_more_pages = False
                print(f"Reached last page of {section_type}")
                
        driver.quit()
        
        # Save raw data
        raw_data_path = os.path.join(RAW_DATA_DIR, "shl_catalog_raw.json")
        os.makedirs(os.path.dirname(raw_data_path), exist_ok=True)
        with open(raw_data_path, 'w') as f:
            json.dump(all_assessments, f, indent=2)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_assessments)
        
        # Save processed data
        processed_data_path = os.path.join(PROCESSED_DATA_DIR, "shl_assessments.csv")
        os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
        df.to_csv(processed_data_path, index=False)
        
        print(f"\nSuccessfully scraped {len(all_assessments)} assessments")
        return df
    
    except Exception as e:
        print(f"Error scraping SHL catalog: {e}")
        # If scraping fails, try to load from backup data if available
        try:
            return pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "shl_assessments.csv"))
        except:
            print("No backup data available. Creating mock data for development.")
            return create_mock_data()

def find_next_page_url(driver):
    """Find the URL for the next page by extracting it directly from the pagination 'Next' button"""
    try:
        # Find the pagination
        pagination = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination"))
        )
        
        # Look for the "Next" button that's not disabled
        next_buttons = pagination.find_elements(By.CSS_SELECTOR, 
                                             "li.pagination__item.-arrow.-next:not(.-disabled) a")
        
        if next_buttons and len(next_buttons) > 0:  # Fixed syntax error in this line
            # Get the exact URL from the Next button without any modification
            next_url = next_buttons[0].get_attribute("href")
            print(f"Found next page URL: {next_url}")
            
            # Log if URL has unexpected type parameters (for debugging)
            if "start=60" in next_url and "type=1" in next_url:
                print("Note: Detected page 6 with type=1 parameters (expected behavior)")
            elif "type=1" in next_url and "start=60" not in next_url:
                print("Warning: Unexpected type=1 parameter in URL")
            
            return next_url
        return None
    except Exception as e:
        print(f"Error finding next page URL: {e}")
        return None

def scrape_products_from_page(driver, section_type, test_type_legend):
    """Extract all products from the current catalog page."""
    products = []
    
    try:
        # Try multiple approaches to find the correct table
        table = find_correct_table(driver)
        if not table:
            print(f"Could not find table for {section_type}, skipping...")
            return products
        
        # Get all rows except the header
        rows = table.find_elements(By.CSS_SELECTOR, "tr:not(:first-child)")
        
        if not rows:
            print(f"No product rows found in table")
            return products
            
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 4:
                    continue
                
                # Extract basic product data
                title_cell = cells[0]
                title_link = title_cell.find_element(By.TAG_NAME, "a")
                name = title_link.text.strip()
                url = title_link.get_attribute("href")
                
                # Check for Remote Testing
                remote_cell = cells[1]
                remote_testing = "Yes" if remote_cell.find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
                
                # Check for Adaptive/IRT
                adaptive_cell = cells[2]
                adaptive_irt = "Yes" if adaptive_cell.find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
                
                # Extract test types
                test_types_cell = cells[3]
                test_type_elements = test_types_cell.find_elements(By.CSS_SELECTOR, "span.product-catalogue__key")
                test_types = [elem.text for elem in test_type_elements]
                
                # Create product dictionary with basic information
                product = {
                    "name": name,
                    "url": url,
                    "remote_testing": remote_testing,
                    "adaptive_irt": adaptive_irt,
                    "test_types": ", ".join(test_types),
                    "solution_type": section_type,
                }
                
                # Add expanded test type descriptions
                test_types_expanded = []
                for tt in test_types:
                    if tt in test_type_legend:
                        test_types_expanded.append(f"{tt}: {test_type_legend[tt]}")
                product["test_types_expanded"] = "; ".join(test_types_expanded)
                
                products.append(product)
            except Exception as e:
                print(f"Error processing row: {e}")
    
    except Exception as e:
        print(f"Error extracting products from table: {e}")
    
    return products

def find_correct_table(driver):
    """Find the correct table on the current page regardless of section type or URL parameters"""
    try:
        # Get current URL to determine context
        current_url = driver.current_url
        print(f"Finding table on page: {current_url}")
        
        # Look for tables with producttable class first (most reliable)
        tables = driver.find_elements(By.CSS_SELECTOR, "table.producttable")
        
        # Special handling for the anomalous page with start=60&type=1
        if "start=60" in current_url and "type=1" in current_url:
            print("Using special handling for page 6 (start=60)")
            # For this specific case, we want the first table regardless
            if tables:
                return tables[0]
                
        # Standard handling for normal pages
        if tables:
            if "type=2" in current_url:
                # For Pre-packaged, take the first table
                return tables[0]
            elif "type=1" in current_url:
                # For Individual Tests, take the first table
                return tables[0]
        
        # Fallback - look for any table
        all_tables = driver.find_elements(By.TAG_NAME, "table")
        if all_tables:
            return all_tables[0]
        
        # Last resort - try to find a table via a more complex path
        content_container = driver.find_elements(By.CSS_SELECTOR, ".content__container")
        if content_container:
            tables_in_content = content_container[0].find_elements(By.TAG_NAME, "table")
            if tables_in_content:
                return tables_in_content[0]
        
        print("No table found on the page!")
        return None
    except Exception as e:
        print(f"Error finding table: {e}")
        return None

def extract_product_details(driver, url):
    """
    Visit the product detail page and extract comprehensive information.
    Returns a dictionary with product details.
    """
    details = {
        "description": "Description not available",
        "duration": "Not specified",
        "languages": "Not specified",
        "job_levels": "Not specified",
        "assessment_length": "Not specified",
        "downloads": []
    }
    
    max_retries = 3
    for retry in range(max_retries):
        try:
            # Store current window handle
            main_window = driver.current_window_handle
            
            # Reset any stale tabs
            try:
                # Close any extra tabs except the main one
                if len(driver.window_handles) > 1:
                    for handle in driver.window_handles:
                        if handle != main_window:
                            driver.switch_to.window(handle)
                            driver.close()
                    driver.switch_to.window(main_window)
            except:
                # If there's an issue, just continue with main window
                driver.switch_to.window(main_window)
            
            # Open new tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            
            # Navigate to product URL with timeout
            driver.set_page_load_timeout(30)
            driver.get(url)
            time.sleep(3)  # Wait for initial page load
            
            # Extract product information
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                
                # Get product name
                try:
                    product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
                    details["name_verification"] = product_name
                except:
                    pass
                
                # Extract description - try multiple approaches
                try:
                    description_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Description']/following-sibling::p"
                    )
                    if description_elements:
                        details["description"] = description_elements[0].text.strip()
                except:
                    pass
                
                # If no description found yet, try alternative methods
                if details["description"] == "Description not available":
                    try:
                        description_elements = driver.find_elements(
                            By.CSS_SELECTOR, ".product-catalogue-training-calendar__row p"
                        )
                        if description_elements:
                            details["description"] = description_elements[0].text.strip()
                    except:
                        pass
                
                # Extract other fields using more robust selectors
                try:
                    # Try to find job levels
                    job_level_elements = driver.find_elements(
                        By.XPATH, "//h4[contains(text(), 'Job level')]/following-sibling::p"
                    )
                    if job_level_elements:
                        details["job_levels"] = job_level_elements[0].text.strip()
                        
                    # Try to find languages
                    language_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Languages']/following-sibling::p"
                    )
                    if language_elements:
                        details["languages"] = language_elements[0].text.strip()
                        
                    # Try to find assessment length
                    length_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Assessment length']/following-sibling::p"
                    )
                    if length_elements:
                        length_text = length_elements[0].text.strip()
                        details["assessment_length"] = length_text
                        
                        # Extract minutes from assessment length
                        minutes_match = re.search(r'(\d+)\s*minutes', length_text, re.IGNORECASE)
                        if minutes_match:
                            details["duration"] = f"{minutes_match.group(1)} minutes"
                except:
                    pass
                
                # Extract downloads
                try:
                    download_items = driver.find_elements(By.CSS_SELECTOR, "li.product-catalogue__download")
                    downloads = []
                    
                    for item in download_items:
                        try:
                            link_element = item.find_element(By.CSS_SELECTOR, ".product-catalogue__download-title a")
                            language_element = item.find_element(By.CSS_SELECTOR, ".product-catalogue__download-language")
                            
                            downloads.append({
                                "title": link_element.text.strip(),
                                "url": link_element.get_attribute("href"),
                                "language": language_element.text.strip()
                            })
                        except:
                            pass
                    
                    if downloads:
                        details["downloads"] = downloads
                except:
                    pass
                    
                # Successfully extracted info, break out of retry loop
                break
                
            except Exception as e:
                print(f"Error extracting details from {url}: {e}")
                if retry < max_retries - 1:
                    print(f"Retrying ({retry + 2}/{max_retries})...")
                    time.sleep(3)
                    
            finally:
                # Close tab and switch back
                try:
                    driver.close()
                    driver.switch_to.window(main_window)
                except:
                    # Make sure we go back to main window no matter what
                    for handle in driver.window_handles:
                        if handle == main_window:
                            driver.switch_to.window(main_window)
                            break
        
        except Exception as e:
            print(f"Error processing {url}: {e}")
            if retry < max_retries - 1:
                print(f"Retrying ({retry + 2}/{max_retries})...")
                time.sleep(3)
            
            # Make sure we're on the main window
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
    
    return details

def determine_page_url_pattern(driver, section_type):
    """Determine the URL pattern used for pagination for the specific section type"""
    try:
        # Find the pagination
        pagination = driver.find_element(By.CSS_SELECTOR, "ul.pagination")
        
        # Try to find links with type parameter
        links = pagination.find_elements(By.CSS_SELECTOR, "li.pagination__item:not(.-arrow) a")
        
        if links:
            # Get the first page URL
            href = links[0].get_attribute("href")
            if "type=2" in href:
                return "type=2"  # Pre-packaged Job Solutions
            elif "type=1" in href:
                return "type=1"  # Individual Test Solutions
    except:
        pass
    
    # Default patterns based on section type
    return "type=2" if section_type == "Pre-packaged Job Solutions" else "type=1"

def extract_test_type_legend(driver):
    """Extract the legend/key meanings for test types."""
    test_types = {}
    try:
        # Find the tooltip that explains test type codes
        tooltip = driver.find_element(By.ID, "productCatalogueTooltip")
        items = tooltip.find_elements(By.CSS_SELECTOR, "li.custom__tooltip-item")
        
        for item in items:
            key = item.find_element(By.CSS_SELECTOR, "span.product-catalogue__key").text.strip()
            value = item.text.replace(key, "").strip()
            test_types[key] = value
    except Exception as e:
        print(f"Error extracting test type legend: {e}")
        # Default values if extraction fails
        test_types = {
            "A": "Ability & Aptitude",
            "B": "Biodata & Situational Judgement",
            "C": "Competencies",
            "D": "Development & 360",
            "E": "Assessment Exercises",
            "K": "Knowledge & Skills",
            "P": "Personality & Behavior",
            "S": "Simulations"
        }
    
    return test_types

def scrape_product_details_batch(urls, output_path=None, max_retries=3):
    """
    Batch scrape details for multiple product URLs and update the raw data file.
    
    Args:
        urls: List of product URLs to scrape
        output_path: Path to save updated data (defaults to raw_data_path)
        max_retries: Maximum number of retries for failed scrapes
    """
    print(f"Batch scraping details for {len(urls)} products...")
    
    # Load existing data if available
    try:
        raw_data_path = os.path.join(RAW_DATA_DIR, "shl_catalog_raw.json")
        with open(raw_data_path, 'r') as f:
            all_products = json.load(f)
    except:
        all_products = []
    
    # Create URL to product index mapping
    url_to_product = {product['url']: i for i, product in enumerate(all_products)}
    
    # Set up WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)  # Set page load timeout
    
    # Process each URL
    for url in tqdm(urls, desc="Extracting product details"):
        retries = 0
        success = False
        
        while not success and retries < max_retries:
            try:
                details = extract_product_details(driver, url)
                
                # Update product if it exists
                if url in url_to_product:
                    index = url_to_product[url]
                    all_products[index].update(details)
                    success = True
                else:
                    print(f"Warning: URL {url} not found in existing data")
                    break
                    
            except Exception as e:
                print(f"Error processing {url}: {e}")
                retries += 1
                time.sleep(2)  # Wait before retry
    
    driver.quit()
    
    # Save updated data
    output_path = output_path or raw_data_path
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_products, f, indent=2)
    
    print(f"Updated data saved to {output_path}")
    return all_products

# Helper function to update only Pre-packaged Job Solutions
def update_prepackaged_solutions_details():
    """
    Updates details for all Pre-packaged Job Solutions by fetching from detail pages.
    """
    # Load existing data
    raw_data_path = os.path.join(RAW_DATA_DIR, "shl_catalog_raw.json")
    with open(raw_data_path, 'r') as f:
        all_products = json.load(f)
    
    # Filter for Pre-packaged Job Solutions
    prepackaged_products = [p for p in all_products if p['solution_type'] == 'Pre-packaged Job Solutions']
    urls = [p['url'] for p in prepackaged_products]
    
    # Start batch scraping
    return scrape_product_details_batch(urls)

def create_mock_data():
    """Create mock assessment data for development."""
    mock_assessments = [
        {
            "name": "Claims/Operations Supervisor Solution",
            "url": "https://www.shl.com/solutions/products/product-catalog/view/claimsoperations-supervisor-solution/",
            "remote_testing": "Yes",
            "adaptive_irt": "Yes",
            "test_types": "P, S, A, B",
            "test_types_expanded": "P: Personality & Behavior; S: Simulations; A: Ability & Aptitude; B: Biodata & Situational Judgement",
            "solution_type": "Pre-packaged Job Solutions",
            "description": "The Claims/Operations Supervisor solution is for entry-level management positions that involve supervising hourly employees. Sample tasks for this job include, but are not limited to: planning and preapring work schedules; assigning employees to specific dutites; coaching employees on attendance, conduct, schedule adherence, and work tasks; developing employees' skills; training subordinates; prioritizing multiple tasks and priorities; making day-to-day decisions with minimal guidance from others.",
            "duration": "48 minutes",
            "assessment_length": "Approximate Completion Time in minutes = 48",
            "languages": "English (USA)",
            "job_levels": "Manager",
            "downloads": [
                {
                    "title": "Product fact sheet",
                    "url": "https://service.shl.com/docs/Fact Sheet_ Claims Operations Supervisor One Sitting_USE.pdf",
                    "language": "English (USA)"
                }
            ]
        }
    ]
    
    df = pd.DataFrame(mock_assessments)
    processed_data_path = os.path.join(PROCESSED_DATA_DIR, "shl_assessments.csv")
    os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
    df.to_csv(processed_data_path, index=False)
    return df

if __name__ == "__main__":
    import argparse
    
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description='Scrape the SHL product catalog')
    parser.add_argument('--max-pages', type=int, default=None, 
                      help='Maximum number of pages to scrape (default: all)')
    parser.add_argument('--section', type=str, default="Pre-packaged Job Solutions",
                      choices=["Pre-packaged Job Solutions", "Individual Test Solutions"],
                      help='Section type to scrape')
    parser.add_argument('--skip-descriptions', action='store_true',
                      help='Skip fetching detailed descriptions (faster)')
    
    args = parser.parse_args()
    
    # Run the scraper with the specified options
    scrape_shl_catalog(
        get_descriptions=not args.skip_descriptions,
        section_type=args.section,
        max_pages=args.max_pages
    )
