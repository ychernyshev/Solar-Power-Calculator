import { defineStore } from 'pinia'
import {computed, ref} from 'vue'
import backendApi from "../src/services/backendApi.ts";

export const useDateRangeStore = defineStore('dateRange', () => {
    const dateRange = ref({ min: null, max: null })

    const now = new Date()
    const selectedYear = ref(now.getFullYear())
    const selectedMonth = ref(now.getMonth()) // 0-11
    const monthGenerationChartData = ref(null)

    const loading = ref(false)

    const errorMsg = ref("");
    const errorClass = ref("");

    const compareLastYear = ref(false)
    const compareTwoYearsAgo = ref(false)

    const hasLastYearData = ref(false)
    const hasTwoYearsAgoData = ref(false)

    // Year
    // const hasLastYearData = computed(() => {
    //     if (!dateRange.value.min) return false;
    //     const minYear = new Date(dateRange.value.min).getFullYear();
    //     return selectedYear.value - 1 >= minYear;
    // });
    //
    // const hasTwoYearsAgoData = computed(() => {
    //     if (!dateRange.value.min) return false;
    //     const minYear = new Date(dateRange.value.min).getFullYear();
    //     return selectedYear.value - 2 >= minYear;
    // });

    // Chenge month
    const fetchDateRange = async () => {
        try {
            const response = await backendApi.get('calculator/date_range/')
            dateRange.value = {
                min: response.data.min_date,
                max: response.data.max_date
            }
        } catch (error) {
            console.error('Error loading date range:', error)
        }
    }

    const getMonthGeneration = async () => {
        loading.value = true
        try {
            const response = await backendApi.get('calculator/power_generation_month_analytics/', {
                params: {
                    year: selectedYear.value,
                    month: selectedMonth.value + 1,
                    compare_last_year: compareLastYear.value,
                    compare_two_years_ago: compareTwoYearsAgo.value
                }
            })
            monthGenerationChartData.value = response.data

            hasLastYearData.value = !!response.data.has_last_year_data
            hasTwoYearsAgoData.value = !!response.data.has_two_years_ago_data

            if (!hasLastYearData.value) compareLastYear.value = false
            if (!hasTwoYearsAgoData.value) compareTwoYearsAgo.value = false
        } catch (error) {
            console.error('MNo data is being received from the server:', error)
            monthGenerationChartData.value = null
            errorMsg.value = "No data is being received from the server.";
            errorClass.value = "alert-warning";
        } finally {
            loading.value = false
        }
    }

    const setSelectedPeriod = (year, month) => {
        selectedYear.value = year
        selectedMonth.value = month
        if (!hasLastYearData.value) compareLastYear.value = false;
        if (!hasTwoYearsAgoData.value) compareTwoYearsAgo.value = false;
        getMonthGeneration()
    }

    const toggleCompareLastYear = () => {
        compareLastYear.value = !compareLastYear.value
        getMonthGeneration()
    }

    const toggleCompareTwoYearsAgo = () => {
        compareTwoYearsAgo.value = !compareTwoYearsAgo.value
        getMonthGeneration()
    }

    return {
        dateRange,
        selectedYear,
        selectedMonth,
        monthGenerationChartData,
        loading,
        errorMsg,
        errorClass,
        compareLastYear,
        compareTwoYearsAgo,
        hasLastYearData,
        hasTwoYearsAgoData,
        fetchDateRange,
        getMonthGeneration,
        setSelectedPeriod,
        toggleCompareLastYear,
        toggleCompareTwoYearsAgo
    }
})