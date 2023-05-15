""" Handle interactions with TVDB database
    Refresh_cache will pull favourites from TVDB and store them for use.
    All other accesses will pull from the cache itself.
"""


import os
import pickle
import sys
from dataclasses import dataclass, field

import appdirs
import tvdb_v4_official
from pycommon import MyException, config

CACHE_DIR = appdirs.user_cache_dir("net.dmlane/tvdb.cache")
CONFIG_DIR = appdirs.user_config_dir(appname="dmlane")
os.makedirs(CACHE_DIR, exist_ok=True)


@dataclass(eq=False)
class Episode:
    """Structure for storing episode information"""

    tvdb_id: int
    season_number: int
    episode_number: int
    name: str = None
    overview: str = None
    run_time: int = 0
    image_url: str = None


@dataclass(eq=False)
class Series:
    """Structure for storing series information"""

    tvdb_id: int
    name: str
    image_url: str = None
    episodes: list[Episode] = field(default_factory=list)


@dataclass(eq=False)
class Movie:
    """Structure for storing movie information"""

    tvdb_id: int
    name: str = None
    overview: str = None
    runtime: int = 0
    image_url: str = None


class MyTVDB:
    """Fetch information from TVDB."""

    def __init__(self):
        config.load_toml_file(package_name="pytvdb")
        if not (hasattr(config.tvdb, "api_key") and hasattr(config.tvdb, "api_pin")):
            config_file = appdirs.user_config_dir("dmlane", "dave") + "/settings.toml"
            print(f"Please add the following keys to {config_file}:")
            print("[tvdb]\napi_key='Your API key'\napi_pin='Your API pin'\n")
            sys.exit(1)

        # self.validate_action(action, tvdb_id)
        self.api = None
        self.cache_file = f"{CACHE_DIR}/favourites.pickle"
        self.data = {}

    def refresh_cache(self):
        """Fetch favourites from TVDB"""
        self._connect()
        favourites = self._fetch_favourites()
        self._fetch_all_data(favourites)

    def _connect(self):
        """Connect to TVDB API"""

        try:
            self.api = tvdb_v4_official.TVDB(config.tvdb.api_key, config.tvdb.api_pin)
        except Exception as inst:  # pylint: disable=broad-except
            raise MyException("Could not connect to TVDB") from inst

    def load_cache(self, cache_file=None):
        """Load favourites from cache"""
        if cache_file is not None:
            self.cache_file = cache_file
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as file:
                self.data = pickle.load(file)
        else:
            raise MyException(f"Cache file {self.cache_file} does not exist")

    def _fetch_all_data(self, favourites, cache_file=None):
        """Fetch all data from TVDB using favourites"""
        self.data = {}
        for tvdb_id in favourites["series"]:
            slug, result = self._fetch_series(tvdb_id)
            self.data[slug] = result
        for tvdb_id in favourites["movies"]:
            slug, result = self._fetch_movie(tvdb_id)
            self.data[slug] = result
        if cache_file is not None:
            self.cache_file = cache_file
        with open(self.cache_file, "wb") as file:
            pickle.dump(self.data, file)

    def _fetch_favourites(self):
        """Fetch favourites from TVDB"""
        url = self.api.url.construct("user/favorites")
        favourites = self.api.request.make_request(url)
        if favourites is None:
            raise MyException("Could not fetch favourites from TVDB")
        return favourites

    def _fetch_movie(self, tvdb_id: int):
        """Fetch movie from TVDB"""
        print(f"Fetching movie {tvdb_id} ", end="", flush=True)
        data = self.api.get_movie(tvdb_id)
        print(f" '{data['slug']}' .......... ", end="", flush=True)
        translations = self.api.get_movie_translation(tvdb_id, lang="eng")
        result = Movie(
            tvdb_id=tvdb_id,
            name=translations["name"],
            overview=translations["overview"],
            runtime=data["runtime"],
            image_url=data["image"],
        )
        print(" Done")
        return data["slug"], result

    def _fetch_series(self, tvdb_id: int):
        """Fetch series from TVDB"""
        # cache_file = f"{CACHE_DIR}/series_{tvdb_id}.pickle"
        # try:
        #     with open(cache_file, "rb") as handle:
        #         return pickle.load(handle)
        # except FileNotFoundError:
        #     pass
        print(f"Fetching series {tvdb_id} ", end="", flush=True)
        data = self.api.get_series_extended(tvdb_id)
        print(f" '{data['slug']}' .......... ", end="", flush=True)
        translations = self.api.get_series_translation(tvdb_id, lang="eng")

        result = Series(
            tvdb_id=tvdb_id,
            name=translations["name"],
            image_url=data["image"],
            episodes=self.fetch_episodes(tvdb_id),
        )
        # with open(cache_file, "wb") as file:
        #     pickle.dump(result, file)
        print(" Done")
        return data["slug"], result

    def print_slugs(self, cache_file=None):
        """Print slugs"""
        if cache_file is not None:
            self.cache_file = cache_file
        self.load_cache()
        print("Listing series and files from cache")
        maxwidth = 0
        for slug, _ in self.data.items():
            if len(slug) > maxwidth:
                maxwidth = len(slug)

        for slug, result in sorted(self.data.items()):
            if isinstance(result, Series):
                print(f"{slug:>{maxwidth}}: Series: {result.name}")
            else:
                print(f"{slug:>{maxwidth}}:  Movie: {result.name}")

    def fetch_episodes(self, tvdb_id: int):
        """Fetch episodes from TVDB"""
        data = self.api.get_series_episodes(id=tvdb_id)
        results = []
        for episode in data["episodes"]:
            if episode["seasonNumber"] > 0:
                if episode["number"] > 0:
                    translations = self.api.get_episode_translation(episode["id"], lang="eng")

                    results.append(
                        Episode(
                            tvdb_id=episode["id"],
                            season_number=episode["seasonNumber"],
                            episode_number=episode["number"],
                            run_time=episode["runtime"],
                            image_url=episode["image"],
                            name=translations["name"],
                            overview=translations["overview"],
                        )
                    )

        return results


def refresh_cache():
    """Refresh cache"""
    handler = MyTVDB()
    handler.refresh_cache()
