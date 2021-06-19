import json
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

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
    def test_get_videos(self, mock_get, mock_argv):
        mock_argv.return_value = [
            "plugin://plugin.video.picta/",
            "1",
            "",
            "resume:false",
        ]
        from resources.plugin import get_videos

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

        self.assertEqual(videos[0].get("name"), "CON CUBA NO TE METAS - Virulo")
        self.assertEqual(
            videos[0].get("thumb"),
            "https://www.picta.cu/imagen/img_5mBRhLl.jpeg_380x250",
        )
        self.assertEqual(
            videos[0].get("video"),
            "https://www.picta.cu/videos/9b25196524f94db49a07d81cb0b9b471/manifest.mpd",
        )
        self.assertEqual(videos[0].get("genre"), "  Conga")
        self.assertEqual(videos[0].get("plot"), "Ministerio de Cultura de Cuba")
        self.assertEqual(videos[0].get("sub"), "")

        self.assertEqual(len(videos), 296)
