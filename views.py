import base64
import json
import re
from io import BytesIO
from os import path, makedirs

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from PIL import Image

from top_charts.render_chart import RenderChart
from top_charts.models import Image as ImageModel
from top_charts.utils import construct_image_path


def index(request):
    context = {}
    return render(request, 'top_charts/index.html', context)


def chart(request):
    if request.is_ajax():
        if request.method == 'POST':
            chart_renderer = RenderChart(json.loads(request.body))
            chart = chart_renderer.render_chart()
            response = HttpResponse(content_type="image/png")
            chart.save(response, "PNG")
            return response


def image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request_image = data['image']

        # TODO: check for collisions with path.
        # Get the path to save the image at.
        # The format is x/x/x/xxxxx.png.
        # This is to prevent having every image in one directory, which could cause performance issues.
        image_path = construct_image_path(str(abs(hash(request_image))))
        image_dir = path.dirname(image_path)
        image_filename = path.basename(image_path)

        # Save image object in database.
        im = ImageModel(image_path=image_path, image_title=data['title'], creation_date=timezone.now())
        im.save()

        # Save image file in the file system.
        makedirs(path.join(settings.IMAGE_DIR, image_dir), exist_ok=True)
        pil_image = Image.open(BytesIO(base64.b64decode(request_image)))
        pil_image.save(path.join(settings.IMAGE_DIR, image_path), format='png')

        response = HttpResponse("OK")
        # We want the ID to be sent back so that the image has a reference to its representation in the database.
        response['id'] = im.id
        # We want the path to be sent back so we don't need to re-query the database later when we want to construct
        # the chart server-side.
        response['path'] = im.image_path
    elif request.method == 'GET':
        pass
        # use bytesio then pil image.save(bytesio var, format='JPEG')
    return response
