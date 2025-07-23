<template>
  <div class="signup-page">
    <Navbar />

    <div class="signup-wrapper">
      <div class="form-container">
        <h1>Sign Up</h1>

        <form @submit.prevent="handleSubmit">
          <label for="first_name">First Name</label>
          <input type="text" id="first_name" v-model="first_name" placeholder="Enter your First Name" required />

          <label for="last_name">Last Name</label>
          <input type="text" id="last_name" v-model="last_name" placeholder="Enter your Last Name" required />


          <label for="username">Username</label>
          <input type="text" id="username" v-model="username" placeholder="Enter a username" required />

          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" placeholder="Enter a password" required />

          <label for="confirm_password">Confirm Password</label>
          <input type="password" id="confirm_password" v-model="confirm_password" placeholder="Confirm password" required />

          <label for="role">Role</label>
          <select id="role" v-model="role" required>
            <option value="">Select Role</option>
            <option value="care_giver">Care Giver</option>
            <option value="senior_citizen">Senior Citizen</option>
          </select>

          <button type="submit">Register</button>
        </form>

        <p v-if="message" :class="{ error: !success, success: success }">
          {{ message }}
        </p>

        <div class="mt-2">
          <span style="font-size: smaller"
            >Already have an account? <a href="/login">Login here</a></span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from "@/components/Navbar.vue";
export default {
  name: "SignUpPage",
  components: {
     Navbar,
  },
  data() {
    return {
      first_name: "",
      last_name:"",
      username: "",
      password: "",
      confirm_password:"",
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
      const response = await fetch('http://localhost:5000/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: this.first_name,
          last_name: this.last_name,
          username: this.username,
          password: this.password,
          confirm_password: this.confirm_password,
          role: this.role
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
          this.last_name="";
          this.username = "";
          this.password = "";
          this.role = "";
          setTimeout(() => {
          this.$router.push('/login');
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
  background-color: #d6eed6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.signup-wrapper {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.form-container {
  padding: 2rem;
  border-radius: 20px;
  width: 600px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  font-family: "Times New Roman", serif;
  border: 1px solid #e0e0e0;
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

input,
select {
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
