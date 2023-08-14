document.addEventListener("DOMContentLoaded", function() {
  const registerForm = document.getElementById("register-form");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const usernameError = document.getElementById("username-error");
  const passwordError = document.getElementById("password-error");

  registerForm.addEventListener("submit", function(event) {
    event.preventDefault();

    usernameError.textContent = "";
    passwordError.textContent = "";

    const username = usernameInput.value;
    const password = passwordInput.value;

    let errorMessages = [];

    if (username.length < 3) {
      errorMessages.push("Username (min. 3 characters)");
    }

    if (password.length < 8) {
      errorMessages.push("Password (min. 8 characters)");
    }

    for (const message of errorMessages) {
      const errorDiv = document.createElement("div");
      errorDiv.classList.add("error-message");
      errorDiv.textContent = message;

      if (message.includes("Username")) {
        usernameError.appendChild(errorDiv);
      } else if (message.includes("Password")) {
        passwordError.appendChild(errorDiv);
      }
    }

    const noErrorDiv = document.createElement("div");
    noErrorDiv.classList.add("no-error");
    noErrorDiv.textContent = "No error";

    if (username.length >= 3) {
      usernameError.appendChild(noErrorDiv);
    }

    if (password.length >= 8) {
      passwordError.appendChild(noErrorDiv);
    }

    if (errorMessages.length === 0) {
      registerForm.submit();
    }
  });
});
