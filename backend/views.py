from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import json
import shutil
from .file_operations.file_utils import (
    list_directory,
    create_directory,
    rename_item,
    delete_item,
    get_file_content,
    save_file_content,
    create_file,
    is_valid_path,
    get_root_directory
)
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

@csrf_exempt
def list_dir(request):
    """列出目录内容"""
    if request.method == 'GET':
        path = request.GET.get('path', '')
        
        if not is_valid_path(path):
            return JsonResponse({'error': '路径不合法'}, status=400)
            
        try:
            items = list_directory(path)
            return JsonResponse({'items': items})
        except Exception as e:
            logger.error(f"列出目录错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def file_operations(request):
    """处理文件操作"""
    if request.method == 'POST':
        data = json.loads(request.body)
        operation = data.get('operation')
        path = data.get('path', '')
        
        if not is_valid_path(path):
            return JsonResponse({'error': '路径不合法'}, status=400)
        
        try:
            if operation == 'create_directory':
                name = data.get('name', '')
                result = create_directory(path, name)
                return JsonResponse({'success': True, 'result': result})
                
            elif operation == 'rename':
                old_name = data.get('old_name', '')
                new_name = data.get('new_name', '')
                result = rename_item(path, old_name, new_name)
                return JsonResponse({'success': True, 'result': result})
                
            elif operation == 'delete':
                name = data.get('name', '')
                result = delete_item(path, name)
                return JsonResponse({'success': True, 'result': result})
                
            elif operation == 'create_file':
                name = data.get('name', '')
                content = data.get('content', '')
                result = create_file(path, name, content)
                return JsonResponse({'success': True, 'result': result})
                
            else:
                return JsonResponse({'error': '不支持的操作'}, status=400)
                
        except Exception as e:
            logger.error(f"文件操作错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def upload_file(request):
    """处理文件上传"""
    if request.method == 'POST':
        path = request.POST.get('path', '')
        
        if not is_valid_path(path):
            return JsonResponse({'error': '路径不合法'}, status=400)
            
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': '没有文件上传'}, status=400)
            
        try:
            root_dir = get_root_directory()
            full_path = os.path.join(root_dir, path.strip('/'))
            file_path = os.path.join(full_path, uploaded_file.name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
                    
            return JsonResponse({'success': True, 'filename': uploaded_file.name})
        except Exception as e:
            logger.error(f"上传文件错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def download_file(request):
    """处理文件下载"""
    if request.method == 'GET':
        path = request.GET.get('path', '')
        filename = request.GET.get('filename', '')
        
        # 修复路径验证问题：确保正确处理编码后的URL参数
        try:
            # 对路径进行解码处理
            if path:
                path = path.strip('/')
            
            if not filename:
                return JsonResponse({'error': '文件名不能为空'}, status=400)
                
            # 单独验证路径和文件名
            if not is_valid_path(path) or (filename and '../' in filename):
                return JsonResponse({'error': '路径不合法'}, status=400)
                
            root_dir = get_root_directory()
            file_path = os.path.join(root_dir, path, filename)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # 基本的文件下载实现
                response = FileResponse(open(file_path, 'rb'))
                
                # 使用三种方式处理文件名，兼容不同浏览器
                # 1. 使用RFC 5987规范 (现代浏览器)
                encoded_filename_utf8 = quote(filename)
                # 2. ASCII编码名称 (旧浏览器)
                ascii_filename = filename.encode('ascii', 'replace').decode('ascii')
                # 3. 使用UTF-8编码参数
                response['Content-Disposition'] = f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{encoded_filename_utf8}'
                
                # 设置正确的MIME类型
                import mimetypes
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type:
                    response['Content-Type'] = content_type
                else:
                    # 默认使用二进制流类型
                    response['Content-Type'] = 'application/octet-stream'
                
                return response
            else:
                return JsonResponse({'error': '文件不存在'}, status=404)
        except Exception as e:
            logger.error(f"下载文件错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def preview_file(request):
    """预览文件内容"""
    if request.method == 'GET':
        path = request.GET.get('path', '')
        filename = request.GET.get('filename', '')
        
        if not path or not filename or not is_valid_path(os.path.join(path, filename)):
            return JsonResponse({'error': '路径不合法'}, status=400)
            
        try:
            content = get_file_content(path, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            # 处理不同类型的文件
            if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml']:
                return JsonResponse({'content': content, 'type': 'text'})
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                return JsonResponse({'type': 'image'})
            elif file_ext == '.pdf':
                return JsonResponse({'type': 'pdf'})
            else:
                return JsonResponse({'error': '不支持的文件类型预览'}, status=400)
        except Exception as e:
            logger.error(f"预览文件错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def save_file(request):
    """保存文件内容"""
    if request.method == 'POST':
        data = json.loads(request.body)
        path = data.get('path', '')
        filename = data.get('filename', '')
        content = data.get('content', '')
        
        if not path or not filename or not is_valid_path(os.path.join(path, filename)):
            return JsonResponse({'error': '路径不合法'}, status=400)
            
        try:
            result = save_file_content(path, filename, content)
            return JsonResponse({'success': True, 'result': result})
        except Exception as e:
            logger.error(f"保存文件错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def move_item(request):
    """移动文件或文件夹"""
    if request.method == 'POST':
        data = json.loads(request.body)
        source_path = data.get('source_path', '')
        source_name = data.get('source_name', '')
        target_path = data.get('target_path', '')
        
        if not is_valid_path(source_path) or not is_valid_path(target_path):
            return JsonResponse({'error': '路径不合法'}, status=400)
            
        try:
            root_dir = get_root_directory()
            source_full_path = os.path.join(root_dir, source_path.strip('/'), source_name)
            target_full_path = os.path.join(root_dir, target_path.strip('/'), source_name)
            
            if not os.path.exists(source_full_path):
                return JsonResponse({'error': '源文件或文件夹不存在'}, status=404)
                
            if os.path.exists(target_full_path):
                return JsonResponse({'error': '目标位置已存在同名文件或文件夹'}, status=400)
                
            shutil.move(source_full_path, target_full_path)
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"移动文件错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

@csrf_exempt
def copy_item(request):
    """复制文件或文件夹"""
    if request.method == 'POST':
        data = json.loads(request.body)
        source_path = data.get('source_path', '')
        source_name = data.get('source_name', '')
        target_path = data.get('target_path', '')
        
        if not is_valid_path(source_path) or not is_valid_path(target_path):
            return JsonResponse({'error': '路径不合法'}, status=400)
            
        try:
            root_dir = get_root_directory()
            source_full_path = os.path.join(root_dir, source_path.strip('/'), source_name)
            target_full_path = os.path.join(root_dir, target_path.strip('/'), source_name)
            
            if not os.path.exists(source_full_path):
                return JsonResponse({'error': '源文件或文件夹不存在'}, status=404)
                
            if os.path.exists(target_full_path):
                return JsonResponse({'error': '目标位置已存在同名文件或文件夹'}, status=400)
                
            if os.path.isdir(source_full_path):
                shutil.copytree(source_full_path, target_full_path)
            else:
                shutil.copy2(source_full_path, target_full_path)
                
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"复制文件错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405)

def get_system_info(request):
    """获取系统信息"""
    if request.method == 'GET':
        try:
            import platform
            system_info = {
                'os': platform.system(),
                'root_dir': get_root_directory()
            }
            return JsonResponse(system_info)
        except Exception as e:
            logger.error(f"获取系统信息错误: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '不支持的请求方法'}, status=405) 