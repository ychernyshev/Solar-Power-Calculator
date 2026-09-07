// SPDX-License-Identifier: AGPL-3.0-or-later
<script setup>
import {ref, onMounted, computed} from "vue";
import backendApi from "@/services/backendApi.ts";
import WeatherIcon from "./WeatherIcon.vue";
import {useNotificationStore} from "../../../store/useNotificationStore.js";
import {useCalculatorStore} from "../../../store/useCalculatorStore.js";
import ButtonComp from "@/components/personal/ButtonComp.vue";

const emit = defineEmits(["entry-added"]);

// Messages
const messageRef = ref(null);
const useCustomPower = ref(false);
const notificationStore = useNotificationStore();
const store = useCalculatorStore();
const handleMessage = (payload) => {
  notificationStore.addNotification(payload);
};

const formData = ref({
  date: new Date().toISOString().split("T")[0],
  // power: "600",
  morning_data_charge: 0,
  morning_data_price: [0],
  afternoon_data_charge: 0,
  afternoon_data_price: [0],
  evening_data_charge: 0,
  evening_data_price: [0],
  extra_power: 0,
  weather: {},
});

const addPriceRow = () => {
  formData.value.morning_data_price.push(0);
  formData.value.afternoon_data_price.push(0);
  formData.value.evening_data_price.push(0);
};

// Weather
const weatherOptions = ref([]);

const fetchWeather = async () => {
  try {
    const res = await backendApi.get("calculator/weather-conditions/");
    weatherOptions.value = res.data.results || res.data;
  } catch (e) {
    console.error("Error loading weather types", e);
  }
};

const toggleWeather = (id) => {
  if (formData.value.weather[id] !== undefined) {
    delete formData.value.weather[id];
  } else {
    formData.value.weather[id] = 3;
  }
};

const submitForm = async () => {
  try {
    const weatherIds = Object.keys(formData.value.weather).map(Number);
    const weatherScores = { ...formData.value.weather };

    const sumMorningPrice = formData.value.morning_data_price.reduce((acc, val) => acc + (Number(val) || 0), 0);
    const sumAfternoonPrice = formData.value.afternoon_data_price.reduce((acc, val) => acc + (Number(val) || 0), 0);
    const sumEveningPrice = formData.value.evening_data_price.reduce((acc, val) => acc + (Number(val) || 0), 0);

    const payload = {
      ...formData.value,
      morning_data_price: sumMorningPrice,
      afternoon_data_price: sumAfternoonPrice,
      evening_data_price: sumEveningPrice,
      weather: weatherIds,
      weather_scores: weatherScores,
    };

    await backendApi.post("calculator/entries/", payload);
    await store.fetchStats();
    await store.fetchEntries(1);
    notificationStore.addNotification({
      title: 'Data has been recorded',
      text: 'Power indicators successfully updated.',
      level: 'success',
      msg_type: 'success',
      isPersistent: false,
    });
    emit("entry-added", {
      title: "New solar power generation data for the day has been added"
    });
    const nextDay = new Date(formData.value.date);
    nextDay.setDate(nextDay.getDate() + 1);
    const nextDayString = nextDay.toISOString().split("T")[0];

    formData.value = {
      date: nextDayString,
      // power: "600",
      morning_data_charge: 0,
      morning_data_price: [0],
      afternoon_data_charge: 0,
      afternoon_data_price: [0],
      evening_data_charge: 0,
      evening_data_price: [0],
      extra_power: 0,
      weather: {},
    };

  } catch (e) {
    console.error(e);
    notificationStore.addNotification({
      title: 'Error',
      text: 'Failed to save data.',
      level: 'danger',
      msg_type: 'warning',
      isPersistent: false,
    });
    emit("entry-added", { title: "Error", level: "danger", error: e });
  }
};

// Used data validation
const calculatorStore = useCalculatorStore();

const existingDates = computed(() => {
  return calculatorStore.entries.map(entry => entry.date);
});

const isDuplicateDate = computed(() => {
  return existingDates.value.includes(formData.value.date);
});

// Important fields
const isDayDataMissing = computed(() => {
  const morning_charge = formData.value.morning_data_charge;
  const morning_price = formData.value.morning_data_price[0];
  const afternoon_charge = formData.value.afternoon_data_charge;
  const afternoon_price = formData.value.afternoon_data_price[0];

  return morning_charge === 0 || morning_charge === "" || morning_price === 0 || morning_price === "" || afternoon_charge === 0 || afternoon_charge === "" || afternoon_price === 0 || afternoon_price === "";
});

const isEveningDataMissing = computed(() => {
  const evening_charge = formData.value.evening_data_charge;
  const evening_price = formData.value.evening_data_price[0];

  return evening_charge === 0 || evening_charge === "" || evening_price === 0 || evening_price === "";
})

const isWeatherSelected = computed(() => {
  return Object.keys(formData.value.weather).length === 0;
})

onMounted(fetchWeather);
</script>

<template>
  <div class="card row shadow-sm border-0">
    <div class="card-body card-light pl-3 pr-3 pb-2">
      <form @submit.prevent="submitForm">
        <div class="row mt-1">
          <div class="col-12 col-lg-2">
            <div class="d-flex flex-row align-items-center">
              <label class="form-label m-0 p-0 fw-bold text-info-emphasis">Date:</label>
              <input
                  type="date"
                  v-model="formData.date"
                  class="form-control border-0"
                  :class="{ 'is-invalid': isDuplicateDate }"
                  required
              />
            </div>
          </div>
          <div class="col-12 col-lg-6 my-auto text-start">
            <div v-if="isDuplicateDate" class="invalid-feedback d-block fw-normal" style="font-size: 0.8rem;">
              This date already has a record. Please choose another.
            </div>
          </div>
          <div class="col-12 col-lg-4">
            <div class="row h-100">
              <div class="col-4">
                <input
                    type="text"
                    class="form-control"
                    placeholder="Set power"
                    v-if="useCustomPower"
                >
              </div>
              <div class="col-8 d-flex ilign-items-center">
                <div class="form-check d-flex flex-row align-items-center">
                  <input
                      class="form-check-input my-auto"
                      type="checkbox"
                      v-model="useCustomPower"
                      id="checkDefault"
                  >
                  <label class="form-check-label p-0" for="checkDefault">
                    Use custom solar system power
                  </label>
                </div>
              </div>
            </div>
          </div>
<!--          <div class="col-12 col-md-6">-->
<!--            <label class="form-label">System Power</label>-->
<!--            <select v-model="formData.power" class="form-select">-->
<!--              <option value="200">200</option>-->
<!--              <option value="400">400</option>-->
<!--              <option value="600">600</option>-->
<!--              <option value="800">800</option>-->
<!--            </select>-->
<!--          </div>-->
        </div>

        <hr class="mt-3 mb-2"/>

        <div class="row text-center">
          <div class="row">
            <div class="col-12 col-lg-6">
              <div class="text-info-emphasis d-block text-start" style="font-size: 0.8rem;">
                You need to fill out the <span class="fw-bold">morning</span> metrics section and/or the <span class="fw-bold">afternoon</span> metrics section.
              </div>
            </div>
            <div class="col-12 col-lg-6">
              <div class="text-info-emphasis d-block text-end" style="font-size: 0.8rem;">
                You need to fill out the <span class="fw-bold">evening</span> metrics section.
              </div>
            </div>
          </div>
          <div class="col-12 col-md-4 border-md-end p-0">
            <div class="time-section pt-3 pl-3 pr-3">
              <h6 class="text-success fw-bold mb-3">Morning</h6>
              <div class="input-group w-100 mb-2">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">
                      <path d="M2 6h10v4H2V6z"/>
                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>
                    </svg>
                  </span>
                <input
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0"
                    v-model="formData.morning_data_charge"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>
              </div>

              <div v-for="(priceItem, pIndex) in formData.morning_data_price" :key="'morning-price-' + pIndex" class="input-group w-100 mb-2">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">
                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>
                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>
                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>
                    </svg>
                  </span>
                <input
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0.00"
                    v-model="formData.morning_data_price[pIndex]"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>
              </div>
            </div>
          </div>
          <div class="col-12 col-md-4 border-md-end p-0 pb-3 d-flex flex-column justify-content-center">
            <div class="time-section pt-3 pl-3 pr-3">
              <h6 class="text-primary fw-bold mb-3">Afternoon</h6>
              <div class="input-group w-100 mb-2">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">
                      <path d="M2 6h10v4H2V6z"/>
                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>
                    </svg>
                  </span>
                <input
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0"
                    v-model="formData.afternoon_data_charge"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>
              </div>

              <div v-for="(priceItem, pIndex) in formData.afternoon_data_price" :key="'afternoon-price-' + pIndex" class="input-group w-100 mb-2">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">
                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>
                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>
                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>
                    </svg>
                  </span>
                <input
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0.00"
                    v-model="formData.afternoon_data_price[pIndex]"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>
              </div>
            </div>
            <button-comp title="" @click.prevent="addPriceRow" class="btn btn-white p-1 pt-0 mt-0 d-none d-lg-block">
              <span class="small text-info-emphasis">Add a new electricity meter row</span>
            </button-comp>
          </div>
          <div class="col-12 col-md-4 p-0">
            <div class="time-section pt-3 pl-3 pr-3">
              <h6 class="text-purple fw-bold mb-3">Evening</h6>
              <div class="input-group w-100 mb-2">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">
                      <path d="M2 6h10v4H2V6z"/>
                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>
                    </svg>
                  </span>
                <input
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0"
                    v-model="formData.evening_data_charge"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>
              </div>

              <div v-for="(priceItem, pIndex) in formData.evening_data_price" :key="'evening-price-' + pIndex" class="input-group w-100 mb-2">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">
                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>
                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>
                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>
                    </svg>
                    </span>
                <input
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0.00"
                    v-model="formData.evening_data_price[pIndex]"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>
                <button-comp title="" @click.prevent="addPriceRow" class="input-group-text ml-3 text-purple bg-transparent d-lg-none">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square" viewBox="0 0 16 16">
                    <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
                    <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>
                  </svg>
                </button-comp>
              </div>
            </div>
          </div>
        </div>

        <div class="row pt-0">
          <div class="col-12 col-xl-4 p-0 pr-2">
            <div class="time-section pl-3 pr-3">
              <label class="form-label d-block text-center">
                Extra power (from USB)
              </label>
              <div class="input-group w-100 mb-3">
                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6f42c1" viewBox="0 0 16 16">
                      <path d="M5.52.359A.5.5 0 0 1 6 0h4a.5.5 0 0 1 .474.658L8.694 6H12.5a.5.5 0 0 1 .395.807l-7 9a.5.5 0 0 1-.873-.454L6.823 9.5H3.5a.5.5 0 0 1-.48-.641l2.5-8.5zM6.374 1 4.168 8.5H7.5a.5.5 0 0 1 .478.647L6.78 13.04 11.478 7H8a.5.5 0 0 1-.474-.658L9.306 1H6.374z"/>
                      <path fill-rule="evenodd" d="M12.5 11a.5.5 0 0 1 .5.5v1.5h1.5a.5.5 0 0 1 0 1H13v1.5a.5.5 0 0 1-1 0V14h-1.5a.5.5 0 0 1 0-1H12v-1.5a.5.5 0 0 1 .5-.5z"/>
                    </svg>
                  </span>
                <input
                    v-model="formData.extra_power"
                    type="number"
                    step="any"
                    class="form-control border-start-0 rounded-end-3"
                    placeholder="0"
                >
                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons alt-text">Wh</span>
              </div>
            </div>
          </div>

          <!-- Weather Indicators із вибором балу (1-5) -->
          <div class="col-12 col-xl-4">
            <label class="form-label d-block text-center">Weather Indicators</label>
            <div class="d-flex justify-content-start gap-2" :class="{'not-chosen': isWeatherSelected}">
              <div
                  v-for="opt in weatherOptions"
                  :key="opt.id"
                  class="p-2 border rounded text-center cursor-pointer weather-btn d-flex flex-column align-items-center justify-content-between"
                  :class="{
                      'bg-primary text-white border-primary shadow':
                        formData.weather[opt.id] !== undefined,
                  }"
              >
                <!-- Клік на іконку вмикає/вимикає погоду -->
                <div @click="toggleWeather(opt.id)" class="w-100">
                  <WeatherIcon :name="opt.name" />
                  <div class="small text-capitalize">{{ opt.name }}</div>
                </div>

                <!-- Випадаючий список з'являється тільки якщо погода обрана -->
                <div v-if="formData.weather[opt.id] !== undefined" class="mt-2 w-100" @click.stop>
                  <select
                      v-model.number="formData.weather[opt.id]"
                      class="form-select form-select-sm text-center p-1"
                      style="font-size: 0.75rem;"
                  >
                    <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="col-12 col-xl-4">
            <div class="time-section">
              <label class="form-label d-block text-center"
              >Form controllers</label
              >
              <div class="btn-group my-3" role="group" aria-label="Basic example">
                <button type="button" class="btn btn-light mb-1 w-10 py-2">Clear form</button>
                <button
                    type="submit"
                    class="btn btn-success mb-1 w-10 py-2"
                    :disabled="isDuplicateDate || isWeatherSelected || isEveningDataMissing">
                  Add Record
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.alt-icons {
  width: 1%;
}

.alt-text {
  font-size: .7rem
}

.not-filled {
  background-color: var(--dark-gray-rgba);
}

.not-chosen {
  padding-bottom: .4rem;
  border-bottom: 0.1rem solid var(--sunset-yelow);
}

@media (min-width: 576px) {
  .weather-btn {
    width: 20%;
  }
}

@media (min-width: 768px) {
  .border-md-end {
    border-right: 1px solid var(--bs-border-color) !important;
  }
  .weather-btn {
    width: 10%;
  }
}

@media (min-width: 1200px) {
  .weather-btn {
    width: 20%;
  }
}
</style>


<!--<script setup>-->
<!--import {ref, onMounted, computed} from "vue";-->
<!--import backendApi from "../../services/calculator/backendApi.js";-->
<!--import WeatherIcon from "./WeatherIcon.vue";-->
<!--import {useNotificationStore} from "../../../store/useNotificationStore.js";-->
<!--import {useCalculatorStore} from "../../../store/useCalculatorStore.js";-->
<!--import ButtonComp from "@/components/personal/ButtonComp.vue";-->

<!--const emit = defineEmits(["entry-added"]);-->

<!--// Messages-->
<!--const messageRef = ref(null);-->
<!--const notificationStore = useNotificationStore();-->
<!--const store = useCalculatorStore();-->
<!--const handleMessage = (payload) => {-->
<!--  notificationStore.addNotification(payload);-->
<!--};-->

<!--const formData = ref({-->
<!--  date: new Date().toISOString().split("T")[0],-->
<!--  power: "600",-->
<!--  morning_data_charge: 0,-->
<!--  morning_data_price: [0],-->
<!--  afternoon_data_charge: 0,-->
<!--  afternoon_data_price: [0],-->
<!--  evening_data_charge: 0,-->
<!--  evening_data_price: [0],-->
<!--  extra_power: 0,-->
<!--  weather: {},-->
<!--  // weather: [],-->
<!--});-->

<!--const addPriceRow = () => {-->
<!--  formData.value.morning_data_price.push(0);-->
<!--  formData.value.afternoon_data_price.push(0);-->
<!--  formData.value.evening_data_price.push(0);-->
<!--};-->

<!--// Weather-->
<!--const weatherOptions = ref([]);-->

<!--const fetchWeather = async () => {-->
<!--  try {-->
<!--    const res = await backendApi.get("calculator/weather-conditions/");-->
<!--    weatherOptions.value = res.data.results || res.data;-->
<!--  } catch (e) {-->
<!--    console.error("Error loading weather types", e);-->
<!--  }-->
<!--};-->

<!--const toggleWeather = (id) => {-->
<!--  const index = formData.value.weather.indexOf(id);-->
<!--  if (index > -1) {-->
<!--    formData.value.weather.splice(index, 1);-->
<!--  } else {-->
<!--    formData.value.weather.push(id);-->
<!--  }-->
<!--};-->

<!--const submitForm = async () => {-->
<!--  try {-->
<!--    await backendApi.post("calculator/entries/", formData.value);-->
<!--    await store.fetchStats();-->
<!--    await store.fetchEntries(1);-->
<!--    notificationStore.addNotification({-->
<!--      title: 'Data has been recorded',-->
<!--      text: 'Power indicators successfully updated.',-->
<!--      level: 'success',-->
<!--      msg_type: 'success',-->
<!--      isPersistent: false,-->
<!--    });-->
<!--    emit("entry-added", {-->
<!--      title: "New solar power generation data for the day has been added"-->
<!--    });-->
<!--    const nextDay = new Date(formData.value.date);-->
<!--    nextDay.setDate(nextDay.getDate() + 1);-->
<!--    const nextDayString = nextDay.toISOString().split("T")[0];-->

<!--    formData.value = {-->
<!--      date: nextDayString,-->
<!--      power: "600",-->
<!--      morning_data_charge: 0,-->
<!--      morning_data_price: [0],-->
<!--      afternoon_data_charge: 0,-->
<!--      afternoon_data_price: [0],-->
<!--      evening_data_charge: 0,-->
<!--      evening_data_price: [0],-->
<!--      extra_power: 0,-->
<!--      weather: [],-->
<!--    };-->

<!--  } catch (e) {-->
<!--    console.error(e);-->
<!--    notificationStore.addNotification({-->
<!--      title: 'Error',-->
<!--      text: 'Failed to save data.',-->
<!--      level: 'danger',-->
<!--      msg_type: 'warning',-->
<!--      isPersistent: false,-->
<!--    });-->
<!--    emit("entry-added", { title: "Error", level: "danger", error: e });-->
<!--  }-->
<!--};-->

<!--// Used data validation-->
<!--const calculatorStore = useCalculatorStore();-->

<!--const existingDates = computed(() => {-->
<!--  return calculatorStore.entries.map(entry => entry.date);-->
<!--});-->

<!--const isDuplicateDate = computed(() => {-->
<!--  return existingDates.value.includes(formData.value.date);-->
<!--});-->

<!--// Important fields-->
<!--const isDayDataMissing = computed(() => {-->
<!--  const morning_charge = formData.value.morning_data_charge;-->
<!--  const morning_price = formData.value.morning_data_price[0];-->
<!--  const afternoon_charge = formData.value.afternoon_data_charge;-->
<!--  const afternoon_price = formData.value.afternoon_data_price[0];-->

<!--  return morning_charge === 0 || morning_charge === "" || morning_price === 0 || morning_price === "" || afternoon_charge === 0 || afternoon_charge === "" || afternoon_price === 0 || afternoon_price === "";-->
<!--});-->

<!--const isEveningDataMissing = computed(() => {-->
<!--  const evening_charge = formData.value.evening_data_charge;-->
<!--  const evening_price = formData.value.evening_data_price[0];-->

<!--  return evening_charge === 0 || evening_charge === "" || evening_price === 0 || evening_price === "";-->
<!--})-->

<!--const isWeatherSelected = computed(() => {-->
<!--  return formData.value.weather.length === 0;-->
<!--})-->

<!--onMounted(fetchWeather);-->
<!--</script>-->

<!--<template>-->
<!--  <div class="card row shadow-sm border-0">-->
<!--    <div class="card-body card-light pl-3 pr-3 pb-2">-->
<!--      <form @submit.prevent="submitForm">-->
<!--        <div class="row mt-1">-->
<!--          <div class="col-12 col-md-6">-->
<!--            <label class="form-label">Date</label>-->
<!--            <input-->
<!--                type="date"-->
<!--                v-model="formData.date"-->
<!--                class="form-control"-->
<!--                :class="{ 'is-invalid': isDuplicateDate }"-->
<!--                required-->
<!--            />-->
<!--            <div v-if="isDuplicateDate" class="invalid-feedback d-block" style="font-size: 0.8rem;">-->
<!--              This date already has a record. Please choose another.-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-6">-->
<!--            <label class="form-label">System Power</label>-->
<!--            <select v-model="formData.power" class="form-select">-->
<!--              <option value="200">200</option>-->
<!--              <option value="400">400</option>-->
<!--              <option value="600">600</option>-->
<!--              <option value="800">800</option>-->
<!--            </select>-->
<!--          </div>-->
<!--        </div>-->

<!--        <hr class="mt-3 mb-2"/>-->

<!--        <div class="row text-center">-->
<!--          <div class="row">-->
<!--            <div class="col-12 col-lg-6">-->
<!--              <div class="text-info-emphasis d-block text-start" style="font-size: 0.8rem;">-->
<!--                You need to fill out the <span class="fw-bold">morning</span> metrics section and/or the <span class="fw-bold">afternoon</span> metrics section.-->
<!--              </div>-->
<!--            </div>-->
<!--            <div class="col-12 col-lg-6">-->
<!--              <div class="text-info-emphasis d-block text-end" style="font-size: 0.8rem;">-->
<!--                You need to fill out the <span class="fw-bold">evening</span> metrics section.-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-4 border-md-end p-0">-->
<!--            <div class="time-section pt-3 pl-3 pr-3">-->
<!--              <h6 class="text-success fw-bold mb-3">Morning</h6>-->
<!--              <div class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">-->
<!--                      <path d="M2 6h10v4H2V6z"/>-->
<!--                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                    v-model="formData.morning_data_charge"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>-->
<!--              </div>-->

<!--              &lt;!&ndash; Динамічний вивід рядків ціни &ndash;&gt;-->
<!--              <div v-for="(priceItem, pIndex) in formData.morning_data_price" :key="'morning-price-' + pIndex" class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">-->
<!--                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>-->
<!--                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>-->
<!--                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0.00"-->
<!--                    v-model="formData.morning_data_price[pIndex]"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-4 border-md-end p-0 pb-3 d-flex flex-column justify-content-center">-->
<!--            <div class="time-section pt-3 pl-3 pr-3">-->
<!--              <h6 class="text-primary fw-bold mb-3">Afternoon</h6>-->
<!--              <div class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">-->
<!--                      <path d="M2 6h10v4H2V6z"/>-->
<!--                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                    v-model="formData.afternoon_data_charge"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>-->
<!--              </div>-->

<!--              &lt;!&ndash; Динамічний вивід рядків ціни &ndash;&gt;-->
<!--              <div v-for="(priceItem, pIndex) in formData.afternoon_data_price" :key="'afternoon-price-' + pIndex" class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">-->
<!--                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>-->
<!--                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>-->
<!--                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0.00"-->
<!--                    v-model="formData.afternoon_data_price[pIndex]"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>-->
<!--              </div>-->
<!--            </div>-->
<!--            <button-comp title="" @click.prevent="addPriceRow" class="btn btn-white p-1 pt-0 mt-0 d-none d-lg-block">-->
<!--              <span class="small text-info-emphasis">Add a new electricity meter row</span>-->
<!--            </button-comp>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-4 p-0">-->
<!--            <div class="time-section pt-3 pl-3 pr-3">-->
<!--              <h6 class="text-purple fw-bold mb-3">Evening</h6>-->
<!--              <div class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">-->
<!--                      <path d="M2 6h10v4H2V6z"/>-->
<!--                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                    v-model="formData.evening_data_charge"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>-->
<!--              </div>-->

<!--              &lt;!&ndash; Динамічний вивід рядків ціни &ndash;&gt;-->
<!--              <div v-for="(priceItem, pIndex) in formData.evening_data_price" :key="'evening-price-' + pIndex" class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">-->
<!--                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>-->
<!--                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>-->
<!--                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>-->
<!--                    </svg>-->
<!--                    </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0.00"-->
<!--                    v-model="formData.evening_data_price[pIndex]"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>-->
<!--                <button-comp title="" @click="addPriceRow" class="input-group-text ml-3 text-purple bg-transparent d-lg-none">-->
<!--                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square" viewBox="0 0 16 16">-->
<!--                    <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>-->
<!--                    <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>-->
<!--                  </svg>-->
<!--                </button-comp>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="row pt-0">-->
<!--          <div class="col-12 col-xl-4 p-0 pr-2">-->
<!--            <div class="time-section pl-3 pr-3">-->
<!--              <label class="form-label d-block text-center">-->
<!--                Extra power (from USB)-->
<!--              </label>-->
<!--              <div class="input-group w-100 mb-3">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6f42c1" viewBox="0 0 16 16">-->
<!--                      <path d="M5.52.359A.5.5 0 0 1 6 0h4a.5.5 0 0 1 .474.658L8.694 6H12.5a.5.5 0 0 1 .395.807l-7 9a.5.5 0 0 1-.873-.454L6.823 9.5H3.5a.5.5 0 0 1-.48-.641l2.5-8.5zM6.374 1 4.168 8.5H7.5a.5.5 0 0 1 .478.647L6.78 13.04 11.478 7H8a.5.5 0 0 1-.474-.658L9.306 1H6.374z"/>-->
<!--                      <path fill-rule="evenodd" d="M12.5 11a.5.5 0 0 1 .5.5v1.5h1.5a.5.5 0 0 1 0 1H13v1.5a.5.5 0 0 1-1 0V14h-1.5a.5.5 0 0 1 0-1H12v-1.5a.5.5 0 0 1 .5-.5z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    v-model="formData.extra_power"-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons alt-text">Wh</span>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-xl-4">-->
<!--            <label class="form-label d-block text-center"-->
<!--            >Weather Indicators</label-->
<!--            >-->
<!--            <div class="d-flex justify-content-start gap-2" :class="{'not-chosen': isWeatherSelected}">-->
<!--              <div-->
<!--                  v-for="opt in weatherOptions"-->
<!--                  :key="opt.id"-->
<!--                  @click="toggleWeather(opt.id)"-->
<!--                  class="p-2 border rounded text-center cursor-pointer weather-btn"-->
<!--                  :class="{-->
<!--                      'bg-primary text-white border-primary shadow':-->
<!--                        formData.weather.includes(opt.id),-->
<!--                    }"-->
<!--              >-->
<!--                <WeatherIcon :name="opt.name" />-->
<!--                <div class="small text-capitalize">{{ opt.name }}</div>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-xl-4">-->
<!--            <div class="time-section">-->
<!--              <label class="form-label d-block text-center"-->
<!--              >Form controllers</label-->
<!--              >-->
<!--              <div class="btn-group my-3" role="group" aria-label="Basic example">-->
<!--                <button type="button" class="btn btn-light mb-1 w-10 py-2">Clear form</button>-->
<!--                <button-->
<!--                    type="submit"-->
<!--                    class="btn btn-success mb-1 w-10 py-2"-->
<!--                    :disabled="isDuplicateDate || isWeatherSelected || isEveningDataMissing">-->
<!--                  Add Record-->
<!--                </button>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </form>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<style scoped>-->
<!--.alt-icons {-->
<!--  width: 1%;-->
<!--}-->

<!--.alt-text {-->
<!--  font-size: .7rem-->
<!--}-->

<!--.not-filled {-->
<!--  background-color: var(&#45;&#45;dark-gray-rgba);-->
<!--}-->

<!--.not-chosen {-->
<!--  padding-bottom: .4rem;-->
<!--  border-bottom: 0.1rem solid var(&#45;&#45;sunset-yelow);-->
<!--}-->

<!--@media (min-width: 576px) {-->
<!--  .weather-btn {-->
<!--    width: 20%;-->
<!--  }-->
<!--}-->

<!--@media (min-width: 768px) {-->
<!--  .border-md-end {-->
<!--    border-right: 1px solid var(&#45;&#45;bs-border-color) !important;-->
<!--  }-->
<!--  .weather-btn {-->
<!--    width: 10%;-->
<!--  }-->
<!--}-->

<!--@media (min-width: 1200px) {-->
<!--  .weather-btn {-->
<!--    width: 20%;-->
<!--  }-->
<!--}-->
<!--</style>-->





<!--// SPDX-License-Identifier: AGPL-3.0-or-later-->
<!--<script setup>-->
<!--import {ref, onMounted, computed} from "vue";-->
<!--import backendApi from "../../services/calculator/backendApi.js";-->
<!--import WeatherIcon from "./WeatherIcon.vue";-->
<!--import {useNotificationStore} from "../../../store/useNotificationStore.js";-->
<!--import {useCalculatorStore} from "../../../store/useCalculatorStore.js";-->
<!--import ButtonComp from "@/components/personal/ButtonComp.vue";-->

<!--const emit = defineEmits(["entry-added"]);-->

<!--// Messages-->
<!--const messageRef = ref(null);-->
<!--const notificationStore = useNotificationStore();-->
<!--const store = useCalculatorStore();-->
<!--const handleMessage = (payload) => {-->
<!--  notificationStore.addNotification(payload);-->
<!--};-->

<!--const formData = ref({-->
<!--  date: new Date().toISOString().split("T")[0],-->
<!--  power: "600",-->
<!--  morning_data_charge: 0,-->
<!--  morning_data_price: 0,-->
<!--  afternoon_data_charge: 0,-->
<!--  afternoon_data_price: 0,-->
<!--  evening_data_charge: 0,-->
<!--  evening_data_price: 0,-->
<!--  extra_power: 0,-->
<!--  weather: [],-->
<!--});-->

<!--// Weather-->
<!--const weatherOptions = ref([]);-->

<!--const fetchWeather = async () => {-->
<!--  try {-->
<!--    const res = await backendApi.get("calculator/weather-conditions/");-->
<!--    weatherOptions.value = res.data.results || res.data;-->
<!--  } catch (e) {-->
<!--    console.error("Error loading weather types", e);-->
<!--  }-->
<!--};-->

<!--const toggleWeather = (id) => {-->
<!--  const index = formData.value.weather.indexOf(id);-->
<!--  if (index > -1) {-->
<!--    formData.value.weather.splice(index, 1);-->
<!--  } else {-->
<!--    formData.value.weather.push(id);-->
<!--  }-->
<!--};-->

<!--const submitForm = async () => {-->
<!--  try {-->
<!--    await backendApi.post("calculator/entries/", formData.value);-->
<!--    await store.fetchStats();-->
<!--    await store.fetchEntries(1);-->
<!--    notificationStore.addNotification({-->
<!--      title: 'Data has been recorded',-->
<!--      text: 'Power indicators successfully updated.',-->
<!--      level: 'success',-->
<!--      msg_type: 'success',-->
<!--      isPersistent: false,-->
<!--    });-->
<!--    emit("entry-added", {-->
<!--      title: "New solar power generation data for the day has been added"-->
<!--    });-->
<!--    const nextDay = new Date(formData.value.date);-->
<!--    nextDay.setDate(nextDay.getDate() + 1);-->
<!--    const nextDayString = nextDay.toISOString().split("T")[0];-->

<!--    formData.value = {-->
<!--      date: nextDayString,-->
<!--      power: "600",-->
<!--      morning_data_charge: 0,-->
<!--      morning_data_price: 0,-->
<!--      afternoon_data_charge: 0,-->
<!--      afternoon_data_price: 0,-->
<!--      evening_data_charge: 0,-->
<!--      evening_data_price: 0,-->
<!--      extra_power: 0,-->
<!--      weather: [],-->
<!--    };-->

<!--  } catch (e) {-->
<!--    console.error(e);-->
<!--    notificationStore.addNotification({-->
<!--      title: 'Error',-->
<!--      text: 'Failed to save data.',-->
<!--      level: 'danger',-->
<!--      msg_type: 'warning',-->
<!--      isPersistent: false,-->
<!--    });-->
<!--    emit("entry-added", { title: "Error", level: "danger", error: e });-->
<!--  }-->
<!--};-->

<!--// Used data validation-->
<!--const calculatorStore = useCalculatorStore();-->

<!--const existingDates = computed(() => {-->
<!--  return calculatorStore.entries.map(entry => entry.date);-->
<!--});-->

<!--const isDuplicateDate = computed(() => {-->
<!--  return existingDates.value.includes(formData.value.date);-->
<!--});-->

<!--// Important fields-->
<!--const isDayDataMissing = computed(() => {-->
<!--  const morning_charge = formData.value.morning_data_charge;-->
<!--  const morning_price = formData.value.morning_data_price;-->
<!--  const afternoon_charge = formData.value.afternoon_data_charge;-->
<!--  const afternoon_price = formData.value.afternoon_data_price;-->

<!--  return morning_charge === 0 || morning_charge === "" || morning_price === 0 || morning_price === "" || afternoon_charge === 0 || afternoon_charge === "" || afternoon_price === 0 || afternoon_price === "";-->
<!--});-->

<!--const isEveningDataMissing = computed(() => {-->
<!--  const evening_charge = formData.value.evening_data_charge;-->
<!--  const evening_price = formData.value.evening_data_price;-->

<!--  return evening_charge === 0 || evening_charge === "" || evening_price === 0 || evening_price === "";-->
<!--})-->

<!--const isWeatherSelected = computed(() => {-->
<!--  return formData.value.weather.length === 0;-->
<!--})-->

<!--onMounted(fetchWeather);-->
<!--</script>-->

<!--<template>-->
<!--  <div class="card row shadow-sm border-0">-->
<!--    <div class="card-body card-light pl-3 pr-3 pb-2">-->
<!--      <form @submit.prevent="submitForm">-->
<!--        <div class="row mt-1">-->
<!--          <div class="col-12 col-md-6">-->
<!--            <label class="form-label">Date</label>-->
<!--            <input-->
<!--                type="date"-->
<!--                v-model="formData.date"-->
<!--                class="form-control"-->
<!--                :class="{ 'is-invalid': isDuplicateDate }"-->
<!--                required-->
<!--            />-->
<!--            <div v-if="isDuplicateDate" class="invalid-feedback d-block" style="font-size: 0.8rem;">-->
<!--              This date already has a record. Please choose another.-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-6">-->
<!--            <label class="form-label">System Power</label>-->
<!--            <select v-model="formData.power" class="form-select">-->
<!--              <option value="200">200</option>-->
<!--              <option value="400">400</option>-->
<!--              <option value="600">600</option>-->
<!--              <option value="800">800</option>-->
<!--            </select>-->
<!--          </div>-->
<!--        </div>-->

<!--        <hr class="mt-3 mb-2"/>-->

<!--        <div class="row text-center">-->
<!--          <div class="row">-->
<!--            <div class="col-12 col-lg-6">-->
<!--              <div class="text-info-emphasis d-block text-start" style="font-size: 0.8rem;">-->
<!--                You need to fill out the <span class="fw-bold">morning</span> metrics section and/or the <span class="fw-bold">afternoon</span> metrics section.-->
<!--              </div>-->
<!--            </div>-->
<!--            <div class="col-12 col-lg-6">-->
<!--              <div class="text-info-emphasis d-block text-end" style="font-size: 0.8rem;">-->
<!--                You need to fill out the <span class="fw-bold">evening</span> metrics section.-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-4 border-md-end p-0">-->
<!--            <div class="time-section pt-3 pl-3 pr-3">-->
<!--              <h6 class="text-success fw-bold mb-3">Morning</h6>-->
<!--                <div class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">-->
<!--                      <path d="M2 6h10v4H2V6z"/>-->
<!--                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                  <input-->
<!--                      type="number"-->
<!--                      step="any"-->
<!--                      class="form-control border-start-0 rounded-end-3"-->
<!--                      placeholder="0"-->
<!--                      v-model="formData.morning_data_charge"-->
<!--                  >-->
<!--                  <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>-->
<!--                </div>-->
<!--                <div class="input-group w-100">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">-->
<!--                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>-->
<!--                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>-->
<!--                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>-->
<!--                    </svg>-->
<!--                    </span>-->
<!--                  <input-->
<!--                      type="number"-->
<!--                      step="any"-->
<!--                      class="form-control border-start-0 rounded-end-3"-->
<!--                      placeholder="0.00"-->
<!--                      v-model="formData.morning_data_price"-->
<!--                  >-->
<!--                  <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>-->
<!--                </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-4 border-md-end p-0 pb-3 d-flex flex-column justify-content-center">-->
<!--            <div class="time-section pt-3 pl-3 pr-3">-->
<!--              <h6 class="text-primary fw-bold mb-3">Afternoon</h6>-->
<!--              <div class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">-->
<!--                      <path d="M2 6h10v4H2V6z"/>-->
<!--                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                    v-model="formData.afternoon_data_charge"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>-->
<!--              </div>-->
<!--              <div class="input-group w-100">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">-->
<!--                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>-->
<!--                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>-->
<!--                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>-->
<!--                    </svg>-->
<!--                    </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0.00"-->
<!--                    value=""-->
<!--                    v-model="formData.afternoon_data_price"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>-->
<!--              </div>-->
<!--            </div>-->
<!--            <button-comp title="" class="btn btn-white p-1 pt-0 mt-0 d-none d-lg-block">-->
<!--              <span class="small text-info-emphasis">Add a new electricity meter row</span>-->
<!--            </button-comp>-->
<!--          </div>-->
<!--          <div class="col-12 col-md-4 p-0">-->
<!--            <div class="time-section pt-3 pl-3 pr-3">-->
<!--              <h6 class="text-purple fw-bold mb-3">Evening</h6>-->
<!--              <div class="input-group w-100 mb-2">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6c757d" viewBox="0 0 16 16">-->
<!--                      <path d="M2 6h10v4H2V6z"/>-->
<!--                      <path d="M2 4a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H2zm10 1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h10zm4 3a1.5 1.5 0 0 1-1.5 1.5v-3A1.5 1.5 0 0 1 16 8z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                    v-model="formData.evening_data_charge"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">%</span>-->
<!--              </div>-->
<!--              <div class="input-group w-100">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#f1c40f" viewBox="0 0 16 16">-->
<!--                      <path d="M5.5 9.511c.076.04.16.08.252.117a18.721 18.721 0 0 0 2.248.707V12.5c0 .017.001.033.001.05a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518V9.51a10.39 10.39 0 0 0 2.248-.707c.417-.147.756-.323 1.001-.518v3.018c0 .697-.463 1.442-1.26 1.956C12.192 13.754 10.916 14 9.5 14c-1.416 0-2.692-.246-3.488-.744-.797-.514-1.26-1.259-1.26-1.956V9.511z"/>-->
<!--                      <path d="M14 6.5c0 .697-.463 1.442-1.26 1.956C11.942 8.954 10.666 9.2 9.5 9.2c-1.416 0-2.692-.246-3.488-.744C5.215 7.942 4.75 7.197 4.75 6.5c0-.697.463-1.442 1.26-1.956C6.808 4.046 8.084 3.8 9.5 3.8c1.416 0 2.692.246 3.488.744.797.514 1.26 1.259 1.26 1.956z"/>-->
<!--                      <path d="M9.5 10c-1.416 0-2.692-.246-3.488-.744C5.215 8.742 4.75 7.997 4.75 7.3V9.5c0 .697.463 1.442 1.26 1.956C6.808 11.954 8.084 12.2 9.5 12.2c1.416 0 2.692-.246 3.488-.744.797-.514 1.26-1.259 1.26-1.956V7.3c0 .697-.463 1.442-1.26 1.956C12.192 9.754 10.916 10 9.5 10z"/>-->
<!--                    </svg>-->
<!--                    </span>-->
<!--                <input-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0.00"-->
<!--                    v-model="formData.evening_data_price"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons">₴</span>-->
<!--                <button-comp title="" class="input-group-text ml-3 text-purple bg-transparent d-lg-none">-->
<!--                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square" viewBox="0 0 16 16">-->
<!--                    <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>-->
<!--                    <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"/>-->
<!--                  </svg>-->
<!--                </button-comp>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="row pt-0">-->
<!--          <div class="col-12 col-xl-4 p-0 pr-2">-->
<!--            <div class="time-section pl-3 pr-3">-->
<!--              <label class="form-label d-block text-center">-->
<!--                Extra power (from USB)-->
<!--              </label>-->
<!--              <div class="input-group w-100 mb-3">-->
<!--                  <span class="input-group-text bg-white border-end-0 rounded-start-3 text-muted p-0 pl-2">-->
<!--                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6f42c1" viewBox="0 0 16 16">-->
<!--                      <path d="M5.52.359A.5.5 0 0 1 6 0h4a.5.5 0 0 1 .474.658L8.694 6H12.5a.5.5 0 0 1 .395.807l-7 9a.5.5 0 0 1-.873-.454L6.823 9.5H3.5a.5.5 0 0 1-.48-.641l2.5-8.5zM6.374 1 4.168 8.5H7.5a.5.5 0 0 1 .478.647L6.78 13.04 11.478 7H8a.5.5 0 0 1-.474-.658L9.306 1H6.374z"/>-->
<!--                      <path fill-rule="evenodd" d="M12.5 11a.5.5 0 0 1 .5.5v1.5h1.5a.5.5 0 0 1 0 1H13v1.5a.5.5 0 0 1-1 0V14h-1.5a.5.5 0 0 1 0-1H12v-1.5a.5.5 0 0 1 .5-.5z"/>-->
<!--                    </svg>-->
<!--                  </span>-->
<!--                <input-->
<!--                    v-model="formData.extra_power"-->
<!--                    type="number"-->
<!--                    step="any"-->
<!--                    class="form-control border-start-0 rounded-end-3"-->
<!--                    placeholder="0"-->
<!--                >-->
<!--                <span class="input-group-text bg-transparent border-0 small text-muted pe-2 alt-icons alt-text">Wh</span>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-xl-4">-->
<!--            <label class="form-label d-block text-center"-->
<!--            >Weather Indicators</label-->
<!--            >-->
<!--            <div class="d-flex justify-content-start gap-2" :class="{'not-chosen': isWeatherSelected}">-->
<!--              <div-->
<!--                  v-for="opt in weatherOptions"-->
<!--                  :key="opt.id"-->
<!--                  @click="toggleWeather(opt.id)"-->
<!--                  class="p-2 border rounded text-center cursor-pointer weather-btn"-->
<!--                  :class="{-->
<!--                      'bg-primary text-white border-primary shadow':-->
<!--                        formData.weather.includes(opt.id),-->
<!--                    }"-->
<!--              >-->
<!--                <WeatherIcon :name="opt.name" />-->
<!--                <div class="small text-capitalize">{{ opt.name }}</div>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--          <div class="col-12 col-xl-4">-->
<!--            <div class="time-section">-->
<!--              <label class="form-label d-block text-center"-->
<!--              >Form controllers</label-->
<!--              >-->
<!--              <div class="btn-group my-3" role="group" aria-label="Basic example">-->
<!--                <button type="button" class="btn btn-light mb-1 w-10 py-2">Clear form</button>-->
<!--                <button-->
<!--                    type="submit"-->
<!--                    class="btn btn-success mb-1 w-10 py-2"-->
<!--                    :disabled="isDuplicateDate || isWeatherSelected || isEveningDataMissing">-->
<!--                  Add Record-->
<!--                </button>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </form>-->
<!--    </div>-->
<!--  </div>-->
<!--</template>-->

<!--<style scoped>-->
<!--  .alt-icons {-->
<!--    width: 1%;-->
<!--  }-->

<!--  .alt-text {-->
<!--    font-size: .7rem-->
<!--  }-->

<!--  .not-filled {-->
<!--    background-color: var(&#45;&#45;dark-gray-rgba);-->
<!--  }-->

<!--  .not-chosen {-->
<!--    padding-bottom: .4rem;-->
<!--    border-bottom: 0.1rem solid var(&#45;&#45;sunset-yelow);-->
<!--  }-->

<!--  @media (min-width: 576px) {-->
<!--    .weather-btn {-->
<!--      width: 20%;-->
<!--    }-->
<!--  }-->

<!--  @media (min-width: 768px) {-->
<!--    .border-md-end {-->
<!--      border-right: 1px solid var(&#45;&#45;bs-border-color) !important;-->
<!--    }-->
<!--    .weather-btn {-->
<!--      width: 10%;-->
<!--    }-->
<!--  }-->

<!--  @media (min-width: 1200px) {-->
<!--    .weather-btn {-->
<!--      width: 20%;-->
<!--    }-->
<!--  }-->
<!--</style>-->

