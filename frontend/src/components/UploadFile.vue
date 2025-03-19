<template>
  <div class="upload-file">
    <el-upload
      class="upload-area"
      :action="uploadUrl"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :before-upload="beforeUpload"
      :multiple="true"
      :data="uploadData"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          可以一次上传多个文件，上传过程中请勿关闭窗口
        </div>
      </template>
    </el-upload>
    
    <div v-if="fileList.length > 0" class="upload-list">
      <el-divider>上传列表</el-divider>
      <el-table :data="fileList" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小">
          <template #default="scope">
            {{ formatSize(scope.row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度">
          <template #default="scope">
            <el-progress 
              v-if="scope.row.status === 'uploading'"
              :percentage="scope.row.progress" 
            />
            <span v-else-if="scope.row.status === 'success'">已完成</span>
            <span v-else-if="scope.row.status === 'error'" class="error-message">
              {{ scope.row.errorMessage || '上传失败' }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  currentPath: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['uploaded'])

// 上传列表
const fileList = ref([])

// 上传URL
const uploadUrl = '/api/upload'

// 上传附加数据
const uploadData = computed(() => {
  return { path: props.currentPath }
})

// 格式化文件大小
const formatSize = (size) => {
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

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'uploading': return 'info'
    case 'success': return 'success'
    case 'error': return 'danger'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'uploading': return '上传中'
    case 'success': return '成功'
    case 'error': return '失败'
    default: return '等待'
  }
}

// 上传前处理
const beforeUpload = (file) => {
  const existingFile = fileList.value.find(item => item.name === file.name)
  if (existingFile) {
    // 文件已存在，移除旧记录
    const index = fileList.value.indexOf(existingFile)
    if (index !== -1) {
      fileList.value.splice(index, 1)
    }
  }
  
  // 添加到上传列表
  fileList.value.push({
    name: file.name,
    size: file.size,
    status: 'uploading',
    progress: 0,
    file: file
  })
  
  return true
}

// 上传进度处理
const handleProgress = (event, file) => {
  const uploadFile = fileList.value.find(item => item.name === file.name)
  if (uploadFile) {
    uploadFile.progress = Math.round(event.percent)
  }
}

// 上传成功处理
const handleSuccess = (response, file) => {
  const uploadFile = fileList.value.find(item => item.name === file.name)
  if (uploadFile) {
    uploadFile.status = 'success'
    uploadFile.progress = 100
  }
  
  ElMessage.success(`文件 ${file.name} 上传成功`)
  emit('uploaded')
}

// 上传失败处理
const handleError = (error, file) => {
  const uploadFile = fileList.value.find(item => item.name === file.name)
  if (uploadFile) {
    uploadFile.status = 'error'
    
    // 尝试解析错误消息
    let errorMessage = '上传失败'
    if (error && error.message) {
      errorMessage = error.message
    } else if (typeof error === 'string') {
      errorMessage = error
    } else if (error && error.response && error.response.data) {
      try {
        const data = JSON.parse(error.response.data)
        errorMessage = data.error || '上传失败'
      } catch (e) {
        errorMessage = error.response.data
      }
    }
    
    uploadFile.errorMessage = errorMessage
  }
  
  ElMessage.error(`文件 ${file.name} 上传失败`)
}
</script>

<style scoped>
.upload-file {
  width: 100%;
}

.upload-area {
  width: 100%;
}

.upload-list {
  margin-top: 20px;
}

.error-message {
  color: #f56c6c;
}
</style> 