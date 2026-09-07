<script setup>

import MiniCalendar from "@/components/calculator/wingets/MiniCalendar.vue";
</script>

<template>
  <div class="modal fade" id="CalendarModal" data-bs-backdrop="false" aria-hidden="true" aria-labelledby="CalendarModalLabel" tabindex="-1">
    <div class="modal-dialog modal-xxl modal-dialog-centered">
      <div class="modal-content neomorphic p-0">
        <div class="modal-body ps-2 pe-2 pb-0">
          <div class="row pt-1 pe-2">
            <div class="d-flex flex-row justify-content-end">
              <p class="small text-purple my-auto">Power generation analytics for the full period</p>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="container-fluid">
              <div class="row">
                <div class="col-12 col-lg-3">
                  <mini-calendar class="mb-0"/>
                </div>
                <div class="col-12 col-lg-9"></div>
              </div>
              <div class="row">
                <div class="col-12"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>