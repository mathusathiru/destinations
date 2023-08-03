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
      errorMessages.push("Username must be at least three characters");
    }
    if (password.length < 8) {
      errorMessages.push("Password must be at least eight characters");
    }

    // Clear previous error messages
    while (usernameError.firstChild) {
      usernameError.removeChild(usernameError.firstChild);
    }
    while (passwordError.firstChild) {
      passwordError.removeChild(passwordError.firstChild);
    }

    if (errorMessages.length > 0) {
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
    } else {
      registerForm.submit();
    }
  });
});
