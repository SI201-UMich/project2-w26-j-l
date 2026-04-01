# SI 201 HW4 (Library Checkout System)
# Your name: Luciana Lacroix and Jessica Kozyra
# Your student id:3867 8419/71221230
# Your email: lucianal@umich.edu/jkozyra@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): Worked with each other, but also used AI
#when we needed help with debugging, especially when output was coming out a bit odd. We also ended up asking AI if the fact
#that we were getting 0.0 for some of the location ratings meant that we were doing something wrong in our code, but the instructions said
#it was normal. AI was also used to double check with rubric requirements to make sure we were hitting all points. Sometimes it would suggest
#wats to structure code that we hadn't thought of, but we would mostly end up sticking with our original code if it still ended up working. 
# If you worked with generative AI also add a statement for how you used it.
# e.g.: Already explauned above. 
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#Yes it did! We stuck to our guidelines and goals, and only used GenAI for debugging help and to double check rubric, we also did make sure
#to double check code if we did end up taking any suggestions just to make sure it still aligned with out guidelines. 
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    results = []
    seen_ids = set()
    
    title_divs = soup.find_all('div', {'data-testid': 'listing-card-title'})
    
    for title_div in title_divs:
        title = title_div.get_text(strip=True)
        
        parent = title_div.parent
        listing_id = None
        
        for _ in range(10):
            if parent is None:
                break
            link = parent.find('a', href=re.compile(r'/rooms/'))
            if link:
                match = re.search(r'/rooms/(?:plus/)?(\d+)', link['href'])
                if match:
                    listing_id = match.group(1)
                    break
            parent = parent.parent
        
        if title and listing_id and listing_id not in seen_ids:
            results.append((title, listing_id))
            seen_ids.add(listing_id)
    
    return results
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    html_path = f'html_files/listing_{listing_id}.html'
 
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
 
    policy_number = 'Exempt'   
 
    for li in soup.find_all('li'):
        text = li.get_text(strip=True)    
        if 'policy number' in text.lower():
            raw = text.split(':', 1)[-1].strip() if ':' in text else ''
 
            if not raw or 'exempt' in raw.lower():
                policy_number = 'Exempt'
            elif 'pending' in raw.lower():
                policy_number = 'Pending'
            else:
                policy_number = raw   
            break
 

    page_text = soup.get_text()
    host_type = 'Superhost' if 'Superhost' in page_text else 'regular'
 

    host_name = None
    for h2 in soup.find_all('h2'):
        text = h2.get_text(strip=True)
        if text.startswith('Hosted by'):
            host_name = text.replace('Hosted by', '').strip()
            break
 

    room_type = 'Entire Room' 
    for h2 in soup.find_all('h2'):
        text = h2.get_text(strip=True)
        if 'hosted by' in text.lower():
            if 'Private' in text:
                room_type = 'Private Room'
            elif 'Shared' in text:
                room_type = 'Shared Room'
            else:
                room_type = 'Entire Room'
            break
 

    location_rating = 0.0
    
    for div in soup.find_all('div'):
        if div.get_text(strip=True) == 'Location':
            parent = div.parent
            if parent:
                rating_div = parent.find(attrs={'aria-label': re.compile(r'\d+\.?\d*\s+out of')})
                if rating_div:
                    aria = rating_div.get('aria-label', '')
                    match = re.search(r'([\d.]+)\s+out of', aria)
                    if match:
                        location_rating = float(match.group(1))
                        break
 
    return {
        listing_id: {
            'policy_number'   : policy_number,
            'host_type'       : host_type,
            'host_name'       : host_name,
            'room_type'       : room_type,
            'location_rating' : location_rating,
        }
    }

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = load_listing_results(html_path)
 
    database = []
 
    for listing_title, listing_id in listings:
        details = get_listing_details(listing_id)
        info = details[listing_id]
 
        row = (
            listing_title,
            listing_id,
            info['policy_number'],
            info['host_type'],
            info['host_name'],
            info['room_type'],
            info['location_rating'],
        )
        database.append(row)
 
    return database
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda row: row[6], reverse=True)
 
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
 

        writer.writerow([
            'Listing Title', 'Listing ID', 'Policy Number',
            'Host Type', 'Host Name', 'Room Type', 'Location Rating'
        ])
 
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    room_ratings = {}  
 
    for row in data:
        room_type       = row[5]   
        location_rating = row[6]   
 
        if location_rating == 0.0:
            continue
 
        if room_type not in room_ratings:
            room_ratings[room_type] = []
        room_ratings[room_type].append(location_rating)
 
    averages = {}
    for room_type, ratings in room_ratings.items():
        avg = sum(ratings) / len(ratings)
        averages[room_type] = round(avg, 2)
 
    return averages
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    format_a = re.compile(r'^20\d{2}-00\d{4}STR$')  
    format_b = re.compile(r'^STR-000\d{4}$')          
 
    invalid_ids = []
 
    for row in data:
        listing_id    = row[1]  
        policy_number = row[2]   
 
        if policy_number in ('Pending', 'Exempt'):
            continue
 
        if not (format_a.match(policy_number) or format_b.match(policy_number)):
            invalid_ids.append(listing_id)
 
    return invalid_ids
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    url = 'https://scholar.google.com/scholar'
    params = {'q': query}
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }
 
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
 
    titles = []
    for h3 in soup.find_all('h3', class_='gs_rt'):
        title_text = h3.get_text(strip=True)
        if title_text:
            titles.append(title_text)
 
    return titles
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        results = load_listing_results('html_files/search_results.html')
 
        assert len(results) == 18, (
            f"Expected 18 listings, got {len(results)}"
        )
    
        expected_first = ("Loft in Mission District", "1944564")
        assert results[0] == expected_first, (
            f"Expected {expected_first}, got {results[0]}"
        )
    

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        listing_ids = [row[1] for row in load_listing_results('html_files/search_results.html')]
    
        for lid in listing_ids:
            get_listing_details(lid)
    
        r467 = get_listing_details('467507')
        assert r467['467507']['policy_number'] == 'STR-0005349', (
            f"Expected 'STR-0005349', got {r467['467507']['policy_number']}"
        )
    
        r194 = get_listing_details('1944564')
        assert r194['1944564']['host_type'] == 'Superhost', (
            f"Expected 'Superhost', got {r194['1944564']['host_type']}"
        )
        assert r194['1944564']['room_type'] == 'Entire Room', (
            f"Expected 'Entire Room', got {r194['1944564']['room_type']}"
        )
    
        assert r194['1944564']['location_rating'] == 4.9, (
            f"Expected 4.9, got {r194['1944564']['location_rating']}"
        )
    

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        detailed_data = create_listing_database('html_files/search_results.html')
        for row in detailed_data: 
            assert len(row) == 7, (
                f"Expected 7 elements per row, got {len(row)}: {row}"
            )
 
        expected_last = (
            "Guest suite in Mission District",
            "467507",
            "STR-0005349",
            "Superhost",
            "Jennifer",
            "Entire Room",
            4.8
        )
        assert detailed_data[-1] == expected_last, (
            f"Last tuple mismatch:\n  Expected: {expected_last}\n  Got:      {detailed_data[-1]}"
        )
    


    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test_output.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        
        detailed_data = create_listing_database('html_files/search_results.html')
        output_csv(detailed_data, 'test_output.csv')

        rows = []
        with open('test_output.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)   # Skip the header row
            for row in reader:
                rows.append(row)
    
        expected_first_row = [
            "Guesthouse in San Francisco",
            "49591060",
            "STR-0000253",
            "Superhost",
            "Ingrid",
            "Entire Room",
            "5.0"
        ]
        assert rows[0] == expected_first_row, (
            f"First CSV row mismatch:\n  Expected: {expected_first_row}\n  Got:      {rows[0]}"
        )
    


        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        detailed_data = create_listing_database('html_files/search_results.html')
        averages = avg_location_rating_by_room_type(detailed_data)
 
        assert averages.get('Private Room') == 4.9, (
        f"Expected 4.9 for 'Private Room', got {averages.get('Private Room')}")

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        detailed_data = create_listing_database('html_files/search_results.html')
        invalid = validate_policy_numbers(detailed_data)
    
        assert invalid == ['16204265'], (
            f"Expected ['16204265'], got {invalid}"
        )


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)