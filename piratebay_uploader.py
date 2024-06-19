#!/usr/bin/env python3

# upload torrents to thepiraetbay.org

# based on
# https://github.com/genericclient/genericclient-aiohttp/raw/master/genericclient_aiohttp/__init__.py
# https://old.reddit.com/r/learnpython/comments/12ershy/how_to_maintain_a_single_aiohttp_session_for_all/



import os
import re
import sys
import uuid
import asyncio

import aiohttp
import aiohttp_socks



# TODO update
# generated by docs/categories.json.py
upload_categories = {
    "Audio": {
        "Music": 101,
        "Audio books": 102,
        "Sound clips": 103,
        "FLAC": 104,
        "Other": 199
    },
    "Video": {
        "Movies": 201,
        "Movies DVDR": 202,
        "Music videos": 203,
        "Movie clips": 204,
        "TV shows": 205,
        "Handheld": 206,
        "HD - Movies": 207,
        "HD - TV shows": 208,
        "3D": 209,
        "CAM/TS": 210,
        "UHD/4k - Movies": 211,
        "UHD/4k - TV shows": 212,
        "Other": 299
    },
    "Applications": {
        "Windows": 301,
        "Mac": 302,
        "UNIX": 303,
        "Handheld": 304,
        "IOS (iPad/iPhone)": 305,
        "Android": 306,
        "Other OS": 399
    },
    "Games": {
        "PC": 401,
        "Mac": 402,
        "PSx": 403,
        "XBOX360": 404,
        "Wii": 405,
        "Handheld": 406,
        "IOS (iPad/iPhone)": 407,
        "Android": 408,
        "Other": 499
    },
    "Porn": {
        "Movies": 501,
        "Movies DVDR": 502,
        "Pictures": 503,
        "Games": 504,
        "HD - Movies": 505,
        "Movie clips": 506,
        "UHD/4k - Movies": 507,
        "Other": 599
    },
    "Other": {
        "E-books": 601,
        "Comics": 602,
        "Pictures": 603,
        "Covers": 604,
        "Physibles": 605,
        "Other": 699
    }
}



def get_category_id(name):
    a, b = name.split(">")
    a = a.strip()
    b = b.strip()
    if not a in upload_categories:
        return
    if not b in upload_categories[a]:
        return
    return upload_categories[a][b]

def get_category_name(id):
    id = int(id)
    for a in upload_categories:
        for b in upload_categories[a]:
            if upload_categories[a][b] == id:
                return f"{a} > {b}"

def print_categories():
    for a in upload_categories:
        for b in upload_categories[a]:
            id = upload_categories[a][b]
            print(f"{id} = {a} > {b}")



class LoginError(Exception):
    pass

class UploadError(Exception):
    pass



class PiratebayUploader:

    """a client for thepiraetbay.org with focus on uploading torrents"""

    def __init__(
            self,
            username,
            password,
            tor_user=None,
            # the default system-wide tor proxy
            tor_host="127.0.0.1",
            tor_port=9050,
        ):

        self.username = username
        self.password = password
        if not tor_user:
            # random username to get a new tor circuit (tor identity)
            tor_user = str(uuid.uuid4())
        self.proxy_url = f"socks5://{tor_user}@{tor_host}:{tor_port}"
        self.base_url = "http://piratebayo3klnzokct3wt5yyxb2vpebbuyjl7m623iaxmqhsd52coid.onion"

    async def __aenter__(self):

        connector = aiohttp_socks.ProxyConnector.from_url(self.proxy_url)

        # TODO cache the cookies in ~/.cache/piratebay_uploader/cookies.json
        self.cookie_jar = aiohttp.CookieJar(quote_cookie=False)

        self.session = aiohttp.ClientSession(
            connector=connector,
            cookie_jar=self.cookie_jar,
        )

        return self

    async def __aexit__(self, *args, **kwargs):

        if not self.session.closed:
            await self.session.__aexit__(*args, **kwargs)

    async def login(
            self,
            username=None,
            password=None,
        ):

        # TODO retry requests on "502 Bad Gateway"

        # TODO check if we are already logged in
        # what is the duration of a login session? 1 hour? 1 day?

        username = username or self.username
        password = password or self.password
        assert username and password, "login requires username and password"

        url = self.base_url + "/session/"

        # docs/forms/login.html

        data = dict(
            username=username,
            password=password,
            act="login",
        )

        async with self.session.post(url, data=data) as response:

            html = await response.text()

            if response.status != 200 or not '<h1><label id="toptxt">Welcome back' in html:

                errors = re.findall('<font color="red">(.*?)</font>', html, re.S)

                errors = list(map(lambda s: s.strip(), errors))

                raise LoginError(" ".join(errors))

            print("login ok")

    async def upload_torrent(
            self,
            torrent_file,
            description,
            category="Other > Other",
            anonymous=False,
        ):

        # validate input

        category_id = None
        if isinstance(category, int) or (
                isinstance(category, str) and re.fullmatch("[0-9]+", category)
            ):
            category_id = category
            category_name = get_category_name(category_id)
            if category_name is None:
                raise ValueError(f"invalid category id {category!r}")
        elif isinstance(category, str):
            category_id = get_category_id(category)
            if category_id is None:
                raise ValueError(f"invalid category name {category!r}")

        # TODO validate the torrent file
        # for example, the title must not be longer than 80 chars (or 80 bytes)
        # https://forum.suprbay.org/Thread-ThePirateBay-Error-Upload-error4?pid=401482#pid401482

        await self.login()

        # docs/forms/upload.html

        data = dict(
            cate=str(category_id),
            desc=description,
            act="upload",
            torrent=open(torrent_file, "rb"),
        )

        if anonymous:
            data["anon"] = "anon"

        url = self.base_url + "/session/"

        async with self.session.post(url, data=data) as response:

            # TODO check for positive result
            # redirect to description page
            # https://thepiratebay.org/description.php?id=75584652

            html = await response.text()

            errors = re.findall('<font color="red">(.*?)</font>', html, re.S)

            errors = list(map(lambda s: s.strip(), errors))

            if response.status != 200 or len(errors) > 0:

                #print("upload Status:", response.status)
                #print("upload Content-type:", response.headers["content-type"])
                #print("upload errors:", errors)
                #print("upload body:", html)

                raise UploadError(" ".join(errors))

        print("upload ok")

        #print("upload body:", html)


async def main():

    import argparse

    parser = argparse.ArgumentParser()

    # TODO allow to read login from file
    parser.add_argument("-u", "--username")

    parser.add_argument("-p", "--password")

    # TODO also allow magnet link
    parser.add_argument("-f", "--torrent-file")

    parser.add_argument("-d", "--description")

    parser.add_argument("-c", "--category", default="Other > Other")

    parser.add_argument("--list-categories", action="store_true")

    parser.add_argument("-a", "--anonymous", action="store_true")

    # by default, we use the system-wide tor proxy at 127.0.0.1:9050
    #parser.add_argument("--start-tor", action="store_true")

    args = parser.parse_args()

    if args.list_categories:
        return print_categories()

    if not args.torrent_file:
        print("error: torrent file is required")
        sys.exit(1)

    if not args.description:
        print("error: description is required")
        sys.exit(1)

    kwargs = dict(
        username = args.username,
        password = args.password,
    )

    async with PiratebayUploader(**kwargs) as uploader:

        await uploader.upload_torrent(
            args.torrent_file,
            args.description,
            args.category,
            args.anonymous,
        )



if __name__ == "__main__":

    asyncio.run(main())
