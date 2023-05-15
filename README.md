# pytvdb

My Tvdb interface classes

Setup:
Create a file in your user settings folder aand subdirectory dmlane
``[tvdb]
api_key='Your API key'
api_pin='Your API pin' ``

Usage:
- Setup favourites on TVDB
- run tvdb_refresh_cache
- pull the data into your program by calling MyTVDB.get_tvdb_data(slug)

Provided 2 commands:
tvdb_refresh_cache - Pulls favourites from TVDB into a local cache
tvdb_print_slugs - Print slugs from the cache
