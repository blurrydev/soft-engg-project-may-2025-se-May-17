<template>
  <div class="login-wrapper">
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
        <span style="font-size: smaller">Not yet registered? <a href="/">Click here</a></span>
      </div>
    </div>
  </div>
</template>

<script>
// Import our new mock login function directly, instead of a generic service
import { login } from '@/services/mockApi.js';
import { jwtDecode } from "jwt-decode";

export default {
  name: 'LibLogin',
  
  data() {
    return {
      username: '',
      password: '',
      message: '', 
      success: false 
    };
  },
  methods: {
    async handleSubmit() {
      try {
        // Call our new mock API function
        const result = await login(this.username, this.password);

        if (result.success) {
          // The structure of 'result.data' matches what the original code expected
          const decodedToken = jwtDecode(result.data.access_token);
          const role = decodedToken.role;
          const user_id = result.data.user_id;

          sessionStorage.setItem("accesstoken", result.data.access_token);
          sessionStorage.setItem("role", role);
          sessionStorage.setItem("user_id", user_id);
          sessionStorage.setItem("first_name", decodedToken.name); // Store first name for greetings
          sessionStorage.setItem("loggedIn", "true"); // Use string 'true' for consistency

          this.message = 'Logged in successfully! Redirecting...';
          this.success = true;

          // --- DYNAMIC REDIRECTION LOGIC ---
          setTimeout(() => {
            if (role === 'senior_citizen') {
              this.$router.push(`/sc/${user_id}`);
            } else if (role === 'care_giver') {
              this.$router.push(`/cg/${user_id}`);
            } else if (role === 'admin') {
              this.$router.push('/admin'); // Assuming you will create an /admin page
            } else {
              // Fallback to a generic homepage if role is unknown
              this.$router.push('/homepage');
            }
          }, 1500); // 1.5-second delay to show the success message
          
        } else {
          // Handle login failure from our mock API
          this.message = result.message || 'Invalid credentials. Please try again!';
          this.success = false;
        }
      } catch (error) {
        // This catch block will handle unexpected errors
        console.error('An unexpected error occurred during login:', error);
        this.message = 'An error occurred. Please try again later.';
        this.success = false;
      }
    }
  },
  mounted() {
    // This part is fine, it prevents logged-in users from seeing the login page again.
    // For a better user experience, we could add logic here to redirect them to their
    // correct dashboard instead of a generic one, but for now, we'll leave it as is.
    if (sessionStorage.getItem('loggedIn')) {
      // this.$router.push('/homepage');
    }
  }
}
</script>

<style scoped>
.login-wrapper {
  background-color: #d6eed6;
  min-height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: "Times New Roman", serif;
}

.form-container {
  padding: 2rem;
  border-radius: 10px;
  width: 400px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  background-color: #ffffff;
  box-sizing: border-box;
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
