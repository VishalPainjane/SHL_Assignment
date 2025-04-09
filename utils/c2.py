# """Web scraper for the SHL Individual Test Solutions Product Catalog."""
# import os
# import json
# import time
# import re
# from tqdm import tqdm
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# # Add project root to path - similar to existing crawler
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# # Base URL for the catalog
# BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
# INITIAL_URL = "https://www.shl.com/solutions/products/product-catalog/?start=12&type=1&type=1"
# TOTAL_PAGES = 32

# def setup_driver(headless=True):
#     """Set up and return a configured Chrome WebDriver."""
#     chrome_options = Options()
#     # if headless:
#         # chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920,1080")
    
#     driver = webdriver.Chrome(options=chrome_options)
#     driver.set_page_load_timeout(60)  # Increase timeout for page loads
#     return driver

# def extract_test_type_legend(driver):
#     """Extract the legend/key meanings for test types like K, P, etc."""
#     test_types = {}
#     try:
#         # Find the tooltip that explains test type codes
#         tooltip = driver.find_element(By.ID, "productCatalogueTooltip")
#         items = tooltip.find_elements(By.CSS_SELECTOR, "li.custom__tooltip-item")
        
#         for item in items:
#             key = item.find_element(By.CSS_SELECTOR, "span.product-catalogue__key").text.strip()
#             value = item.text.replace(key, "").strip()
#             test_types[key] = value
#     except Exception as e:
#         print(f"Error extracting test type legend: {e}")
#         # Default values if extraction fails
#         test_types = {
#             "A": "Ability & Aptitude",
#             "B": "Biodata & Situational Judgement",
#             "C": "Competencies",
#             "D": "Development & 360",
#             "E": "Assessment Exercises",
#             "K": "Knowledge & Skills",
#             "P": "Personality & Behavior",
#             "S": "Simulations"
#         }
    
#     return test_types

# def extract_products_from_table(driver, test_type_legend):
#     """Extract all products from the current catalog page table."""
#     products = []
    
#     try:
#         # Wait for table to load
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.TAG_NAME, "table"))
#         )
        
#         # Get the table
#         table = driver.find_element(By.TAG_NAME, "table")
        
#         # Get all rows except the header
#         rows = table.find_elements(By.CSS_SELECTOR, "tr:not(:first-child)")
        
#         if not rows:
#             print("No product rows found in table")
#             return products
            
#         for row in rows:
#             try:
#                 cells = row.find_elements(By.TAG_NAME, "td")
#                 if len(cells) < 4:
#                     continue
                
#                 # Extract basic product data
#                 title_cell = cells[0]
#                 title_link = title_cell.find_element(By.TAG_NAME, "a")
#                 name = title_link.text.strip()
#                 url = title_link.get_attribute("href")
                
#                 # Check for Remote Testing
#                 remote_cell = cells[1]
#                 remote_testing = "Yes" if remote_cell.find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
                
#                 # Check for Adaptive/IRT
#                 adaptive_cell = cells[2]
#                 adaptive_irt = "Yes" if adaptive_cell.find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
                
#                 # Extract test types
#                 test_types_cell = cells[3]
#                 test_type_elements = test_types_cell.find_elements(By.CSS_SELECTOR, "span.product-catalogue__key")
#                 test_types = [elem.text for elem in test_type_elements]
                
#                 # Create product dictionary with basic information
#                 product = {
#                     "name": name,
#                     "url": url,
#                     "remote_testing": remote_testing,
#                     "adaptive_irt": adaptive_irt,
#                     "test_types": ", ".join(test_types),
#                     "solution_type": "Individual Test Solutions",
#                 }
                
#                 # Add expanded test type descriptions
#                 test_types_expanded = []
#                 for tt in test_types:
#                     if tt in test_type_legend:
#                         test_types_expanded.append(f"{tt}: {test_type_legend[tt]}")
#                 product["test_types_expanded"] = "; ".join(test_types_expanded)
                
#                 products.append(product)
#             except Exception as e:
#                 print(f"Error processing row: {e}")
    
#     except Exception as e:
#         print(f"Error extracting products from table: {e}")
    
#     return products

# def extract_product_details(driver, url):
#     """
#     Visit the product detail page and extract comprehensive information.
#     Returns a dictionary with product details.
#     """
#     details = {
#         "description": "Description not available",
#         "duration": "Not specified",
#         "languages": "Not specified",
#         "job_levels": "Not specified",
#         "assessment_length": "Not specified",
#         "downloads": []
#     }
    
#     max_retries = 3
#     for retry in range(max_retries):
#         try:
#             # Store current window handle
#             main_window = driver.current_window_handle
            
#             # Reset any stale tabs
#             try:
#                 # Close any extra tabs except the main one
#                 if len(driver.window_handles) > 1:
#                     for handle in driver.window_handles:
#                         if handle != main_window:
#                             driver.switch_to.window(handle)
#                             driver.close()
#                     driver.switch_to.window(main_window)
#             except:
#                 # If there's an issue, just continue with main window
#                 driver.switch_to.window(main_window)
            
#             # Open new tab
#             driver.execute_script("window.open('');")
#             driver.switch_to.window(driver.window_handles[1])
            
#             # Navigate to product URL with timeout
#             driver.set_page_load_timeout(30)
#             driver.get(url)
#             time.sleep(3)  # Wait for page load
            
#             # Extract product information
#             try:
#                 WebDriverWait(driver, 15).until(
#                     EC.presence_of_element_located((By.TAG_NAME, "h1"))
#                 )
                
#                 # Get product name
#                 try:
#                     product_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
#                     details["name_verification"] = product_name
#                 except:
#                     pass
                
#                 # Extract description
#                 try:
#                     description_elements = driver.find_elements(
#                         By.XPATH, "//h4[text()='Description']/following-sibling::p"
#                     )
#                     if description_elements:
#                         details["description"] = description_elements[0].text.strip()
#                 except:
#                     pass
                
#                 # Try alternative description method if needed
#                 if details["description"] == "Description not available":
#                     try:
#                         description_elements = driver.find_elements(
#                             By.CSS_SELECTOR, ".product-catalogue-training-calendar__row p"
#                         )
#                         if description_elements:
#                             details["description"] = description_elements[0].text.strip()
#                     except:
#                         pass
                
#                 # Extract job levels
#                 try:
#                     job_level_elements = driver.find_elements(
#                         By.XPATH, "//h4[text()='Job levels']/following-sibling::p"
#                     )
#                     if job_level_elements:
#                         details["job_levels"] = job_level_elements[0].text.strip()
#                 except:
#                     pass
                
#                 # Extract languages
#                 try:
#                     language_elements = driver.find_elements(
#                         By.XPATH, "//h4[text()='Languages']/following-sibling::p"
#                     )
#                     if language_elements:
#                         details["languages"] = language_elements[0].text.strip()
#                 except:
#                     pass
                
#                 # Extract assessment length
#                 try:
#                     length_elements = driver.find_elements(
#                         By.XPATH, "//h4[text()='Assessment length']/following-sibling::p"
#                     )
#                     if length_elements:
#                         length_text = length_elements[0].text.strip()
#                         details["assessment_length"] = length_text
                        
#                         # Extract minutes from assessment length for duration
#                         minutes_match = re.search(r'(\d+)\s*minutes', length_text, re.IGNORECASE)
#                         if not minutes_match:
#                             minutes_match = re.search(r'=\s*(\d+)', length_text)
                        
#                         if minutes_match:
#                             details["duration"] = f"{minutes_match.group(1)} minutes"
#                 except:
#                     pass
                
#                 # Extract downloads
#                 try:
#                     download_items = driver.find_elements(By.CSS_SELECTOR, "li.product-catalogue__download")
#                     downloads = []
                    
#                     for item in download_items:
#                         try:
#                             link_element = item.find_element(By.CSS_SELECTOR, ".product-catalogue__download-title a")
#                             language_element = item.find_element(By.CSS_SELECTOR, ".product-catalogue__download-language")
                            
#                             downloads.append({
#                                 "title": link_element.text.strip(),
#                                 "url": link_element.get_attribute("href"),
#                                 "language": language_element.text.strip()
#                             })
#                         except:
#                             pass
                    
#                     if downloads:
#                         details["downloads"] = downloads
#                 except:
#                     pass
                
#                 # Successfully extracted info, break out of retry loop
#                 break
                
#             except Exception as e:
#                 print(f"Error extracting details from {url}: {e}")
#                 if retry < max_retries - 1:
#                     print(f"Retrying ({retry + 2}/{max_retries})...")
#                     time.sleep(3)
                    
#             finally:
#                 # Close tab and switch back
#                 try:
#                     driver.close()
#                     driver.switch_to.window(main_window)
#                 except:
#                     # Make sure we go back to main window no matter what
#                     for handle in driver.window_handles:
#                         if handle == main_window:
#                             driver.switch_to.window(main_window)
#                             break
        
#         except Exception as e:
#             print(f"Error processing {url}: {e}")
#             if retry < max_retries - 1:
#                 print(f"Retrying ({retry + 2}/{max_retries})...")
#                 time.sleep(3)
            
#             # Make sure we're on the main window
#             try:
#                 driver.switch_to.window(driver.window_handles[0])
#             except:
#                 pass
    
#     return details

# def get_next_page_url(driver):
#     """Find and return the URL for the next page."""
#     try:
#         next_button = driver.find_element(By.CSS_SELECTOR, "li.pagination__item.-arrow.-next:not(.-disabled) a")
#         return next_button.get_attribute("href")
#     except (NoSuchElementException, TimeoutException):
#         return None

# def scrape_shl_test_solutions(start_page=2, end_page=32):
#     """
#     Main function to scrape all Individual Test Solutions from the catalog.
    
#     Args:
#         start_page: Page number to start scraping from (2-32)
#         end_page: Last page number to scrape (max 32)
    
#     Returns:
#         List of all products scraped
#     """
#     print(f"Starting Individual Test Solutions scraper from page {start_page} to {end_page}...")
    
#     # Setup output directories
#     os.makedirs(RAW_DATA_DIR, exist_ok=True)
#     os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
#     # Initialize driver
#     driver = setup_driver(headless=False)  # Set to False for debugging
    
#     # Calculate start URL based on page number
#     if start_page == 1:
#         current_url = f"{BASE_URL}?start=0&type=1&type=1"
#     else:
#         # Page 2 starts at 12, Page 3 at 24, etc.
#         start_index = (start_page - 1) * 12
#         current_url = f"{BASE_URL}?start={start_index}&type=1&type=1"
    
#     all_products = []
#     current_page = start_page
    
#     try:
#         # Navigate to starting page
#         driver.get(current_url)
#         time.sleep(5)  # Wait for page to load
        
#         # Extract test type legend once
#         test_type_legend = extract_test_type_legend(driver)
#         print(f"Extracted test type legend: {test_type_legend}")
        
#         # Process all pages
#         while current_page <= end_page:
#             print(f"Processing page {current_page} of {end_page}")
            
#             # Extract products from current page
#             products = extract_products_from_table(driver, test_type_legend)
#             print(f"Found {len(products)} products on page {current_page}")
            
#             # Get details for each product
#             for product in tqdm(products, desc=f"Extracting details from page {current_page}"):
#                 try:
#                     details = extract_product_details(driver, product["url"])
#                     product.update(details)
#                     all_products.append(product)
                    
#                     # Save intermediate results after each product
#                     if len(all_products) % 5 == 0:
#                         with open(os.path.join(RAW_DATA_DIR, "test_solutions_intermediate.json"), 'w') as f:
#                             json.dump(all_products, f, indent=2)
                
#                 except Exception as e:
#                     print(f"Error processing product {product.get('name', 'unknown')}: {e}")
            
#             # Check if we should continue to next page
#             if current_page >= end_page:
#                 break
                
#             # Get next page URL
#             next_url = get_next_page_url(driver)
#             if not next_url:
#                 print("No next page found, ending scrape")
#                 break
                
#             # Navigate to next page
#             print(f"Navigating to next page: {next_url}")
#             driver.get(next_url)
#             time.sleep(5)  # Wait for page to load
            
#             current_page += 1
        
#         print(f"Scraping complete! Extracted {len(all_products)} products")
        
#         # Save final results
#         raw_data_path = os.path.join(RAW_DATA_DIR, "test_solutions_raw.json")
#         with open(raw_data_path, 'w') as f:
#             json.dump(all_products, f, indent=2)
        
#         # Create DataFrame and save CSV
#         df = pd.DataFrame(all_products)
#         csv_path = os.path.join(PROCESSED_DATA_DIR, "shl_test_solutions.csv")
#         df.to_csv(csv_path, index=False)
#         print(f"Data saved to {csv_path}")
        
#         return all_products
        
#     except Exception as e:
#         print(f"Error during scraping: {e}")
        
#         # Save whatever we collected so far
#         if all_products:
#             raw_data_path = os.path.join(RAW_DATA_DIR, "test_solutions_raw_partial.json")
#             with open(raw_data_path, 'w') as f:
#                 json.dump(all_products, f, indent=2)
#             print(f"Partial data saved to {raw_data_path}")
        
#         return all_products
    
#     finally:
#         # Clean up
#         driver.quit()

# def create_mock_data():
#     """Create a small sample of mock data for testing"""
#     mock_test_solutions = [
#         {
#             "name": "Adobe Experience Manager (New)",
#             "url": "https://www.shl.com/solutions/products/product-catalog/view/adobe-experience-manager-new/",
#             "remote_testing": "Yes",
#             "adaptive_irt": "No",
#             "test_types": "K",
#             "test_types_expanded": "K: Knowledge & Skills",
#             "solution_type": "Individual Test Solutions",
#             "description": "Multi-choice test that measures the knowledge of AEM components, templates, workflows, AEM collections, OSGi services and troubleshooting of AEM projects.",
#             "duration": "17 minutes",
#             "assessment_length": "Approximate Completion Time in minutes = 17",
#             "languages": "English (USA)",
#             "job_levels": "Mid-Professional, Professional Individual Contributor",
#             "downloads": [
#                 {
#                     "title": "Product Fact Sheet",
#                     "url": "https://service.shl.com/docs/Adobe Experience Manager (New).pdf",
#                     "language": "English (USA)"
#                 }
#             ]
#         }
#     ]
    
#     # Save to test files
#     os.makedirs(RAW_DATA_DIR, exist_ok=True)
#     os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
#     with open(os.path.join(RAW_DATA_DIR, "test_solutions_mock.json"), 'w') as f:
#         json.dump(mock_test_solutions, f, indent=2)
    
#     df = pd.DataFrame(mock_test_solutions)
#     df.to_csv(os.path.join(PROCESSED_DATA_DIR, "shl_test_solutions_mock.csv"), index=False)
    
#     return mock_test_solutions

# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Scrape SHL Individual Test Solutions Catalog")
#     parser.add_argument("--start", type=int, default=2, help="Starting page number (1-32)")
#     parser.add_argument("--end", type=int, default=32, help="Ending page number (1-32)")
#     parser.add_argument("--mock", action="store_true", help="Create mock data instead of scraping")
    
#     args = parser.parse_args()
    
#     if args.mock:
#         create_mock_data()
#     else:
#         scrape_shl_test_solutions(start_page=args.start, end_page=args.end)


















"""Resume scraping the SHL Individual Test Solutions Catalog from page 12."""
import os
import json
import time
import re
from tqdm import tqdm
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add project root to path - similar to existing crawler
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Base URL and continuation URL
BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
RESUME_URL = "https://www.shl.com/solutions/products/product-catalog/?start=132&type=1&type=1"
TOTAL_PAGES = 32

def setup_driver(headless=True):
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)  # Increase timeout for page loads
    return driver

def extract_test_type_legend(driver):
    """Extract the legend/key meanings for test types like K, P, etc."""
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

def extract_products_from_table(driver, test_type_legend):
    """Extract all products from the current catalog page table."""
    products = []
    
    try:
        # Wait for table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Get the table
        table = driver.find_element(By.TAG_NAME, "table")
        
        # Get all rows except the header
        rows = table.find_elements(By.CSS_SELECTOR, "tr:not(:first-child)")
        
        if not rows:
            print("No product rows found in table")
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
                    "solution_type": "Individual Test Solutions",
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
            time.sleep(3)  # Wait for page load
            
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
                
                # Extract description
                try:
                    description_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Description']/following-sibling::p"
                    )
                    if description_elements:
                        details["description"] = description_elements[0].text.strip()
                except:
                    pass
                
                # Try alternative description method if needed
                if details["description"] == "Description not available":
                    try:
                        description_elements = driver.find_elements(
                            By.CSS_SELECTOR, ".product-catalogue-training-calendar__row p"
                        )
                        if description_elements:
                            details["description"] = description_elements[0].text.strip()
                    except:
                        pass
                
                # Extract job levels
                try:
                    job_level_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Job levels']/following-sibling::p"
                    )
                    if job_level_elements:
                        details["job_levels"] = job_level_elements[0].text.strip()
                except:
                    pass
                
                # Extract languages
                try:
                    language_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Languages']/following-sibling::p"
                    )
                    if language_elements:
                        details["languages"] = language_elements[0].text.strip()
                except:
                    pass
                
                # Extract assessment length
                try:
                    length_elements = driver.find_elements(
                        By.XPATH, "//h4[text()='Assessment length']/following-sibling::p"
                    )
                    if length_elements:
                        length_text = length_elements[0].text.strip()
                        details["assessment_length"] = length_text
                        
                        # Extract minutes from assessment length for duration
                        minutes_match = re.search(r'(\d+)\s*minutes', length_text, re.IGNORECASE)
                        if not minutes_match:
                            minutes_match = re.search(r'=\s*(\d+)', length_text)
                        
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

def get_next_page_url(driver):
    """Find and return the URL for the next page."""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.pagination__item.-arrow.-next:not(.-disabled) a")
        return next_button.get_attribute("href")
    except (NoSuchElementException, TimeoutException):
        return None

def load_existing_data():
    """Load existing data from the partial JSON file."""
    try:
        partial_data_path = os.path.join(RAW_DATA_DIR, "test_solutions_raw_partial.json")
        with open(partial_data_path, 'r') as f:
            existing_data = json.load(f)
        print(f"Loaded {len(existing_data)} existing entries from partial data file")
        return existing_data
    except Exception as e:
        print(f"Error loading existing data: {e}")
        return []

def resume_scrape_from_page12(end_page=32):
    """
    Resume scraping from page 12 and continue with the existing data file.
    
    Args:
        end_page: Last page number to scrape (max 32)
    
    Returns:
        Combined list of existing and newly scraped products
    """
    print("Resuming Individual Test Solutions scraper from page 12...")
    
    # Load existing data
    existing_data = load_existing_data()
    
    # Setup output directories
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Initialize driver
    driver = setup_driver(headless=False)  # Set to False for debugging
    
    # Start from the resume URL
    current_url = RESUME_URL
    
    all_products = existing_data.copy()
    current_page = 12
    
    try:
        # Navigate to starting page
        driver.get(current_url)
        time.sleep(5)  # Wait for page to load
        
        # Extract test type legend once
        test_type_legend = extract_test_type_legend(driver)
        print(f"Extracted test type legend: {test_type_legend}")
        
        # Process remaining pages
        while current_page <= end_page:
            print(f"Processing page {current_page} of {end_page}")
            
            # Extract products from current page
            products = extract_products_from_table(driver, test_type_legend)
            print(f"Found {len(products)} products on page {current_page}")
            
            # Get details for each product
            for product in tqdm(products, desc=f"Extracting details from page {current_page}"):
                try:
                    details = extract_product_details(driver, product["url"])
                    product.update(details)
                    all_products.append(product)
                    
                    # Save intermediate results after each product
                    if len(all_products) % 5 == 0:
                        with open(os.path.join(RAW_DATA_DIR, "test_solutions_raw_partial.json"), 'w') as f:
                            json.dump(all_products, f, indent=2)
                        print(f"Saved progress: {len(all_products)} total products")
                
                except Exception as e:
                    print(f"Error processing product {product.get('name', 'unknown')}: {e}")
            
            # Check if we should continue to next page
            if current_page >= end_page:
                break
                
            # Get next page URL
            next_url = get_next_page_url(driver)
            if not next_url:
                print("No next page found, ending scrape")
                break
                
            # Navigate to next page
            print(f"Navigating to next page: {next_url}")
            driver.get(next_url)
            time.sleep(5)  # Wait for page to load
            
            current_page += 1
        
        print(f"Scraping complete! Total products: {len(all_products)}")
        
        # Save final results to both partial and complete files
        partial_data_path = os.path.join(RAW_DATA_DIR, "test_solutions_raw_partial.json")
        with open(partial_data_path, 'w') as f:
            json.dump(all_products, f, indent=2)
            
        complete_data_path = os.path.join(RAW_DATA_DIR, "test_solutions_raw_complete.json")
        with open(complete_data_path, 'w') as f:
            json.dump(all_products, f, indent=2)
        
        # Create DataFrame and save CSV
        df = pd.DataFrame(all_products)
        csv_path = os.path.join(PROCESSED_DATA_DIR, "shl_test_solutions.csv")
        df.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")
        
        return all_products
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        
        # Save whatever we collected so far
        if all_products:
            partial_data_path = os.path.join(RAW_DATA_DIR, "test_solutions_raw_partial.json")
            with open(partial_data_path, 'w') as f:
                json.dump(all_products, f, indent=2)
            print(f"Partial data saved to {partial_data_path}")
        
        return all_products
    
    finally:
        # Clean up
        driver.quit()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Resume scraping SHL Individual Test Solutions Catalog from page 12")
    parser.add_argument("--end", type=int, default=32, help="Ending page number (12-32)")
    
    args = parser.parse_args()
    
    resume_scrape_from_page12(end_page=args.end)