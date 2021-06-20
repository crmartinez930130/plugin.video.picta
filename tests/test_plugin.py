import json
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

from resources.plugin import get_episodes, get_series, get_videos

sys.modules["xbmc"] = xbmcMock = MagicMock()
sys.modules["xbmcaddon"] = MagicMock()
sys.modules["xbmcgui"] = MagicMock()


class PluginTestCase(TestCase):
    @staticmethod
    def load_json_file(file_path):
        mock_data = ""
        with open(file_path) as f:
            mock_data = f.read()

        return mock_data

    @patch("sys.argv")
    @patch("requests.get")
    def test_get_videos_musicales(self, mock_get, mock_argv):
        """Test Musicales"""
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

        videos = get_videos("Musicales")
        expected = {
            "name": "CON CUBA NO TE METAS - Virulo",
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
        json_data = [
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_documental_page_{idx}.json"
                )
            )
            for idx in range(1, 3)
        ]
        mock_get.return_value.json.side_effect = json_data

        videos = get_videos("Documentales")
        expected = {
            "name": "La Historia de Pixar",
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
        json_data = [
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_pelicula_page_{idx}.json"
                )
            )
            for idx in range(1, 6)
        ]
        mock_get.return_value.json.side_effect = json_data

        videos = get_videos("Peliculas")
        expected = {
            "name": "Luca",
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
        json_data = [
            json.loads(
                self.load_json_file(f"./tests/mocks/api_videos_serie_page_{idx}.json")
            )
            for idx in range(1, 4)
        ]
        mock_get.return_value.json.side_effect = json_data

        videos = get_series()
        expected = {
            "name": "Calculo",
            "id": 824,
            "thumb": "https://www.picta.cu/imagen/img_lo20hRv.jpeg_380x250",
            "genre": "Serie Documental",
            "cant_temp": 2,
        }

        self.assertDictEqual(videos[0], expected)
        self.assertEqual(len(videos), 280)

    @patch("requests.get")
    def test_get_episodes(self, mock_get):
        """Test Episodes"""
        json_data = [
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_serie_temporada_224.json"
                )
            ),
            json.loads(
                self.load_json_file(
                    f"./tests/mocks/api_videos_serie_temporada_capitulos.json"
                )
            ),
        ]
        mock_get.return_value.json.side_effect = json_data

        videos = get_episodes("224", "0")
        expected = {
            "name": "Biohackers 1x01",
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
