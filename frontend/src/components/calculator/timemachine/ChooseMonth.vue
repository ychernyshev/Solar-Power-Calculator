<script setup>
import ButtonComp from "@/components/personal/ButtonComp.vue";
import {computed, onMounted, ref} from "vue";
import {useDateRangeStore} from "../../../../store/useDateRangeStore.js";
import {storeToRefs} from "pinia";

const DateRangeStore = useDateRangeStore();
const {dateRange} = storeToRefs(DateRangeStore);

onMounted(() => {
  DateRangeStore.fetchDateRange();
});

const now = new Date()
const currentYear = now.getFullYear()
const currentMonth = now.getMonth()

const activeYear = ref(currentYear)
const activeMonth = ref(currentMonth)

const minDataDate = computed(() => {
  if (!dateRange.value || !dateRange.value.min) {
    return { year: currentYear, month: currentMonth }
  }

  const dateObj = new Date(dateRange.value.min)
  return {
    year: dateObj.getFullYear(),
    month: dateObj.getMonth()
  }
})

const maxDataDate = computed(() => {
  const current = { year: currentYear, month: currentMonth }
  if (!dateRange.value || !dateRange.value.max) {
    return current
  }

  const maxObj = new Date(dateRange.value.max)
  const maxFromDb = { year: maxObj.getFullYear(), month: maxObj.getMonth() }

  const totalMaxDb = maxFromDb.year * 12 + maxFromDb.month
  const totalCurrent = current.year * 12 + current.month

  return totalMaxDb > totalCurrent ? maxFromDb : current
})

const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

const formattedDate = computed(() => {
  return `${monthNames[activeMonth.value]} ${activeYear.value}`
})

const canGoPrev = computed(() => {
  const totalMonthsActive = activeYear.value * 12 + activeMonth.value
  const totalMonthsMin = minDataDate.value.year * 12 + minDataDate.value.month
  return totalMonthsActive > totalMonthsMin
})

const canGoNext = computed(() => {
  const totalMonthsActive = activeYear.value * 12 + activeMonth.value
  const totalMonthsMax = maxDataDate.value.year * 12 + maxDataDate.value.month
  return totalMonthsActive < totalMonthsMax
})

const dateRangeStore = useDateRangeStore();

const prevMonth = () => {
  if (!canGoPrev.value) return
  if (activeMonth.value === 0) {
    activeMonth.value = 11
    activeYear.value--
  } else {
    activeMonth.value--
  }
  dateRangeStore.setSelectedPeriod(activeYear.value, activeMonth.value);
}

const nextMonth = () => {
  if (!canGoNext.value) return
  if (activeMonth.value === 11) {
    activeMonth.value = 0
    activeYear.value++
  } else {
    activeMonth.value++
  }
  dateRangeStore.setSelectedPeriod(activeYear.value, activeMonth.value);
}

const isCurrentMonth = computed(() => {
  return activeYear.value === now.getFullYear() && activeMonth.value === now.getMonth()
})

const goToCurrentMonth = () => {
  activeYear.value = now.getFullYear()
  activeMonth.value = now.getMonth()
  dateRangeStore.setSelectedPeriod(activeYear.value, activeMonth.value)
}
</script>

<template>
  <button-comp type="button"
               title="<<"
               class="neomorphic text-purple p-1 pl-3 pr-3"
               @click="prevMonth"
               :disabled="!canGoPrev"
               :class="{ 'opacity-40 cursor-not-allowed': !canGoPrev }" />
  <span class="ml-3 mr-3">{{ formattedDate }}</span>
  <button-comp type="button"
               title=">>"
               class="neomorphic text-purple p-1 pl-3 pr-3"
               @click="nextMonth"
               :disabled="!canGoNext"
               :class="{ 'opacity-40 cursor-not-allowed': !canGoNext }" />
  <button-comp type="button"
               title="Today"
               @click="goToCurrentMonth"
               class="neomorphic ml-4 p-2 pl-3 pr-3 border text-purple fw-lighter"
               :class="{ 'opacity-40 cursor-not-allowed': isCurrentMonth }"
               :disabled="isCurrentMonth"
               style="font-size: clamp(1.1rem, 0.8vh, 0.8rem)" />
</template>

<style scoped>

</style>