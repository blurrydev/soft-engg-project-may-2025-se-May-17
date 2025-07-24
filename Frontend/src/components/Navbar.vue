<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
            integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh"
            crossorigin="anonymous"/>
      <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
            crossorigin="anonymous"/>
    </head>
    <nav class="navbar navbar-expand-lg navbar-dark bg-info fixed-top">
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbar">
        <div class="navbar-nav">
          <a class="nav-item nav-link text-dark" @click="userHome">
            <h3>SilverCare</h3>
          </a>
        </div>
        <div class="navbar-nav ml-auto" v-if='role'>
          <!-- Notification Bell Icon -->
          <div v-if="role === 'senior_citizen'" class="nav-item position-relative mr-3" @click="toggleModal">
            <i class="fa fa-bell text-white" style="font-size: 24px; cursor: pointer;"></i>
            <span v-if="notificationCount > 0" class="badge badge-danger badge-pill notification-badge">
              {{ notificationCount }}
            </span>
          </div>
          <div class="nav-item dropdown-container">
            <a class="nav-link profile-icon-link" href="#">
              <i class="fa fa-user-circle"></i>
            </a>
            <div class="dropdown-menu-hover">
              <template v-if="role==='care_giver'">
              <a class="dropdown-item" href="/cg">Home</a>
              </template>
              <template v-if="role==='senior_citizen'">
              <a class="dropdown-item" href="/sc">Home</a>
              </template>
              <template v-if="role === 'senior_citizen' || role === 'care_giver'">
              <a class="dropdown-item" href="/profile">My Profile</a>
              <a class="dropdown-item" href="/stats">Reports</a>
              </template>
              <template v-if="role==='care_giver'">
              <a class="dropdown-item" @click="memberDetails">Member Details</a>
              </template>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item logout-item" @click="logout">Logout</a>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <NotificationModal
        :show="showModal"
        @close="showModal = false"
        @updated="getNotificationCount"
      />
    </div>
</template>


<script setup >
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NotificationModal from "@/components/NotificationModal.vue"; 
import apiService from '@/services/apiService';
const role = ref(null)
const router = useRouter()
//const route = useRoute()
const showModal = ref(false)
const notificationCount = ref(0)
onMounted(() => {
  role.value = sessionStorage.getItem('role')
  if (role.value === "senior_citizen") {
    getNotificationCount()
  }
})
function toggleModal() {
  showModal.value = true
}

async function getNotificationCount() {
  try {
    const res = await apiService.get("/sc/pending-caregiver-requests")
    notificationCount.value = res.data?.requests?.length || 0
  } catch (err) {
    console.error("Error fetching notifications:", err)
  }
}
function logout() {
    sessionStorage.clear();
    router.push('/login');
  }
function memberDetails() {
    router.push('/cg/user_101/manageDependants');
  }
</script>

<style>
.navbar {
  background-color: #3b5998; /* Facebook blue */
  padding: 16px;
  font-family: 'Times New Roman';
  font-style: italic;
}

.navbar ul {
  list-style-type: none;
  padding: 0;
  display: flex;
  justify-content: space-around;
}

.navbar li {
  display: inline;
}

.navbar a {
  color: white !important;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: font-weight 0.3s ease;
  cursor: pointer; /* Change cursor to pointer */
}

.navbar a:hover {
  font-weight: bold;
}

.navbar .fa {
  font-size: 18px;
}

.text-dark {
  color: white !important;
}
.dropdown-container {
  position: relative;
}

.dropdown-menu-hover {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  width: 180px;
  padding: 0.5rem 0;
  z-index: 1000;
  border: 1px solid #eee;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.25s ease-out;
}

.dropdown-container:hover .dropdown-menu-hover {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-menu-hover .dropdown-item {
  display: block;
  padding: 0.6rem 1rem;
  font-size: 0.95rem;
  color: #333 !important;
  font-weight: 500;
}

.dropdown-menu-hover .dropdown-item:hover {
  background-color: #f0f0f0;
}

.dropdown-divider {
  height: 1px;
  background-color: #eee;
  margin: 0.5rem 0;
}

.logout-item {
  color: #d9534f !important;
  font-weight: bold !important;
}
.notification-badge {
  position: absolute;
  top: 0;
  right: -6px;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 50%;
}

</style>
