import json
from math import floor
from os.path import join

from django.conf import settings
from PIL import Image, ImageFont, ImageDraw, ImageColor

from .models import Image as ImageModel
from .utils import crop_image


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
        self.chart = Image.new("RGB", (self.chart_width, self.chart_height), color=self.chart_cfg['background_color'])
        self.tile_y_offset, self.title_x_offset, self.tile_name_y_offset, self.tile_name_row_x_offset, \
            self.tile_name_x_offset = self._get_offsets()

    def render_chart(self):
        """Renders a chart made of a grid of tiles."""

        row_count = 1

        if self.chart_cfg['title_text']['show']:
            self.tile_y_offset = self._draw_text(self.chart_cfg['title_text']['text'],
                                                 self.chart_cfg['title_text'],
                                                 self.tile_y_offset,
                                                 self.title_x_offset
                                                 ) - self.chart_cfg['title_text']['height_padding']
            # By default, have the tile names start past the title.
            # ENHANCEMENT May give the option to change in the future.
            self.tile_name_y_offset = self.tile_y_offset

        for group, ((x, y), (w, h)) in enumerate(zip(self.chart_cfg['tile_count'], self.chart_cfg['tile_sizes'])):
            # Draw the header for the group.
            if self.chart_cfg['group_title_text']['show']:
                self.tile_y_offset = self._draw_text(self.chart_cfg['group_title_text']['text'][group],
                                                     self.chart_cfg['group_title_text'], self.tile_y_offset,
                                                     self.title_x_offset)

            # Put space between the last block of names and the next one for
            # purposes of readability.
            self.tile_name_y_offset += self.chart_cfg['tile_name_text']['size'] + \
                (2 * self.chart_cfg['tile_name_text']['height_padding'])

            for img_num, image in enumerate(self.chart_cfg['images'][group]):
                # Paste the image onto the tile.
                self._paste_tile(img_num, image, x, w, h)

                # If we're at the beginning of a row...
                if img_num % w == 0:
                    # Draw image name row number.
                    if self.chart_cfg['tile_name_row_text']['show']:
                        self._draw_text(str(row_count),
                                        self.chart_cfg['tile_name_row_text'],
                                        self.tile_name_y_offset,
                                        self.tile_name_row_x_offset)

                    # Draw the tile row number.
                    if self.chart_cfg['tile_row_text']['show']:
                        self._draw_text(str(row_count), self.chart_cfg['tile_row_text'], self.tile_y_offset,
                                        self.grid_width)
                    row_count += 1

                # Draw the image's name.        # TODO
                if self.chart_cfg['tile_name_text']['show']:
                    name = ImageModel.objects.get(image_path=image['path']).image_title
                    self.tile_name_y_offset = self._draw_text(name, self.chart_cfg['tile_name_text'],
                                                              self.tile_name_y_offset, self.tile_name_x_offset)

            # Once at the end of the group, increase the Y offset to be at the
            # edge of the end of the last group.
            self.tile_y_offset += y * (h + self.chart_cfg['gap_size'])

        return self.chart

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
        # The Y offset of the next tile to draw.
        tile_y_offset = 0

        # The X offset of the chart and group titles.
        title_x_offset = 0

        # The Y offset of the next tile name to draw.
        tile_name_y_offset = 0

        # The X offset of the tile names.
        tile_name_x_offset = self.grid_width + (2 * self.chart_cfg['chart_width_padding']) + \
            self.chart_cfg['tile_name_text']['width_padding']

        # The X offset of the tile name row numbers.
        tile_name_row_x_offset = self.grid_width + (2 * self.chart_cfg['chart_width_padding']) + \
            self.chart_cfg['tile_name_row_text']['width_padding']

        if self.chart_cfg['title_text']['show']:
            title_x_offset = self.chart_cfg['title_text']['width_padding']

        if self.chart_cfg['tile_name_row_text']['show']:
            tile_name_x_offset += self.chart_cfg['tile_name_row_text']['size'] + \
                (2 * self.chart_cfg['tile_name_row_text']['width_padding'])

        if self.chart_cfg['tile_row_text']['show']:
            tile_name_x_offset += self.chart_cfg['tile_row_text']['width_padding']
            tile_name_row_x_offset += self.chart_cfg['tile_row_text']['width_padding']
            title_x_offset += self.chart_cfg['tile_row_text']['width_padding']

        return tile_y_offset, title_x_offset, tile_name_y_offset, tile_name_row_x_offset, tile_name_x_offset

    def _paste_tile(self, img_num, image, x, w, h):
        # Pastes tile in the appropriate location.

        col_num = img_num % x
        row_num = floor(img_num / x)

        # + 1 for the gap size because we want the gaps on each side.
        # If there are 5 tiles, there are 4 spaces in between and 2 on the outer
        # edges.
        x_pos = (col_num * w) + (self.chart_cfg['gap_size'] * (col_num + 1)) + self.chart_cfg['chart_width_padding']
        y_pos = (row_num * h) + (self.chart_cfg['gap_size'] * (row_num + 1)) + self.tile_y_offset

        tile = self._transform_image(Image.open(join(settings.IMAGE_DIR, image['path'])), w, h, image['crop'])

        self.chart.paste(tile, (x_pos, y_pos))

    def _draw_text(self, text, text_cfg, y_offset, x_offset):
        # Draws text in the appropriate location.

        draw = ImageDraw.Draw(self.chart)
        font = ImageFont.truetype(text_cfg['font'], text_cfg['size'])

        # ENHANCEMENT Alignment of text. Right now it's only aligned left.
        draw.text((x_offset, y_offset + text_cfg['height_padding']), text, font=font)

        # Increase the y_offset for the next line of text.
        # FIXME ?Not optimal to do here? Not sure. Seems sloppy.
        y_offset += text_cfg['size'] + (2 * text_cfg['height_padding'])

        return y_offset

    def _transform_image(self, image, tile_width, tile_height, crop_coor=None):
        return crop_image(image, tile_width, tile_height, crop_coor)
