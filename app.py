import streamlit as st
from annotated_text import annotated_text
from utils import iso_to_how_long_ago

from urllib.parse import quote


import os
import requests

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=80)

API_KEY = os.environ['NYT_API_KEY']

NYT_URL = f"https://api.nytimes.com/svc/movies/v2/reviews/picks.json?api-key={API_KEY}"

APP_NAME = "Critics\u2019 Picks"
ATTRIBUTION = "[Data provided by The New York Times](https://developer.nytimes.com)"

MOVIE_CAMERA = "\U0001F3A5"
LAST_TRACK = "\u23ee\ufe0f"
NEXT_TRACK = "\u23ed\ufe0f"


LEFT_POINTING_TRIANGLE  = "\u25c0"
RIGHT_POINTING_TRIANGLE = "\u25b6"

BATCH_SIZE = 20

HTTP_RESPONSE_TOO_MANY_REQUESTS = 429


@st.cache_data(show_spinner="Fetching data from API...")
def fetch(url, offset):
    print("fetching, offset:", offset)
    object = {}
    response = requests.get(url + f"&offset={offset}")

    # If not status code == 200
    # Raise an exception

    if response.status_code == 200:
        object = response.json()
    elif response.status_code == HTTP_RESPONSE_TOO_MANY_REQUESTS:
        print("Response: Too Many Requests")
        raise Exception("Request Failed")
    else:
        print(f"response.state_code {response.status_code}")
        raise Exception("Request Failed")

    return object


@st.cache_resource
def get_image_url(article):
    print("get_image_url")
    return article['multimedia']['src']


def show_controls(show_header=True):
    key_prev_page = "prev_page"
    key_next_page = "next_page"

    if show_header:
        key_prev_page += "_header"
        key_next_page += "_header"

    left_col, mid_col, right_col = st.columns([10, 1, 1])

    with left_col:
        if show_header:
            st.header(f"{APP_NAME} {MOVIE_CAMERA}")

    with mid_col:
        if st.button(LEFT_POINTING_TRIANGLE, key=key_prev_page):
            if st.session_state['offset'] >= BATCH_SIZE:
                st.session_state["offset"] -= BATCH_SIZE
                st.experimental_rerun()
    with right_col:
        if st.button(RIGHT_POINTING_TRIANGLE, key=key_next_page):
            if st.session_state['has_more']:
                st.session_state["offset"] += BATCH_SIZE
                st.experimental_rerun()


def show_picks(object):
    if 'results' not in object:
        print("No Articles")
        st.session_state["has_more"] = False
        return

    for article in object.get('results', []):
        left_col, mid_col, right_col = st.columns([2, 1, 4])
        with left_col:
            if 'multimedia' in article and 'src' in article['multimedia']:
                st.image(get_image_url(article))
            else:
                print("missing image!!!")
        with right_col:
            st.write(iso_to_how_long_ago(article['publication_date']))

            display_title = article['display_title']
            encoded_display_title = quote(display_title)
            st.markdown(f"### [{display_title}](https://www.imdb.com/find/?s=tt&q={encoded_display_title})")

            st.write(article['summary_short'])

            if len(article['mpaa_rating']):
                annotated_text((article['mpaa_rating'], "mpaa rating"))

        st.divider()


def show_images(object):
    if 'results' not in object:
        print("No images")
        st.session_state["has_more"] = False
        return

    list_of_articles = object['results']

    if list_of_articles is None:
        print("can't find articles")
        return

    count = len(list_of_articles)
    for i in range(0, count, 4):
        cols = st.columns(4)
        for i, article in enumerate(list_of_articles[i:i+4]):
            cols[i].image(get_image_url(article))
    st.divider()


def view(object):
    show_controls()

    st.write("Tracking recent movies selected by The New York Time\u2019s Movie Critics")

    tabs = st.tabs(["Their Picks", "Related Images"])
    with tabs[0]:
        show_picks(object)
    with tabs[1]:
        show_images(object)

    show_controls(show_header=False)
    st.markdown(ATTRIBUTION)


def main():
    st.set_page_config(APP_NAME, layout="centered", page_icon=MOVIE_CAMERA,
                       menu_items={
                           "About": "Data provided by The New York Times"
                       })

    if "offset" not in st.session_state:
        st.session_state["offset"] = 0
        st.session_state["has_more"] = True

    print("offset:", st.session_state['offset'])

    try:
        object = fetch(NYT_URL, st.session_state['offset'])
        # TODO: check for "status" field in object?
        st.session_state["has_more"] = object.get('has_more', False)
    except Exception as e:
        print(f"Exception caught: {e}")
        st.session_state['offset'] = 0
        object = fetch(NYT_URL, st.session_state['offset'])

    view(object)


if __name__ == "__main__":
    main()
