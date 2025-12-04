function eyesPassword() {
  const a = document.getElementById("password");
  const b = document.getElementById("eyes");
  if (a.type === "password") {
    a.type = "text";
    b.innerHTML = "visibility";
  } else {
    a.type = "password";
    b.innerHTML = "visibility_off";
  }
}

function eyesPasswordConfirm() {
  const a = document.getElementById("password_confirmation");
  const b = document.getElementById("eyesConfirm");
  if (a.type === "password") {
    a.type = "text";
    b.innerHTML = "visibility";
  } else {
    a.type = "password";
    b.innerHTML = "visibility_off";
  }
}

