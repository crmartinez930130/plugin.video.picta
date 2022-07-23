import json
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

from resources.plugin import (
    DOCUMENTALES,
    MUSICALES,
    PELICULAS,
    get_canales,
    get_canales_videos,
    get_episodes,
    get_series,
    get_videos,
    get_search,
    get_generos,
)

sys.modules["xbmc"] = xbmcMock = MagicMock()
sys.modules["xbmcaddon"] = MagicMock()
sys.modules["xbmcgui"] = MagicMock()


class PluginTestCase(TestCase):
    @staticmethod
    def load_json_file(file_path: str) -> str:
        mock_data = ""
        with open(file_path, encoding="utf-8") as f:
            mock_data = f.read()

        return mock_data

    @patch("sys.argv")
    @patch("requests.get")
    def test_get_videos_musicales(self, mock_get, mock_argv):
        """Test Musicales"""
        videos = []
        mock_argv.return_value = [
            "plugin://plugin.video.picta/",
            "1",
            "",
            "resume:false",
        ]
        json_data = [
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_musicales_page_{idx}.json"
                )
            )
            for idx in range(1, 4)
        ]
        mock_get.return_value.json.side_effect = json_data

        for idx in range(1, 4):
            videos.extend(get_videos(MUSICALES, next_page=idx))

        expected = {
            "name": "CON CUBA NO TE METAS - Virulo\n► 2139 · ♥ 158 · ▼ 1581",
            "thumb": "https://www.picta.cu/imagen/img_5mBRhLl.jpeg_380x250",
            "video": "https://www.picta.cu/videos/9b25196524f94db49a07d81cb0b9b471/manifest.mpd",
            "genre": "Conga",
            "plot": "Ministerio de Cultura de Cuba",
            "sub": "",
        }

        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 296)

    @patch("requests.get")
    def test_get_videos_documental(self, mock_get):
        """Test Documentales"""
        videos = []
        json_data = [
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_documental_page_{idx}.json"
                )
            )
            for idx in range(1, 3)
        ]
        mock_get.return_value.json.side_effect = json_data

        for idx in range(1, 3):
            videos.extend(get_videos(DOCUMENTALES, next_page=idx))

        expected = {
            "name": "La Historia de Pixar\n► 27 · ♥ 4 · ▼ 28",
            "thumb": "https://www.picta.cu/imagen/img_lUFmT8c.jpeg_380x250",
            "video": "https://www.picta.cu/videos/49be1481dfdb4eed84c8394c9544be42/manifest.mpd",
            "genre": "",
            "plot": (
                "The Pixar Story, dirigido por Leslie Iwerks, es un documental de "
                "la historia de la compañía Pixar Animation Studios.\r\n\r\nLa primera "
                "versión de la película se estrenó en el Sonoma Film Festival, en 2007, "
                "y tenía una duración teatral limitada después de que un año antes "
                "fuese tomada por la red de cable Starz en Estados Unidos.\r\n\r\nLa "
                "cinta se estrenó, fuera de Estados Unidos, en formato DVD en el verano "
                'de 2008 como parte de "Ultimate Pixar Collection",\u200b un box set de '
                "las películas de Pixar. Se incluyó como una sección especial en la "
                "edición especial de DVD y Blu-ray de WALL·E, que se lanzó el 18 de "
                "noviembre de 2008. \r\n\r\n<< no olvide suscribirse al canal para "
                "conocer sobre nuevos materiales, asi como calificar esta publicación. gracias >>"
            ),
            "sub": "",
        }

        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 118)

    @patch("requests.get")
    def test_get_videos_pelicula(self, mock_get):
        """Test Peliculas"""
        videos = []
        json_data = [
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_pelicula_page_{idx}.json"
                )
            )
            for idx in range(1, 6)
        ]
        mock_get.return_value.json.side_effect = json_data

        for idx in range(1, 6):
            videos.extend(get_videos(PELICULAS, next_page=idx))

        expected = {
            "name": "Luca\n► 126 · ♥ 11 · ▼ 388",
            "thumb": "https://www.picta.cu/imagen/img_cbyHM4G.jpeg_380x250",
            "video": "https://www.picta.cu/videos/26fcf76822d647a681e2ca0a610cda3e/manifest.mpd",
            "genre": "Animación, Aventura, Comedia, Fantasía",
            "plot": (
                "Ambientada en un hermoso pueblo costero de la Riviera italiana, "
                "esta nueva película animada original es la historia del paso de "
                "la niñez a la adultez de un niño que vive un verano inolvidable "
                "repleto de gelato, pastas y viajes interminables en scooter. "
                "Luca comparte estas aventuras con su nuevo mejor amigo, pero toda "
                "la diversión se ve amenazada por un secreto muy bien escondido: "
                "Luca es un monstruo marino de un mundo que se encuentra justo por "
                "debajo de la superficie del agua."
            ),
            "sub": "",
        }

        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 445)

    @patch("requests.get")
    def test_get_series(self, mock_get):
        """Test Series"""
        series = []
        json_data = [
            json.loads(
                self.load_json_file(f"./tests/mocks/api_videos_serie_page_{idx}.json")
            )
            for idx in range(1, 4)
        ]
        mock_get.return_value.json.side_effect = json_data

        for idx in range(1, 4):
            series.extend(get_series(next_page=idx))

        expected = {
            "name": "Calculo",
            "id": 824,
            "thumb": "https://www.picta.cu/imagen/img_lo20hRv.jpeg_380x250",
            "genre": "Serie Documental",
            "cant_temp": 2,
        }

        self.assertDictEqual(series[0], expected)
        self.assertEqual(len(series), 280)

    @patch("requests.get")
    def test_get_episodes(self, mock_get):
        """Test Episodes"""
        json_data = [
            json.loads(
                self.load_json_file("./tests/mocks/api_videos_serie_temporada_224.json")
            ),
            json.loads(
                self.load_json_file(
                    "./tests/mocks/api_videos_serie_temporada_capitulos.json"
                )
            ),
        ]

        mock_get.return_value.json.side_effect = json_data

        videos = get_episodes("224", "0")
        expected = {
            "name": "Biohackers 1x01\n► 238 · ♥ 15 · ▼ 431",
            "thumb": "https://www.picta.cu/imagen/img_30VUtC6.jpeg_380x250",
            "video": "https://www.picta.cu/videos/86c1c873227c410a9f8195c0643c4e6c/manifest.mpd",
            "genre": "Ciencia ficción, Fantasía",
            "plot": (
                "Una estudiante de medicina va a la universidad con una misión "
                "secreta: exponer la supuesta conspiración que vincula una tragedia "
                "familiar con una profesora de biología."
            ),
            "sub": "https://www.picta.cu/sub/86c1c873227c410a9f8195c0643c4e6c",
        }

        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 6)

    @patch("requests.get")
    def test_get_canales(self, mock_get):
        """Test Canales"""
        canales = []
        json_data = [
            json.loads(
                self.load_json_file(f"./tests/mocks/api_videos_canal_page_{idx}.json")
            )
            for idx in range(1, 4)
        ]
        mock_get.return_value.json.side_effect = json_data

        for idx in range(1, 4):
            canales.extend(get_canales(next_page=idx))

        expected = {
            "name": "Películas",
            "id": 16,
            "thumb": "https://www.picta.cu/imagen/Pel%C3%ADculas1.png_380x250",
            "plot": "Películas sobre géneros variados.",
        }
        self.assertDictEqual(canales[0], expected)
        self.assertEqual(len(canales), 253)

    @patch("requests.get")
    def test_get_canales_videos(self, mock_get):
        """Test Canales Videos"""
        json_data = [
            json.loads(
                self.load_json_file("./tests/mocks/api_videos_canal_bachecubano.json")
            )
        ]

        mock_get.return_value.json.side_effect = json_data

        videos = get_canales_videos("Bachecubano")
        expected = {
            "name": "Pesquisador Virtual para Cuba en tiempos de COVID19\n► 249 · ♥ 79 · ▼ 86",
            "thumb": "https://www.picta.cu/imagen/img_iMbjsnc.jpeg_380x250",
            "video": "https://www.picta.cu/videos/bd6b880cd2444bc094cbb167aa9c4113/manifest.mpd",
            "genre": "",
            "plot": (
                "La Universidad de las Ciencias Informáticas, de conjunto con los "
                "ministerios de Salud Pública y de Comunicaciones, lanzó Pesquisador "
                "Virtual, una aplicación para recabar información sobre el estado de "
                "salud de la población, como complemento del proceso de pesquisa "
                "activa que realiza el sistema de salud cubano en el marco del "
                'enfrentamiento epidemiológico de la pandemia COVID-19.\r\n\r\n"Para '
                "utilizar esta plataforma usted debe tener más de 18 años de edad y "
                "estar en plena capacidad legal. Usted se responsabiliza con la "
                "absoluta veracidad de la información suministrada. Esta información "
                "será analizada exclusivamente por el sistema de salud y al llenar la "
                "encuesta usted expresa su conformidad con la utilización de sus "
                'datos", cita Apklis en la descripción de la aplicación.\r\n\r\nLa apk '
                "funciona con acceso a Internet y es libre de costo. Los interesados "
                "podrán descargarla desde la tienda cubana de aplicaciones Apklis, o "
                "vía web en la red del Ministerio de Salud Pública. \r\n\r\nLo puedes "
                "descargar desde el enlace de ApkLis:\r\nhttps://www.apklis.cu/application/cu.online.survey"
            ),
            "sub": "",
        }
        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 8)

    @patch("requests.get")
    def test_get_search(self, mock_get):
        """Test Search"""
        json_data = [
            json.loads(
                self.load_json_file("./tests/mocks/api_videos_search_page_1.json")
            ),
        ]

        mock_get.return_value.json.side_effect = json_data

        videos = get_search(query="cuba", next_page=1)

        expected = {
            "name": "CON CUBA NO TE METAS - Virulo\n► 3960 · ♥ 356 · ▼ 2507",
            "thumb": "https://www.picta.cu/imagen/img_5mBRhLl.jpeg_380x250",
            "video": "https://www.picta.cu/videos/9b25196524f94db49a07d81cb0b9b471/manifest.mpd",
            "genre": "",
            "plot": "Ministerio de Cultura de Cuba",
            "sub": "",
        }

        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 8)

    @patch("requests.get")
    def test_get_generos(self, mock_get):
        """Test Generos"""
        json_data = [
            json.loads(
                self.load_json_file("./tests/mocks/api_videos_genero_page_1.json")
            ),
        ]

        mock_get.return_value.json.side_effect = json_data

        generos = get_generos(next_page=1)

        expected = {
            "id": 5,
            "nombre": "Acción",
            "tipo": "ci",
        }

        self.assertDictEqual(generos[0], expected)
        self.assertEqual(len(generos), 38)
