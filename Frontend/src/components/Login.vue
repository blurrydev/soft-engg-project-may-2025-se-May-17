<template>
  <div class="login-page">
    <Navbar />

    <div class="login-wrapper">
      <div class="branding-section">
        <div class="branding-text">
          <h1>SilverCare</h1>
          <p>Never Miss a Dose, Never Miss a Moment</p>
        </div>
      </div>

      <div class="form-container">
        <h1>Login</h1>
        <form @submit.prevent="handleSubmit">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="Enter your username"
            required
          />

          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Enter your password"
            required
          />

          <button type="submit">Login</button>
        </form>

        <p v-if="message" :class="{ error: !success, success: success }">
          {{ message }}
        </p>

        <div class="mt-2">
          <span style="font-size: smaller"
            >Not yet registered? <a href="/signup">Click here</a></span
          >
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { jwtDecode } from "jwt-decode";
import Navbar from "@/components/Navbar.vue";

export default {
  name: "LibLogin",
  components: {
    Navbar,
  },
  data() {
    return {
      username: "",
      password: "",
      message: "",
      success: false,
    };
  },
  methods: {
    async handleSubmit() {
      try {
        const response = await fetch('http://localhost:5000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: this.username,
          password: this.password,
        }),
      });const data = await response.json();

    const result = response.ok
      ? { success: true, data }
      : { success: false, message: data.message };

        if (result.success) {
          const decodedToken = jwtDecode(result.data.access_token);
          const role = decodedToken.role;
          const user_id = result.data.user_id;

          sessionStorage.setItem("accesstoken", result.data.access_token);
          sessionStorage.setItem("role", role);
          sessionStorage.setItem("user_id", user_id);
          sessionStorage.setItem("first_name", decodedToken.name);
          sessionStorage.setItem("user_name", decodedToken.username)
          sessionStorage.setItem("loggedIn", "true");

          this.message = "Logged in successfully! Redirecting...";
          this.success = true;

          setTimeout(() => {
            if (role === "senior_citizen") {
              this.$router.push(`/sc`);
            } else if (role === "care_giver") {
              this.$router.push(`/cg`);
            } else if (role === "admin") {
              this.$router.push(`/admin`);
            } else {
              this.$router.push("/login");
            }
          }, 1500);
        } else {
          this.message = result.message || "Invalid credentials. Please try again!";
          this.success = false;
        }
      } catch (error) {
        console.error("Login error:", error);
        this.message = "An error occurred. Please try again later.";
        this.success = false;
      }
    },
  },
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f0f8ff;
}

.login-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: row;
}

.branding-section {
  flex: 1.2;
  background-image: linear-gradient(
      rgba(0, 0, 0, 0.4),
      rgba(0, 0, 0, 0.4)
    ),
    url('@/assets/elderly-medicine-care.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  color: white;
  font-family: "Georgia", serif;
  padding-left: 15%;
}

.branding-text h1 {
  font-size: 5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #fff5b0;
}

.branding-text p {
  font-size: 1.7rem;
  font-style: italic;
  color: #ffffffcc;
  max-width: 600px;
}

.form-container {
  flex: 1;
  padding: 2rem;
  border-radius: 20px;
  width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  font-family: "Times New Roman", serif;
  border: 1px solid #e0e0e0;
  margin: auto;
}

h1 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin: 0.5rem 0 0.2rem;
  font-weight: bold;
  text-align: left;
  color: #333;
}

input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
  margin-bottom: 1rem;
  font-family: "Times New Roman", serif;
}

button {
  padding: 0.6rem;
  background-color: #4caf50;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-family: "Times New Roman", serif;
}

button:hover {
  background-color: #388e3c;
}

p.success {
  color: green;
  margin-top: 1rem;
  text-align: center;
}

p.error {
  color: red;
  margin-top: 1rem;
  text-align: center;
}
</style>

