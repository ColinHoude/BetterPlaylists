import os
import re
from docx import Document
from html import unescape
import pandas as pd
from youtubesearchpython import VideosSearch
import random
import time
from pytube import YouTube
import requests
from bs4 import BeautifulSoup
from DownloadMp3 import *

url = 'https://www.beatport.com/top-100'
output_path = "mp3Folder/MelodicHouse"  # specify your output directory
ffmpeg_path = "C:/ffmpeg"


# ------------------------------------------------------------------------------------ #
# ------------------------------ EXTRACT HTML FROM URL ------------------------------- #
# ------------------------------------------------------------------------------------ #


def copy_html_after_div(url, div_class):
    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send a GET request with headers
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the target div with the specified class
    target_div = soup.find("div", class_=div_class)
    if not target_div:
        raise Exception(f"Div with class '{div_class}' not found.")

    # Get all inner HTML after the target div
    html_after_div = ''
    for sibling in target_div.find_all_next():
        html_after_div += str(sibling)

    return html_after_div


# GET HTML
div_class = 'Table-style__TableData-sc-fdd08fbd-2 hKhaa'
text = copy_html_after_div(url, div_class)


def extract_text_between_substrings(text, start_substring, end_substring):
    extracted_segments = []
    capturing = False
    segment = ""
    buffer = ""  # Temporary buffer to check for start_substring

    # Iterate over each character in the text
    for char in text:
        buffer += char  # Add the character to the buffer

        # Check if the buffer ends with the start substring
        if buffer.endswith(start_substring) and not capturing:
            capturing = True
            segment = ""  # Start a new segment
            buffer = ""  # Reset buffer after finding start substring
            continue

        # If capturing, start adding characters to the segment
        if capturing:
            # Check if the segment ends with the end substring
            if segment.endswith(end_substring):
                # Remove the end substring from the segment
                segment = segment[: -len(end_substring)]
                extracted_segments.append(segment.strip())  # Add to results
                capturing = False
                segment = ""  # Reset for the next segment
                buffer = ""  # Reset buffer
            else:
                segment += char  # Continue building the segment

    return extracted_segments


# Usage
start_substring = "TracksTable-style__ReleaseName"
end_substring = "</a></div></div></div></div></"
extracted_segments = extract_text_between_substrings(text, start_substring, end_substring)
# print(extracted_segments) -- this is the html string


def parse_list(input_list):
    result = []
    for s in input_list:
        # Extract track name and mix
        try:
            start_index = s.find('kGvbaR">') + len('kGvbaR">')
            # Find the end of the track info
            end_index = s.find('</span></div></div></a>', start_index)
            if end_index == -1:
                # If the closing tags are missing, find the start of the artist section
                end_index = s.find('<div data-testid="marquee-parent"', start_index)
                if end_index == -1:
                    end_index = len(s)
            track_info = s[start_index:end_index]
            # Remove HTML tags from track_info
            track_info_clean = re.sub('<[^>]+>', '', track_info)
            track_info_clean = track_info_clean.strip()
        except Exception as e:
            track_info_clean = ''

        # Extract artist names
        try:
            # Start searching after the end of the track info
            artist_start = s.find('ArtistNames-sc-72fc6023-0 galPMj', end_index)
            if artist_start == -1:
                artist_start = s.find('ArtistNames__ArtistNamesContainer-sc-72fc6023-0 cNRTjL', end_index)
            if artist_start == -1:
                artist_start = s.find('ArtistNames-sc-72fc6023-0 galPMj')
            if artist_start == -1:
                artist_names_str = ''
            else:
                # Find the end of the artist section
                artist_end = s.find('</div>', artist_start)
                if artist_end == -1:
                    artist_end = len(s)
                artist_section = s[artist_start:artist_end]
                # Extract all artist names even if the closing </a> tags are missing
                artist_names = re.findall(r'<a[^>]*>([^<]*)', artist_section)
                artist_names = [unescape(name.strip()) for name in artist_names if name.strip()]
                artist_names_str = ' '.join(artist_names)
        except Exception as e:
            artist_names_str = ''

        # Combine track info and artist names
        full_info = track_info_clean + ' ' + artist_names_str
        full_info = full_info.strip()
        result.append(full_info)
    return result


output = parse_list(extracted_segments)


# ------------------------------------------------------------------------------------ #
# -------------------------------- DELETE DUPLICATES --------------------------------- #
# ------------------------------------------------------------------------------------ #

def remove_duplicates(input_list):
    seen = set()
    output_list = []

    for item in input_list:
        if item not in seen:
            seen.add(item)
            output_list.append(item)

    return output_list


unique_list = remove_duplicates(output)


def remove_substring_from_list(input_list, substring):
    output_list = [item.replace(substring, "&") for item in input_list]
    return output_list


substring = "&amp;"
unique_list = remove_substring_from_list(unique_list, substring)
print(unique_list)


# ------------------------------------------------------------------------------------- #
# --------------------------------- Keep only first 50--------------------------------- #
# ------------------------------------------------------------------------------------- #


def keep_first_50_elements(uniqueList):
    # Keep only the first 50 elements
    del uniqueList[10:]


keep_first_50_elements(unique_list)

# ------------------------------------------------------------------------------------ #
# ------------------------------ PREFORM YOUTUBE SEARCH ------------------------------ #
# --------------------------- FOR EACH LIST ITEM GET LINK ---------------------------- #
# ------------------------------------------------------------------------------------ #


def get_youtube_links_no_api(queries):
    links = []
    total_queries = len(queries)
    for index, query in enumerate(queries, start=1):
        print(f"Processing {index}/{total_queries}: {query}")
        try:
            videos_search = VideosSearch(query, limit=1)
            result = videos_search.result()
            if result['result']:
                video_id = result['result'][0]['id']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                links.append(video_url)
            else:
                links.append('No results found')
            # Add a random delay between 1 and 4 seconds
            time_to_sleep = random.uniform(1, 3)
            time.sleep(time_to_sleep)
        except Exception as e:
            print(f'An error occurred: {e}')
            links.append('Error occurred')
    return links


links = get_youtube_links_no_api(unique_list)
print(links)


# ------------------------------------------------------------------------------------- #
# ---------------------------------- Download Audio ---------------------------------- #
# ------------------------------------------------------------------------------------- #


# Process the first 50 links
for link in links[:10]:
    youtube_to_mp3_with_cover(link, output_path, ffmpeg_path)


# ------------------------------------------------------------------------------------- #
# ---------------------------------- CHECKPOINT SAVE ---------------------------------- #
# ------------------------------------------------------------------------------------- #

# def write_lists_to_excel(list1, list2, file_name):
#     # Create a DataFrame from the two lists
#     df = pd.DataFrame({'Column1': list1, 'Column2': list2})
#
#     # Write the DataFrame to an Excel file
#     df.to_excel(file_name, index=False)
#
#
# file_name = "checkpoint.xlsx"
# write_lists_to_excel(unique_list, links, file_name)


