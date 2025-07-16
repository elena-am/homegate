# Goal: Create a program that gets the latest flat rental postings that fit your criteria, and store important data in a database for future analytics (study price fluctuations for example).
# 
# Involves: Web scraping, data cleaning with Python, visualization, API
# 
# Description: The idea is to write a program with the following functionalities:
# - Get data from homegate.ch on the flat/house rental for the criteria of your interest
# - Store the raw data
# - Clean up the data and filter it according to keywords (for example 'view', 'bright', ' Attika',....)
# - Perform some analytics (average price for example)
# - Visualize the results (histogram of rent prices for example) 
# 
# 
# Possible extensions:
# - Setup an automatic reporting system, where you just need to run one script to get a full pdf report on new listings available for your criteria 
# - Get acquainted with nltk, a natural language processing software and basic word analysis 
# - Connect to gmaps API and implement a distance filter from a specific address
# - Extend to other websites.
# 
# Work Packages:
# 
# - Explore homegate.ch, make a list of data to extract and then write the notebook to extract them. Save the data as a csv file
# - Write the notebook to clean the data, filter by keyword and analyze and plot the data 
# - Write the notebook to connect to the gmaps API and filter by distance
 
import time
import re
import numpy as np
import pandas as pd
import traceback  # For detailed exception logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# I was having issues because ChromeDriverManager().install() matches the version of the Chrome browser installed on the system and 
# it was too old, so I had to update the version on the system manually.
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--no-sandbox")  # Disable sandboxing
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1500,1080")
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
options.add_argument("--remote-debugging-port=9222")  # Debugging port
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
print(time.ctime())
# stablishing the connection with HOMEGATE
driver.get("https://www.homegate.ch/mieten/immobilien/ort-zuerich/trefferliste")
print(driver.title)

# ## Defining function to get the elements from the website

def listing_ID():
    try:
        listing_ID = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dl.ListingTechReferences_techReferencesList_jlZwL"))
            )
        id_raw= listing_ID.text
        id_flat = re.split('[\n]', id_raw)[1]
        return id_flat
    except:
        print(f'No id_flat value for {url}')
        return None

def object_ref():
    try:
        object_ref = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dl.ListingTechReferences_techReferencesList_jlZwL"))
            )
        ref_raw= object_ref.text
        ref_flat = re.split('[\n]', ref_raw)[3]
        return ref_flat
    except:
        print(f'No object_ref value for {url}')
        return None 

        
def flat_address():
    try:
        address_find = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "address.AddressDetails_address_i3koO"))
                    )
        address = address_find.text
        return address
    except:
        print(f'None address value for {url}')
        return None

def postcode():
    try:
        postcode_find = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//address[contains(@class, 'AddressDetails_address')]//span[2]"))
        )
        postcode_text = postcode_find.text.split()[0]  
        return postcode_text
    except:
        print(f'No postcode value for {url}')
        return None

def net_rent_price():
    try:
        # Find the element containing the net_rent
        net_rent_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-test='costs']//dl//dt/following-sibling::dd/span[contains(., 'CHF')]"))
            )
        if len(net_rent_elements) > 1:
            net_rent_price = net_rent_elements[0].text 
        else:
            net_rent_price = None  # Handle cases where there is only one element

        return net_rent_price
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        print(f'No net price value for {url}')
        return None

def expenses_price():
    try:
        # Find the element containing the expenses
        expenses_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located ((By.XPATH, "//div[@data-test='costs']//dl//dt/following-sibling::dd/span[contains(., 'CHF')]"))
            )
        if len(expenses_elements) > 1:
            expenses_price = expenses_elements[1].text
        else:
            expenses_price = None

        return expenses_price
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        print(f'No expenses value for {url}')
        return None

def rent_price():
    try:
        # Find the element containing the rent
        rent_element = driver.find_element(By.XPATH, "//div[@data-test='costs']//dl//dd[strong]//span[contains(., 'CHF')]")
        rent_price = rent_element.text
        return rent_price
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        print(f'No rent price value for {url}')
        return None

def flat_availability():
    try:
        if 'Available from:' in main_info_dict:
            return main_info_dict.get('Available from:')
        else:
            raise Exception('error')
    except:
        return None
    
def flat_type():
    try:
        if 'Type:' in main_info_dict:
            return main_info_dict.get('Type:')
        else:
            raise Exception('error')
    except:
        return None

def flat_n_rooms():
    try:
        if 'No. of rooms:' in main_info_dict:
            return main_info_dict.get('No. of rooms:')
        else:
            raise Exception('error')        
    except:
        return None

def flat_floor():
    try:
        if 'Floor:' in main_info_dict:
            return main_info_dict.get('Floor:')
        else:
            raise Exception('error')        
    except:
        return None
    
def flat_n_floors():
    try:
        if 'Number of floors:' in main_info_dict:
            return main_info_dict.get('Number of floors:')
        else:
            raise Exception('error')        
    except:
        return None
    
def flat_surface():
    try:
        if 'Surface living:' in main_info_dict:
            return main_info_dict.get('Surface living:')
        else:
            raise Exception('error')        
    except:
        return None
    
def flat_floor_space():
    try:
        if 'Floor space:' in main_info_dict:
            return main_info_dict.get('Floor space:')
        else:
            raise Exception('error')        
    except:
        return None
    
def flat_Room_height():
    try:
        if 'Room height:' in main_info_dict:
            return main_info_dict.get('Room height:')
        else:
            raise Exception('error')        
    except:
        return None

def flat_last_refurbishment():
    try:
        if 'Last refurbishment:' in main_info_dict:
            return main_info_dict.get('Last refurbishment:')
        else:
            raise Exception('error')        
    except:
        return None
    
def flat_year():
    try:
        if 'Year built:' in main_info_dict:
            return main_info_dict.get('Year built:')
        else:
            raise Exception('error')        
    except:
        return None
    
    
def flat_features():
    try:
        features_find = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.FeaturesFurnishings_list_S54KV"))
        )
        features_raw = features_find.text
        features = (re.split('[\n]', features_raw))
        features = [element.lower() for element in features]
        return features
    except:
        return None


flats_lst = []
more_pages = True
current_page = 1

# testing new atributes:
# url='https://www.homegate.ch/mieten/4001662556'

# print(driver.page_source)
# 
# while more_pages:
#     try:
#         driver.get(url)
#         # Step 1: Handle the cookie consent or blocking element
#         try:
#             cookie_button = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
#             )
#             cookie_button.click()
#             print("Cookie consent accepted.")
#         except TimeoutException:
#             print(f"Cookie consent button not found on {url}. Proceeding without interaction.")
#         except Exception as cookie_exception:
#             print(f"Cookie consent issue on {url}: {cookie_exception}")
#             with open("page_source_error.html", "w") as f:
#                 f.write(driver.page_source)
#             traceback.print_exc()  # Log full stack trace for debugging
#             continue  # Skip to the next URL
        
#         # Step 2: Handle the language switcher
#         # try:
#         #     # Wait for the language switcher to be present
#         #     language_switcher = WebDriverWait(driver, 10).until(
#         #         EC.element_to_be_clickable((By.XPATH, '//button[@aria-controls="header-language-switch"]'))
#         #     )

#         #     # Click the language switcher to change the language
#         #     language_switcher.click()
#         #     # Wait for the dropdown to appear
#         #     english_option = WebDriverWait(driver, 10).until(
#         #         EC.element_to_be_clickable((By.XPATH, '//a[@class="HgLanguageSwitch_link_GCiHc" and normalize-space(text())="EN"]'))
#         #     )

#         #     # Click the English option
#         #     english_option.click()
#         # except Exception as language_exception:
#         #     print(f"Language switch issue on {url}: {language_exception}")
#         #     traceback.print_exc()
#         #     #continue  # Skip to the next URL
#         try: 
#             print('Trying to get the next page')
#             next_page_url = f"https://www.homegate.ch/rent/real-estate/city-zurich/matching-list?ep={current_page + 1}"
#             driver.get(next_page_url)
#             current_page += 1  # Increment manually
#             time.sleep(2)  # Wait for the page to load
#             print("Navigated to the next page.")
#         except Exception as e:
#             print(f"Could not navigate to the next page: {e}")   
#         if not next_page_buttons:
#             more_pages = False
#             print("No more pages to navigate.")
#         else:
#             print('Trying to click the next page button')
            
#     except Exception as e:
#             print(f"Error scraping {url}: {e}")
#             continue  # Skip to next listing

#     df = pd.DataFrame(flats_lst)
#     df.to_csv('flats.csv', index=False)
#     driver.close()  # Close the tab
#     driver.switch_to.window(driver.window_handles[0])  # Switch back to main page
#     time.sleep(1)  # Allow time for focus switch

while more_pages:

    # get all the elements containing the flats
    entire_page = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@data-test="result-list-item"]'))
                )
    # get all the urls from the current page
    urls = [
    item.find_element(By.XPATH, './/a[@href]').get_attribute("href")  # Use relative XPath
    for item in entire_page
    ]
    # # get the entire_page url
    # entire_page_url = driver.current_url
       
    for url in urls:
        try:
            # driver.get(url)
            driver.execute_script(f"window.open('{url}');")  # Open in new tab
            driver.switch_to.window(driver.window_handles[1])  # Switch to new tab

            # Step 1: Handle the cookie consent or blocking element
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
                )
                cookie_button.click()
                print("Cookie consent accepted.")
            except TimeoutException:
                print(f"Cookie consent button not found on {url}. Proceeding without interaction.")
            except Exception as cookie_exception:
                print(f"Cookie consent issue on {url}: {cookie_exception}")
                with open("page_source_error.html", "w") as f:
                    f.write(driver.page_source)
                traceback.print_exc()  # Log full stack trace for debugging
                continue  # Skip to the next URL
            
            # Step 2: Handle the language switcher
            try:
                # Wait for the language switcher to be present
                language_switcher = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-controls="header-language-switch"]'))
                )

                # Click the language switcher to change the language
                language_switcher.click()
                # Wait for the dropdown to appear
                english_option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//a[@class="HgLanguageSwitch_link_GCiHc" and normalize-space(text())="EN"]'))
                )

                # Click the English option
                english_option.click()
            except Exception as language_exception:
                print(f"Language switch issue on {url}: {language_exception}")
                traceback.print_exc()
                #continue  # Skip to the next URL

            # Creating a dictionary with the 'Main Information'
            key_type_find = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="CoreAttributes_coreAttributes_e2NAm"]/dl/dt'))
            )
            key_type = []
            for type in key_type_find:
                key_type.append(type.text)

            value_type_find = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, '//div[@class="CoreAttributes_coreAttributes_e2NAm"]/dl/dd'))
                        )
            value_type = []
            for type in value_type_find:
                value_type.append(type.text)
            main_info_dict = dict(zip(key_type, value_type))

            # Creating a dictionary with the 'entire_page Information'
            flats_dict = {'listing_ID': listing_ID(),
                            'object_ref': object_ref(),
                            'address': flat_address(),
                            'postcode': postcode(),
                            'net_rent': net_rent_price(),
                            'expenses': expenses_price(),
                            'rent': rent_price(),
                            'availability': flat_availability(), 
                            'type': flat_type(), 
                            'n_of_rooms': flat_n_rooms(),
                            'floor': flat_floor(),
                            'n_of_floors': flat_n_floors(),
                            'surface_living': flat_surface(),
                            'floor_space': flat_floor_space(),
                            'room_height': flat_Room_height(),
                            'last_refurbishment': flat_last_refurbishment(),
                            'year_built': flat_year(),
                            'link': driver.current_url,
                            'features': flat_features(),
                        }
            flats_lst.append(flats_dict)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            continue  # Skip to next listing
        
        df = pd.DataFrame(flats_lst)
        df.to_csv('flats.csv', index=False)
        driver.close()  # Close the tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back to main page
        time.sleep(1)  # Allow time for focus switch
    
    # go to the next page
    try:
        
        # Step 1: Handle the cookie consent or blocking element
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
            )
            cookie_button.click()
            print("Cookie consent accepted.")
        except TimeoutException:
            print(f"Cookie consent button not found on {url}. Proceeding without interaction.")
        except Exception as cookie_exception:
            print(f"Cookie consent issue on {url}: {cookie_exception}")
            with open("page_source_error.html", "w") as f:
                f.write(driver.page_source)
            traceback.print_exc()  # Log full stack trace for debugging
            continue  # Skip to the next URL
        
        # Step 2: find the next_page button and click it
        next_page_url = f"https://www.homegate.ch/rent/real-estate/city-zurich/matching-list?ep={current_page + 1}"
        driver.get(next_page_url)

        if 'An error has occurred' in driver.title:
            more_pages = False
            print("No more pages to navigate.")
            print(f'{len(flats_lst)} flats were added to the dataframe')
            df = df.append(flats_lst, ignore_index=True)
            df.to_csv('flats.csv')
        else:
            current_page += 1  # Increment manually
            time.sleep(2)  # Wait for the page to load
            print(f'{time.ctime()} Navigated to the next page {current_page}.')

    except Exception as e:
        print(f"Could not navigate to the next page: {e}")        
        
    
        


# df= df.drop(df.iloc[:,:3],1)

# df.listing_ID.nunique()


# # entire_page = driver.find_elements_by_xpath('//*[@class="ListItemTopPremium_itemLink_11yOE ResultList_ListItem_3AwDq"]')
# # urls = [i.get_attribute('href') for i in entire_page]


# df = pd.DataFrame(flats_lst)

# df

# ### Getting the urls

#df = pd.read_csv('flats.csv')

# flats_lst = []
# more_pages = True
# total_flats_find = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, '//*[@class="ResultListHeader_locations_zQj9c ResultListHeader_locations_bold_OhksP"]'))
#                 )
# total_flats = float(total_flats_find.text.split()[0])

# entire_page = WebDriverWait(driver, 10).until(
#                 EC.presence_of_all_elements_located((By.XPATH, '//*[@data-test="result-list-item"]'))
#                 )

# urls = [
#     item.find_element(By.XPATH, './/a[@href]').get_attribute("href")  # Use relative XPath
#     for item in entire_page
# ]

# for url in urls:
#     try:
#         driver.get(url)
#         # Step 1: Handle the cookie consent or blocking element
#         try:
#             cookie_button = WebDriverWait(driver, 20).until(
#                 EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept")]'))
#             )
#             cookie_button.click()
#             print("Cookie consent accepted.")
#         except TimeoutException:
#             print(f"Cookie consent button not found on {url}. Proceeding without interaction.")
#         except Exception as cookie_exception:
#             print(f"Cookie consent issue on {url}: {cookie_exception}")
#             with open("page_source_error.html", "w") as f:
#                 f.write(driver.page_source)
#             traceback.print_exc()  # Log full stack trace for debugging
#             continue  # Skip to the next URL
        
#         # Step 2: Handle the language switcher
#         try:
#             # Wait for the language switcher to be present
#             language_switcher = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, '//button[@aria-controls="header-language-switch"]'))
#             )

#             # Click the language switcher to change the language
#             language_switcher.click()
#             # Wait for the dropdown to appear
#             english_option = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, '//a[@class="HgLanguageSwitch_link_GCiHc" and normalize-space(text())="EN"]'))
#             )

#             # Click the English option
#             english_option.click()
#         except Exception as language_exception:
#             print(f"Language switch issue on {url}: {language_exception}")
#             traceback.print_exc()
#             #continue  # Skip to the next URL

#         # Creating a dictionary with the 'main Information'
#         key_type_find = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.XPATH, '//div[@class="CoreAttributes_coreAttributes_e2NAm"]/dl/dt'))
#             )
#         key_type = []
#         for type in key_type_find:
#             key_type.append(type.text)

#         value_type_find = WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_elements_located((By.XPATH, '//div[@class="CoreAttributes_coreAttributes_e2NAm"]/dl/dd'))
#                     )
#         value_type = []
#         for type in value_type_find:
#             value_type.append(type.text)
#         main_info_dict = dict(zip(key_type, value_type))
          

#         flats_dict = {'listing_ID': listing_ID(),
#                             'address': flat_address(),
#                             'price': flat_price(),
#                             'availability': flat_availability(), 
#                             'type': flat_type(), 
#                             'n_of_rooms': flat_n_rooms(),
#                             'floor': flat_floor(),
#                             'n_of_floors': flat_n_floors(),
#                             'surface_living': flat_surface(),
#                             'floor_space': flat_floor_space(),
#                             'room_height': flat_Room_height(),
#                             'last_refurbishment': flat_last_refurbishment(),
#                             'year_built': flat_year(),
#                             'link': driver.current_url,
#                             'features': flat_features(),
#                         }
#         flats_lst.append(flats_dict)
#     except Exception as e:
#         # df = df.append(flats_lst,ignore_index=True)
#         # df.to_csv('flats.csv')
#         print(f"Exception details: {e}")