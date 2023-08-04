import streamlit as st
from annotated_text import annotated_text
from utils import iso_to_how_long_ago

import os
import requests

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=80)


API_KEY = os.environ['NYT_API_KEY']

NYT_URL = f"https://api.nytimes.com/svc/movies/v2/reviews/picks.json?api-key={API_KEY}"
ATTRIBUTION = "[Data provided by The New York Times](https://developer.nytimes.com)"

CLAPPING = "\U0001F44F"
MOVIE_CAMERA = "\U0001F3A5"
LAST_TRACK = "\u23ee\ufe0f"
NEXT_TRACK = "\u23ed\ufe0f"
APP_NAME = "Critics\u2019 Picks"

menu_items = {
  "About": "Data provided by The New York Times"
}


@st.cache_data
def fetch(url, offset):
    print("fetch...")
    object = {}
    response = requests.get(url + f"&offset={offset}")
    if response.status_code == 200:
        object = response.json()
    return object


@st.cache_resource
def get_image_url(article):
    print("get_image_url")
    return article['multimedia']['src']


def show_controls(show_header=True):
    left_col, mid_col, right_col = st.columns([10, 1, 1])

    with left_col:
        if show_header:
            st.header(f"{APP_NAME} {MOVIE_CAMERA}")

    with mid_col:
        if st.button(LAST_TRACK):
            if st.session_state['offset'] >= 20:
                st.session_state["offset"] -= 20
                st.experimental_rerun()
    with right_col:
        if st.button(NEXT_TRACK):
            if st.session_state['has_more']:
                st.session_state["offset"] += 20
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
        with right_col:
            st.write(iso_to_how_long_ago(article['publication_date']))
            st.subheader(article['display_title'])
            st.write(article['summary_short'])
        st.divider()


def show_images(object):
    if 'results' not in object:
        print("No images")
        st.session_state["has_more"] = False
        return

    list_of_articles = object['results']

    if list_of_articles == None:
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

    st.markdown(ATTRIBUTION)


def main():
    st.set_page_config(APP_NAME, layout="centered", page_icon=MOVIE_CAMERA, menu_items=menu_items)

    if "offset" not in st.session_state:
        st.session_state["offset"] = 0
        st.session_state["has_more"] = True

    object = fetch(NYT_URL, st.session_state['offset'])
    # TODO: check for "status" field in object?
    st.session_state["has_more"] = object.get('has_more', False)

    view(object)

if __name__ == "__main__":
    main()
