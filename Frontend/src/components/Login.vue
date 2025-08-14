<template>
  <div class="login-page">
    <Navbar />

    <div class="overlay">
      <div class="glass-container">
        <div class="branding-text">
          <h1>SilverCare</h1>
          <p>Never Miss a Dose, Never Miss a Moment</p>
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
            <span style="color:white" >
              Not yet registered? <a href="/signup">Click here</a>
            </span>
          </div>
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
  components: { Navbar },
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
        const response = await fetch("http://localhost:5000/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
          }),
        });
        const data = await response.json();

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
          sessionStorage.setItem("loggedIn", "true");

          this.message = "Logged in successfully! Redirecting...";
          this.success = true;

          setTimeout(() => {
            if (role === "senior_citizen") this.$router.push(`/sc`);
            else if (role === "care_giver") this.$router.push(`/cg`);
            else if (role === "admin") this.$router.push(`/admin`);
            else this.$router.push("/login");
          }, 1500);
        } else {
          this.message =
            result.message || "Invalid credentials. Please try again!";
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
  height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  background: url('https://media.swncdn.com/via/16464-happy-senior-mature-dad-hugging-prodigal-adul.jpg') no-repeat center center;
  background-size: cover;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* Black overlay over entire background */
.login-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3); /* Adjust for more/less darkness */
  z-index: 0;
}

.overlay {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative; /* keeps it above overlay */
  z-index: 1;
}

.glass-container {
  background: rgba(0, 0, 0, 0.35); /* Dark tint */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 2.5rem;
  width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  text-align: center;
}

/* Branding text inside glass */
.branding-text h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 0.3rem;
  color: #fff5b0;
}

.branding-text p {
  font-size: 1.2rem;
  font-style: italic;
  color: #ffffffcc;
  margin-bottom: 1.5rem;
}

/* Form styling inside glass */
.form-container h1 {
  color: white;
  margin-bottom: 1rem;
}

label {
  display: block;
  margin: 0.5rem 0 0.2rem;
  font-weight: bold;
  color: white;
  text-align: left;
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border-radius: 5px;
  border: none;
  background: rgba(255, 255, 255, 0.15); /* Slightly translucent */
  color: white;
}

input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

button {
  width: 100%;
  padding: 0.6rem;
  background-color: #4caf50;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #388e3c;
}

/* Message styles */
p.success {
  color: lightgreen;
}

p.error {
  color: #ff6b6b;
}
.form-container a {
  color: #00bfff; /* bright cyan for contrast */
  font-weight: bold;
  text-decoration: underline;
}

.form-container a:hover {
  color: #1ec8ff; /* lighter on hover */
  text-decoration: none; /* optional: remove underline on hover */
}

</style>
