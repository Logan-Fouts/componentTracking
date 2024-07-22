import requests
import xml.etree.ElementTree as ET

app_id = 'WillLaue-Finding-PRD-ac1cfea6d-bbddde16'
endpoint = 'https://svcs.ebay.com/services/search/FindingService/v1'

card_names = [
    "GeForce RTX 3090", "Radeon RX 6900 XT", "GeForce RTX 3080 Ti",
    "Radeon RX 6800 XT", "GeForce RTX 3070"
]

params = {
    'Operation-Name': 'findItemsByKeywords',
    'Service-Version': '1.0.0',
    'Security-AppName': app_id,
    'Response-Data-Format': 'XML',
    'paginationInput.entriesPerPage': 8,
    'sortOrder': 'BestMatch',
    'itemFilter(0).name': 'ListingType',
    'itemFilter(0).value': 'FixedPrice'
}

all_prices = {card_name: [] for card_name in card_names}

try:
    for card_name in card_names:
        params['keywords'] = card_name
        
        # Send request to the eBay Finding API
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200: # successful query
            # for debugging
            print(f"Response for {card_name}:")
            
            # Parse response
            root = ET.fromstring(response.content)

            ns = {'ns': 'http://www.ebay.com/marketplace/search/v1/services'}

            search_result = root.find('.//ns:searchResult', namespaces=ns)
            if search_result is not None:
                items = search_result.findall('ns:item', namespaces=ns)
                # for debugging
                print(f"Number of items found for {card_name}: {len(items)}")
                prices = []

                for item in items:
                    title = item.find('ns:title', namespaces=ns).text if item.find('ns:title', namespaces=ns) is not None else 'N/A'
                    price = float(item.find('.//ns:currentPrice', namespaces=ns).text) if item.find('.//ns:currentPrice', namespaces=ns) is not None else float('inf')
                    url = item.find('ns:viewItemURL', namespaces=ns).text if item.find('ns:viewItemURL', namespaces=ns) is not None else 'N/A'
                    all_prices[card_name].append((price, title, url))
                    prices.append((price, title, url)) 
                    
            else:
                print(f"No 'searchResult' found in the response for {card_name}.")
        else:
            print(f"Request failed with status code {response.status_code} for {card_name}.")
    
    lowest_prices = {}
    for card_name, prices in all_prices.items():
        if prices:
            # Sort by price
            sorted_prices = sorted(prices, key=lambda x: x[0])
            lowest_price = sorted_prices[0]
            other_prices = [price for price, _, _ in sorted_prices[1:]]
            average_price = sum(other_prices) / len(other_prices) if other_prices else float('inf')
            
            # if lowest_price[0] is > 0.4*average_price, odds are it's "For Parts Only"
            # this is an okay fix for not being able to filter by condition
            if lowest_price[0] >= 0.4*average_price:
                lowest_prices[card_name] = lowest_price

    # write to txt file for now, soon to be csv
    with open('test.txt', 'w') as file:
        for card_name, (price, title, url) in lowest_prices.items():
            file.write(f"Card: {card_name}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Price: ${price}\n")
            file.write(f"URL: {url}\n")
            file.write("\n")
    
    print("Results have been written to 'gpu_results.txt'")

except Exception as e:
    print(f"An error occurred: {e}")
