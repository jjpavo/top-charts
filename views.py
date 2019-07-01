import base64
import json
import re
from io import BytesIO
from os import path, makedirs

from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from PIL import Image

from top_charts.render_chart import RenderChart
from top_charts.models import Image as ImageModel
from top_charts.models import Tag
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

        # Create image object in database.
        im = ImageModel(image_path=image_path, image_title=data['title'], creation_date=timezone.now())
        im.save()

        for tag_name in data['tags']:
            tag = Tag.objects.filter(tag=tag_name)
            if not tag:
                tag = Tag(tag=tag_name)
                tag.save()
            else:
                # Get the tag from the QuerySet
                tag = tag[0]
            im.tags.add(tag)

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
        data = dict(request.GET)
        tags = data['tags']

        image_objects = ImageModel.objects.filter(tags__tag__in=tags).annotate(
            num_tags=Count('tags')).filter(num_tags=len(tags))

        images = {}
        for image in image_objects:
            images[image.id] = {
                "title": image.image_title,
                # The full path is to load the image client-side and the relative is for when the path is sent to the
                # server in the chart config it is independent of the server setup, which I believe is the correct
                # decision.
                "path": path.join(settings.IMAGE_DIR_REL, image.image_path),
                "relpath": image.image_path
            }

        response = JsonResponse(images)
    return response
