import json
from math import floor
from os.path import join

from django.conf import settings
from PIL import Image, ImageFont, ImageDraw, ImageColor

from .models import Image as ImageModel


class RenderChart():
    """Renders a chart made of a grid of tiles.

    Attributes:
        chart_cfg (dict): A dictionary conveying the configuration of the chart.
                          Examples at tests/chart_configs.
        grid_width (int): The width of the tile grid.
        grid_height (int): The height of the tile grid.
        chart_width (int): The width of the chart.
        chart_height (int): The height of the chart.
        chart (PIL Image): The image representation of the chart.
        tile_y_offset (int): The Y offset of the next tile to draw.
        title_x_offset (int): The X offset of the chart and group titles.
        tile_name_y_offset (int): The Y offset of the next tile name to draw.
        tile_name_x_offset (int): The X offset of the tile names.
        tile_name_row_x_offset (int): The X offset of the tile name row numbers.
    """

    def __init__(self, chart_cfg):
        """
        Args:
            chart_cfg (dict): A dictionary conveying the configuration of the chart.
                              Examples at tests/chart_configs.
        """
        self.chart_cfg = chart_cfg
        self.grid_width, self.grid_height = self._get_grid_dimensions()
        self.chart_width, self.chart_height = self._get_chart_dimensions()
        # self.chart = Image.new("RGB", (self.chart_width, self.chart_height), color=self.chart_cfg['background_color'])
        # self.tile_y_offset, self.title_x_offset, self.tile_name_y_offset, self.tile_name_row_x_offset, \
        #     self.tile_name_x_offset = self._get_offsets()

    def render_chart(self):
        """Renders a chart made of a grid of tiles."""
        # TODO

    def _get_chart_dimensions(self):
        # Start with the dimensions of the grid with padding.
        chart_width, chart_height = self.grid_width + self.chart_cfg['chart_width_padding'], self.grid_height + \
            self.chart_cfg['chart_height_padding']

        if self.chart_cfg['title_text']['show']:
            # TODO check whether using the font.getsize slows things down.
            # Also, check whether the results are better than just using the
            # size from the chart_cfg.
            font = ImageFont.truetype(self.chart_cfg['title_text']['font'], self.chart_cfg['title_text']['size'])
            chart_height += (2 * self.chart_cfg['title_text']['height_padding']) + \
                font.getsize(self.chart_cfg['title_text']['text'])[1]

        if self.chart_cfg['group_title_text']['show']:
            font = ImageFont.truetype(self.chart_cfg['group_title_text']['font'],
                                      self.chart_cfg['group_title_text']['size'])
            longest_group_title = max(
                [group_title for group_title in self.chart_cfg['group_title_text']['text']], key=len)
            chart_height += ((2 * self.chart_cfg['group_title_text']['height_padding']) +
                             font.getsize(longest_group_title)[1]) * self.chart_cfg['group_count']

        if self.chart_cfg['tile_name_row_text']['show']:
            font = ImageFont.truetype(self.chart_cfg['tile_name_row_text']['font'],
                                      self.chart_cfg['tile_name_row_text']['size'])
            # Font size of string "00" since most charts will not have more than
            # 99 rows, meaning we just pick a two digit string.
            chart_width += (2 * self.chart_cfg['tile_name_row_text']['width_padding']) + font.getsize("00")[0]

        if self.chart_cfg['tile_row_text']['show']:
            font = ImageFont.truetype(self.chart_cfg['tile_row_text']['font'], self.chart_cfg['tile_row_text']['size'])
            # Font size of string "00" since most charts will not have more than
            # 99 rows, meaning we just pick a two digit string.
            chart_width += (2 * self.chart_cfg['tile_row_text']['width_padding']) + font.getsize("00")[0]

        if self.chart_cfg['tile_name_text']['show']:
            font = ImageFont.truetype(self.chart_cfg['tile_name_text']['font'],
                                      self.chart_cfg['tile_name_text']['size'])
            names = [ImageModel.objects.get(
                image_path=image['path']).image_title for group in self.chart_cfg['images'] for image in group]
            longest_name = max([name for name in names], key=len)
            chart_width += (2 * self.chart_cfg['tile_name_text']['width_padding']) + font.getsize(longest_name)[0]

        return chart_width, chart_height

    def _get_grid_dimensions(self):
        gap_size = self.chart_cfg['gap_size']
        tile_sizes = self.chart_cfg['tile_sizes']
        tile_count = self.chart_cfg['tile_count']

        # grid_width is the width of the widest grid group.
        # The width of each grid group is the sum of the widths of the grid
        # tiles and the gaps between each tile, and on the outer perimeter of
        # the group.
        grid_width = max([(tile_size[0] + gap_size) * tile_count[0] + gap_size
                          for tile_size, tile_count in zip(tile_sizes, tile_count)])

        # grid_height is the sum of the heights of each grid group.
        # The height of each grid group is the sum of the heights of the grid
        # tiles and the gaps between each tile, and on the outer perimeter of
        # the group.
        grid_height = sum([(tile_size[1] + gap_size) * tile_count[1] + gap_size
                           for tile_size, tile_count in zip(tile_sizes, tile_count)])

        return grid_width, grid_height

    def _get_offsets(self):
        # TODO
        pass

    def _paste_tile(self, img_num, image, x, w, h):
        # TODO
        pass

    def _draw_text(self, text, text_cfg, y_offset, x_offset):
        # TODO
        pass

    def _transform_image(self, image, tile_width, tile_height, crop_coor=None):
        # TODO
        pass
