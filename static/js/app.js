// Select the toggle button
const toggleThemeButton = document.querySelector(".theme-toggle");

// Check and apply the saved theme from localStorage
const savedTheme = localStorage.getItem("theme") || "light";
document.body.classList.add(savedTheme);
updateThemeIcon(savedTheme);

// Toggle theme on button click
toggleThemeButton.addEventListener("click", () => {
    const currentTheme = document.body.classList.contains("dark") ? "dark" : "light";
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    // Update the theme
    document.body.classList.remove(currentTheme);
    document.body.classList.add(newTheme);

    // Save the theme in localStorage
    localStorage.setItem("theme", newTheme);

    // Update the toggle button icon
    updateThemeIcon(newTheme);
});

// Function to update the theme toggle button icon
function updateThemeIcon(theme) {
    toggleThemeButton.textContent = theme === "dark" ? "🌙" : "☀️";
}
