import os
from unittest.mock import patch

from django.test import SimpleTestCase

from ai_engine.yolo_service import YoloDetector


from django.conf import settings

class YoloDetectorModelTests(SimpleTestCase):
    @patch("ai_engine.yolo_service.YOLO")
    def test_get_models_loads_all_available_model_weights(self, mock_yolo):
        mock_yolo.return_value = object()

        models = YoloDetector.get_models()

        self.assertEqual(len(models), 3)
        self.assertEqual(mock_yolo.call_count, 3)
        expected_paths = [
            os.path.join(settings.BASE_DIR, "ai_engine", "models", "best.pt"),
            os.path.join(settings.BASE_DIR, "ai_engine", "models", "best_4c.pt"),
            os.path.join(settings.BASE_DIR, "ai_engine", "models", "best_7c.pt"),
        ]
        self.assertEqual([call.args[0] for call in mock_yolo.call_args_list], expected_paths)
