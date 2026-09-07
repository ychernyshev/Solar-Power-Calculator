// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>

import {computed, ref} from "vue";
import MessagesStack from "./MessagesStack.vue";
import {useNotificationStore} from "../../../store/useNotificationStore.js";
import {storeToRefs} from "pinia";
import SunriseSunsetTimeWidget from "@/components/calculator/wingets/SunriseSunsetTimeWidget.vue";
import MiniCalendar from "@/components/calculator/wingets/MiniCalendar.vue";
import {useCalculatorStore} from "../../../store/useCalculatorStore.js";

const calculatorStore = useCalculatorStore();
const { entries } = storeToRefs(calculatorStore);

// Messages
const notificationStore = useNotificationStore();
const handleMessage = (payload) => {
  notificationStore.addNotification(payload);
};

// Notification
const { messages } = storeToRefs(notificationStore);

const  isMessage = computed(() => {
  return messages.value.length > 0;
})

// Charts
const chartLabels = computed(() => {
  return entries.value.map((item) => item.date);
});

const chartValues = computed(() => {
  return entries.value.map((item) => item.full_day_power);
});

const chartCosts = computed(() => {
  return entries.value.map((item) => item.full_day_cost);
});
</script>

<template>
  <aside class="sidebar m-0 row justify-content-center">
    <div class="row neomorphic graphics-card justify-content-between align-items-end p-0">
      <div class="col-xl-12 d-none d-lg-block message-card">
        <div v-if="!isMessage" class="no-messages text-center d-flex flex-column justify-content-center align-items-center p-3">
          <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" fill="currentColor" class="bi bi-mailbox-flag " viewBox="0 0 16 16">
            <path d="M10.5 8.5V3.707l.854-.853A.5.5 0 0 0 11.5 2.5v-2A.5.5 0 0 0 11 0H9.5a.5.5 0 0 0-.5.5v8zM5 7c0 .334-.164.264-.415.157C4.42 7.087 4.218 7 4 7s-.42.086-.585.157C3.164 7.264 3 7.334 3 7a1 1 0 0 1 2 0"/>
            <path d="M4 3h4v1H6.646A4 4 0 0 1 8 7v6h7V7a3 3 0 0 0-3-3V3a4 4 0 0 1 4 4v6a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1V7a4 4 0 0 1 4-4m0 1a3 3 0 0 0-3 3v6h6V7a3 3 0 0 0-3-3"/>
          </svg>
          <span>No messages yet...</span>
        </div>
        <messages-stack ref="messagesRef" class="custom-position" />
      </div>
      <div class="col-12 p-0">
        <sunrise-sunset-time-widget />
      </div>
    </div>
  </aside>
</template>

<style scoped>
  .btn-graphic-tab {
    padding: 1rem 0.5rem;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 48px;
  }

  .message-card {
    position: relative;
  }

  .no-messages {
    font-size: clamp(1.4rem, 1.4vw, 1.4rem);
    font-weight: 300;
    color: var(--sky-blue-1);
    border: 0.1rem dashed var(--sky-blue-1);
  }

  @media (min-width: 992px) {
    .btn-graphic-tab {
      padding: 0.5rem 1rem;
      width: auto;
      min-height: auto;
    }
  }

  @media (min-width: 1200px) and (max-width: 1399px) {
    .custom-position {
      margin-top: -12rem;
    }
  }
</style>