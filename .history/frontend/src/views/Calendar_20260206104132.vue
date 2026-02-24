<!-- frontend/src/views/Calendar.vue -->
<template>
  <div class="calendar-container">
    <!-- En-tête avec navigation -->
    <div class="calendar-header">
      <button @click="prevMonth" class="nav-button">&#10094;</button>
      <h2>{{ currentMonthName }} {{ currentYear }}</h2>
      <button @click="nextMonth" class="nav-button">&#10095;</button>
    </div>

    <!-- Jours de la semaine -->
    <div class="weekdays">
      <div v-for="day in weekdays" :key="day" class="weekday">
        {{ day }}
      </div>
    </div>

    <!-- Jours du mois -->
    <div class="days">
      <div
        v-for="day in daysInMonth"
        :key="day.date"
        class="day"
        :class="{ 'empty': !day.inMonth, 'today': day.isToday }"
      >
        {{ day.day }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Day {
  day: string | number;
  inMonth: boolean;
  isToday: boolean;
  date?: Date; // Optionnel, si vous voulez stocker la date complète
}

const weekdays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
const today = new Date();
const currentMonth = ref(today.getMonth());
const currentYear = ref(today.getFullYear());

const monthNames = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
];

const currentMonthName = computed(() => monthNames[currentMonth.value]);

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
};

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0;
    currentYear.value++;
  } else {
    currentMonth.value++;
  }
};

const daysInMonth = computed((): Day[] => {
  const firstDay = new Date(currentYear.value, currentMonth.value, 1).getDay();
  const days: Day[] = [];
  const daysCount = new Date(currentYear.value, currentMonth.value + 1, 0).getDate();

  // Ajouter les jours vides avant le 1er du mois
  for (let i = 0; i < firstDay - 1; i++) {
    days.push({ day: '', inMonth: false, isToday: false });
  }

  // Ajouter les jours du mois
  for (let i = 1; i <= daysCount; i++) {
    const date = new Date(currentYear.value, currentMonth.value, i);
    const isToday = date.toDateString() === today.toDateString();
    days.push({ day: i, inMonth: true, isToday, date });
  }

  return days;
});
</script>


<style scoped>
.calendar-container {
  max-width: 600px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.nav-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #333;
}

.nav-button:hover {
  color: #007bff;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-weight: bold;
  margin-bottom: 10px;
}

.weekday {
  padding: 8px;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
}

.day {
  padding: 10px;
  text-align: center;
  border-radius: 4px;
}

.day.empty {
  visibility: hidden;
}

.day.today {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}
</style>
