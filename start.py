#!/usr/bin/env python
"""
GFinder 启动脚本
根据系统环境自动配置并启动服务
"""

import os
import sys
import platform
import subprocess
import webbrowser
import argparse
import venv
import site
from pathlib import Path
from typing import Optional, Tuple

def create_default_directory() -> str:
    """
    创建默认数据目录
    
    Returns:
        str: 数据目录的路径
    """
    system = platform.system()
    if system == 'Windows':
        data_dir = 'd:\\data'
    else:  # Linux, Darwin等
        data_dir = '/var/opt/gfinder/data'
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"创建数据目录: {data_dir}")
    
    return data_dir

def get_venv_path(base_dir: str) -> str:
    """
    获取虚拟环境路径
    
    Args:
        base_dir: 基础目录路径
        
    Returns:
        str: 虚拟环境路径
    """
    return os.path.join(base_dir, "venv")

def get_venv_bin_dir(venv_dir: str) -> str:
    """
    获取虚拟环境二进制目录
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        str: 二进制目录路径
    """
    if platform.system() == 'Windows':
        return os.path.join(venv_dir, 'Scripts')
    return os.path.join(venv_dir, 'bin')

def get_venv_python(venv_dir: str) -> str:
    """
    获取虚拟环境Python解释器路径
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        str: Python解释器路径
    """
    bin_dir = get_venv_bin_dir(venv_dir)
    if platform.system() == 'Windows':
        return os.path.join(bin_dir, 'python.exe')
    return os.path.join(bin_dir, 'python')

def get_venv_site_packages(venv_dir: str) -> str:
    """
    获取虚拟环境的site-packages路径
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        str: site-packages目录路径
    """
    if platform.system() == 'Windows':
        return os.path.join(venv_dir, 'Lib', 'site-packages')
    else:
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        return os.path.join(venv_dir, 'lib', python_version, 'site-packages')

def create_or_update_venv(venv_dir: str) -> bool:
    """
    创建或更新虚拟环境
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        bool: 是否为新创建的虚拟环境
    """
    if not os.path.exists(venv_dir):
        print(f"创建虚拟环境: {venv_dir}")
        venv.create(venv_dir, with_pip=True)
        return True
    else:
        print(f"使用已存在的虚拟环境: {venv_dir}")
        return False

def install_requirements_in_venv(venv_dir: str) -> bool:
    """
    在虚拟环境中安装所需的Python依赖
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        bool: 安装是否成功
    """
    python_exec = get_venv_python(venv_dir)
    
    try:
        print("正在安装依赖...")
        requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        if os.path.exists(requirements_file):
            subprocess.check_call([python_exec, "-m", "pip", "install", "-r", requirements_file])
        else:
            subprocess.check_call([python_exec, "-m", "pip", "install", "django", "django-cors-headers"])
        print("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装依赖失败: {e}")
        return False

def check_venv_dependencies(venv_dir: str) -> bool:
    """
    检查虚拟环境中是否已安装所需依赖
    
    Args:
        venv_dir: 虚拟环境目录
        
    Returns:
        bool: 依赖是否已安装
    """
    python_exec = get_venv_python(venv_dir)
    
    try:
        result = subprocess.run(
            [python_exec, "-c", "import django; import corsheaders; print('OK')"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == 'OK'
    except Exception:
        return False

def build_frontend(force_build: bool = False) -> None:
    """
    构建前端
    
    Args:
        force_build: 是否强制重新构建
    """
    base_dir = Path(__file__).resolve().parent
    frontend_dir = os.path.join(base_dir, 'frontend')
    dist_dir = os.path.join(frontend_dir, 'dist')
    
    if not os.path.exists(dist_dir) or force_build:
        print("需要构建前端...")
        if os.path.exists(os.path.join(frontend_dir, 'package.json')):
            try:
                if platform.system() == 'Windows':
                    print("在Windows上构建前端...")
                    subprocess.check_call('cd frontend && npm install', shell=True)
                    subprocess.check_call('cd frontend && npm run build', shell=True)
                else:
                    print("在Linux/Mac上构建前端...")
                    subprocess.check_call('cd frontend && npm install && npm run build', shell=True)
                print("前端构建完成")
            except subprocess.CalledProcessError as e:
                print(f"前端构建失败: {e}")
                print("请手动构建前端: cd frontend && npm install && npm run build")
        else:
            print("未找到前端项目，请检查frontend目录")
    else:
        print("前端已构建")

def main() -> None:
    """主函数"""
    base_dir = Path(__file__).resolve().parent
    
    parser = argparse.ArgumentParser(description='启动GFinder服务')
    parser.add_argument('--build', action='store_true', help='强制重新构建前端')
    parser.add_argument('--no-build', action='store_true', help='跳过前端构建')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口号')
    parser.add_argument('--no-venv', action='store_true', help='不使用虚拟环境')
    args = parser.parse_args()
    
    data_dir = create_default_directory()
    print(f"数据存储位置: {data_dir}")
    
    venv_dir = get_venv_path(base_dir)
    
    if args.no_venv:
        print("按要求不使用虚拟环境")
    else:
        is_new_venv = create_or_update_venv(venv_dir)
        
        if is_new_venv or not check_venv_dependencies(venv_dir):
            if not install_requirements_in_venv(venv_dir):
                print("依赖安装失败，请检查错误信息")
                return
        
        venv_site_packages = get_venv_site_packages(venv_dir)
        if os.path.exists(venv_site_packages):
            print(f"使用虚拟环境包路径: {venv_site_packages}")
            sys.path.insert(0, venv_site_packages)
        else:
            print(f"错误: 虚拟环境site-packages不存在: {venv_site_packages}")
            return
    
    if not args.no_build:
        build_frontend(force_build=args.build)
    
    frontend_dir = os.path.join(base_dir, 'frontend', 'dist')
    if not os.path.exists(frontend_dir):
        print("警告: 前端文件未构建，可能影响系统使用")
        print("您可以运行: python start.py --build 来构建前端")
    
    port = args.port
    host = '0.0.0.0'
    print(f"正在启动GFinder服务，访问地址: http://localhost:{port}")
    
    webbrowser.open(f"http://localhost:{port}")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gfinder.settings')
    
    try:
        if args.no_venv:
            from django.core.management import execute_from_command_line
            execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
        else:
            try:
                import django
                from django.core.management import execute_from_command_line
                execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])
            except ImportError as e:
                print(f"导入Django失败: {e}")
                print("尝试使用虚拟环境Python执行...")
                python_exec = get_venv_python(venv_dir)
                manage_py = os.path.join(base_dir, 'manage.py')
                subprocess.check_call([python_exec, manage_py, 'runserver', f'{host}:{port}'])
    except Exception as e:
        print(f"启动Django服务失败: {e}")
        print("请确保虚拟环境中已安装所有依赖")
        return

if __name__ == '__main__':
    main() 