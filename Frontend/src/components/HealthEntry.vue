<template>
  <div class="modal-overlay" @click.self="emitClose">
    <div class="modal-content">
      <h3>Health Entry</h3>
      <div v-if="role === 'care_giver'">
        <label for="senior">Select Senior Citizen:</label>
        <select v-model="selectedSenior" class="form-control">
          <option v-for="senior in seniors" :key="senior.id" :value="senior">{{ senior.username }}</option>
        </select>
      </div>
      <form @submit.prevent="submitHealthEntry">
        <div>
          <label for="bp_systolic">BP Systolic:</label>
          <input type="number" v-model="healthData.bp_systolic" required />
        </div>
        <div>
          <label for="bp_diastolic">BP Diastolic:</label>
          <input type="number" v-model="healthData.bp_diastolic" required />
        </div>
        <div>
          <label for="sugar_level">Sugar Level:</label>
          <input type="number" step="0.1" v-model="healthData.sugar_level" required />
        </div>
        <div>
          <button type="button" class="btn btn-secondary" @click="emitClose">Cancel</button>
          <button type="submit" class="btn btn-success" :disabled="!isFormValid">Submit</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits,defineProps } from 'vue'
import apiService from '@/services/apiService'
//import { useRouter } from 'vue-router'
const props = defineProps({
  role: String,
})
const healthData = ref({
  bp_systolic: '',
  bp_diastolic: '',
  sugar_level: ''
})
const selectedSenior = ref(null)
const seniors = ref([])
const isFormValid = computed(() =>
  healthData.value.bp_systolic && healthData.value.bp_diastolic && healthData.value.sugar_level
)

import { watch } from 'vue'

watch(
() => props.role,
(role) => {
 if (role === 'care_giver') {
   fetchDependents()
 }
},
{ immediate: true }
)

const emit = defineEmits(['close'])
function emitClose() {
  emit('close')
}

async function fetchDependents() {
  try {
    const res = await apiService.get('/sc/my-dependents');
    const data = res.data;
    seniors.value = Array.isArray(data.dependents) ? data.dependents : [];
  } catch (err) {
    seniors.value = []
  }
}

async function submitHealthEntry() {
  if (!isFormValid.value) {
    alert("Please fill in all the fields.")
    return
  }
  if (props.role === 'care_giver' && !selectedSenior.value) {
    alert("Please select a senior citizen first.")
    return
  }
  try {
    const data = {
      ...healthData.value,
      senior_id: props.role === 'care_giver' ? selectedSenior.value.id : undefined
    }
    const res = await apiService.post("/sc/health-entry", data)
    if (res.status === 201) {
      alert(res.data.message)
      healthData.value = { bp_systolic: '', bp_diastolic: '', sugar_level: '' }
      emitClose()
    } else if (res.status === 400) {
      alert(res.data.error)
    }
  } catch (error) {
    if (error.response) {
      alert(error.response.data.error || "Invalid input")
    }
    emitClose()
  }
}
</script>

<style scoped>
/* Copy your modal-overlay and modal-content styles from previous component */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}
.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 10px;
  width: 400px;
  max-width: 50%;
  z-index: 1060;
}
</style>
