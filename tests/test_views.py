from os import path
import json

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from PIL import Image

from top_charts.models import Image as ImageModel
from top_charts.models import Chart


class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        with open(path.join(settings.TEST_DIR, "chart_configs/test_show_all_text.json"), "r") as json_file:
            cls.chart_cfg = json.load(json_file)
            for group in cls.chart_cfg['images']:
                for image in group:
                    name = path.basename(image['path'])
                    im = ImageModel(image_path=image['path'], image_title=name, creation_date=timezone.now())
                    im.save()

    def setUp(self):
        self.client = Client()
        self.render_url = reverse('chart')

    def test_render_chart(self):
        response = self.client.post(self.render_url, self.chart_cfg,
                                    content_type="application/json",
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
