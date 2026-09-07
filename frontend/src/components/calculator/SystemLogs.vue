// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
import {useNotificationStore} from "../../../store/useNotificationStore.js";
import {storeToRefs} from "pinia";

const notificationStore = useNotificationStore();
const { messages } = storeToRefs(notificationStore);
</script>

<template>
  <div class="modal fade" id="SystemLogsModal" data-bs-backdrop="false" aria-hidden="true" aria-labelledby="SystemLogsLabel" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-centered">
      <div class="modal-content neomorphic p-0">
        <div class="modal-body ps-2 pe-2 pb-0">
          <div class="row pt-1 pe-2">
            <div class="d-flex flex-row justify-content-end">
              <p class="small text-purple my-auto">The log of system events, warnings, or notifications</p>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
          </div>

          <div class="container-fluid">
            <div class="row mb-3 text-purple fw-bold p-2">
              <div class="col-3 col-lg-2">
                Event date
              </div>
              <div class="col-2 col-lg-2">
                Event type
              </div>
              <div class="col-7 col-lg-8">
                Event description
              </div>
            </div>
            <div class="row mb-2 bg-white p-2" v-for="msg in messages" :key="msg.id">
              <div class="col-3 col-lg-2 fw-bold">
                {{ msg.date }}
              </div>
              <div class="col-2 col-lg-2 fw-bold">
                <span :class="{'text-success-1': msg.type === 'peak', 'text-alert': msg.type === 'wind'}">
                  {{ msg.type }}
                </span>
              </div>
              <div class="col-7 col-lg-8">
                {{ msg.title }}:
                <span v-if="msg.type === 'wind'">
                  <span class="fw-bold">{{ msg.event_time.substring(0, 5) }}</span>. Wind strength:
                  <span :class="{ 'text-alert': Number(msg.wind_strength) >= 15, 'fw-bold': Number(msg.wind_strength) <= 15 }">
                    {{ msg.wind_strength }}
                  </span> m/s.
                  Wind gust:
                  <span :class="{ 'text-alert': Number(msg.gust_strength) >= 15 }">
                    {{ msg.gust_strength }}
                  </span> m/s.
                </span>
                <span v-else-if="msg.type === 'peak'">
                  <span class="fw-bold">{{ msg.formatted_time_range }}</span>
                </span>
              </div>
            </div>
          </div>

          <div v-if="errorMsg" :class="['alert', errorClass, 'text-center']">
            {{ errorMsg }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .text-alert {
    color: #FFB307 !important;
    font-weight: bold;
  }
</style>