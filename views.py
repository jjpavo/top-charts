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
from top_charts.models import Tag, Chart
from top_charts.utils import construct_image_path, crop_image


def index(request):
    context = {}
    return render(request, 'top_charts/index.html', context)


def chart(request):
    if request.method == 'POST':
        chart_config = json.loads(request.body)
        chart_name = chart_config["title_text"]["text"]
        username = None

        chart_renderer = RenderChart(chart_config)
        # Change this name
        chart = chart_renderer.render_chart()
        chart_obj = Chart(chart=chart_config, name=chart_name, creation_date=timezone.now(),
                          modification_date=timezone.now(), user=username)
        chart_obj.save()

        response = HttpResponse(content_type="image/png")
        chart.save(response, "PNG")
        return response


def config(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chart_config = data["chart"]
        chart_name = data["name"]
        username = None  # TODO
        chart_obj = Chart(chart=chart_config, name=chart_name, creation_date=timezone.now(),
                          modification_date=timezone.now(), user=username)
        chart_obj.save()

        response = HttpResponse()
        response["id"] = chart_obj.id
        return response
    elif request.method == "GET":
        data = dict(request.GET)


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
        status = 200
        responseJSON = {}

        data = dict(request.GET)

        image_objects = _image_query(data)
        full_path = None
        if image_objects:
            for image in image_objects:
                # If image is model turn to dict so that both can use ["key"]
                # Also, the paths must be different, since "image_path" from searching via the path name
                # gives the base64 string.
                if type(image) is ImageModel:
                    image = image.__dict__
                    full_path = path.join(settings.IMAGE_DIR_REL, image["image_path"])
                    relpath = image["image_path"]
                else:
                    full_path = image["image_path"]
                    relpath = image["relpath"]
                responseJSON[image["id"]] = {
                    "title": image["image_title"],
                    # The full path is to load the image client-side and the relative is for when the path is sent to
                    # the server in the chart config it is independent of the server setup, which I believe is the
                    # correct decision.
                    "path": full_path,
                    "relpath": relpath
                }

        else:
            status = 500
            responseJSON = {
                "message": "Image(s) not found."
            }

        response = JsonResponse(responseJSON, status=status)
    return response


# TODO Find more elegant way of querying images.
def _image_query(data):
    image_objects = None

    if "tags" in data:
        image_objects = ImageModel.objects.filter(tags__tag__in=data['tags']).annotate(
            num_tags=Count('tags')).filter(num_tags=len(data['tags']))
    elif "path" in data:
        # TODO look into cropping images and saving those, instead of cropping on demand every time.
        PIL_image = Image.open(path.join(settings.IMAGE_DIR, data['path'][0]))

        try:
            image_object = ImageModel.objects.filter(image_path=data['path'][0])[0]
        except IndexError:
            return None

        if 'crop[]' in data:
            crop_coor = [float(coor) for coor in data['crop[]']]
        else:
            crop_coor = None

        buffer = BytesIO()
        cropped_image = crop_image(PIL_image, int(
            data['tile_size[]'][0]), int(data['tile_size[]'][1]), crop_coor)

        cropped_image.save(buffer, format="JPEG")
        cropped_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        image_objects = [
            {
                "id": image_object.id,
                "image_title": image_object.image_title,
                "image_path": cropped_base64,
                "relpath": image_object.image_path
            }
        ]

    return image_objects
