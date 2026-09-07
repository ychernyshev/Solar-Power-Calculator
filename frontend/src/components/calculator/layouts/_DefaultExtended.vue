// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
  import { onMounted, onUnmounted } from 'vue';

  import TopNav from "../navs/_TopNav.vue";
  import CurrentMonthStats from "@/components/calculator/charts/CurrentMonthStats/CurrentMonthStats.vue";
  import DifferenceMonthsStats from "@/components/calculator/charts/DifferenceMonthsStats/DifferenceMonthsStats.vue";
  import CurrentYearStats from "@/components/calculator/charts/CurrentYearStats/CurrentYearStats.vue";
  import SystemLogs from "@/components/calculator/SystemLogs.vue";
  import CalendarModal from "@/components/calculator/calendar/CalendarModal.vue";

  const BOOTSWATCH_ID = 'bootswatch-theme';
  const POWER_CALCULATOR_CLASS = 'power-calculator-class';

  onMounted(() => {
    const links = [
      '/assets/calculator/js/bootswatch.min.css',
      '/assets/calculator/css/calculator.css',
      '/assets/calculator/css/style.css',
      '/assets/calculator/css/mobile.css'
    ];

    if (document.getElementsByClassName(POWER_CALCULATOR_CLASS).length === 0) {
      links.forEach(linkValue => {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.className = POWER_CALCULATOR_CLASS;
        link.href = linkValue;

        document.head.appendChild(link);
      })
    }
  });

  onUnmounted(() => {
    const dynamicStyles = document.getElementsByClassName(POWER_CALCULATOR_CLASS);
    while (dynamicStyles.length > 0) {
      dynamicStyles[0].remove();
    }
  });
</script>

<template>
  <div class="dashboard-grid">
    <top-nav />
    <current-month-stats />
    <difference-months-stats />
    <current-year-stats />
    <calendar-modal />
    <system-logs />
    <slot />
  </div>
</template>

<style scoped>
  .dashboard-grid {
    min-width: 100%;
    padding: 30px 10px 0 10px;
    display: grid;
    grid-template-areas:
      "header"
      "widgets"
      "content"
      "sidebar";
    ;
  }

  @media (min-width: 1200px) {
    .dashboard-grid {
      display: grid;
      grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);
      grid-template-rows: auto 1fr; /* верхня частина + залишок */
      grid-template-areas:
    "header header"
    "content sidebar";
      gap: 30px;
      padding: 20px;
      height: 100vh; /* головний контейнер займає весь екран */
    }

    .dashboard-grid > * {
      min-width: 0;
      min-height: 0; /* критично для правильного розподілу */
    }
  }

  @media (min-width: 1400px) {}
</style>

<!--.dashboard-grid {-->
<!--grid-template-columns: minmax(0, 3fr) minmax(0, 1fr);-->
<!--grid-template-rows: auto 1fr;-->
<!--grid-template-areas:-->
<!--"header header"-->
<!--"content sidebar"-->
<!--;-->
<!--gap: 30px;-->
<!--padding: 20px;-->
<!--}-->

<!--.dashboard-grid > * {-->
<!--min-width: 0;-->
<!--}-->