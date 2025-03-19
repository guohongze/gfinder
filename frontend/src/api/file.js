import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    if (response.status === 200) {
      return response.data
    }
    return Promise.reject(new Error('请求失败'))
  },
  error => {
    let errorMessage = '网络错误'
    if (error.response) {
      const { status, data } = error.response
      if (data && data.error) {
        errorMessage = data.error
      } else {
        switch (status) {
          case 400: errorMessage = '请求参数错误'; break
          case 401: errorMessage = '未授权，请重新登录'; break
          case 403: errorMessage = '拒绝访问'; break
          case 404: errorMessage = '请求资源不存在'; break
          case 500: errorMessage = '服务器内部错误'; break
          default: errorMessage = `请求失败(${status})`
        }
      }
    } else if (error.request) {
      errorMessage = '服务器无响应'
    } else {
      errorMessage = error.message
    }
    
    return Promise.reject(new Error(errorMessage))
  }
)

// 文件API服务
export const fileApi = {
  // 获取系统信息
  getSystemInfo() {
    return api.get('/api/system-info')
  },
  
  // 列出目录内容
  listDirectory(path = '') {
    return api.get('/api/list', { params: { path } })
  },
  
  // 创建目录
  createDirectory(path, name) {
    return api.post('/api/operation', {
      operation: 'create_directory',
      path,
      name
    })
  },
  
  // 重命名项目
  renameItem(path, oldName, newName) {
    return api.post('/api/operation', {
      operation: 'rename',
      path,
      old_name: oldName,
      new_name: newName
    })
  },
  
  // 删除项目
  deleteItem(path, name) {
    return api.post('/api/operation', {
      operation: 'delete',
      path,
      name
    })
  },
  
  // 创建文件
  createFile(path, name, content = '') {
    return api.post('/api/operation', {
      operation: 'create_file',
      path,
      name,
      content
    })
  },
  
  // 预览文件
  previewFile(path, filename) {
    return api.get('/api/preview', { 
      params: { path, filename }
    })
  },
  
  // 保存文件内容
  saveFile(path, filename, content) {
    return api.post('/api/save', {
      path,
      filename,
      content
    })
  },
  
  // 上传文件 - 使用formData
  uploadFile(path, file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('path', path)
    
    return api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 下载文件 - 使用浏览器重定向
  downloadFile(path, filename) {
    // 确保路径不以/开头或结尾，防止路径验证问题
    const cleanPath = path ? path.replace(/^\/+|\/+$/g, '') : '';
    const url = `/api/download?path=${encodeURIComponent(cleanPath)}&filename=${encodeURIComponent(filename)}`;
    
    // 使用fetch代替window.open以便处理可能的错误
    return fetch(url)
      .then(response => {
        if (!response.ok) {
          // 如果响应不成功，尝试解析错误信息
          return response.json().then(data => {
            throw new Error(data.error || '下载失败');
          });
        }
        
        // 获取响应中的文件名
        const contentDisposition = response.headers.get('Content-Disposition');
        let finalFilename = filename;
        if (contentDisposition) {
          const matches = /filename="(.+?)"/.exec(contentDisposition);
          if (matches && matches[1]) {
            finalFilename = matches[1];
          }
        }
        
        // 转为blob并使用a标签下载
        return response.blob().then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = finalFilename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          a.remove();
        });
      })
      .catch(error => {
        console.error('下载文件失败:', error);
        throw error;
      });
  },
  
  // 移动项目
  moveItem(sourcePath, sourceName, targetPath) {
    return api.post('/api/move', {
      source_path: sourcePath,
      source_name: sourceName,
      target_path: targetPath
    })
  },
  
  // 复制项目
  copyItem(sourcePath, sourceName, targetPath) {
    return api.post('/api/copy', {
      source_path: sourcePath,
      source_name: sourceName,
      target_path: targetPath
    })
  }
} 