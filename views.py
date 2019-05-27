import os

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def index(request):
    return HttpResponse('hello world')
