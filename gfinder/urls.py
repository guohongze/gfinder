"""
URL configuration for gfinder project.
"""
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.views.static import serve
from django.conf import settings
import os


def health_check(request):
    """健康检查接口"""
    return HttpResponse("GFinder is running", content_type="text/plain")


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('', include('backend.urls')),
    path('health', health_check, name='health_check'),
    
    # 添加直接服务static和assets目录的URL
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'frontend/dist/static')}),
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'frontend/dist/assets')}),
    
    # 捕获所有其他URL并返回index.html (SPA路由)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]