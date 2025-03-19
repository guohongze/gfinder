from django.urls import path
from . import views

urlpatterns = [
    path('api/list', views.list_dir, name='list_dir'),
    path('api/operation', views.file_operations, name='file_operations'),
    path('api/upload', views.upload_file, name='upload_file'),
    path('api/download', views.download_file, name='download_file'),
    path('api/preview', views.preview_file, name='preview_file'),
    path('api/save', views.save_file, name='save_file'),
    path('api/move', views.move_item, name='move_item'),
    path('api/copy', views.copy_item, name='copy_item'),
    path('api/system-info', views.get_system_info, name='get_system_info'),
] 