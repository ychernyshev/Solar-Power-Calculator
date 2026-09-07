import { defineStore } from 'pinia';
import { ref } from 'vue';
import backendApi from "@/services/backendApi.ts";

export const useNotificationStore = defineStore('notifications', () => {
    const messages = ref([]);
    let socket = null;

    const initMessages = async () => {
        try {
            const response = await backendApi.get('calculator/system_event/?limit=5');
            const data = response.data.results || response.data;

            if (Array.isArray(data)) {
                const formattedMessages = [];

                data.forEach(m => {
                    if (m.wind_records && m.wind_records.length > 0) {
                        const windRec = m.wind_records[0];

                        let adjustedTime = windRec.event_time || m.event_time;
                        if (adjustedTime) {
                            const parts = adjustedTime.split(':');
                            let hour = parseInt(parts[0], 10) - 1;
                            if (hour < 0) hour = 23;
                            parts[0] = String(hour).padStart(2, '0');
                            adjustedTime = parts.join(':');
                        }

                        formattedMessages.push({
                            id: `wind-${m.id}-${windRec.id || Math.random()}`,
                            type: 'wind',
                            title: 'Wind Forecast',
                            date: m.date,
                            level: m.level || 'info',
                            event_time: adjustedTime,
                            wind_strength: windRec.wind_strength,
                            gust_strength: windRec.gust_strength,
                            wind_direction: windRec.wind_direction,
                            isPersistent: true,
                            created_at: m.created_at
                        });
                    }

                    if (m.peak_records && m.peak_records.length > 0) {
                        const startPeak = m.peak_records.find(p => p.status === 'PEAK_START');
                        const endPeak = m.peak_records.find(p => p.status === 'PEAK_END');

                        if (startPeak && endPeak) {
                            const startHourStr = `${String(startPeak.peak_hour).padStart(2, '0')}:00`;
                            const endHourVal = (endPeak.peak_hour + 1) % 24;
                            const endHourStr = `${String(endHourVal).padStart(2, '0')}:00`;

                            formattedMessages.push({
                                id: `peak-range-${m.id}-${startPeak.peak_hour}`,
                                type: 'peak',
                                title: 'Solar Peak Hours',
                                level: 'success',
                                date: m.date,
                                formatted_time_range: `${startHourStr} - ${endHourStr}`,
                                status: 'PEAK_RANGE',
                                isPersistent: true,
                                created_at: m.created_at
                            });
                        } else {
                            m.peak_records.forEach(peak => {
                                const hour = peak.peak_hour;
                                const formattedHour = `${String(hour).padStart(2, '0')}:00`;
                                const timeRange = peak.status === 'PEAK_START'
                                    ? `${formattedHour} - ${String((hour + 1) % 24).padStart(2, '0')}:00`
                                    : formattedHour;

                                formattedMessages.push({
                                    id: `peak-${m.id}-${hour}`,
                                    type: 'peak',
                                    title: peak.status === 'PEAK_START' ? 'Solar Peak Start' : 'Solar Peak End',
                                    level: 'success',
                                    formatted_time_range: timeRange,
                                    status: peak.status,
                                    isPersistent: true,
                                    created_at: m.created_at
                                });
                            });
                        }
                    }

                    if (!m.wind_records?.length && !m.peak_records?.length) {
                        formattedMessages.push({
                            id: `system-${m.id}`,
                            type: 'system',
                            title: m.title || 'System Notification',
                            text: m.text || m.payload?.message || '',
                            level: m.level ? m.level.toLowerCase() : 'info',
                            isPersistent: true,
                            created_at: m.created_at
                        });
                    }
                });

                messages.value = formattedMessages.slice(0, 10);
            }
        } catch (e) {
            console.error("Помилка завантаження повідомлень з бази даних", e);
        }
    };

    const initWebSocket = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const host = 'localhost:8001';

        socket = new WebSocket(`${protocol}${host}/ws/calculator/events/`);

        socket.onopen = () => {
            console.log("WS: Connected to Calculator events successfully.");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WS: New event received:", data);
                addNotification(data);
            } catch (e) {
                console.error("WS: Failed to parse incoming message", e);
            }
        };

        socket.onerror = (error) => {
            console.error("WS: WebSocket error observed:", error);
        };

        socket.onclose = (event) => {
            console.warn("WS: Connection lost. Trying to reconnect in 3s...", event.reason);
            setTimeout(initWebSocket, 3000);
        };
    };

    const addNotification = (eventData) => {
        const newMessage = {
            id: eventData.id || Date.now(),
            type: eventData.type || 'system',
            title: eventData.title || 'System Notification',
            text: eventData.text || eventData.payload?.message || '',
            level: eventData.level ? eventData.level.toLowerCase() : 'info',
            isPersistent: eventData.is_persistent,
            created_at: eventData.created_at || new Date().toISOString()
        };

        messages.value.unshift(newMessage);
        if (messages.value.length > 5) {
            messages.value.pop();
        }
    };

    const removeNotification = (id) => {
        messages.value = messages.value.filter(m => m.id !== id);
    };

    const disconnectWebSocket = () => {
        if (socket) {
            socket.close();
            socket = null;
        }
    };

    return {
        messages,
        initMessages,
        addNotification,
        removeNotification,
        initWebSocket,
        disconnectWebSocket
    };
});