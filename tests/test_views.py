import base64
import json
from glob import glob
from io import BytesIO
from os import path
from shutil import rmtree

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from PIL import Image
from SSIM_PIL import compare_ssim as ssim

from top_charts.models import Image as ImageModel
from top_charts.models import Chart
from top_charts.utils import construct_image_path


class TestChart(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('chart')
        with open(path.join(settings.TEST_DIR, "chart_configs/test_show_all_text.json"), "r") as json_file:
            cls.chart_cfg = json.load(json_file)
            for group in cls.chart_cfg['images']:
                for image in group:
                    name = path.basename(image['path'])
                    im = ImageModel(image_path=image['path'], image_title=name, creation_date=timezone.now())
                    im.save()

    def setUp(self):
        self.client = Client()

    # FIXME
    def test_render_chart(self):
        response = self.client.post(self.url, self.chart_cfg,
                                    content_type="application/json",
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)


class TestImage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('image')
        with open(path.join(settings.IMAGE_DIR, "evangelion.jpg"), "rb") as file:
            cls.img_base64 = base64.b64encode(file.read()).decode('utf-8')
        cls.data = {
            "image": cls.img_base64,
            "title": "eva"
        }

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.setUpTestData()

    @classmethod
    def tearDownClass(cls):
        # The test images directory does not have any permanent subdirectories.
        # So delete the ones made by the image uploading.
        paths = glob(path.join(settings.IMAGE_DIR, '*/'))
        for im_path in paths:
            rmtree(im_path)

    def test_image_upload(self):
        image_path = construct_image_path(str(abs(hash(self.img_base64))))
        response = self.client.post(self.url, self.data,
                                    content_type="application/json",
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        id = response['id']
        db_image = ImageModel.objects.get(pk=id)
        saved_path = db_image.image_path
        saved_title = db_image.image_title
        saved_tags = db_image.tags.all()

        pil_saved_image = Image.open(path.join(settings.IMAGE_DIR, saved_path))
        pil_original_image = Image.open(BytesIO(base64.b64decode(self.img_base64)))
        correct_tags = [Tag(tag="anime"), Tag(tag="90s"), Tag(tag="classic"), Tag(tag="gainax"), Tag(
            tag="hideaki anno"), Tag(tag="evangelion"), Tag(tag="neon genesis evangelion"), Tag(tag="shinseiki evangelion")]

        diff = ssim(pil_saved_image, pil_original_image)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(saved_title, self.data['title'])
        self.assertEqual(response['path'], image_path)
        self.assertEqual(response['path'], saved_path)
        self.assertEqual(set(correct_tags), set(saved_tags))
        self.assertEqual(diff, 1.0)
