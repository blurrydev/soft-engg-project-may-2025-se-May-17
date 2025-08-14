<template>
  <div class="signup-page">
    <Navbar />

    <div class="overlay">
      <div class="glass-container">
        <!-- Branding text like login page -->
        <div class="branding-text">
          <h1>SilverCare</h1>
          <p>Never Miss a Dose, Never Miss a Moment</p>
        </div>

        <!-- Form -->
        <div class="form-container">
          <h1>Sign Up</h1>
          <form @submit.prevent="handleSubmit">

    <!-- First & Last Name on same line -->
    <div class="form-row">
      <div>
        <label for="first_name">First Name</label>
        <input type="text" id="first_name" v-model="first_name" placeholder="Enter your First Name" required />
      </div>
      <div>
        <label for="last_name">Last Name</label>
        <input type="text" id="last_name" v-model="last_name" placeholder="Enter your Last Name" required />
      </div>
    </div>

    <label for="username">Username</label>
    <input type="text" id="username" v-model="username" placeholder="Enter a username" required />

    <!-- Password & Confirm Password on same line -->
    <div class="form-row">
      <div>
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" placeholder="Enter a password" required />
      </div>
      <div>
        <label for="confirm_password">Confirm Password</label>
        <input type="password" id="confirm_password" v-model="confirm_password" placeholder="Confirm password" required />
      </div>
    </div>

    <label for="role">Role</label>
    <select id="role" v-model="role" required>
      <option value="">Select Role</option>
      <option value="care_giver">Care Giver</option>
      <option value="senior_citizen">Senior Citizen</option>
    </select>

    <button type="submit">Register</button>
  </form>

          <p v-if="message" :class="{ error: !success, success: success }">{{ message }}</p>

          <div class="mt-2">
            <span style="font-size: smaller">
              Already have an account?
              <a href="/login">Login here</a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from "@/components/Navbar.vue";
export default {
  name: "SignUpPage",
  components: { Navbar },
  data() {
    return {
      first_name: "",
      last_name: "",
      username: "",
      password: "",
      confirm_password: "",
      role: "",
      message: "",
      success: false,
    };
  },
  methods: {
    async handleSubmit() {
      if (this.password !== this.confirm_password) {
        this.message = "Confirmation password must be the same as your password.";
        this.success = false;
        return;
      }
      try {
        const response = await fetch("http://localhost:5000/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            first_name: this.first_name,
            last_name: this.last_name,
            username: this.username,
            password: this.password,
            confirm_password: this.confirm_password,
            role: this.role,
          }),
        });

        const data = await response.json();
        const result = response.ok
          ? { success: true }
          : { success: false, message: data.message };

        if (result.success) {
          this.message = "Registered successfully! Please login.";
          this.success = true;
          this.first_name = "";
          this.last_name = "";
          this.username = "";
          this.password = "";
          this.confirm_password = "";
          this.role = "";
          setTimeout(() => {
            this.$router.push("/login");
          }, 1500);
        } else {
          this.message = result.message || "Registration failed.";
          this.success = false;
        }
      } catch (error) {
        console.error("Registration error:", error);
        this.message = "An error occurred. Please try again.";
        this.success = false;
      }
    },
  },
};
</script>

<style scoped>
.signup-page {
  height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
  background: url("https://media.swncdn.com/via/16464-happy-senior-mature-dad-hugging-prodigal-adul.jpg")
    no-repeat center center;
  background-size: cover;
  position: relative;
  display: flex;
  flex-direction: column;
}

.signup-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 0;
}

.overlay {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 1;
}

.glass-container {
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 2.5rem;
  width: 400px;
  max-width: 92vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  text-align: center;
  height: 700px; 
}

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

input,
select {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border-radius: 5px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
}
input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}
select option {
  color: #333;
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

p.success {
  color: lightgreen;
}
p.error {
  color: #ff6b6b;
}

.form-row {
  display: flex;
  gap: 20px; /* space between the two fields */
}

.form-row > div {
  flex: 1; /* makes both fields equal width */
}

</style>
