// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
import {onMounted, onUnmounted} from "vue";
import { storeToRefs } from "pinia";
import { useNotificationStore } from "../../../store/useNotificationStore.js";

// Icons
import successIcon from '../../../public/assets/calculator/images/icons/messages/success.png';
import infoIcon from '../../../public/assets/calculator/images/icons/messages/info.png';
import warningIcon from '../../../public/assets/calculator/images/icons/messages/warning.png';
import errorIcon from '../../../public/assets/calculator/images/icons/messages/error.png';

const notificationStore = useNotificationStore();
const { messages } = storeToRefs(notificationStore);
let socketInstance = null;

const getIcon = (type) => {
  const icons = {
    'weather': '',
    'storm': 'bi-cloud-lightning-rain',
    'success': new URL(successIcon, import.meta.url).href,
    'warning': new URL(warningIcon, import.meta.url).href,
    'info': new URL(infoIcon, import.meta.url).href,
    'danger': new URL(errorIcon, import.meta.url).href,
  };
  return icons[type] || 'bi-bell';
};

onMounted(async () => {
  notificationStore.initWebSocket();

  await notificationStore.initMessages();
});

onUnmounted(() => {
  notificationStore.disconnectWebSocket();

  if (socketInstance) {
    socketInstance.close();
  }
});

const pushLocalMessage = (newMsg) => {
  notificationStore.addNotification(newMsg);
};

defineExpose({ pushLocalMessage });
</script>

<template>
  <div class="notification-stack w-100 pl-4 pr-1">
    <transition-group name="list" tag="div">
      <div v-for="msg in messages" :key="msg.id" class="neomorphic msg-card shadow-sm rounded-2 p-2 pl-3 mb-2 border-0" :class="msg.level">
        <div class="d-flex align-items-center">
          <img :src="getIcon(msg.level)" class="me-2 text-dark icon" alt=""/>

          <div class="my-auto w-100">

            <!-- 1. КАРТКА ВІТРУ -->
            <template v-if="msg.type === 'wind'">
              <h6 class="mb-0 text-dark">{{ msg.title }} <span class="small text-muted">({{ msg.date }} {{ msg.event_time?.slice(0, 5) }})</span></h6>
              <p class="text-muted my-auto">
                Wind:
                <span>
                  <strong :class="{ 'text-alert': msg.wind_strength >= 15 }">{{ msg.wind_strength }}</strong>
                  m/s;&nbsp;
                </span>
                Gust:
                <span :class="{ 'text-alert': Number(msg.gust_strength) >= 15 }">
                  {{ msg.gust_strength }}
                </span>
                m/s
              </p>
            </template>

            <!-- 2. КАРТКА ПІКОВИХ ГОДИН -->
            <template v-else-if="msg.type === 'peak'">
              <h6 class="mb-0 text-dark">{{ msg.title }} <span class="small text-muted">({{ msg.date }})</span></h6>
              <p class="text-muted my-auto">
                Time range: <strong>{{ msg.formatted_time_range }}</strong>
              </p>
            </template>

            <!-- 3. ЗВИЧАЙНА СИСТЕМНА КАРТКА / АЛЕРТ -->
            <template v-else>
              <h6 class="mb-0 text-dark">{{ msg.title }}</h6>
              <p class="text-muted my-auto">
                {{ msg.text }}
              </p>
            </template>

          </div>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<!--<template>-->
<!--  <div class="notification-stack w-100 pl-4 pr-1">-->
<!--    <transition-group name="list" tag="div">-->
<!--      <div v-for="msg in messages" :key="msg.id" class="neomorphic msg-card shadow-sm rounded-2 p-2 pl-3 mb-2 border-0" :class="msg.level">-->
<!--        <div class="d-flex align-items-center">-->
<!--          <img :src="getIcon(msg.level)" class="me-2 text-dark icon" alt=""/>-->
<!--          <div class="my-auto">-->
<!--            <h6 class="mb-0 text-dark">{{ msg.title }} {{ msg.event_time?.slice(0, 5) }}</h6>-->
<!--            <p class="text-muted my-auto">-->
<!--              <span>{{ msg.wind_strength }} m/s;&nbsp;</span>-->
<!--              <span :class="{ 'text-alert': Number(msg.gust_strength) >= 15 }">-->
<!--                {{ msg.gust_strength }}-->
<!--              </span>-->
<!--              m/s-->
<!--            </p>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->
<!--    </transition-group>-->
<!--  </div>-->
<!--</template>-->

<style scoped>
.notification-stack {
  position: absolute;
  top: -20rem;
  right: 10px;
  z-index: 1000;
  width: 1400px;
}

.msg-card {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 12px;
  margin-bottom: 8px;
  transition: all 0.5s ease;
}

.icon {
  width: 24px;
  height: 24px;
  filter: drop-shadow(0 0 2px rgba(0,0,0,0.2));
}

@media (min-width: 1200px) {
  .notification-stack {
    width: 390px;
  }
}

.msg-card.success { border-left: 4px solid #198754; }
.msg-card.warning { border-left: 4px solid #ffc107; }
.msg-card.danger  { border-left: 4px solid #dc3545; }
.msg-card.info    { border-left: 4px solid #0dcaf0; }

.list-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
.list-leave-active {
  position: absolute;
  width: 100%;
}

.text-alert {
  color: #FFB307 !important;
  font-weight: bold;
}
</style>