import xml.etree.ElementTree as ET
import csv
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict
import aiohttp
from dataBase.gpu import graphics_cards as card_names
from dataBase.cpu import cpus

APP_ID = "WillLaue-Finding-PRD-ac1cfea6d-bbddde16"
ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"

SEARCHGPUS = True
SEARCHCPUS = False

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
]

params = {
    "Operation-Name": "findItemsByKeywords",
    "Service-Version": "1.0.0",
    "Security-AppName": APP_ID,
    "Response-Data-Format": "XML",
    "paginationInput.entriesPerPage": 50,
    "sort_by": "best_match",
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


async def fetch_data(session, keyword):
    """Aync method to fetch info about cards or cpus quickly."""

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
            for item in items:
                title = (
                    item.find("ns:title", namespaces=ns).text
                    if item.find("ns:title", namespaces=ns) is not None
                    else "N/A"
                )
                if any(
                    banned_word.lower() in title.lower() for banned_word in banned_words
                ):
                    continue
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
        self.csv_filename = "gpu_info.csv" if SEARCHGPUS else "cpu_info.csv"
        self.data_list = card_names if SEARCHGPUS else cpus
        self.all_prices = {item: [] for item in self.data_list}


def update_csv(gen_info):
    """Read in csv data and update"""

    csv_data = []
    try:
        with open(gen_info.csv_filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_data.append(row)
    except FileNotFoundError:
        print(f"CSV file '{gen_info.csv_filename}' not found.")

    if csv_data:
        for row in csv_data:
            name = row["Card"] if SEARCHGPUS else row["Name"]
            if name in gen_info.lowest_prices:
                ebay_price, _, ebay_url, _ = gen_info.lowest_prices[name]
                row["Price ($)"] = f"{ebay_price:,.2f}"
                row["URL"] = ebay_url
            fps_or_score = float(row["FPS"]) if SEARCHGPUS else float(row["Score"])
            watts = float(row["TDP"])
            row["Power Efficiency (FPS/W)"] = (
                f"{(fps_or_score / watts) if watts != 0 else float('inf'):.4f}"
            )
            price = float(row["Price ($)"].replace(",", ""))
            if SEARCHGPUS:
                row["Price Efficiency (FPS/$)"] = (
                    f"{(fps_or_score / price) if price != 0 else float('inf'):.4f}"
                )
                price_efficiency = float(row["Price Efficiency (FPS/$)"])
                power_efficiency = float(row["Power Efficiency (FPS/W)"])
            if SEARCHCPUS:
                row["Price Efficiency (Score/$)"] = (
                    f"{(fps_or_score / price) if price != 0 else float('inf'):.4f}"
                )
                price_efficiency = float(row["Price Efficiency (Score/$)"])
                power_efficiency = float(row["Power Efficiency (Score/W)"])
            row["Average Efficiency"] = (
                f"{(price_efficiency + power_efficiency) / 2:.4f}"
            )

        with open(
            gen_info.csv_filename, mode="w", newline="", encoding="utf-8"
        ) as file:
            fieldnames = csv_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

        print(f"Results have been written to '{gen_info.csv_filename}'")
    else:
        print("No data found in the CSV file to process.")


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

