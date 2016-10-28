"""Helpers for Homework 03 of ADA"""

import requests
import bs4
import googlemaps
import numpy as np
import pandas as pd


def get_google_soup(query):
    """Get a BeautifulSoup object for Google results page."""

    base_url = "https://www.google.ch/search"
    params = {'q': query}
    response = requests.get(base_url, params)
    return bs4.BeautifulSoup(response.text, "html.parser")


def get_info(university_name, swiss_cantons):
    """Get location information about a university, given a name and the list
    of valid cantons codes. Returns a tuple :
        (name, address, latitude, longitude, canton)

    The canton is retrieved following this method :
    1. We scrape the Google results page to find an address
    2. If an address is found, we use Google Geocoding API to get the GPS
       coordinates and the canton code

    If the search does not give result, return NaNs.
    """

    address = np.nan
    lat = np.nan
    lng = np.nan
    code = np.nan

    # 1 : Scrape Google results to find an address
    name_split = university_name.split('-')[0].strip() # omit abbreviations
    soup = get_google_soup(name_split)
    spans = soup.find_all('span', {'class': '_tA'})
    if len(spans) != 0:
        span = spans[0]
        address = span.text

        # 2 : Use Geocoding API to get extra information from the address
        with open('api-key.txt', 'r') as api_file:
            api_key = api_file.read().replace('\n', '') # api key for Google API
        gmaps = googlemaps.Client(key=api_key)
        geocode_result = gmaps.geocode(address)

        # Extract info from Geocoding result
        if len(geocode_result) != 0:
            result = geocode_result[0]
            geometry = result['geometry']
            if len(geometry) != 0:
                location = geometry['location']
                if len(location) != 0:
                    lat, lng = location['lat'], location['lng']

            for component in result['address_components']:
                types = component['types']
                if 'administrative_area_level_1' in types:
                    code = component['short_name']
                    if code in swiss_cantons:
                        return university_name, address, lat, lng, code

    return university_name, address, lat, lng, np.nan


def build_df(universities, swiss_cantons):
    """Build a DataFrame containing location data for universities"""

    cols = ['university', 'address', 'latitude', 'longitude', 'canton']
    uni_df = pd.DataFrame(columns=cols)

    num_iter = 1
    for university in universities:
        print("\rSearching for cantons... {}/{}".format(num_iter,
            len(universities)), end='', flush=True)
        num_iter = num_iter + 1
        if pd.notnull(university):
            info = list(get_info(university, swiss_cantons))
            row = pd.DataFrame([info], columns=cols)
            uni_df = pd.concat([uni_df, row], ignore_index=True)

    return uni_df
