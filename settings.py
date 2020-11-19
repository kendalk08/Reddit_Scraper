"""
This is the settings file for all the programs in Reddit_Scraper
"""

def returnSettings():
    settings = {
        # slideshow_height/width = starting size of slideshow app
        "slideshow_height": 900,
        "slideshow_width": 900,
        # change slideshow pause time
        "slideshow_wait": 2,
        # change default limit of all sub downloads
        "all_query_limit": 25,
        # change default limit for new sub downloads
        "new_query_limit": 50,
        # change default limit for big sub downloads
        "big_query_limit": 30,
        # change default limit for small sub downloads
        "small_query_limit": 10,
        # change default limit for junk folders, Default = 1
        "file_limit": 1
    }
    return settings
