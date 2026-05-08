<!-- components/dashboard/AppHeader.vue -->
<template>
  <header class="app-header">
    <div class="header-left">
      <button class="avatar-btn" @click="$emit('openProfile')">
        <img 
          :src="user?.avatar || '/images/avatar_default.png'" 
          :alt="user?.nombre_completo || 'Usuario'"
          class="avatar-img"
        />
      </button>
    </div>
    
    <div class="header-center">
      <span class="header-title">ComparApp</span>
    </div>
    
    <div class="header-right">
      <button class="notif-btn" @click="$emit('openNotifications')">
        <span class="notif-icon">🔔</span>
        <span v-if="unreadCount" class="notif-badge">{{ unreadCount }}</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
const props = defineProps({
  user: {
    type: Object,
    default: null
  },
  notifications: {
    type: Array,
    default: () => []
  }
})

defineEmits(['openProfile', 'openNotifications'])

const unreadCount = computed(() => {
  return props.notifications.filter((n: any) => !n.read).length
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.avatar-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid rgba(102, 126, 234, 0.5);
  overflow: hidden;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.header-title {
  color: white;
  font-weight: 600;
  font-size: 1.1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.notif-btn {
  position: relative;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.notif-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>