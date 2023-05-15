""" Test the MyTVDB class."""
import os
import sys

import pytest
from pycommon import MyException, config

from pytvdb.my_tvdb import Movie, MyTVDB, Series

THE_POSTMAN = 7606  # "The Postman" was released in Italian - good film to work with
THE_GLORY = 411469  # "The Glory" was released in Korean - TV Series

# pylint: disable=protected-access


def test_connection(capsys):
    """Test the connect function"""
    my_tvdb = MyTVDB()
    my_tvdb._connect()
    if "Please add the following keys" in capsys.readouterr().out:
        sys.exit(1)
    assert my_tvdb.api is not None


def test_wrong_credntials():
    """Test the connect function with wrong credentials"""
    my_tvdb = MyTVDB()
    config.tvdb.api_pin = "wrong_pin"
    with pytest.raises(MyException) as exc:
        my_tvdb._connect()
    assert "Could not connect to TVDB" in str(exc.value)


def test_fetch_movie():
    """Test the fetch_movies function"""
    my_tvdb = MyTVDB()
    my_tvdb._connect()
    slug, result = my_tvdb._fetch_movie(tvdb_id=THE_POSTMAN)
    assert slug == "the-postman-1994" and isinstance(result, Movie)


def test_fetch_series():
    """Test the fetch_series function"""
    my_tvdb = MyTVDB()
    my_tvdb._connect()
    slug, result = my_tvdb._fetch_series(tvdb_id=THE_GLORY)  # pylint: disable=protected-access
    assert slug == "the-glory" and isinstance(result, Series) and len(result.episodes) == 16


def test_fetch_favourites():
    """Test the fetch_vaourites function"""
    my_tvdb = MyTVDB()
    my_tvdb._connect()
    try:
        my_tvdb._fetch_favourites()
    except MyException as exc:
        pytest.fail("Unexpected MyException " + str(exc))


def test_refresh_cache():
    """Test the refresh_cache function"""
    my_tvdb = MyTVDB()
    my_tvdb._connect()
    temp_cache = "/tmp/test_cache.pickle"
    my_tvdb._fetch_all_data(
        {"series": [THE_GLORY], "movies": [THE_POSTMAN]},
        cache_file=temp_cache,
    )
    assert os.path.isfile(temp_cache) and my_tvdb.data != {}


def test_load_cache():
    """Test the load_cache function"""

    my_tvdb = MyTVDB()
    my_tvdb._connect()
    temp_cache = "/tmp/test_cache.pickle"
    my_tvdb._load_cache(cache_file=temp_cache)
    assert my_tvdb.data != {}


def test_print_slugs(capsys):
    """Test the print_slugs function"""
    my_tvdb = MyTVDB()
    my_tvdb._connect()
    temp_cache = "/tmp/test_cache.pickle"
    my_tvdb.print_slugs(cache_file=temp_cache)
    captured = capsys.readouterr()

    assert (
        "the-glory: Series: The Glory" in captured.out
        and "the-postman-1994:  Movie:" in captured.out
    )


# def test_get_movie_from_db():
#     """Test the get_movies function"""
#     # "The Postman" was released in Italian - good one to work with
#     tvdb_id = 7606
#     cache_file = f"{CACHE_DIR}/movie_{tvdb_id}.pickle"
#     if os.path.exists(cache_file):
#         os.remove(cache_file)
#
#     my_tvdb = MyTVDB(action="M", tvdb_id=7606)
#     assert len(my_tvdb.movies) == 1 and os.path.exists(cache_file) and not my_tvdb.cached_fetch
#
#
# def test_get_movie_from_cache():
#     """Test the get_movies function"""
#     # "The Postman" was released in Italian - good one to work with
#     tvdb_id = 7606
#     cache_file = f"{CACHE_DIR}/movie_{tvdb_id}.pickle"
#     my_tvdb = MyTVDB(action="M", tvdb_id=7606)
#     assert len(my_tvdb.movies) == 1 and os.path.exists(cache_file) and my_tvdb.cached_fetch
