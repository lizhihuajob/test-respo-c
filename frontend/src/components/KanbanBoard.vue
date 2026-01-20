<template>
  <div class="kanban-container">
    <div class="header">
      <h1 class="kanban-title">任务看板</h1>
      <a-button type="primary" @click="showModal" class="add-task-btn">
        <plus-outlined /> 添加任务
      </a-button>
    </div>
    <div class="kanban-board">
      <div 
        v-for="status in statuses" 
        :key="status.value"
        class="kanban-column"
        :class="`column-${status.value}`"
        @drop="handleDrop($event, status.value)"
        @dragover.prevent
      >
        <div class="column-header">
          <h2>{{ status.label }}</h2>
          <span class="task-count">{{ getTasksByStatus(status.value).length }}</span>
        </div>
        <div class="task-list">
          <div
            v-for="task in getTasksByStatus(status.value)"
            :key="task.id"
            class="task-card"
            draggable="true"
            @dragstart="handleDragStart($event, task)"
          >
            <div class="task-header">
              <h3>{{ task.title }}</h3>
              <a-popconfirm
                title="确定要删除这个任务吗？"
                @confirm="deleteTask(task.id)"
              >
                <a-button danger type="text" size="small">删除</a-button>
              </a-popconfirm>
            </div>
            <p v-if="task.description" class="task-description">{{ task.description }}</p>
            <div class="task-meta">
              <span class="task-created-at">{{ formatDate(task.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <a-modal
      v-model:open="isModalVisible"
      title="添加新任务"
      @ok="handleAddTask"
      @cancel="handleCancel"
    >
      <a-form :model="newTask">
        <a-form-item label="任务标题" required>
          <a-input v-model:value="newTask.title" placeholder="请输入任务标题" />
        </a-form-item>
        <a-form-item label="任务描述">
          <a-textarea v-model:value="newTask.description" placeholder="请输入任务描述" :rows="3" />
        </a-form-item>
        <a-form-item label="任务状态">
          <a-select v-model:value="newTask.status">
            <a-select-option value="todo">待办</a-select-option>
            <a-select-option value="doing">进行中</a-select-option>
            <a-select-option value="done">已完成</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import axios from 'axios'

export default {
  name: 'KanbanBoard',
  components: {
    PlusOutlined
  },
  setup() {
    const tasks = ref([])
    const statuses = [
      { label: '待办', value: 'todo' },
      { label: '进行中', value: 'doing' },
      { label: '已完成', value: 'done' }
    ]
    const isModalVisible = ref(false)
    const newTask = ref({
      title: '',
      description: '',
      status: 'todo'
    })
    const draggedTask = ref(null)

    // 获取所有任务
    const fetchTasks = async () => {
      try {
        const response = await axios.get('/api/tasks')
        tasks.value = response.data
      } catch (error) {
        message.error('获取任务失败')
        console.error(error)
      }
    }

    // 添加任务
    const handleAddTask = async () => {
      if (!newTask.value.title.trim()) {
        message.error('任务标题不能为空')
        return
      }
      try {
        const response = await axios.post('/api/tasks', newTask.value)
        tasks.value.push(response.data)
        message.success('任务添加成功')
        isModalVisible.value = false
        // 重置表单
        newTask.value = {
          title: '',
          description: '',
          status: 'todo'
        }
      } catch (error) {
        message.error('添加任务失败')
        console.error(error)
      }
    }

    // 删除任务
    const deleteTask = async (taskId) => {
      try {
        await axios.delete(`/api/tasks/${taskId}`)
        tasks.value = tasks.value.filter(task => task.id !== taskId)
        message.success('任务删除成功')
      } catch (error) {
        message.error('删除任务失败')
        console.error(error)
      }
    }

    // 更新任务状态
    const updateTaskStatus = async (taskId, newStatus) => {
      try {
        const task = tasks.value.find(t => t.id === taskId)
        if (task) {
          const updatedTask = { ...task, status: newStatus }
          await axios.put(`/api/tasks/${taskId}`, updatedTask)
          task.status = newStatus
          message.success('任务状态更新成功')
        }
      } catch (error) {
        message.error('更新任务状态失败')
        console.error(error)
      }
    }

    // 根据状态获取任务
    const getTasksByStatus = (status) => {
      return tasks.value.filter(task => task.status === status)
    }

    // 拖拽开始
    const handleDragStart = (event, task) => {
      draggedTask.value = task
    }

    // 拖拽结束
    const handleDrop = (event, newStatus) => {
      event.preventDefault()
      if (draggedTask.value && draggedTask.value.status !== newStatus) {
        updateTaskStatus(draggedTask.value.id, newStatus)
      }
      draggedTask.value = null
    }

    // 显示添加任务模态框
    const showModal = () => {
      isModalVisible.value = true
    }

    // 取消添加任务
    const handleCancel = () => {
      isModalVisible.value = false
      // 重置表单
      newTask.value = {
        title: '',
        description: '',
        status: 'todo'
      }
    }

    // 格式化日期
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 初始化时获取任务
    onMounted(() => {
      fetchTasks()
    })

    return {
      tasks,
      statuses,
      isModalVisible,
      newTask,
      fetchTasks,
      handleAddTask,
      deleteTask,
      getTasksByStatus,
      handleDragStart,
      handleDrop,
      showModal,
      handleCancel,
      formatDate
    }
  }
}
</script>

<style scoped>
.kanban-container {
  max-width: 1200px;
  height: 70vh;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-shrink: 0;
}

.kanban-title {
  color: #1890ff;
  margin: 0;
}

.kanban-board {
  display: flex;
  gap: 20px;
  flex: 1;
  overflow-x: auto;
  flex-wrap: nowrap;
}

.kanban-column {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

/* 待办列样式 */
.column-todo {
  background-color: #f0f5ff;
  border-top: 4px solid #1890ff;
}

/* 进行中列样式 */
.column-doing {
  background-color: #fff7e6;
  border-top: 4px solid #faad14;
}

/* 已完成列样式 */
.column-done {
  background-color: #f6ffed;
  border-top: 4px solid #52c41a;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e8e8e8;
}

.column-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

/* 不同状态列标题颜色 */
.column-todo .column-header h2 {
  color: #1890ff;
}

.column-doing .column-header h2 {
  color: #faad14;
}

.column-done .column-header h2 {
  color: #52c41a;
}

.task-count {
  color: white;
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: bold;
}

/* 不同状态列任务数量指示器颜色 */
.column-todo .task-count {
  background-color: #1890ff;
}

.column-doing .task-count {
  background-color: #faad14;
}

.column-done .task-count {
  background-color: #52c41a;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.task-card {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: move;
  transition: all 0.3s ease;
}

.task-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.task-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.task-description {
  margin: 10px 0;
  color: #666;
  line-height: 1.5;
}

.task-meta {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.task-created-at {
  font-size: 12px;
  color: #999;
}

.add-task-btn {
  display: block;
}
</style>