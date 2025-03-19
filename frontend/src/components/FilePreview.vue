<template>
  <div class="file-preview">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="10" animated />
    </div>
    
    <!-- 文本预览 -->
    <div v-else-if="fileType === 'text'" class="text-preview">
      <el-input
        v-model="fileContent"
        type="textarea"
        :rows="20"
        :readonly="!editable"
        resize="none"
      />
      <div class="preview-actions">
        <el-button-group v-if="fileType === 'text'">
          <el-button 
            v-if="!editable" 
            @click="startEdit"
            type="primary"
            :icon="Edit"
          >
            编辑
          </el-button>
          <template v-else>
            <el-button 
              @click="saveFile"
              type="success"
              :icon="Check"
            >
              保存
            </el-button>
            <el-button 
              @click="cancelEdit"
              :icon="Close"
            >
              取消
            </el-button>
          </template>
        </el-button-group>
      </div>
    </div>
    
    <!-- 图片预览 -->
    <div v-else-if="fileType === 'image'" class="image-preview">
      <img :src="imageUrl" alt="图片预览" />
    </div>
    
    <!-- PDF预览 -->
    <div v-else-if="fileType === 'pdf'" class="pdf-preview">
      <iframe :src="pdfUrl" width="100%" height="600" frameborder="0"></iframe>
    </div>
    
    <!-- 不支持的文件类型 -->
    <div v-else class="unsupported-preview">
      <el-empty description="不支持预览该文件类型" />
      <el-button @click="downloadFile" type="primary">
        <el-icon><Download /></el-icon>
        下载文件
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, Check, Close, Download } from '@element-plus/icons-vue'
import { fileApi } from '../api/file'

const props = defineProps({
  file: {
    type: Object,
    required: true
  },
  currentPath: {
    type: String,
    default: ''
  }
})

const loading = ref(true)
const fileContent = ref('')
const originalContent = ref('')
const editable = ref(false)
const fileType = ref('')

// 根据文件扩展名确定文件类型
const getFileType = (filename) => {
  const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase()
  
  if (['.txt', '.md', '.js', '.py', '.html', '.css', '.json', '.xml', '.yaml', '.yml'].includes(ext)) {
    return 'text'
  } else if (['.jpg', '.jpeg', '.png', '.gif', '.bmp'].includes(ext)) {
    return 'image'
  } else if (ext === '.pdf') {
    return 'pdf'
  } else {
    return 'unsupported'
  }
}

// 图片URL
const imageUrl = computed(() => {
  if (fileType.value !== 'image') return ''
  return `/api/download?path=${encodeURIComponent(props.currentPath)}&filename=${encodeURIComponent(props.file.name)}`
})

// PDF URL
const pdfUrl = computed(() => {
  if (fileType.value !== 'pdf') return ''
  return `/api/download?path=${encodeURIComponent(props.currentPath)}&filename=${encodeURIComponent(props.file.name)}`
})

// 获取文件内容
const fetchFileContent = async () => {
  loading.value = true
  try {
    if (fileType.value === 'text') {
      const response = await fileApi.previewFile(props.currentPath, props.file.name)
      fileContent.value = response.content
      originalContent.value = response.content
    }
  } catch (error) {
    ElMessage.error('获取文件内容失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 开始编辑
const startEdit = () => {
  editable.value = true
}

// 取消编辑
const cancelEdit = () => {
  fileContent.value = originalContent.value
  editable.value = false
}

// 保存文件
const saveFile = async () => {
  try {
    loading.value = true
    await fileApi.saveFile(
      props.currentPath,
      props.file.name,
      fileContent.value
    )
    originalContent.value = fileContent.value
    editable.value = false
    ElMessage.success('文件保存成功')
  } catch (error) {
    ElMessage.error('保存文件失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 下载文件
const downloadFile = async () => {
  try {
    await fileApi.downloadFile(props.currentPath, props.file.name)
  } catch (error) {
    ElMessage.error('下载文件失败: ' + error.message)
  }
}

// 监听文件变化
watch(() => props.file, (newVal) => {
  if (newVal) {
    fileType.value = getFileType(newVal.name)
    fetchFileContent()
  }
}, { immediate: true })
</script>

<style scoped>
.file-preview {
  width: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.loading {
  padding: 20px;
}

.text-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.preview-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.image-preview {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.image-preview img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.pdf-preview {
  width: 100%;
  height: 70vh;
}

.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.unsupported-preview .el-button {
  margin-top: 20px;
}
</style> 