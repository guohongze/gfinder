<template>
  <div class="file-manager">
    <!-- 顶部导航栏 -->
    <header class="file-header">
      <div class="logo">
        <el-icon><Folder /></el-icon>
        <span>GFinder</span>
      </div>
      <div class="breadcrumb">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">
            <el-icon><HomeFilled /></el-icon>
            根目录
          </el-breadcrumb-item>
          <el-breadcrumb-item 
            v-for="(item, index) in breadcrumbItems" 
            :key="index" 
            :to="{ path: `/folder/${getBreadcrumbPath(index)}` }"
          >
            {{ item }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="operations">
        <!-- 视图切换按钮 -->
        <el-dropdown @command="changeViewMode" trigger="click">
          <el-button>
            <el-icon><Menu /></el-icon>
            视图
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item :command="'table'" :class="{ 'active-view': viewMode === 'table' }">
                <el-icon><Document /></el-icon> 详细信息
              </el-dropdown-item>
              <el-dropdown-item :command="'grid-small'" :class="{ 'active-view': viewMode === 'grid-small' }">
                <el-icon><Grid /></el-icon> 小图标
              </el-dropdown-item>
              <el-dropdown-item :command="'grid-medium'" :class="{ 'active-view': viewMode === 'grid-medium' }">
                <el-icon><Grid /></el-icon> 中图标
              </el-dropdown-item>
              <el-dropdown-item :command="'grid-large'" :class="{ 'active-view': viewMode === 'grid-large' }">
                <el-icon><Grid /></el-icon> 大图标
              </el-dropdown-item>
              <el-dropdown-item :command="'list'" :class="{ 'active-view': viewMode === 'list' }">
                <el-icon><Menu /></el-icon> 列表
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <el-button type="primary" @click="refreshFiles">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="file-content" v-loading="loading">
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-button-group>
          <el-button @click="createNewFolder">
            <el-icon><FolderAdd /></el-icon>
            新建文件夹
          </el-button>
          <el-button @click="uploadFilesDialog = true">
            <el-icon><Upload /></el-icon>
            上传文件
          </el-button>
          <el-button 
            v-if="selectedFiles.length > 0" 
            :disabled="selectedFiles.length === 0"
            @click="downloadSelectedFiles"
          >
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </el-button-group>
        
        <div class="selection-operations" v-if="selectedFiles.length > 0">
          <el-button-group>
            <el-button @click="cutSelectedFiles">
              <el-icon><Scissors /></el-icon>
              剪切
            </el-button>
            <el-button @click="copySelectedFiles">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button 
              type="danger" 
              @click="deleteSelectedFiles"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </el-button-group>
          
          <span class="selection-count">已选择 {{ selectedFiles.length }} 项</span>
        </div>
        
        <div class="clipboard-operations" v-if="clipboard.items.length > 0">
          <el-button @click="pasteFiles">
            <el-icon><DocumentCopy /></el-icon>
            粘贴 ({{ clipboard.items.length }}项)
          </el-button>
          <el-button @click="clearClipboard">
            <el-icon><Close /></el-icon>
            清空剪贴板
          </el-button>
        </div>
      </div>

      <!-- 文件列表 -->
      <div 
        class="file-container"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
        @click="handleContainerClick"
        :class="{ 'drag-over': isDragOver }"
      >
        <!-- 表格视图 (详细信息) -->
        <el-table
          v-if="viewMode === 'table'"
          ref="fileTable"
          :data="filesList"
          style="width: 100%"
          @selection-change="handleSelectionChange"
          @row-contextmenu="handleContextMenu"
          @row-click="handleRowClick"
          @row-dblclick="handleRowDblClick"
          :default-sort="{ prop: 'is_dir', order: 'descending' }"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="名称" sortable>
            <template #default="scope">
              <div class="file-name">
                <el-icon :color="getFileIconColor(scope.row)" :size="20">
                  <component :is="getFileIconComponent(scope.row)" />
                </el-icon>
                <span>{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="大小" sortable width="180">
            <template #default="scope">
              {{ scope.row.is_dir ? '-' : formatFileSize(scope.row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="modified" label="修改时间" sortable width="200" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button-group>
                <el-button
                  v-if="!scope.row.is_dir"
                  size="small"
                  @click.stop="downloadFile(scope.row)"
                >
                  <el-icon><Download /></el-icon>
                </el-button>
                <el-button
                  v-if="!scope.row.is_dir && isPreviewable(scope.row)"
                  size="small"
                  @click.stop="previewFile(scope.row)"
                >
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button
                  size="small"
                  @click.stop="renameItem(scope.row)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click.stop="deleteItem(scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 网格视图 (图标视图) -->
        <div v-else-if="viewMode.startsWith('grid')" class="grid-view" :class="viewMode">
          <div
            v-for="(item, index) in filesList"
            :key="index"
            class="grid-item"
            @dblclick="handleItemDblClick(item)"
            @click="handleItemClick(item, $event)"
            @contextmenu.prevent="handleItemContextMenu(item, $event)"
            :class="{ 'selected': isSelected(item) }"
          >
            <div class="icon">
              <el-icon :color="getFileIconColor(item)" :size="viewMode === 'grid-small' ? 32 : viewMode === 'grid-medium' ? 48 : 64">
                <component :is="getFileIconComponent(item)" />
              </el-icon>
            </div>
            <div class="name" :title="item.name">{{ item.name }}</div>
            <div v-if="viewMode === 'grid-medium' || viewMode === 'grid-large'" class="details">
              <small>{{ item.is_dir ? '文件夹' : formatFileSize(item.size) }}</small>
            </div>
          </div>
        </div>
        
        <!-- 列表视图 -->
        <div v-else-if="viewMode === 'list'" class="list-view">
          <ul>
            <li
              v-for="(item, index) in filesList"
              :key="index"
              @dblclick="handleItemDblClick(item)"
              @click="handleItemClick(item, $event)"
              @contextmenu.prevent="handleItemContextMenu(item, $event)"
              :class="{ 'selected': isSelected(item) }"
            >
              <div class="list-item">
                <div class="icon">
                  <el-icon :color="getFileIconColor(item)" :size="18">
                    <component :is="getFileIconComponent(item)" />
                  </el-icon>
                </div>
                <div class="name">{{ item.name }}</div>
                <div class="size">{{ item.is_dir ? '-' : formatFileSize(item.size) }}</div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </main>

    <!-- 右键菜单 -->
    <div
      v-show="contextMenu.visible"
      class="context-menu"
      :style="{
        left: `${contextMenu.x}px`,
        top: `${contextMenu.y}px`
      }"
    >
      <div v-if="contextMenu.item">
        <ul>
          <li v-if="contextMenu.item.is_dir" @click="openFolder(contextMenu.item)">
            <el-icon><FolderOpened /></el-icon> 打开
          </li>
          <li v-if="!contextMenu.item.is_dir && isPreviewable(contextMenu.item)" @click="previewFile(contextMenu.item)">
            <el-icon><View /></el-icon> 预览
          </li>
          <li v-if="!contextMenu.item.is_dir" @click="downloadFile(contextMenu.item)">
            <el-icon><Download /></el-icon> 下载
          </li>
          <li @click="renameItem(contextMenu.item)">
            <el-icon><Edit /></el-icon> 重命名
          </li>
          <li @click="cutItem(contextMenu.item)">
            <el-icon><Scissors /></el-icon> 剪切
          </li>
          <li @click="copyItem(contextMenu.item)">
            <el-icon><CopyDocument /></el-icon> 复制
          </li>
          <li @click="deleteItem(contextMenu.item)">
            <el-icon><Delete /></el-icon> 删除
          </li>
        </ul>
      </div>
      <div v-else>
        <ul>
          <li @click="createNewFolder">
            <el-icon><FolderAdd /></el-icon> 新建文件夹
          </li>
          <li @click="uploadFilesDialog = true">
            <el-icon><Upload /></el-icon> 上传文件
          </li>
          <li v-if="clipboard.items.length > 0" @click="pasteFiles">
            <el-icon><DocumentCopy /></el-icon> 粘贴
          </li>
          <li @click="refreshFiles">
            <el-icon><Refresh /></el-icon> 刷新
          </li>
        </ul>
      </div>
    </div>

    <!-- 对话框: 上传文件 -->
    <el-dialog
      v-model="uploadFilesDialog"
      title="上传文件"
      width="500px"
    >
      <upload-file
        :current-path="currentPath"
        @uploaded="handleFileUploaded"
      />
    </el-dialog>

    <!-- 对话框: 预览文件 -->
    <el-dialog
      v-model="previewDialog.visible"
      :title="previewDialog.title"
      width="80%"
      top="5vh"
      :before-close="closePreview"
    >
      <file-preview
        v-if="previewDialog.visible" 
        :file="previewDialog.file"
        :current-path="currentPath"
      />
    </el-dialog>

    <!-- 对话框: 新建文件夹 -->
    <el-dialog
      v-model="newFolderDialog.visible"
      title="新建文件夹"
      width="400px"
    >
      <el-form @submit.prevent="confirmCreateFolder">
        <el-form-item label="文件夹名称">
          <el-input
            v-model="newFolderDialog.name"
            placeholder="请输入文件夹名称"
            autofocus
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="confirmCreateFolder">创建</el-button>
          <el-button @click="newFolderDialog.visible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- 对话框: 重命名 -->
    <el-dialog
      v-model="renameDialog.visible"
      title="重命名"
      width="400px"
    >
      <el-form @submit.prevent="confirmRename">
        <el-form-item label="新名称">
          <el-input
            v-model="renameDialog.newName"
            placeholder="请输入新名称"
            autofocus
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="confirmRename">确定</el-button>
          <el-button @click="renameDialog.visible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import FilePreview from '../components/FilePreview.vue'
import UploadFile from '../components/UploadFile.vue'
import { fileApi } from '../api/file'
import { 
  ArrowDown, Picture, Files, Menu, Grid, Document, Folder, Finished,
  VideoPlay, Link, Collection, Tickets, PriceTag, Connection, Film, Reading
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 获取文件图标类型
const getFileIconComponent = (file) => {
  if (file.is_dir) return Folder
  
  const ext = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
  
  // 根据文件扩展名返回对应图标
  switch(ext) {
    // 图片类
    case 'jpg': case 'jpeg': case 'png': case 'gif': case 'svg': case 'bmp': case 'webp':
      return Picture
    // 文档类
    case 'pdf': case 'doc': case 'docx': case 'txt': case 'md':
      return Document 
    // 表格类
    case 'xls': case 'xlsx': case 'csv':
      return Tickets
    // 演示文稿
    case 'ppt': case 'pptx':
      return Finished
    // 视频文件
    case 'mp4': case 'avi': case 'mov': case 'wmv': case 'flv':
      return VideoPlay
    // 音频文件
    case 'mp3': case 'wav': case 'ogg': case 'flac':
      return Film
    // 压缩文件
    case 'zip': case 'rar': case '7z': case 'tar': case 'gz':
      return Collection
    // 代码文件
    case 'js': case 'py': case 'java': case 'c': case 'cpp': case 'php': case 'html': case 'css':
      return Connection
    // 链接文件
    case 'lnk': case 'url':
      return Link
    // 可执行文件
    case 'exe': case 'msi': case 'bat': case 'sh':
      return Reading
    // 其他文件使用通用图标
    default:
      return Files
  }
}

// 获取文件图标颜色
const getFileIconColor = (file) => {
  if (file.is_dir) return '#409EFF' // 文件夹蓝色
  
  const ext = file.name.substring(file.name.lastIndexOf('.') + 1).toLowerCase()
  
  // 根据文件类型返回不同颜色
  // 图片类
  if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp'].includes(ext)) 
    return '#67C23A' // 绿色
  // 文档类
  if (['pdf', 'doc', 'docx', 'txt', 'md'].includes(ext)) 
    return '#E6A23C' // 黄色
  // 表格类
  if (['xls', 'xlsx', 'csv'].includes(ext)) 
    return '#19be6b' // 绿色
  // 演示文稿
  if (['ppt', 'pptx'].includes(ext)) 
    return '#FF7D00' // 橙色
  // 视频文件
  if (['mp4', 'avi', 'mov', 'wmv', 'flv'].includes(ext)) 
    return '#9254de' // 紫色
  // 音频文件
  if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) 
    return '#722ed1' // 紫色
  // 压缩文件
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) 
    return '#F56C6C' // 红色
  // 代码文件
  if (['js', 'py', 'java', 'c', 'cpp', 'php', 'html', 'css'].includes(ext)) 
    return '#17a2b8' // 蓝绿色
  
  return '#909399' // 默认灰色
}

// 状态
const loading = ref(false)
const filesList = ref([])
const selectedFiles = ref([])
const currentPath = ref('')
const clipboard = ref({
  action: '', // 'copy' 或 'cut'
  items: []
})

// 对话框状态
const uploadFilesDialog = ref(false)
const previewDialog = ref({
  visible: false,
  title: '',
  file: null
})
const newFolderDialog = ref({
  visible: false,
  name: ''
})
const renameDialog = ref({
  visible: false,
  item: null,
  newName: ''
})

// 右键菜单状态
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  item: null
})

// 拖拽状态
const isDragOver = ref(false)

// 视图模式状态
const viewMode = ref(localStorage.getItem('gfinder-view-mode') || 'table')

// 计算面包屑项
const breadcrumbItems = computed(() => {
  if (!currentPath.value) return []
  return currentPath.value.split('/').filter(item => item)
})

// 获取面包屑路径
const getBreadcrumbPath = (index) => {
  return breadcrumbItems.value.slice(0, index + 1).join('/')
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) {
    return size + ' B'
  } else if (size < 1024 * 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  } else if (size < 1024 * 1024 * 1024) {
    return (size / 1024 / 1024).toFixed(2) + ' MB'
  } else {
    return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB'
  }
}

// 判断文件是否可预览
const isPreviewable = (file) => {
  if (file.is_dir) return false
  
  const previewableExtensions = [
    // 文本文件
    '.txt', '.md', '.js', '.py', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
    // 图片文件
    '.jpg', '.jpeg', '.png', '.gif', '.bmp',
    // PDF
    '.pdf'
  ]
  
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
  return previewableExtensions.includes(ext)
}

// 加载当前目录文件
const loadFiles = async () => {
  try {
    loading.value = true
    const response = await fileApi.listDirectory(currentPath.value)
    filesList.value = response.items
  } catch (error) {
    ElMessage.error('加载文件列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理路由变化
const handleRouteChange = () => {
  let path = ''
  if (route.params.path) {
    path = Array.isArray(route.params.path) 
      ? route.params.path.join('/') 
      : route.params.path
  }
  currentPath.value = path
  loadFiles()
}

// 刷新文件列表
const refreshFiles = () => {
  loadFiles()
}

// 打开文件夹
const openFolder = (folder) => {
  if (!folder.is_dir) return
  
  const newPath = currentPath.value 
    ? `${currentPath.value}/${folder.name}`
    : folder.name
    
  router.push(`/folder/${newPath}`)
}

// 下载文件
const downloadFile = async (file) => {
  if (file.is_dir) return
  
  try {
    await fileApi.downloadFile(currentPath.value, file.name)
  } catch (error) {
    ElMessage.error('下载文件失败: ' + error.message)
  }
}

// 预览文件
const previewFile = (file) => {
  if (file.is_dir || !isPreviewable(file)) return
  
  previewDialog.value = {
    visible: true,
    title: file.name,
    file: file
  }
}

// 关闭预览
const closePreview = () => {
  previewDialog.value.visible = false
  nextTick(() => {
    previewDialog.value.file = null
  })
}

// 创建文件夹对话框
const createNewFolder = () => {
  newFolderDialog.value = {
    visible: true,
    name: ''
  }
}

// 确认创建文件夹
const confirmCreateFolder = async () => {
  if (!newFolderDialog.value.name) {
    ElMessage.warning('请输入文件夹名称')
    return
  }
  
  try {
    await fileApi.createDirectory(
      currentPath.value, 
      newFolderDialog.value.name
    )
    ElMessage.success('创建文件夹成功')
    newFolderDialog.value.visible = false
    loadFiles()
  } catch (error) {
    ElMessage.error('创建文件夹失败: ' + error.message)
  }
}

// 重命名对话框
const renameItem = (item) => {
  renameDialog.value = {
    visible: true,
    item: item,
    newName: item.name
  }
}

// 确认重命名
const confirmRename = async () => {
  if (!renameDialog.value.newName) {
    ElMessage.warning('请输入新名称')
    return
  }
  
  if (renameDialog.value.item.name === renameDialog.value.newName) {
    renameDialog.value.visible = false
    return
  }
  
  try {
    await fileApi.renameItem(
      currentPath.value,
      renameDialog.value.item.name,
      renameDialog.value.newName
    )
    ElMessage.success('重命名成功')
    renameDialog.value.visible = false
    loadFiles()
  } catch (error) {
    ElMessage.error('重命名失败: ' + error.message)
  }
}

// 删除项目
const deleteItem = (item) => {
  ElMessageBox.confirm(
    `确定要删除 ${item.name} 吗？${item.is_dir ? '将删除文件夹内的所有内容，' : ''}此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await fileApi.deleteItem(currentPath.value, item.name)
      ElMessage.success('删除成功')
      loadFiles()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
}

// 选择文件变化处理
const handleSelectionChange = (selection) => {
  selectedFiles.value = selection
}

// 删除选中的文件
const deleteSelectedFiles = () => {
  if (selectedFiles.value.length === 0) return
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedFiles.value.length} 项吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      loading.value = true
      const promises = selectedFiles.value.map(file => 
        fileApi.deleteItem(currentPath.value, file.name)
      )
      await Promise.all(promises)
      ElMessage.success('删除成功')
      loadFiles()
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
      loadFiles()
    } finally {
      loading.value = false
    }
  }).catch(() => {})
}

// 下载选中的文件
const downloadSelectedFiles = () => {
  if (selectedFiles.value.length === 0) return
  
  // 只能下载文件，不能下载文件夹
  const filesToDownload = selectedFiles.value.filter(item => !item.is_dir)
  
  if (filesToDownload.length === 0) {
    ElMessage.warning('请选择至少一个文件进行下载')
    return
  }
  
  if (filesToDownload.length === 1) {
    // 单个文件直接下载
    downloadFile(filesToDownload[0])
  } else {
    ElMessage.warning('目前仅支持单个文件下载')
    // 如果要支持多文件下载，需要实现后端批量打包下载功能
  }
}

// 剪切选中的文件
const cutSelectedFiles = () => {
  if (selectedFiles.value.length === 0) return
  
  clipboard.value = {
    action: 'cut',
    items: [...selectedFiles.value],
    sourcePath: currentPath.value
  }
  
  ElMessage.success(`已将 ${selectedFiles.value.length} 项添加到剪贴板`)
}

// 复制选中的文件
const copySelectedFiles = () => {
  if (selectedFiles.value.length === 0) return
  
  clipboard.value = {
    action: 'copy',
    items: [...selectedFiles.value],
    sourcePath: currentPath.value
  }
  
  ElMessage.success(`已将 ${selectedFiles.value.length} 项添加到剪贴板`)
}

// 剪切单个项目
const cutItem = (item) => {
  clipboard.value = {
    action: 'cut',
    items: [item],
    sourcePath: currentPath.value
  }
  
  ElMessage.success(`已将 ${item.name} 添加到剪贴板`)
}

// 复制单个项目
const copyItem = (item) => {
  clipboard.value = {
    action: 'copy',
    items: [item],
    sourcePath: currentPath.value
  }
  
  ElMessage.success(`已将 ${item.name} 添加到剪贴板`)
}

// 粘贴文件
const pasteFiles = async () => {
  if (clipboard.value.items.length === 0) return
  
  try {
    loading.value = true
    
    // 避免在相同目录内粘贴剪切的文件
    if (clipboard.value.action === 'cut' && 
        clipboard.value.sourcePath === currentPath.value) {
      ElMessage.warning('不能在同一目录内粘贴剪切的文件')
      return
    }
    
    const promises = clipboard.value.items.map(item => {
      if (clipboard.value.action === 'cut') {
        return fileApi.moveItem(
          clipboard.value.sourcePath,
          item.name,
          currentPath.value
        )
      } else {
        return fileApi.copyItem(
          clipboard.value.sourcePath,
          item.name,
          currentPath.value
        )
      }
    })
    
    await Promise.all(promises)
    
    // 如果是剪切操作，粘贴后清空剪贴板
    if (clipboard.value.action === 'cut') {
      clipboard.value = { action: '', items: [] }
    }
    
    ElMessage.success('粘贴成功')
    loadFiles()
  } catch (error) {
    ElMessage.error('粘贴失败: ' + error.message)
    loadFiles()
  } finally {
    loading.value = false
  }
}

// 清空剪贴板
const clearClipboard = () => {
  clipboard.value = { action: '', items: [] }
}

// 处理文件上传完成
const handleFileUploaded = () => {
  uploadFilesDialog.value = false
  loadFiles()
}

// 处理右键菜单
const handleContextMenu = (row, column, event) => {
  event.preventDefault()
  
  const rect = event.target.getBoundingClientRect()
  
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    item: row
  }
  
  document.addEventListener('click', hideContextMenu, { once: true })
}

// 隐藏右键菜单
const hideContextMenu = () => {
  contextMenu.value.visible = false
}

// 处理行点击
const handleRowClick = (row) => {
  // 如果右键菜单显示，隐藏它
  if (contextMenu.value.visible) {
    hideContextMenu()
  }
}

// 处理行双击
const handleRowDblClick = (row) => {
  if (row.is_dir) {
    openFolder(row)
  } else if (isPreviewable(row)) {
    previewFile(row)
  } else {
    downloadFile(row)
  }
}

// 处理拖拽文件到页面上
const onDragOver = (event) => {
  isDragOver.value = true
}

const onDragLeave = (event) => {
  isDragOver.value = false
}

const onDrop = async (event) => {
  isDragOver.value = false
  
  if (!event.dataTransfer.files || event.dataTransfer.files.length === 0) {
    return
  }
  
  try {
    loading.value = true
    
    const promises = []
    for (let i = 0; i < event.dataTransfer.files.length; i++) {
      const file = event.dataTransfer.files[i]
      promises.push(fileApi.uploadFile(currentPath.value, file))
    }
    
    await Promise.all(promises)
    ElMessage.success('文件上传成功')
    loadFiles()
  } catch (error) {
    ElMessage.error('文件上传失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 更改视图模式
const changeViewMode = (mode) => {
  viewMode.value = mode
  localStorage.setItem('gfinder-view-mode', mode)
}

// 检查文件是否被选中
const isSelected = (item) => {
  return selectedFiles.value.some(file => file.name === item.name)
}

// 处理项目点击
const handleItemClick = (item, event) => {
  // 按住Ctrl键可以多选
  if (event.ctrlKey) {
    const index = selectedFiles.value.findIndex(file => file.name === item.name)
    if (index === -1) {
      selectedFiles.value.push(item)
    } else {
      selectedFiles.value.splice(index, 1)
    }
  } else {
    selectedFiles.value = [item]
  }
}

// 处理项目双击
const handleItemDblClick = (item) => {
  if (item.is_dir) {
    openFolder(item)
  } else if (isPreviewable(item)) {
    previewFile(item)
  } else {
    downloadFile(item)
  }
}

// 处理项目右键菜单
const handleItemContextMenu = (item, event) => {
  // 如果项目未被选中，则选中它
  if (!isSelected(item)) {
    selectedFiles.value = [item]
  }
  
  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    item: item
  }
  
  document.addEventListener('click', hideContextMenu, { once: true })
}

// 处理容器点击事件（清除选择）
const handleContainerClick = (event) => {
  // 只有当点击的是容器本身而不是内部的项目时才清除选择
  const isContainer = event.target.classList.contains('file-container') || 
                      (event.target.closest('.file-container') && 
                       !event.target.closest('.grid-item') && 
                       !event.target.closest('.list-item') && 
                       !event.target.closest('tr'));
  
  if (isContainer) {
    selectedFiles.value = [];
  }
}

// 生命周期钩子
onMounted(() => {
  handleRouteChange()
  window.addEventListener('click', (e) => {
    if (e.button !== 2) { // 不是右键点击
      hideContextMenu()
    }
  })
  
  document.addEventListener('contextmenu', (e) => {
    // 如果在文件容器内右键点击背景
    if (e.target.classList.contains('file-container') || 
        e.target.closest('.file-container') && !e.target.closest('.el-table__row')) {
      e.preventDefault()
      contextMenu.value = {
        visible: true,
        x: e.clientX,
        y: e.clientY,
        item: null
      }
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('click', hideContextMenu)
})

// 监听路由变化
const unwatchRoute = router.afterEach(handleRouteChange)
onUnmounted(() => {
  unwatchRoute()
})
</script>

<style scoped>
.file-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.file-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f7fa;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  margin-right: 20px;
}

.logo .el-icon {
  margin-right: 8px;
  font-size: 20px;
  color: #409eff;
}

.breadcrumb {
  flex: 1;
  font-size: 14px;
}

.file-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.toolbar {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.selection-operations {
  display: flex;
  align-items: center;
}

.selection-count {
  margin-left: 10px;
  color: #606266;
}

.file-container {
  flex: 1;
  border: 2px dashed transparent;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.file-container.drag-over {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

.file-name {
  display: flex;
  align-items: center;
}

.file-name .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.file-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
  object-fit: contain;
}

.context-menu {
  position: fixed;
  z-index: 9999;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px 0;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu li {
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.context-menu li:hover {
  background-color: #f5f7fa;
}

.context-menu .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 视图样式 */
.active-view {
  color: #409eff;
  font-weight: bold;
}

/* 网格视图样式 */
.grid-view {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  padding: 8px;
  transition: background-color 0.2s;
  user-select: none;
}

.grid-item:hover {
  background-color: #f5f7fa;
}

.grid-item.selected {
  background-color: #ecf5ff;
}

.grid-view .icon {
  display: flex;
  justify-content: center;
  align-items: center;
}

.grid-view .name {
  margin-top: 5px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
}

.grid-view .details {
  margin-top: 3px;
  font-size: 12px;
  color: #909399;
}

/* 小图标视图 */
.grid-small .grid-item {
  width: 80px;
  height: 80px;
}

.grid-small .icon {
  font-size: 24px;
}

.grid-small .name {
  width: 75px;
  white-space: nowrap;
}

/* 中图标视图 */
.grid-medium .grid-item {
  width: 120px;
  height: 120px;
}

.grid-medium .icon {
  font-size: 36px;
}

.grid-medium .name {
  width: 110px;
  white-space: nowrap;
}

/* 大图标视图 */
.grid-large .grid-item {
  width: 160px;
  height: 160px;
}

.grid-large .icon {
  font-size: 48px;
}

.grid-large .name {
  width: 150px;
  white-space: nowrap;
}

.grid-large .icon .el-icon {
  font-size: 48px;
}

/* 列表视图样式 */
.list-view {
  width: 100%;
}

.list-view ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-view li {
  padding: 8px 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.list-view li:hover {
  background-color: #f5f7fa;
}

.list-view li.selected {
  background-color: #ecf5ff;
}

.list-item {
  display: flex;
  align-items: center;
}

.list-item .icon {
  margin-right: 8px;
  font-size: 18px;
}

.list-item .name {
  flex: 1;
}

.list-item .size {
  margin-left: auto;
  color: #909399;
  font-size: 14px;
}
</style> 