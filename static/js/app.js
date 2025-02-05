document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");
    const body = document.body;

    // Check user preference in localStorage
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
        themeIcon.textContent = "☀️"; // Sun for Light Mode
    } else {
        body.classList.remove("dark-mode");
        themeIcon.textContent = "🌙"; // Moon for Dark Mode
    }

    // Toggle theme when button is clicked
    themeToggle.addEventListener("click", function () {
        if (body.classList.contains("dark-mode")) {
            body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light");
            themeIcon.textContent = "🌙"; // Show Moon when switching to Light Mode
        } else {
            body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
            themeIcon.textContent = "☀️"; // Show Sun when switching to Dark Mode
        }
    });
});
