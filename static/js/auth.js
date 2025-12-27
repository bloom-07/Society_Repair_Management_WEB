async function loginResident() {
  await login("resident", "/resident");
}

async function loginAdmin() {
  await login("admin", "/admin");
}

async function login(role, redirectUrl) {
  const id = document.getElementById("user_id").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, password, role })
  });

  if (res.ok) {
    window.location.href = redirectUrl;
  } else {
    alert("Invalid credentials");
  }
}

function showRegister() {
  // navigate to the resident registration page
  window.location.href = "/register/resident";
}
async function registerResident() {
  const data = {
    resident_id: document.getElementById("resident_id").value,
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    contact: document.getElementById("contact").value,
    block: document.getElementById("block").value,
    flat_no: document.getElementById("flat").value,
    password: document.getElementById("password").value
  };

  const res = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  if (res.ok) {
    alert("Registered successfully! Login now.");
    window.location.href = "/login/resident";
  } else {
    alert("Registration failed");
  }
}
