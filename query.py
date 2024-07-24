import requests
import xml.etree.ElementTree as ET
import csv

app_id = 'WillLaue-Finding-PRD-ac1cfea6d-bbddde16'
endpoint = 'https://svcs.ebay.com/services/search/FindingService/v1'

# Import graphics card names from gpu.py
from dataBase.gpu import graphics_cards as card_names
from dataBase.cpu import cpus as cpus

searchGpus = False
searchCpus = True

# Search for either Gpus or Cpus 
if (searchGpus):
    params = {
        'Operation-Name': 'findItemsByKeywords',
        'Service-Version': '1.0.0',
        'Security-AppName': app_id,
        'Response-Data-Format': 'XML',
        'paginationInput.entriesPerPage': 50,
        'sort_by': 'best_match',
        'itemFilter(0).name': 'ListingType',
            'itemFilter(0).value': 'FixedPrice',
        'itemFilter(1).name': 'Condition',
        'itemFilter(1).value(0)': '1000',
        'itemFilter(1).value(1)': '2000',
        'itemFilter(1).value(2)': '3000',
        'itemFilter(1).value(3)': '4000',
        'itemFilter(1).value(4)': '5000',
        'itemFilter(1).value(5)': '6000'
    }

    all_prices = {card_name: [] for card_name in card_names}
    banned_words = ['shroud', 'cable', 'bracket', 'Shroud', 'Cable', 'Bracket', 'EMPTY', 'empty', 'Empty',
                    'Shield', 'SHIELD', 'shield', 'kit', 'KIT', 'Powerlink',
                    'POWERLINK', 'powerlink', 'BIOS', 'bios', 'block', 'Block', 'BLOCK', 'backplate',
                    'BACKPLATE', 'Backplate', 'Back Plate', 'Back plate', 'back Plate', 'back plate'
                    'Box-only', 'Mining', 'mining', 'MINING', 'cooling fan', 'graphics card fan',
                    'cooler fan', 'box only', 'only fan', 'parts only', 'no gpu', 'heatsink', 'heat sink']

    # Read the existing CSV file
    csv_filename = 'gpu_info.csv'
    csv_data = []

    with open(csv_filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            csv_data.append(row)
            
    total_cards = len(card_names)
    try:
        for index, card_name in enumerate(card_names, start=1):
            print(f"Processing {index} / {total_cards}: {card_name}")
            params['keywords'] = card_name
            
            # Send request to the eBay Finding API
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                # Parse response
                root = ET.fromstring(response.content)

                ns = {'ns': 'http://www.ebay.com/marketplace/search/v1/services'}

                search_result = root.find('.//ns:searchResult', namespaces=ns)
                if search_result is not None:
                    items = search_result.findall('ns:item', namespaces=ns)
                    for item in items:
                        # Skip items with banned words in the title
                        title = item.find('ns:title', namespaces=ns).text if item.find('ns:title', namespaces=ns) is not None else 'N/A'
                        if any(banned_word.lower() in title.lower() for banned_word in banned_words):
                            continue
                        price = float(item.find('.//ns:currentPrice', namespaces=ns).text.replace(',', '')) if item.find('.//ns:currentPrice', namespaces=ns) is not None else float('inf')
                        url = item.find('ns:viewItemURL', namespaces=ns).text if item.find('ns:viewItemURL', namespaces=ns) is not None else 'N/A'
                        condition = item.find('ns:conditionDisplayName', namespaces=ns).text if item.find('ns:conditionDisplayName', namespaces=ns) is not None else 'N/A'
                        all_prices[card_name].append((price, title, url, condition))
                else:
                    print(f"No 'searchResult' found in the response for {card_name}.")
            else:
                print(f"Request failed with status code {response.status_code} for {card_name}.")

        lowest_prices = {}
        for card_name, prices in all_prices.items():
            if prices:
                # Sort by price
                sorted_prices = sorted(prices, key=lambda x: x[0])
                other_prices = [price for price, _, _, _ in sorted_prices[1:]]
                average_price = sum(other_prices) / len(other_prices) if other_prices else float('inf')
                
                # Find the first price that is greater than 0.4 * average_price
                for price, title, url, condition in sorted_prices:
                    if price >= 0.40 * average_price:
                        lowest_prices[card_name] = (price, title, url, condition)
                        break
                
        
        # Update the CSV data with the eBay prices if they are cheaper
        for row in csv_data:
            card_name = row['Card']
            if card_name in lowest_prices:
                ebay_price, _, ebay_url, _ = lowest_prices[card_name]
                current_price = float(row['Price ($)'].replace(',', ''))
                row['Price ($)'] = f"{ebay_price:,.2f}"
                row['URL'] = ebay_url
            fps = float(row['FPS'])
            watts = float(row['W'])
            row['Power Efficiency (FPS/W)'] = f"{(fps / watts) if watts != 0 else float('inf'):.4f}"
            price = float(row['Price ($)'].replace(',', ''))
            row['Price Efficiency (FPS/$)'] = f"{(fps / price) if price != 0 else float('inf'):.4f}"
            price_efficiency = float(row['Price Efficiency (FPS/$)'])
            power_efficiency = float(row['Power Efficiency (FPS/W)'])
            row['Average Efficiency'] = f"{(price_efficiency + power_efficiency) / 2:.4f}"

        # Write the updated data back to the CSV file
        with open(csv_filename, mode='w', newline='') as file:
            fieldnames = csv_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"Results have been written to '{csv_filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")
if (searchCpus):
    params = {
        'Operation-Name': 'findItemsByKeywords',
        'Service-Version': '1.0.0',
        'Security-AppName': app_id,
        'Response-Data-Format': 'XML',
        'paginationInput.entriesPerPage': 50,
        'sort_by': 'best_match',
        'itemFilter(0).name': 'ListingType',
            'itemFilter(0).value': 'FixedPrice',
        'itemFilter(1).name': 'Condition',
        'itemFilter(1).value(0)': '1000',
        'itemFilter(1).value(1)': '2000',
        'itemFilter(1).value(2)': '3000',
        'itemFilter(1).value(3)': '4000',
        'itemFilter(1).value(4)': '5000',
        'itemFilter(1).value(5)': '6000'
    }

    all_prices = {cpu: [] for cpu in cpus}
    banned_words = ['cooling fan', 'untested', 'cooler fan', '1700 Cooler']

    # Read the existing CSV file
    csv_filename = 'cpu_info.csv'
    csv_data = []

    with open(csv_filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            csv_data.append(row)
            
    total_cpus = len(cpus)
    try:
        for index, cpu in enumerate(cpus, start=1):
            print(f"Processing {index} / {total_cpus}: {cpu}")
            params['keywords'] = cpu
            
            # Send request to the eBay Finding API
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                # Parse response
                root = ET.fromstring(response.content)

                ns = {'ns': 'http://www.ebay.com/marketplace/search/v1/services'}

                search_result = root.find('.//ns:searchResult', namespaces=ns)
                if search_result is not None:
                    items = search_result.findall('ns:item', namespaces=ns)
                    for item in items:
                        # Skip items with banned words in the title
                        title = item.find('ns:title', namespaces=ns).text if item.find('ns:title', namespaces=ns) is not None else 'N/A'
                        if any(banned_word.lower() in title.lower() for banned_word in banned_words):
                            continue
                        price = float(item.find('.//ns:currentPrice', namespaces=ns).text.replace(',', '')) if item.find('.//ns:currentPrice', namespaces=ns) is not None else float('inf')
                        url = item.find('ns:viewItemURL', namespaces=ns).text if item.find('ns:viewItemURL', namespaces=ns) is not None else 'N/A'
                        condition = item.find('ns:conditionDisplayName', namespaces=ns).text if item.find('ns:conditionDisplayName', namespaces=ns) is not None else 'N/A'
                        all_prices[cpu].append((price, title, url, condition))
                else:
                    print(f"No 'searchResult' found in the response for {cpu}.")
            else:
                print(f"Request failed with status code {response.status_code} for {cpu}.")

        lowest_prices = {}
        for cpu, prices in all_prices.items():
            if prices:
                # Sort by price
                sorted_prices = sorted(prices, key=lambda x: x[0])
                other_prices = [price for price, _, _, _ in sorted_prices[1:]]
                average_price = sum(other_prices) / len(other_prices) if other_prices else float('inf')
                
                # Find the first price that is greater than 0.4 * average_price
                for price, title, url, condition in sorted_prices:
                    if price >= 0.40 * average_price:
                        lowest_prices[cpu] = (price, title, url, condition)
                        break
                
        
        # Update the CSV data with the eBay prices if they are cheaper
        for row in csv_data:
            cpu = row['Name']
            if cpu in lowest_prices:
                ebay_price, _, ebay_url, _ = lowest_prices[cpu]
                current_price = float(row['Price ($)'].replace(',', ''))
                row['Price ($)'] = f"{ebay_price:,.2f}"
                row['URL'] = ebay_url
            score = float(row['Score'])
            watts = float(row['TDP'])
            row['Power Efficiency (FPS/W)'] = f"{(score / watts) if watts != 0 else float('inf'):.4f}"
            price = float(row['Price ($)'].replace(',', ''))
            row['Price Efficiency (FPS/$)'] = f"{(score / price) if price != 0 else float('inf'):.4f}"
            price_efficiency = float(row['Price Efficiency (FPS/$)'])
            power_efficiency = float(row['Power Efficiency (FPS/W)'])
            row['Average Efficiency'] = f"{(price_efficiency + power_efficiency) / 2:.4f}"

        # Write the updated data back to the CSV file
        with open(csv_filename, mode='w', newline='') as file:
            fieldnames = csv_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"Results have been written to '{csv_filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")