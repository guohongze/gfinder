import os
import shutil
import platform
import datetime
import mimetypes

def get_root_directory():
    """获取根目录，根据系统类型"""
    system = platform.system()
    if system == 'Windows':
        root_dir = 'd:\\data'
    else:  # Linux, Darwin等
        root_dir = '/var/opt/gfinder/data'
    
    # 如果目录不存在则创建
    if not os.path.exists(root_dir):
        os.makedirs(root_dir, exist_ok=True)
    
    return root_dir

def is_valid_path(path):
    """验证路径是否合法（防止路径穿越攻击）"""
    if not path:
        return True  # 空路径视为根目录
    
    # 标准化路径，去除.和..
    normalized_path = os.path.normpath(path)
    
    # 确保路径不会超出根目录
    if normalized_path.startswith('..') or '/../' in normalized_path:
        return False
    
    return True

def list_directory(path):
    """列出目录内容"""
    root_dir = get_root_directory()
    target_dir = os.path.join(root_dir, path.strip('/'))
    
    if not os.path.exists(target_dir):
        if path == '':  # 如果是根目录不存在，则创建
            os.makedirs(target_dir, exist_ok=True)
        else:
            raise FileNotFoundError(f"目录不存在: {path}")
    
    items = []
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        stat_info = os.stat(item_path)
        is_dir = os.path.isdir(item_path)
        
        # 获取MIME类型
        mimetype = None
        if not is_dir:
            mimetype, _ = mimetypes.guess_type(item_path)
        
        items.append({
            'name': item,
            'is_dir': is_dir,
            'size': stat_info.st_size if not is_dir else 0,
            'modified': datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'mimetype': mimetype,
        })
    
    # 排序：文件夹在前，文件在后，然后按名称排序
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    
    return items

def create_directory(path, name):
    """创建新目录"""
    root_dir = get_root_directory()
    parent_dir = os.path.join(root_dir, path.strip('/'))
    new_dir = os.path.join(parent_dir, name)
    
    if os.path.exists(new_dir):
        raise FileExistsError(f"目录已存在: {name}")
    
    os.makedirs(new_dir, exist_ok=True)
    return {'name': name, 'is_dir': True}

def rename_item(path, old_name, new_name):
    """重命名文件或目录"""
    root_dir = get_root_directory()
    parent_dir = os.path.join(root_dir, path.strip('/'))
    old_path = os.path.join(parent_dir, old_name)
    new_path = os.path.join(parent_dir, new_name)
    
    if not os.path.exists(old_path):
        raise FileNotFoundError(f"文件或目录不存在: {old_name}")
    
    if os.path.exists(new_path):
        raise FileExistsError(f"目标名称已存在: {new_name}")
    
    os.rename(old_path, new_path)
    is_dir = os.path.isdir(new_path)
    
    return {
        'name': new_name,
        'is_dir': is_dir,
        'size': 0 if is_dir else os.path.getsize(new_path)
    }

def delete_item(path, name):
    """删除文件或目录"""
    root_dir = get_root_directory()
    parent_dir = os.path.join(root_dir, path.strip('/'))
    target_path = os.path.join(parent_dir, name)
    
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"文件或目录不存在: {name}")
    
    if os.path.isdir(target_path):
        shutil.rmtree(target_path)
    else:
        os.remove(target_path)
    
    return {'name': name}

def get_file_content(path, filename):
    """获取文件内容"""
    root_dir = get_root_directory()
    file_path = os.path.join(root_dir, path.strip('/'), filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {filename}")
    
    if not os.path.isfile(file_path):
        raise IsADirectoryError(f"不是一个文件: {filename}")
    
    # 检查文件大小，如果过大可能需要特殊处理
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise ValueError("文件过大，无法预览")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果不是文本文件，返回二进制文件提示
        return "二进制文件，无法直接预览内容"

def save_file_content(path, filename, content):
    """保存文件内容"""
    root_dir = get_root_directory()
    file_path = os.path.join(root_dir, path.strip('/'), filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {'name': filename}

def create_file(path, name, content=""):
    """创建新文件"""
    root_dir = get_root_directory()
    parent_dir = os.path.join(root_dir, path.strip('/'))
    file_path = os.path.join(parent_dir, name)
    
    if os.path.exists(file_path):
        raise FileExistsError(f"文件已存在: {name}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {'name': name, 'is_dir': False} 