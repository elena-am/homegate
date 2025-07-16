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
#options.add_argument("--headless")  # Run in headless mode
# options.add_argument("--disable-gpu")  # Disable GPU acceleration
# options.add_argument("--no-sandbox")  # Disable sandboxing
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1500,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# stablishing the connection with HOMEGATE
driver.get("https://www.homegate.ch/mieten/immobilien/ort-zuerich/trefferliste")
print(driver.title)

# ## Defining function to get the elements from the website

def flat_ID():
    try:
        listing_ID = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dl.ListingTechReferences_techReferencesList_jlZwL"))
            )
        id_raw= listing_ID.text
        id_flat = re.split('[\n]', id_raw)[1]
        return id_flat
    except:
        print(f'None id_flat value for {url}')
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

def flat_price():
    try:
        # Find the element containing the rent
        rent_element = driver.find_element(By.XPATH, "//div[@data-test='costs']//dl//dd[strong]//span[contains(., 'CHF')]")
        rent_price = rent_element.text
        return rent_price
    except:
        print(f'None price value for {url}')
        return None 

def flat_availability():
    try:
        if 'Available from:' in main_info_dict:
            return main_info_dict.get('Available from:')
        else:
            raise Exception('error')
    except:
        return None
    # try:
    #     availability_find = WebDriverWait(driver, 10).until(
    #     )
    #     availability = availability_find.text
    #     return availability
    # except:
    #     print(f'None availability value for {url}')
    #     return None
    
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



# ### Getting the urls

#df = pd.read_csv('flats.csv')

flats_lst = []
more_pages = True
total_flats_find = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="ResultListHeader_locations_zQj9c ResultListHeader_locations_bold_OhksP"]'))
                )
total_flats = float(total_flats_find.text.split()[0])

entire_page = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@data-test="result-list-item"]'))
                )

urls = [
    item.find_element(By.XPATH, './/a[@href]').get_attribute("href")  # Use relative XPath
    for item in entire_page
]

for url in urls:
    try:
        driver.get(url)
        # Step 1: Handle the cookie consent or blocking element
        try:
            cookie_button = WebDriverWait(driver, 20).until(
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
            language_switcher = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-controls="header-language-switch"]'))
            )

            # Click the language switcher to change the language
            language_switcher.click()
            # Wait for the dropdown to appear
            english_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="HgLanguageSwitch_link_GCiHc" and normalize-space(text())="EN"]'))
            )

            # Click the English option
            english_option.click()
        except Exception as language_exception:
            print(f"Language switch issue on {url}: {language_exception}")
            traceback.print_exc()
            #continue  # Skip to the next URL

        # Creating a dictionary with the 'main Information'
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
          

        flats_dict = {'flat_ID': flat_ID(),
                            'address': flat_address(),
                            'price': flat_price(),
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
        # df = df.append(flats_lst,ignore_index=True)
        # df.to_csv('flats.csv')
        print(f"Exception details: {e}")



while more_pages:
    # get all the elements containing the flats
    entire_page = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@data-test="result-list-item"]'))
                )
    # get all the urls from the entire_page page
    urls = [item.find_element(By.XPATH, './/a[@href]').get_attribute("href") for item in entire_page]
    # get the entire_page url
    entire_page_url = driver.current_url
       
    for url in urls:
        try:
            driver.get(url)

            # Creating a dictionary with the 'entire_page Information'
            key_type_find = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="CoreAttributes_coreAttributes_2UrTf"]/dl/dt'))
                )
            key_type = []
            for type in key_type_find:
                key_type.append(type.text)

            value_type_find = WebDriverWait(driver, 10).until(
                        )
            value_type = []
            for type in value_type_find:
                value_type.append(type.text)
            entire_page_info_dict = dict(zip(key_type, value_type))

            flats_dict = {'flat_ID': flat_ID(),
                            'address': flat_address(),
                            'price': flat_price(),
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
        except:
            df = df.append(flats_lst,ignore_index=True)
            df.to_csv('flats.csv')
            raise Exception('aaa')
            
    try:
        driver.get(entire_page_url)
        next_page = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Go to next page"]'))
                )
        next_page.click()
    except:
        more_pages = False
        print('no more pages')
        print(f'{len(flats_lst)} flats were added to the dataframe')
        df = df.append(flats_lst, ignore_index=True)
        df.to_csv('flats.csv')
    
        


df= df.drop(df.iloc[:,:3],1)

df.flat_ID.nunique()


entire_page = driver.find_elements_by_xpath('//*[@class="ListItemTopPremium_itemLink_11yOE ResultList_ListItem_3AwDq"]')
urls = [i.get_attribute('href') for i in entire_page]


# Creating the dictionary with all the flats to create the DataFrame

flats_lst = []

for url in urls:
    try:
        driver.get(url)
        
        # Creating a dictionary with the 'entire_page Information'
        key_type_find = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="CoreAttributes_coreAttributes_2UrTf"]/dl/dt'))
            )
        key_type = []
        for type in key_type_find:
            key_type.append(type.text)

        value_type_find = WebDriverWait(driver, 10).until(
                    )
        value_type = []
        for type in value_type_find:
            value_type.append(type.text)
        entire_page_info_dict = dict(zip(key_type, value_type))
        
        flats_dict = {'flat_ID': flat_ID(),
                      'address': flat_address(),
                      'price': flat_price(),
                      'availability': flat_availability(), 
                      'type': flat_type(), 
                      'N_of_rooms': flat_n_rooms(),
                      'floor': flat_floor(),
                      'N_of_floors': flat_n_floors(),
                      'Surface_living': flat_surface(),
                      'Floor_space': flat_floor_space(),
                      'Room_height': flat_Room_height(),
                      'Last_refurbishment': flat_last_refurbishment(),
                      'Year_built': flat_year(),
                      'Features': flat_features(),
                    }
        flats_lst.append(flats_dict)
    
    except:
        print('not possible')
        

df = pd.DataFrame(flats_lst)

df

# %%
# try:
#     entire_page = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "ResultListPage_stickyParent_2d4Bp"))
#     )
#     print(entire_page.text)
# except:
#     driver.quit()

# %%
# driver.quit()

# %%
# driver.back()

# %% [markdown]
# ### printing elements

# %%
# entire_page = driver.find_elements_by_xpath('//*[@class="ListItemTopPremium_itemLink_11yOE ResultList_ListItem_3AwDq"]')
# urls = [i.get_attribute('href') for i in entire_page]
# for url in urls:
#     driver.get(url)
#     try:
# #         link = WebDriverWait(driver, 10).until(
# #             EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/entire_page/div[2]/div/div[3]/div[2]/div[1]/a"))
# #         )
# #         print("\nlink:",each.get_attribute('href'))
# #         link.click()

#         address = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "address.AddressDetails_address_3Uq1m"))
#         )
#         print("\nAddress:",address.text)

#         listing_ID = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "dl.ListingTechReferences_techReferencesList_3qCPT"))
#         )
#         print("\nListing_ID:",listing_ID.text)

#         Price = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.SpotlightAttributes_value_2njuM"))
#         )
#         print("\nPrice:",Price.text)

#         info = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.CoreAttributes_coreAttributes_2UrTf"))
#         )
#         print("\ninfo:",info.text)

#         availability = WebDriverWait(driver, 10).until(
#         )
#         print("\navailability:",availability.text)

#         features = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "ul.FeaturesFurnishings_list_1HzQj"))
#         )
#         print("\nfeatures:",features.text)
#         driver.back()
#     except:
#         print('not possible')
#     #     driver.quit()
#         driver.back()


