from helium import *

# Test homepage
start_chrome("http://127.0.0.1:5000/", maximize="True")
wait_until(Text("elevate guest experiences").exists)
kill_browser()

# Test search page
start_chrome("http://127.0.0.1:5000/search.html", maximize="True")
wait_until(Text("Radius Selection").exists)
kill_browser()

# Test search page functionality
start_chrome("http://127.0.0.1:5000/search.html", maximize="True")
click(RadioButton("500"))
click(S("#search"))
write("SW1A 0AA", into = S("#search"))
click(Button("Search"))
wait_until(Text("OpenStreetMap").exists)
kill_browser()

# Test registration
start_chrome("http://127.0.0.1:5000/register.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Register"))
wait_until(Text("Welcome back newuser!").exists)
kill_browser()

# Test login
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
kill_browser()

# Test search records - with no records
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("Search Past Records"))
click(S("#search-input"))
write("london", into = S("#search-input"))
click(Button("Search"))
wait_until(Text("No matching records found.").exists)
kill_browser()

# Test all searches - with no records
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("All Locations"))
wait_until(Text("Search history is empty").exists)
kill_browser()

# Test popular locatins - with no records
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("Top Locations"))
wait_until(Text("Search history is empty").exists)
kill_browser()

# Test search page as a logged in user
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("Search"))
click(RadioButton("500"))
click(S("#search"))
write("SW1A 0AA", into = S("#search"))
click(Button("Search"))
wait_until(Text("OpenStreetMap").exists)
kill_browser()

# Test all searches - with records
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("All Locations"))
wait_until(S(".search-result-card").exists)
kill_browser()

# Test popular locatins - with records
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("Top Locations"))
wait_until(S(".search-result-card").exists)
kill_browser()

# Test search past records  - with records
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Link("Search Past Records"))
click(S("#search-input"))
write("London", into = S("#search-input"))
click(Button("Search"))
wait_until(S(".search-result-card").exists)
kill_browser()

# Test logout
start_chrome("http://127.0.0.1:5000/login.html", maximize="True")
write("newuser", into = "username")
write("password123", into = "password")
click(Button("Login"))
wait_until(Text("Welcome back newuser!").exists)
click(Button("Logout"))
wait_until(Text("elevate guest experiences").exists)
kill_browser()
