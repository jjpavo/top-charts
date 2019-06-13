import os
import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from top_charts.render_chart import RenderChart


def index(request):
    return HttpResponse('hello world')


def chart(request):
    if request.is_ajax():
        if request.method == 'POST':
            with open(os.path.join(settings.TEST_DIR, "chart_configs/test_show_all_text.json"), "r") as json_file:
                chart_cfg = json.load(json_file)
            # chart_renderer = RenderChart(json.loads(request.body))
            chart_renderer = RenderChart(chart_cfg)
            chart = chart_renderer.render_chart()
            response = HttpResponse(content_type="image/png")
            chart.save(response, "PNG")
            return response

