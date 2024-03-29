# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import requests
import json


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {'Documentales': [],
            'Peliculas': [],
            'Musicales': [],
            'Series' : []}


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():

    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return VIDEOS.iterkeys()


def get_videos(category):

    url_docum = 'https://api.picta.cu/v2/publicacion/?page=1&tipologia_nombre_raw=Documental&ordering=-fecha_creacion'
    url_pelic = 'https://api.picta.cu/v2/publicacion/?page=1&tipologia_nombre_raw=Pel%C3%ADcula&ordering=-fecha_creacion'
    url_musicales = 'https://api.picta.cu/v2/publicacion/?page=1&tipologia_nombre_raw=Video%20Musical&ordering=-fecha_creacion'
    
    if category == 'Documentales':
        r = requests.get(url_docum)
        result = r.json()
        cant_page = result['count'] // 100 + 1
    elif category == 'Peliculas':
        r = requests.get(url_pelic)
        result = r.json()
        cant_page = result['count'] // 100 + 1
    elif category == 'Musicales':
        r = requests.get(url_musicales)
        result = r.json()
        cant_page = result['count'] // 100 + 1

    for v in result['results']:
        genero = ''
        if category == 'Musicales':
             for g in v['categoria']['video']['genero']:
                         genero = genero + '  ' + g['nombre']
        elif category == 'Peliculas':
             for g in v['categoria']['pelicula']['genero']:
                         genero = genero + '  ' + g['nombre']
             
        VIDEOS[category].append({'name': v['nombre'],
                                 'thumb': v['url_imagen']+'_380x250',
                                 'video': v['url_manifiesto'],
                                 'genre': genero,
                                 'plot': v['descripcion'],
                                 'sub': v['url_subtitulo']})
    
    if cant_page > 1:
        for i in range(cant_page - 1):
            if category == 'Documentales':
               url = 'https://api.picta.cu/v2/publicacion/?page='+str(i+2)+'&tipologia_nombre_raw=Documental&ordering=-fecha_creacion'                        
            if category == 'Peliculas':
                url = 'https://api.picta.cu/v2/publicacion/?page='+str(i+2)+'&tipologia_nombre_raw=Pel%C3%ADcula&ordering=-fecha_creacion'
            if category == 'Musicales':
                url = url_musicales = 'https://api.picta.cu/v2/publicacion/?page='+str(i+2)+'&tipologia_nombre_raw=Video%20Musical&ordering=-fecha_creacion'
            
            r = requests.get(url)
            result = r.json()
            for v in result['results']:
                 genero = ''
                 if category == 'Musicales':
                     for g in v['categoria']['video']['genero']:
                         genero = genero + '  ' + g['nombre']
                 elif category == 'Peliculas':
                      for g in v['categoria']['pelicula']['genero']:
                         genero = genero + '  ' + g['nombre']
                 
                 VIDEOS[category].append({'name': v['nombre'],
                                          'thumb': v['url_imagen']+'_380x250',
                                          'video': v['url_manifiesto'],
                                          'genre': genero,
                                          'plot': v['descripcion'],
                                          'sub': v['url_subtitulo']})
                              
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
    return VIDEOS[category]

def get_series():
    
    url_series = 'https://api.picta.cu/v2/serie/?page=1&ordering=-id'
    r = requests.get(url_series)
    result = r.json()
    cant_page = result['count'] // 100 + 1

    for v in result['results']:
        genero = ''
        for g in v['genero']:
             genero = genero + '  ' + g['nombre']
        VIDEOS['Series'].append({'name': v['nombre'],
                                 'id': v['pelser_id'],
                                 'thumb': v['imagen_secundaria']+'_380x250',
                                 'genre': genero,
                                 'cant_temp': v['cantidad_temporadas']})
    
    if cant_page > 1:
        for i in range(cant_page - 1):
            url = 'https://api.picta.cu/v2/serie/?page='+str(i+2)+'&ordering=-id'
            r = requests.get(url)
            result = r.json()
            for v in result['results']:
                 genero = ''
                 for g in v['genero']:
                     genero = genero + '  ' + g['nombre']
                 VIDEOS['Series'].append({'name': v['nombre'],
                                          'id': v['pelser_id'],
                                          'thumb': v['imagen_secundaria']+'_380x250',
                                          'genre': genero,
                                          'cant_temp': v['cantidad_temporadas']})
    
    return VIDEOS['Series']

def get_episodes(id, temp):

    EPISODIOS = []
    url_temp = 'https://api.picta.cu/v2/temporada/?serie_pelser_id='+id+'&ordering=nombre'
    r = requests.get(url_temp)
    result = r.json()
    
    try:
        t = int(temp)
        temp_id = result['results'][t]['id']
        size = result['results'][t]['cantidad_capitulos']

        url_publicacion = 'https://api.picta.cu/v2/publicacion/?temporada_id='+str(temp_id)+'&page=1&page_size='+str(size)+'&ordering=nombre' 
        r = requests.get(url_publicacion)
        result = r.json()
    
        for e in result['results']:
             EPISODIOS.append({'name': e['nombre'],
                               'thumb': e['url_imagen']+'_380x250',
                               'video': e['url_manifiesto'],
                               'plot': e['descripcion'],
                               'sub': e['url_subtitulo']})
    except IndexError:
        xbmc.executebuiltin('Notification(Aviso,La temporada todavía no se encuentra disponible,5000)')
    
    return EPISODIOS

def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
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
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['name'],
                                    'genre': video['genre'],
                                    'plot': video['plot'],
                                    'mediatype': 'video'})
        list_item.setSubtitles([video['sub']])
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)

def list_series():
    
     xbmcplugin.setPluginCategory(_handle, 'Series')

     xbmcplugin.setContent(_handle, 'tvshows')

     series = get_series()
     
     for serie in series:
         list_item = xbmcgui.ListItem(label=serie['name'])
         list_item.setInfo('video', {'title': serie['name'],
                                     'genre': serie['genre'],
                                     'mediatype': 'tvshow'})
         list_item.setArt({'thumb': serie['thumb'], 'icon': serie['thumb'], 'fanart': serie['thumb']})
         url = get_url(action='getSeasons', id=serie['id'], temp=serie['cant_temp'])
         is_folder = True
         xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
     xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_EPISODE)
    
     xbmcplugin.endOfDirectory(_handle)

def list_seasons(pelser_id, temporada):

     xbmcplugin.setPluginCategory(_handle, 'Seasons')
     xbmcplugin.setContent(_handle, 'season')

     cant_temp = int(temporada)
    
     for i in range (cant_temp):
         list_item = xbmcgui.ListItem(label='Temporada '+ str(i+1))
         url = get_url(action='getEpisodes', serie_id=pelser_id, temp=i)
         is_folder = True
         xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
     xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

     xbmcplugin.endOfDirectory(_handle)    

def list_episodes(serie_id, temp):
    
    xbmcplugin.setPluginCategory(_handle, 'Episodes')

    xbmcplugin.setContent(_handle, 'episodes')

    episodes = get_episodes(serie_id, temp)

    for video in episodes:
        list_item = xbmcgui.ListItem(label=video['name'])
        
        list_item.setInfo('video', {'title': video['name'],
                                    'plot': video['plot'],
                                    'mediatype': 'video'})
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        list_item.setSubtitles([video['sub']])
       
        list_item.setProperty('IsPlayable', 'true')
        
        url = get_url(action='play', video=video['video'])
        
        is_folder = False
       
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
   
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    play_item.setMimeType('application/dash+xml')
    play_item.setContentLookup(False)
    xbmc.Player
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            if params['category'] == 'Series':
               list_series()
            else:
                list_videos(params['category'])
        elif params['action'] == 'getSeasons':
             list_seasons(params['id'],params['temp'])
        elif params['action'] == 'getEpisodes':
             list_episodes(params['serie_id'], params['temp'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
