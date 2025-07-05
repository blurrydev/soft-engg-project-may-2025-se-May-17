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
        <div class="navbar-nav ml-auto">
          <div class="nav-item dropdown-container">
            <a class="nav-link profile-icon-link" href="#">
              <i class="fa fa-user-circle"></i>
            </a>
            <div class="dropdown-menu-hover">
              <a class="dropdown-item" @click="myProfile">My Profile</a>
              <a class="dropdown-item" @click="summaryReport">Reports</a>
              <a class="dropdown-item" @click="memberDetails">Member Details</a>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item logout-item" @click="logout">Logout</a>
            </div>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>


<script>
export default {
  name: 'NavBar',
  
  methods: {
  logout() {
    sessionStorage.clear();
    this.$router.push('/login');
  },
  myProfile() {
    const path = this.$route.path;
    if (path.startsWith('/sc/dep_001')) {
      this.$router.push('/sc/dep_001/profile');
    }else if (path.startsWith('/sc/dep_002')) {
      this.$router.push('/sc/dep_002/profile');
    }else{
      this.$router.push('/cg/user_101/profile')
    }
  },
  memberDetails() {
    this.$router.push('/cg/user_101/manageDependants');
  },
  summaryReport() {
    const path = this.$route.path;
    if (path.startsWith('/sc/dep_001')) {
      this.$router.push('/sc/dep_001/stats');
    }else if (path.startsWith('/sc/dep_002')) {
      this.$router.push('/sc/dep_002/stats');
    }else{
      this.$router.push('/cg/user_101/stats');
    }
  },
  goHome() {
    const path = this.$route.path;
    if (path.startsWith('/sc/dep_001')) {
      this.$router.push('/sc/dep_001');
    } else if (path.startsWith('/sc/dep_002')) {
      this.$router.push('/sc/dep_002');
    } else if (path.startsWith('/cg/')) {
      this.$router.push('/cg/user_101');
    } else if (path.startsWith('/admin')) {
      this.$router.push('/admin');
    } else {
      this.$router.push('/');
    }
  },
  triggerSOS() {
    alert('SOS alert triggered!');
  }
}
};
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
</style>
