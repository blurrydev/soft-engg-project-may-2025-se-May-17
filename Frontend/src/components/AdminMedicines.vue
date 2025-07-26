<template>
  <div class="admin-dashboard">
    <div class="header-wrapper">
      <header class="dashboard-header">
        <Navbar />
      </header>
    </div>
    <br>
    <h2>All Medicines</h2>
    <div class="grid-header">
      <div>Name of Medicine</div>
      <div>Description</div>
      <div>Actions</div>
    </div>
    <div v-for="medicine in medicines" :key="medicine.id" :class="['request-row mb-3 p-3 rounded shadow-sm', medicine.colorClass]">
        <div class="grid-row">
        <div class="fw-bold">{{ medicine.title }}</div>
        <div>{{ medicine.description }}</div>
        <div class="action-buttons">
          <button class="btn-approve" @click="openEditModal(medicine)">Edit</button>
          <button class="btn-reject" @click="openDeleteModal(medicine)">Delete</button>
        </div>
      </div>
    </div>
    <!-- Edit Medicine Modal -->
    <div v-if="isEditModalVisible" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <h3>Edit Medicine</h3>
        <form @submit.prevent="updateMedicine">
        <div>
          <label for="title">Title:</label>
          <input type="text" v-model="selectedMedicine.title" required />
        </div>
        <div>
          <label for="description">Description:</label>
          <textarea v-model="selectedMedicine.description" required></textarea>
        </div>
          <button type="submit" class="btn btn-success">Save</button>
          <button @click="closeEditModal" class="btn btn-secondary">Cancel</button>
        </form>
      </div>
    </div>

    <!-- Delete Medicine Modal -->
    <div v-if="isDeleteModalVisible" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal-content">
        <p>Are you sure you want to delete this medicine?</p>
        <h3>{{ selectedMedicine?.title }}</h3>
        <button @click="deleteMedicine" class="btn btn-danger">Delete</button>
        <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script>
import apiService from "@/services/apiService";
import Navbar from "./Navbar.vue";
export default {
    components: {
    Navbar
  },
  data() {
    return {
      medicines: [],
      selectedMedicine: null,
      isEditModalVisible: false,
      isDeleteModalVisible: false,
    };
  },
  async mounted() {
    await this.fetchMedicines();
  },
  methods: {
    // Fetch all medicines from the API
    async fetchMedicines() {
      try {
        const res = await apiService.get("/sc/all-medicines");
        this.medicines = res.data.medicines || [];
      } catch (error) {
        console.error("Failed to fetch medicines:", error);
      }
    },

    // Open the Edit Modal
    openEditModal(medicine) {
      this.selectedMedicine = { ...medicine }; // Create a copy to avoid mutation issues
      this.isEditModalVisible = true;
    },

    // Close the Edit Modal
    closeEditModal() {
      this.isEditModalVisible = false;
      this.selectedMedicine = null;
    },

    // Update the medicine
    async updateMedicine() {
      try {
        const res = await apiService.put(`/sc/edit-medicine/${this.selectedMedicine.id}`, {
          title: this.selectedMedicine.title,
          description: this.selectedMedicine.description,
        });
        console.log("Medicine updated:", res.data);
        this.fetchMedicines(); // Refresh the list
        this.closeEditModal();
      } catch (error) {
        console.error("Failed to update medicine:", error);
      }
    },

    // Open the Delete Modal
    openDeleteModal(medicine) {
      this.selectedMedicine = medicine;
      this.isDeleteModalVisible = true;
    },

    // Close the Delete Modal
    closeDeleteModal() {
      this.isDeleteModalVisible = false;
      this.selectedMedicine = null;
    },

    // Delete the medicine
    async deleteMedicine() {
      try {
        const res = await apiService.delete(`/sc/delete-medicine/${this.selectedMedicine.id}`);
        console.log("Medicine deleted:", res.data);
        this.fetchMedicines(); // Refresh the list
        this.closeDeleteModal();
      } catch (error) {
        console.error("Failed to delete medicine:", error);
      }
    },
  },
};
</script>

<style scoped>
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
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 10px;
  width: 500px;
  max-width: 90%;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-danger {
  background-color: #e53935;
  color: white;
}

.btn-success {
  background-color: #4caf50;
  color: white;
}

.btn-secondary {
  background-color: #ccc;
  color: black;
}

.close-btn {
  background-color: #666;
  color: white;
  padding: 6px 12px;
  border: none;
  cursor: pointer;
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  padding: 1rem;
}

.no-requests {
  text-align: center;
  font-size: 1.2rem;
  padding: 1rem;
}
.grid-header {
  display: grid;
  grid-template-columns: 3fr 2fr 3fr 1fr 1fr 2fr;
  font-weight: bold;
  background-color: #d0f0e0;
  padding: 0.8rem 2rem;
  border-radius: 12px;
  margin: 1rem 3rem;
  font-size: 0.95rem;
  color: #333;
}

.grid-row {
  display: grid;
  grid-template-columns: 3fr 2fr 3fr 1fr 1fr 2fr;
  align-items: center;
  gap: 0.5rem;
}

.request-row {
  background-color: #fef9e7;
  border-left: 6px solid #f9a825;
  border-radius: 16px;
  padding: 1rem;
  font-size: 0.95rem;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
  margin: 0 3rem;
}
.btn-approve {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}

.btn-reject {
  background-color: #e53935;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}
</style>