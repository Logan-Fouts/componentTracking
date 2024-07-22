import requests
import xml.etree.ElementTree as ET
import csv

app_id = 'WillLaue-Finding-PRD-ac1cfea6d-bbddde16'
endpoint = 'https://svcs.ebay.com/services/search/FindingService/v1'

# Import graphics card names from gpu.py
from gpu import graphics_cards as card_names

params = {
    'Operation-Name': 'findItemsByKeywords',
    'Service-Version': '1.0.0',
    'Security-AppName': app_id,
    'Response-Data-Format': 'XML',
    'paginationInput.entriesPerPage': 8,
    'sortOrder': 'BestMatch',
    'itemFilter(0).name': 'ListingType',
    'itemFilter(0).value': 'FixedPrice',
    'itemFilter(1).name' : 'ConditionExclude',
    'itemFilter(1).value' : '7000'
}

all_prices = {card_name: [] for card_name in card_names}

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
                    title = item.find('ns:title', namespaces=ns).text if item.find('ns:title', namespaces=ns) is not None else 'N/A'
                    price = float(item.find('.//ns:currentPrice', namespaces=ns).text.replace(',', '')) if item.find('.//ns:currentPrice', namespaces=ns) is not None else float('inf')
                    url = item.find('ns:viewItemURL', namespaces=ns).text if item.find('ns:viewItemURL', namespaces=ns) is not None else 'N/A'
                    all_prices[card_name].append((price, title, url))
            else:
                print(f"No 'searchResult' found in the response for {card_name}.")
        else:
            print(f"Request failed with status code {response.status_code} for {card_name}.")
    
    lowest_prices = {}
    for card_name, prices in all_prices.items():
        if prices:
            # Sort by price
            sorted_prices = sorted(prices, key=lambda x: x[0])
            other_prices = [price for price, _, _ in sorted_prices[1:]]
            average_price = sum(other_prices) / len(other_prices) if other_prices else float('inf')
            
            if sorted_prices[0][0] >= 0.57 * average_price:
                lowest_prices[card_name] = sorted_prices[0]
    
    # Update the CSV data with the eBay prices if they are cheaper
    for row in csv_data:
        card_name = row['Card']
        if card_name in lowest_prices:
            ebay_price, _, ebay_url = lowest_prices[card_name]
            current_price = float(row['Price ($)'].replace(',', ''))
            if ebay_price < current_price:
                row['Price ($)'] = f"{ebay_price:,.2f}"
                row['URL'] = ebay_url
    
    # Write the updated data back to the CSV file
    with open(csv_filename, mode='w', newline='') as file:
        fieldnames = csv_data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"Results have been written to '{csv_filename}'")

except Exception as e:
    print(f"An error occurred: {e}")
