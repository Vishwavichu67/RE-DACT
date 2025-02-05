// Select theme toggle button
const themeToggleButton = document.querySelector(".theme-button");
const themeIcon = document.getElementById("theme-icon");

// Initialize theme from localStorage or default to light
const savedTheme = localStorage.getItem("theme") || "light";
document.body.classList.add(savedTheme);
updateThemeIcon(savedTheme);

// Event listener for theme toggle
themeToggleButton.addEventListener("click", () => {
    const currentTheme = document.body.classList.contains("dark") ? "dark" : "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    // Switch theme
    document.body.classList.remove(currentTheme);
    document.body.classList.add(newTheme);

    // Save theme in localStorage
    localStorage.setItem("theme", newTheme);

    // Update theme icon
    updateThemeIcon(newTheme);
});

// Function to update the theme icon
function updateThemeIcon(theme) {
    if (themeIcon) {
        themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
}
