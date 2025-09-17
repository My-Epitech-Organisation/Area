const apiUrl = 'http://localhost:8080/users/sql';
let users = [];
let editUserId = null;

function fetchUsers() {
  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      users = data;
      renderUsers();
    });
}


function createSakuraPetal() {
  const petal = document.createElement('div');
  petal.className = 'sakura-petal';
  petal.style.left = Math.random() * window.innerWidth + 'px';
  petal.style.top = '-40px';
  petal.style.transform = `rotate(${Math.random() * 360}deg)`;
  petal.style.opacity = 0.7 + Math.random() * 0.3;
  document.body.appendChild(petal);

  // Animation de chute
  const duration = 6000 + Math.random() * 4000;
  petal.animate([
    { transform: petal.style.transform, top: '-40px' },
    { transform: `rotate(${Math.random() * 360}deg)`, top: window.innerHeight + 'px' }
  ], {
    duration: duration,
    easing: 'linear'
  });

  setTimeout(() => {
    petal.remove();
  }, duration);
}

function startSakuraPetals() {
  setInterval(() => {
    createSakuraPetal();
  }, 400);
}

window.addEventListener('DOMContentLoaded', () => {
  startSakuraPetals();
});

function renderUsers() {
  const list = document.getElementById('users-list');
  list.innerHTML = '';
  users.forEach(user => {
    const li = document.createElement('li');
    li.textContent = user.name;
    const editBtn = document.createElement('button');
    editBtn.textContent = 'Modifier';
    editBtn.onclick = () => showEditForm(user);
    li.appendChild(editBtn);
    list.appendChild(li);
  });
}

function deleteUser(userId) {
  fetch(apiUrl + '/' + userId, {
    method: 'DELETE'
  })
    .then(() => {
      fetchUsers();
    });
}

document.getElementById('delete-user').onclick = function() {
  if (editUserId !== null) {
    deleteUser(editUserId);
    document.getElementById('edit-user-form').style.display = 'none';
  }
};

document.getElementById('add-user-form').onsubmit = function(e) {
  e.preventDefault();
  const name = document.getElementById('add-user-name').value;
  fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  })
    .then(() => {
      document.getElementById('add-user-name').value = '';
      fetchUsers();
    });
};

function showEditForm(user) {
  editUserId = user.id;
  document.getElementById('edit-user-name').value = user.name;
  document.getElementById('edit-user-form').style.display = 'block';
}

document.getElementById('edit-user-form').onsubmit = function(e) {
  e.preventDefault();
  const name = document.getElementById('edit-user-name').value;
  fetch(apiUrl + '/' + editUserId, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  })
    .then(() => {
      document.getElementById('edit-user-form').style.display = 'none';
      fetchUsers();
    });
};

document.getElementById('cancel-edit').onclick = function() {
  document.getElementById('edit-user-form').style.display = 'none';
};

fetchUsers();
