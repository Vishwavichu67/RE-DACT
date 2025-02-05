// Select the toggle button and theme icon
const themeToggleButton = document.querySelector(".theme-button");
const themeIcon = document.getElementById("theme-icon");

// Check the saved theme in localStorage (default: light)
const savedTheme = localStorage.getItem("theme") || "light";
applyTheme(savedTheme); // Apply saved theme

// Toggle theme on button click
themeToggleButton.addEventListener("click", () => {
    const currentTheme = document.body.classList.contains("dark") ? "dark" : "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    // Apply the new theme
    applyTheme(newTheme);

    // Save the theme in localStorage
    localStorage.setItem("theme", newTheme);
});

// Function to apply the theme to the document
function applyTheme(theme) {
    // Remove existing theme classes
    document.body.classList.remove("light", "dark");
    // Add the new theme class
    document.body.classList.add(theme);
    // Update theme icon
    updateThemeIcon(theme);
}

// Function to update the theme icon
function updateThemeIcon(theme) {
    themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
}