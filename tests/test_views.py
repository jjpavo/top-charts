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
from top_charts.models import Tag
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
        with open(path.join(settings.IMAGE_DIR, "evangelion.jpg"), "rb") as image_file:
            cls.eva_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        cls.eva_data = {
            "image": cls.eva_base64,
            "title": "evangelion",
            "tags": [
                "anime",
                "90s",
                "classic",
                "gainax",
                "hideaki anno",
                "evangelion",
                "neon genesis evangelion",
                "shinseiki evangelion"
            ]
        }

        cls.flcl_im = ImageModel(image_path=path.join(settings.IMAGE_DIR, "flcl.jpg"),
                                 image_title="flcl", creation_date=timezone.now())
        cls.flcl_im.save()
        cls.gl_im = ImageModel(image_path=path.join(settings.IMAGE_DIR, "gurren lagann.jpg"),
                               image_title="gurren lagann", creation_date=timezone.now())
        cls.gl_im.save()
        cls.nichijou_im = ImageModel(image_path=path.join(settings.IMAGE_DIR, "nichijou.jpg"),
                                     image_title="nichijou", creation_date=timezone.now())
        cls.nichijou_im.save()

        cls.gainax_tag = Tag(tag="gainax")
        cls.gainax_tag.save()
        cls.kyoani_tag = Tag(tag="kyoani")
        cls.kyoani_tag.save()
        cls.anime_tag = Tag(tag="anime")
        cls.anime_tag.save()
        cls.tsurumaki_tag = Tag(tag="tsurumaki")
        cls.tsurumaki_tag.save()

        cls.flcl_im.tags.add(cls.gainax_tag)
        cls.flcl_im.tags.add(cls.tsurumaki_tag)
        cls.flcl_im.tags.add(cls.anime_tag)
        cls.gl_im.tags.add(cls.gainax_tag)
        cls.gl_im.tags.add(cls.anime_tag)
        cls.nichijou_im.tags.add(cls.kyoani_tag)
        cls.nichijou_im.tags.add(cls.anime_tag)

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
        image_path = construct_image_path(str(abs(hash(self.eva_base64))))
        response = self.client.post(self.url, self.eva_data,
                                    content_type="application/json",
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        id = response['id']
        db_image = ImageModel.objects.get(pk=id)
        saved_path = db_image.image_path
        saved_title = db_image.image_title
        saved_tags = db_image.tags.all()

        pil_saved_image = Image.open(path.join(settings.IMAGE_DIR, saved_path))
        pil_original_image = Image.open(BytesIO(base64.b64decode(self.eva_base64)))

        correct_tags = [Tag(tag="anime"), Tag(tag="90s"), Tag(tag="classic"), Tag(tag="gainax"), Tag(
            tag="hideaki anno"), Tag(tag="evangelion"), Tag(tag="neon genesis evangelion"), Tag(tag="shinseiki evangelion")]

        diff = ssim(pil_saved_image, pil_original_image)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(saved_title, self.eva_data['title'])
        self.assertEqual(response['path'], image_path)
        self.assertEqual(response['path'], saved_path)
        self.assertEqual(set(correct_tags), set(saved_tags))
        self.assertEqual(diff, 1.0)

    def test_image_download_by_one_tag(self):
        tags = ["anime"]
        correct_names = set(["flcl", "gurren lagann", "nichijou"])
        self._test_image_download(tags, correct_names)

    def test_image_download_by_multiple_tags(self):
        tags = ["anime", "gainax"]
        correct_names = set(["flcl", "gurren lagann"])
        self._test_image_download(tags, correct_names)

    def test_image_download_by_incoherent_tags(self):
        tags = ["kyoani", "gainax"]
        correct_names = set()
        self._test_image_download(tags, correct_names)

    def _test_image_download(self, tags, correct_names):
        data = {
            "tags": tags
        }

        response = self.client.get(self.url, data, content_type="application/json")
        response_images = json.loads((response.content).decode('utf-8'))
        image_names = set(response_images[k]['title'] for k in response_images)

        # TODO Possibly not enough?
        self.assertEqual(correct_names, image_names)
