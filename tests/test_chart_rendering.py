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
        chart_renderer = RenderChart(self.chart_cfg)
        tile_y_offset, title_x_offset, tile_name_y_offset, \
            tile_name_row_x_offset, tile_name_x_offset = \
            chart_renderer._get_offsets()
        self.assertEqual(tile_y_offset, 0)
        self.assertEqual(title_x_offset, 165)
        self.assertEqual(tile_name_y_offset, 0)
        self.assertEqual(tile_name_row_x_offset, 1970)
        self.assertEqual(tile_name_x_offset, 2005)

    def test_paste_tile_first_row(self):
        chart_renderer = RenderChart(self.chart_cfg)
        image = self.chart_cfg['images'][0][0]
        tile_width = self.chart_cfg['tile_sizes'][0][0]
        tile_height = self.chart_cfg['tile_sizes'][0][1]
        chart_renderer._paste_tile(1, image, 10, tile_width, tile_height)
        truth = Image.open(path.join(settings.TEST_DIR, "charts/test_all_text_tile_first_row.png"))
        diff = ssim(chart_renderer.chart, truth)
        self.assertGreaterEqual(diff, 0.97)

    def test_paste_tile_second_row(self):
        chart_renderer = RenderChart(self.chart_cfg)
        image = self.chart_cfg['images'][0][0]
        tile_width = self.chart_cfg['tile_sizes'][0][0]
        tile_height = self.chart_cfg['tile_sizes'][0][1]
        chart_renderer._paste_tile(11, image, 10, tile_width, tile_height)
        truth = Image.open(path.join(settings.TEST_DIR, "charts/test_all_text_tile_second_row.png"))
        diff = ssim(chart_renderer.chart, truth)
        self.assertGreaterEqual(diff, 0.97)

    def test_draw_text(self):
        chart_renderer = RenderChart(self.chart_cfg)
        text = self.chart_cfg['title_text']['text']
        chart_renderer._draw_text(text, self.chart_cfg['title_text'], 100, 50)
        truth = Image.open(path.join(settings.TEST_DIR, "charts/test_all_text_draw_text.png"))
        diff = ssim(chart_renderer.chart, truth)
        self.assertGreaterEqual(diff, 0.97)

    # TODO Test for non-square images.
    def test_transform_image_custom_crop(self):
        chart_renderer = RenderChart(self.chart_cfg)
        image = Image.open((path.join(settings.TEST_DIR, "images",
                                      self.chart_cfg['images'][0][0]['path'])))
        tile_width = self.chart_cfg['tile_sizes'][0][0]
        tile_height = self.chart_cfg['tile_sizes'][0][1]
        crop_coor = self.chart_cfg['images'][0][0]['crop']
        cropped = chart_renderer._transform_image(image, tile_width, tile_height, crop_coor)
        truth = Image.open(path.join(settings.TEST_DIR,
                                     "charts/test_transform_image_custom_crop.png"))
        diff = ssim(cropped, truth)
        self.assertGreaterEqual(diff, 0.97)

    def test_transform_image_default_crop(self):
        chart_renderer = RenderChart(self.chart_cfg)
        image = Image.open((path.join(settings.TEST_DIR, "images",
                                      self.chart_cfg['images'][0][0]['path'])))
        tile_width = self.chart_cfg['tile_sizes'][0][0]
        tile_height = self.chart_cfg['tile_sizes'][0][1]
        cropped = chart_renderer._transform_image(image, tile_width, tile_height)
        truth = Image.open(path.join(settings.TEST_DIR,
                                     "charts/test_transform_image_default_crop.png"))
        diff = ssim(cropped, truth)
        self.assertGreaterEqual(diff, 0.97)

    def test_render(self):
        chart_renderer = RenderChart(self.chart_cfg)
        ret = chart_renderer.render_chart()
        # Compare to ground truth.
        truth = Image.open(path.join(settings.TEST_DIR, "charts/test_show_all_text.png"))
        diff = ssim(ret, truth)
        self.assertGreaterEqual(diff, 0.97)
