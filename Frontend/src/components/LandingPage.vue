<template>
  <div class="landing-wrapper">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg fixed-top custom-navbar px-5 py-3">
      <a class="navbar-brand fw-bold fs-4 text-white" href="#">
        SilverCare<span class="text-primary">.</span>
      </a>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
        <ul class="navbar-nav"></ul>
        <!-- Login/Signup Buttons -->
        <div class="d-flex gap-2 ms-4">
          
          <router-link to="/login" class="btn btn-outline-light btn-sm">Login</router-link>
<router-link to="/signup" class="btn btn-primary btn-sm">Signup</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section d-flex justify-content-center align-items-center text-white text-center px-4">
      <div class="text-box">
        <h1 class="fw-bold display-4">Expert Care for the <br />Elderly</h1>

        <div style="color: black; font-weight: bold" class="fs-5 mt-3">
          The Happy Face of Senior Independence
        </div>

        <p class="fs-5 mt-2">
          No matter the level of care, we'll help connect you with a skilled, compassionate
          provider for a better quality of life for you or your loved one.
        </p>

        <router-link to="/signup" class="btn btn-primary mt-4 px-4 py-2">
  GET IN TOUCH
</router-link>

      </div>
    </section>

    <!-- About Section -->
    <section id="about-section" class="info-section bg-light text-dark py-5 px-4">
      <div class="container text-center">
        <h2 class="fw-bold mb-4">About Us</h2>
        <p class="lead">
          We are dedicated to providing the highest level of care to the elderly, ensuring their comfort, dignity,
          and independence. Our team of professionals is trained to handle a wide range of needs with compassion and respect.
        </p>
      </div>
    </section>

    <!-- Contact Section
    <section id="contact-section" class="info-section bg-white text-dark py-5 px-4">
      <div class="container text-center">
        <h2 class="fw-bold mb-4">Contact Us</h2>
        <p class="lead">
          Have questions or need assistance? Reach out to our support team and we'll get back to you as soon as possible.
        </p>
        <p class="mt-3">
          <strong>Email:</strong> support@elderlycare.com<br />
          <strong>Phone:</strong> +91-8010676679
        </p>
      </div>
    </section> -->
  </div>
</template>

<script setup>
// No JavaScript needed
</script>

<style scoped>
.landing-wrapper {
  scroll-behavior: smooth;
}

.custom-navbar {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(6px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
}

/* Hero Section */
.hero-section {
  background-image: url('https://media.swncdn.com/via/16464-happy-senior-mature-dad-hugging-prodigal-adul.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
  padding-top: 100px;
}

.navbar .nav-link {
  font-weight: 500;
  font-size: 1rem;
}

.hero-section h1 {
  line-height: 1.2;
}

.hero-section p {
  max-width: 600px;
  margin: 0 auto;
}

.navbar-brand {
  font-weight: bold;
}

.btn-primary {
  background-color: #337cf7;
  border: none;
}

.btn-primary:hover {
  background-color: #1a6be0;
}

.info-section {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.landing-wrapper {
  scroll-behavior: smooth;
  height: 100vh;
  overflow: hidden; /* prevent scrolling */
}

/* Make sure body and html don’t scroll */
html,
body {
  height: 100vh;
  margin: 0;
}

</style>
