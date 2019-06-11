from os import path
import json
import unittest

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from PIL import Image
from SSIM_PIL import compare_ssim as ssim

from top_charts.render_chart import RenderChart
from top_charts.models import Image as ImageModel


class TestAllTextRender(TestCase):
    """Tests chart rendering when all text is drawn. That is, the title, names, etc."""
    databases = [
        'default',
    ]

    chart_cfg = {}

    @classmethod
    def setUpTestData(cls):
        with open(path.join(settings.TEST_DIR, "chart_configs/test_show_all_text.json"), "r") as json_file:
            cls.chart_cfg = json.load(json_file)
            for group in cls.chart_cfg['images']:
                for image in group:
                    name = path.basename(image['path'])
                    im = ImageModel(image_path=image['path'], image_title=name, creation_date=timezone.now())
                    im.save()

    def test_get_grid_dimensions(self):
        chart_renderer = RenderChart(self.chart_cfg)
        grid_width, grid_height = chart_renderer._get_grid_dimensions()
        self.assertEqual(grid_width, 1855)
        self.assertEqual(grid_height, 925)

    def test_get_chart_dimensions(self):
        chart_renderer = RenderChart(self.chart_cfg)
        chart_renderer.grid_width = 1855
        chart_renderer.grid_height = 925
        chart_width, chart_height = chart_renderer._get_chart_dimensions()

        self.assertEqual(chart_width, 2253)
        self.assertEqual(chart_height, 1389)

    def test_get_offsets(self):
        # TODO
        pass

    def test_paste_tile_first_row(self):
        # TODO
        pass

    def test_paste_tile_second_row(self):
        # TODO
        pass

    def test_draw_text(self):
        # TODO
        pass

    def test_transform_image_custom_crop(self):
        # TODO
        pass

    def test_transform_image_default_crop(self):
        # TODO
        pass

    def test_render(self):
        # TODO
        pass
