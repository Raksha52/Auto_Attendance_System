// Simple storage helpers
function loadUsers() {
	try {
		const raw = localStorage.getItem('users');
		return raw ? JSON.parse(raw) : {};
	} catch {
		return {};
	}
}

function saveUsers(users) {
	localStorage.setItem('users', JSON.stringify(users));
}

function navigateTo(path) {
	window.location.href = path;
}

class BasePage {
	constructor() {}
	init() {}
}

export class RegistrationPage extends BasePage {
	init() {
		const form = document.getElementById('regForm');
		const nameEl = document.getElementById('regName');
		const idEl = document.getElementById('regId');
		const passEl = document.getElementById('regPassword');
		const roleEl = document.getElementById('regRole');
		const msg = document.getElementById('regMsg');
		const toLogin = document.getElementById('toLogin');

		form?.addEventListener('submit', (e) => {
			e.preventDefault();
			const name = nameEl.value.trim();
			const id = idEl.value.trim();
			const pwd = passEl.value;
			const role = roleEl.value;
			if (!name || !id || !pwd) { msg.textContent = 'All fields are required.'; return; }
			const users = loadUsers();
			if (users[id]) { msg.textContent = 'ID already registered.'; return; }
			users[id] = { id, name, password: pwd, role };
			saveUsers(users);
			msg.textContent = 'Registration successful. Proceed to login.';
		});

		toLogin?.addEventListener('click', () => navigateTo('login.html'));
	}
}

export class LoginPage extends BasePage {
	init() {
		const form = document.getElementById('loginForm');
		const idEl = document.getElementById('identifier');
		const passEl = document.getElementById('password');
		const msg = document.getElementById('msg');
		const toRegister = document.getElementById('toRegister');

		form?.addEventListener('submit', (e) => {
			e.preventDefault();
			const id = idEl.value.trim();
			const pwd = passEl.value;
			const users = loadUsers();
			const u = users[id];
			if (!u || u.password !== pwd) { msg.textContent = 'Invalid ID or password.'; return; }
			localStorage.setItem('currentUser', JSON.stringify({ id: u.id, name: u.name, role: u.role }));
			const target = u.role === 'teacher' ? 'teacher.html' : (u.role === 'admin' ? 'admin.html' : 'student.html');
			navigateTo(target);
		});

		toRegister?.addEventListener('click', () => navigateTo('registration.html'));
	}
}

export class StudentPage extends BasePage {
	init() {
		document.getElementById('backLogin')?.addEventListener('click', () => navigateTo('login.html'));
	}
}

export class TeacherPage extends BasePage {
	init() {
		document.getElementById('backLogin')?.addEventListener('click', () => navigateTo('login.html'));
	}
}

export class AdminPage extends BasePage {
	init() {
		document.getElementById('backLogin')?.addEventListener('click', () => navigateTo('login.html'));
	}
}


