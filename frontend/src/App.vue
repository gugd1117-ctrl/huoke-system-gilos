<template>
  <div class="container">
    <div v-if="view === 'home'">
      <HomeView @run-task="onRunTask" @open-task="openTask" />
    </div>
    <div v-else-if="view === 'task' && currentTaskId">
      <TaskDetailView :task-id="currentTaskId" @back="view = 'home'" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import HomeView from './views/HomeView.vue'
import TaskDetailView from './views/TaskDetailView.vue'

const view = ref('home')
const currentTaskId = ref(null)

const onRunTask = (task) => {
  currentTaskId.value = task.id
  view.value = 'task'
}
const openTask = (taskId) => {
  currentTaskId.value = taskId
  view.value = 'task'
}

onMounted(() => {
  const hash = window.location.hash.replace('#', '')
  if (hash && hash.startsWith('task/')) {
    currentTaskId.value = parseInt(hash.split('/')[1])
    view.value = 'task'
  }
})
</script>
