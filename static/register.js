// script executed when the HTML page is loaded
document.addEventListener("DOMContentLoaded", function() {
  // obtain form element with id "register-form"
  const registerForm = document.getElementById("register-form");
  // obtain username and password input values through their respective IDs
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  // obtain error message placeholder elements for the username and password, through their respective IDs
  const usernameError = document.getElementById("username-error");
  const passwordError = document.getElementById("password-error");

  // event listener for the form submit event (submit button), executes when submit event is activated
  registerForm.addEventListener("submit", function(event) {
    // prevent default form submission behavior to execute validation checks
    event.preventDefault();

    // clear previous error messages
    usernameError.textContent = "";
    passwordError.textContent = "";

    // obtain values of username and password inputs, respectively
    const username = usernameInput.value;
    const password = passwordInput.value;

    // initialise array to store error messages
    let errorMessages = [];

    // check username length (valid usernames must be three characters or greater)
    if (username.length < 3) {
      errorMessages.push("Username too short (min. 3 characters)");
    }

    // check password length (valid passwords must be eight characters or greater)
    if (password.length < 8) {
      errorMessages.push("Password too short (min. 8 characters)");
    }

    // iterate through error messages in array, and display them through div elements
    for (const message of errorMessages) {
      const errorDiv = document.createElement("div");
      errorDiv.classList.add("error-message");
      errorDiv.textContent = message;

      // append error message(s) to the correct div element(s)
      if (message.includes("Username")) {
        usernameError.appendChild(errorDiv);
      } else if (message.includes("Password")) {
        passwordError.appendChild(errorDiv);
      }
    }

    // create  div element to display a "No error" message (hidden on the page)
    const noErrorDiv = document.createElement("div");
    noErrorDiv.classList.add("no-error");
    noErrorDiv.textContent = "No error";

    // append "No error" message to the username if it is three characters or greater
    if (username.length >= 3) {
      usernameError.appendChild(noErrorDiv);
    }

    // append "No error" message to the password if it is eight characters or greater
    if (password.length >= 8) {
      passwordError.appendChild(noErrorDiv);
    }

    // submit the form if there are no errors (identied by an empty array of error messages)
    if (errorMessages.length === 0) {
      registerForm.submit();
    }
  });
});