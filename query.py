import xml.etree.ElementTree as ET
import csv
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict
import aiohttp
import re
from datetime import datetime
from dataBase.gpu import graphics_cards as card_names
from dataBase.cpu import cpus

APP_ID = "WillLaue-Finding-PRD-ac1cfea6d-bbddde16"
ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"

SEARCHGPUS = False
SEARCHCPUS = True

banned_words = [
    "shroud",
    "cable",
    "bracket",
    "empty",
    "shield",
    "kit",
    "powerlink",
    "bios",
    "block",
    "backplate",
    "back plate",
    "box-only",
    "mining",
    "cooling fan",
    "graphics card fan",
    "cooler fan",
    "box only",
    "only fan",
    "parts only",
    "no gpu",
    "heatsink",
    "heat sink",
    "untested",
    "1700 Cooler",
    " es ",
    "box only",
    "confidential",
    "merch",
    "nvlink",
    "connector"
]

params = {
    "OPERATION-NAME": "findItemsByKeywords",
    "SERVICE-VERSION": "1.0.0",
    "SECURITY-APPNAME": APP_ID,
    "RESPONSE-DATA-FORMAT": "XML",
    "paginationInput.entriesPerPage": 100,
    "sortOrder": "BestMatch",
    "itemFilter(0).name": "ListingType",
    "itemFilter(0).value": "FixedPrice",
    "itemFilter(1).name": "Condition",
    "itemFilter(1).value(0)": "1000",
    "itemFilter(1).value(1)": "2000",
    "itemFilter(1).value(2)": "3000",
    "itemFilter(1).value(3)": "4000",
    "itemFilter(1).value(4)": "5000",
    "itemFilter(1).value(5)": "6000",
}

def extract_number(keyword):
    """Extracts the important 4-digit or 5-digit CPU number from the keyword."""
    if(SEARCHCPUS):
        match = re.search(r'\d{4,5}', keyword)
        return match.group(0) if match else None

async def fetch_data(session, keyword):
    """Async method to fetch info about cards or cpus quickly."""
    params["keywords"] = keyword
    async with session.get(ENDPOINT, params=params) as response:
        if response.status != 200:
            print(f"Request failed with status code {response.status} for {keyword}.")
            return keyword, []
        content = await response.text()
        root = ET.fromstring(content)
        ns = {"ns": "http://www.ebay.com/marketplace/search/v1/services"}
        search_result = root.find(".//ns:searchResult", namespaces=ns)
        if search_result is not None:
            items = search_result.findall("ns:item", namespaces=ns)
            results = []
            keyword_number = extract_number(keyword)  # Get the 4-digit CPU number (e.g., 5900, 9100, 7600)
            for item in items:
                title = (
                    item.find("ns:title", namespaces=ns).text
                    if item.find("ns:title", namespaces=ns) is not None
                    else "N/A"
                )
                if keyword_number and keyword_number not in title:
                    print(f"Filtered out item with title: {title} (keyword number '{keyword_number}' not in title)")
                    continue
                for banned_word in banned_words:
                    if banned_word.lower() in title.lower():
                        print(f"Filtered out item with title: {title} (banned word '{banned_word}')")
                        break
                else:
                    price = (
                        float(
                            item.find(".//ns:currentPrice", namespaces=ns).text.replace(
                                ",", ""
                            )
                        )
                        if item.find(".//ns:currentPrice", namespaces=ns) is not None
                        else float("inf")
                    )
                    url = (
                        item.find("ns:viewItemURL", namespaces=ns).text
                        if item.find("ns:viewItemURL", namespaces=ns) is not None
                        else "N/A"
                    )
                    condition = (
                        item.find("ns:conditionDisplayName", namespaces=ns).text
                        if item.find("ns:conditionDisplayName", namespaces=ns) is not None
                        else "N/A"
                    )
                    results.append((price, title, url, condition))
            return keyword, results
        print(f"No 'searchResult' found in the response for {keyword}.")
        return keyword, []

@dataclass
class GeneralInfo:
    """Data class to encapsulate general info."""
    csv_filename: str = field(init=False)
    data_list: List[str] = field(init=False)
    all_prices: Dict[str, List[float]] = field(init=False)
    lowest_prices: Dict[str, tuple] = field(default_factory=dict)

    def __post_init__(self):
        self.csv_filename = (
            "Website/CSVs/gpu_info.csv" if SEARCHGPUS else "Website/CSVs/cpu_info.csv"
        )
        self.data_list = card_names if SEARCHGPUS else cpus
        self.all_prices = {item: [] for item in self.data_list}

def update_csv(gen_info):
    """Update the CSV file with new prices."""
    try:
        with open(gen_info.csv_filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            existing_data = list(reader)
    except FileNotFoundError:
        # Initialize the CSV with card names if the file does not exist
        existing_data = [["Card Name"] + gen_info.data_list]

    new_column_header = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_prices = {name: gen_info.lowest_prices.get(name, (float('inf'), '', '', ''))[0] for name in gen_info.data_list}
    
    if len(existing_data) == 1:
        # If only header exists, add prices for the first time
        for card_name in gen_info.data_list:
            existing_data.append([card_name, new_prices[card_name]])
    else:
        # Add new column header
        existing_data[0].append(new_column_header)
        # Append new prices to the existing rows
        for row in existing_data[1:]:
            card_name = row[0]
            row.append(new_prices[card_name])

    with open(gen_info.csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(existing_data)

    print(f"Results have been written to '{gen_info.csv_filename}'")

async def main():
    """Fetches the info and does some parsing/analysis"""
    gen_info = GeneralInfo()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, item) for item in gen_info.data_list]
        results = await asyncio.gather(*tasks)

    for keyword, prices in results:
        gen_info.all_prices[keyword] = prices

    def _check_low_prices():
        """Internal function to just clarify a bit"""
        lowest_prices = {}
        for name, prices in gen_info.all_prices.items():
            if prices:
                sorted_prices = sorted(prices, key=lambda x: x[0])
                other_prices = [price for price, _, _, _ in sorted_prices[1:]]
                average_price = (
                    sum(other_prices) / len(other_prices)
                    if other_prices
                    else float("inf")
                )
                for price, title, url, condition in sorted_prices:
                    if price >= 0.40 * average_price:
                        lowest_prices[name] = (price, title, url, condition)
                        break
        return lowest_prices

    gen_info.lowest_prices = _check_low_prices()
    update_csv(gen_info)

if __name__ == "__main__":
    asyncio.run(main())