class BasePage {
	constructor(id) {
		this.root = document.getElementById(id);
	}
	show() { this.root.classList.remove('hidden'); }
	hide() { this.root.classList.add('hidden'); }
	mount() {}
	unmount() {}
}

class LoginPage extends BasePage {
	constructor(controller) {
		super('frame-login');
		this.controller = controller;
		this.btn = null;
	}
	mount() {
		this.btn = document.getElementById('btnLogin');
		this.btn.addEventListener('click', this.onLogin);
	}
	unmount() {
		this.btn && this.btn.removeEventListener('click', this.onLogin);
	}
	onLogin = () => {
		const identifier = document.getElementById('loginIdentifier').value.trim();
		const role = document.querySelector('input[name="role"]:checked')?.value || 'student';
		this.controller.setSession({ id: identifier || 'guest', role });
		if (role === 'teacher') this.controller.navigate('teacher');
		else if (role === 'admin') this.controller.navigate('admin');
		else this.controller.navigate('student');
	};
}

class StudentPage extends BasePage {
	constructor(controller) { super('frame-student'); this.controller = controller; }
	mount() {
		document.getElementById('btnStudentBack').addEventListener('click', () => this.controller.navigate('login'));
	}
}

class TeacherPage extends BasePage {
	constructor(controller) { super('frame-teacher'); this.controller = controller; }
	mount() {
		document.getElementById('btnTeacherBack').addEventListener('click', () => this.controller.navigate('login'));
	}
}

class AdminPage extends BasePage {
	constructor(controller) { super('frame-admin'); this.controller = controller; }
	mount() {
		document.getElementById('btnAdminBack').addEventListener('click', () => this.controller.navigate('login'));
	}
}

class AppController {
	constructor() {
		this.pages = {
			login: new LoginPage(this),
			student: new StudentPage(this),
			teacher: new TeacherPage(this),
			admin: new AdminPage(this)
		};
		this.current = null;
		this.session = null;
		this._wireNav();
	}
	_wireNav(){
		document.getElementById('navLogin').addEventListener('click', (e)=>{ e.preventDefault(); this.navigate('login');});
		document.getElementById('navStudent').addEventListener('click', (e)=>{ e.preventDefault(); this.navigate('student');});
		document.getElementById('navTeacher').addEventListener('click', (e)=>{ e.preventDefault(); this.navigate('teacher');});
		document.getElementById('navAdmin').addEventListener('click', (e)=>{ e.preventDefault(); this.navigate('admin');});
	}
	setSession(sess){ this.session = sess; try { localStorage.setItem('session', JSON.stringify(sess)); } catch {} }
	getSession(){ if (this.session) return this.session; try { return JSON.parse(localStorage.getItem('session')||'null'); } catch { return null; } }
	navigate(name) {
		if (!this.pages[name]) name = 'login';
		if (this.current) { this.pages[this.current].unmount(); this.pages[this.current].hide(); }
		this.current = name;
		this.pages[name].show();
		this.pages[name].mount();
		history.replaceState({}, '', `#${name}`);
	}
	start() {
		const initial = (location.hash||'').replace('#','') || 'login';
		this.navigate(initial);
	}
}

window.addEventListener('DOMContentLoaded', () => {
	const app = new AppController();
	app.start();
});
