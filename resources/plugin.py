# -*- coding: utf-8 -*-
# Module: plugin
# Author: crmartinez
# Colaborator: oleksis
# Created on: 18.3.2021
# Modified on: 18.6.2021


import sys
from time import sleep
from urllib.parse import parse_qsl, unquote_plus, urlencode

import requests
import xbmc
import xbmcgui
import xbmcplugin

# Free sample videos are provided by www.picta.cu
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {
    "Canales": [],
    "Documentales": [],
    "Peliculas": [],
    "Musicales": [],
    "Series": [],
}

ROOT_BASE_URL = "https://www.picta.cu/"
API_BASE_URL = "https://api.picta.cu/v2/"

# TODO: Manage requests.exceptions.ConnectionError


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    # Get the plugin url in plugin:// notation.
    _url = sys.argv[0]
    return f"{_url}?{urlencode(kwargs)}"


def get_categories():

    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: list
    """
    return VIDEOS.keys()


def get_likes(video):
    reproducciones = video.get("cantidad_reproducciones", 0)
    me_gusta = video.get("cantidad_me_gusta", 0)
    no_me_gusta = video.get("cantidad_no_me_gusta", 0)
    comentarios = video.get("cantidad_comentarios", 0)
    descargas = video.get("cantidad_descargas", 0)

    return f"► {reproducciones} · ♥ {me_gusta} · ▼ {descargas}"


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or API.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    result = {}
    next_page = 1
    # TODO: REFACTOR: ListItem with next
    while next_page:
        url_docum = f"{API_BASE_URL}publicacion/?page={next_page}&tipologia_nombre_raw=Documental&ordering=-fecha_creacion"
        url_pelic = f"{API_BASE_URL}publicacion/?page={next_page}&tipologia_nombre_raw=Pel%C3%ADcula&ordering=-fecha_creacion"
        url_musicales = f"{API_BASE_URL}publicacion/?page={next_page}&tipologia_nombre_raw=Video%20Musical&ordering=-fecha_creacion"

        if category == "Documentales":
            r = requests.get(url_docum)
            result = r.json()
        elif category == "Peliculas":
            r = requests.get(url_pelic)
            result = r.json()
        elif category == "Musicales":
            r = requests.get(url_musicales)
            result = r.json()

        for v in result["results"]:
            generos = ""
            likes = get_likes(v)

            if category == "Musicales":
                generos = ", ".join(
                    g["nombre"] for g in v["categoria"]["video"]["genero"]
                )
            elif category == "Peliculas":
                generos = ", ".join(
                    g["nombre"] for g in v["categoria"]["pelicula"]["genero"]
                )

            VIDEOS[category].append(
                {
                    "name": f'{v["nombre"]}\n{likes}',
                    "thumb": v["url_imagen"] + "_380x250",
                    "video": v["url_manifiesto"],
                    "genre": generos,
                    "plot": v["descripcion"],
                    "sub": v["url_subtitulo"],
                }
            )

        next_page = result.get("next")
        # Avoid rate limit (seconds/request)
        sleep(1 / 20)

    return VIDEOS[category]


def get_series():

    next_page = 1
    # TODO: REFACTOR: ListItem with next
    while next_page:
        url_series = f"{API_BASE_URL}serie/?page={next_page}&ordering=-id"
        r = requests.get(url_series)
        result = r.json()

        for v in result["results"]:
            generos = ", ".join(g["nombre"] for g in v["genero"])

            VIDEOS["Series"].append(
                {
                    "name": v["nombre"],
                    "id": v["pelser_id"],
                    "thumb": v["imagen_secundaria"] + "_380x250",
                    "genre": generos,
                    "cant_temp": v["cantidad_temporadas"],
                }
            )

        next_page = result.get("next")
        # Avoid rate limit (seconds/request)
        sleep(1 / 20)

    return VIDEOS["Series"]


def get_episodes(id, temp):

    EPISODIOS = []
    url_temp = f"{API_BASE_URL}temporada/?serie_pelser_id={id}&ordering=nombre"
    r = requests.get(url_temp)
    result = r.json()

    try:
        t = int(temp)
        temp_id = result["results"][t]["id"]
        size = result["results"][t]["cantidad_capitulos"]

        url_publicacion = f"{API_BASE_URL}publicacion/?temporada_id={temp_id}&page=1&page_size={size}&ordering=nombre"
        r = requests.get(url_publicacion)
        result = r.json()

        for e in result["results"]:
            generos = ", ".join(
                g["nombre"]
                for g in e["categoria"]["capitulo"]["temporada"]["serie"]["genero"]
            )
            likes = get_likes(e)

            EPISODIOS.append(
                {
                    "name": f'{e["nombre"]}\n{likes}',
                    "thumb": e["url_imagen"] + "_380x250",
                    "video": e["url_manifiesto"],
                    "genre": generos,
                    "plot": e["descripcion"],
                    "sub": e["url_subtitulo"],
                }
            )
    except IndexError:
        xbmc.executebuiltin(
            "Notification(Aviso,La temporada todavía no se encuentra disponible,5000)"
        )

    return EPISODIOS


def get_canales():

    next_page = 1
    # TODO: REFACTOR: ListItem with next
    while next_page:
        url_canales = f"{API_BASE_URL}canal/?page={next_page}&ordering=-cantidad_suscripciones&nombre="
        r = requests.get(url_canales)
        result = r.json()

        for ch in result["results"]:
            VIDEOS["Canales"].append(
                {
                    "name": ch["nombre"],
                    "id": ch["id"],
                    "thumb": ch["url_imagen"] + "_380x250",
                    "plot": ch["descripcion"],
                }
            )

        next_page = result.get("next")
        # Avoid rate limit (seconds/request)
        sleep(1 / 20)

    return VIDEOS["Canales"]


def get_canales_videos(canal_nombre_raw):
    VIDEOS = []

    next_page = 1
    # TODO: REFACTOR: ListItem with next
    while next_page:
        url_canal_videos = f"{API_BASE_URL}publicacion/?canal_nombre_raw={canal_nombre_raw}&page={next_page}"
        r = requests.get(url_canal_videos)
        result = r.json()

        for v in result["results"]:
            # Videos diferentes tipologias no siempre tienen genero
            likes = get_likes(v)
            VIDEOS.append(
                {
                    "name": f'{v["nombre"]}\n{likes}',
                    "thumb": v["url_imagen"] + "_380x250",
                    "video": v["url_manifiesto"],
                    "genre": "",
                    "plot": v["descripcion"],
                    "sub": v["url_subtitulo"],
                }
            )

        next_page = result.get("next")
        # Avoid rate limit (seconds/request)
        sleep(1 / 20)

    return VIDEOS


def list_categories(handle):
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(handle, "Categorías")
    categories = get_categories()

    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        #  list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
        #                  'icon': VIDEOS[category][0]['thumb'],
        #                  'fanart': VIDEOS[category][0]['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        #   list_item.setInfo('video', {'title': category,
        #                          'genre': category,
        #                         'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.picta/?action=listing&category=Series
        url = get_url(action="listing", category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(handle)


def set_video_list(handle, video):
    """
    Set Info and Directory to ListItem

    Note: video have 6 keys: "name", "thumb", "video", "genre", "plot", "sub"
    """
    list_item = xbmcgui.ListItem(label=video["name"])
    list_item.setInfo(
        "video",
        {
            "title": video["name"],
            "genre": video["genre"],
            "plot": video["plot"],
            "mediatype": "video",
        },
    )
    list_item.setSubtitles([video["sub"]])
    list_item.setArt(
        {"thumb": video["thumb"], "icon": video["thumb"], "fanart": video["thumb"]}
    )
    list_item.setProperty("IsPlayable", "true")
    url = get_url(action="play", video=video["video"])
    is_folder = False
    xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)


def list_videos(handle, category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    xbmcplugin.setPluginCategory(handle, category)

    videos = get_videos(category)

    for video in videos:
        set_video_list(handle, video)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(handle)


def list_series(handle):

    xbmcplugin.setPluginCategory(handle, "Series")

    xbmcplugin.setContent(handle, "tvshows")

    series = get_series()

    for serie in series:
        list_item = xbmcgui.ListItem(label=serie["name"])
        list_item.setInfo(
            "video",
            {"title": serie["name"], "genre": serie["genre"], "mediatype": "tvshow"},
        )
        list_item.setArt(
            {"thumb": serie["thumb"], "icon": serie["thumb"], "fanart": serie["thumb"]}
        )
        url = get_url(
            action="getSeasons",
            id=serie["id"],
            temp=serie["cant_temp"],
            name=serie["name"],
        )
        is_folder = True
        xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(handle)


def list_canales(handle):

    xbmcplugin.setPluginCategory(handle, "Canales")

    canales = get_canales()

    for canal in canales:
        list_item = xbmcgui.ListItem(label=canal["name"])
        list_item.setInfo(
            "video",
            {"title": canal["name"], "plot": canal["plot"], "mediatype": "video"},
        )
        list_item.setArt(
            {"thumb": canal["thumb"], "icon": canal["thumb"], "fanart": canal["thumb"]}
        )
        url = get_url(action="getChannelVideos", canal_nombre_raw=canal["name"])
        is_folder = True
        xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(handle)


def list_channel_videos(handle, canal_nombre_raw):

    xbmcplugin.setPluginCategory(handle, unquote_plus(canal_nombre_raw))

    videos = get_canales_videos(canal_nombre_raw)

    for video in videos:
        set_video_list(handle, video)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(handle)


def list_seasons(handle, pelser_id, temporada, name):

    xbmcplugin.setPluginCategory(handle, name)
    xbmcplugin.setContent(handle, "season")

    cant_temp = int(temporada) + 1

    for i in range(cant_temp):
        name = f"Temporada {i + 1}"
        list_item = xbmcgui.ListItem(label=name)
        url = get_url(action="getEpisodes", serie_id=pelser_id, temp=i, name=name)
        is_folder = True
        xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(handle)


def list_episodes(handle, serie_id, temp, name):

    xbmcplugin.setPluginCategory(handle, name)
    xbmcplugin.setContent(handle, "episodes")

    episodes = get_episodes(serie_id, temp)

    for video in episodes:
        set_video_list(handle, video)

    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(handle)


def play_video(handle, path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # TODO: Add support for HLS(m3u8)
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    play_item.setContentLookup(False)
    play_item.setMimeType("application/xml+dash")
    play_item.setProperty("inputstream", "inputstream.adaptive")
    play_item.setProperty("inputstream.adaptive.manifest_type", "mpd")
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Get the plugin handle as an integer number.
    handle = int(sys.argv[1])
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(handle, "videos")

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if not params:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories(handle)
        return None

    if params["action"] == "listing":
        # Display the list of videos in a provided category.
        if params["category"] == "Series":
            list_series(handle)
        elif params["category"] == "Canales":
            list_canales(handle)
        else:
            list_videos(handle, params["category"])
    elif params["action"] == "getSeasons":
        list_seasons(handle, params["id"], params["temp"], params["name"])
    elif params["action"] == "getEpisodes":
        list_episodes(handle, params["serie_id"], params["temp"], params["name"])
    elif params["action"] == "getChannelVideos":
        list_channel_videos(handle, params["canal_nombre_raw"])
    elif params["action"] == "play":
        # Play a video from a provided URL.
        play_video(handle, params["video"])
    else:
        # If the provided paramstring does not contain a supported action
        # we raise an exception. This helps to catch coding errors,
        # e.g. typos in action names.
        raise ValueError(
            "Invalid paramstring: {0} debug: {1}".format(paramstring, params)
        )


def run():
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
