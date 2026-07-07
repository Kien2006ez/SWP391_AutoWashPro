// ============================================================
// login.js — AutoWash Pro
// Flow: Phone → Gửi OTP → Nhập OTP → Đăng nhập / Đăng ký
// ============================================================

const API = 'http://localhost:8000';

// ── Nếu đã đăng nhập rồi thì khỏi hiện lại trang login ─────────
// (đọc ?next= để biết quay lại trang nào, mặc định loyalty.html)
function getNextUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('next') || 'loyalty.html';
}

if (localStorage.getItem('aw_token')) {
    window.location.href = getNextUrl();
}

// ── Helpers ──────────────────────────────────────────────────
function validPhone(p) {
    return /^0[0-9]{9}$/.test(p.replace(/\s/g, ''));
}

function showAlert(msg, type = 'error') {
    const el = document.getElementById('alert-box');
    el.textContent = msg;
    el.className = 'alert-box ' + (type === 'ok' ? 'alert-ok' : 'alert-err');
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function clearAlert() {
    const el = document.getElementById('alert-box');
    if (el) { el.style.display = 'none'; el.textContent = ''; }
}

function setLoading(btnId, spinId, loading) {
    const btn  = document.getElementById(btnId);
    const spin = document.getElementById(spinId);
    if (!btn) return;
    btn.disabled = loading;
    if (spin) spin.style.display = loading ? 'inline-block' : 'none';
}

function setErr(id, show) {
    const el = document.getElementById(id);
    if (el) el.style.display = show ? 'block' : 'none';
}

// ── Tab switching ─────────────────────────────────────────────
function switchTab(tab) {
    clearAlert();
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById('tab-' + (tab === 'login' ? 'login' : 'reg')).classList.add('active');
    document.getElementById('panel-' + (tab === 'login' ? 'login' : 'reg')).classList.add('active');
}

// ============================================================
// ĐĂNG NHẬP — Bước 1: Gửi OTP
// ============================================================
document.getElementById('btn-send-otp')?.addEventListener('click', async () => {
    clearAlert();
    const phone = document.getElementById('l-phone').value.replace(/\s/g, '');
    if (!validPhone(phone)) {
        setErr('l-phone-err', true);
        return;
    }
    setErr('l-phone-err', false);
    setLoading('btn-send-otp', 'spin-otp', true);

    try {
        const res = await fetch(`${API}/api/auth/otp/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Gửi OTP thất bại');

        // Hiện bước 2
        document.getElementById('otp-section').style.display = 'block';
        document.getElementById('btn-login').style.display   = 'block';
        document.getElementById('btn-send-otp').style.display = 'none';
        document.getElementById('l-phone').disabled = true;
        showAlert(`Đã gửi OTP về ${phone}. Kiểm tra Terminal VS Code để lấy mã.`, 'ok');

    } catch(e) {
        showAlert(e.message);
    }

    setLoading('btn-send-otp', 'spin-otp', false);
});

// ── Reset về bước 1 (gửi lại OTP)
function resetOtpStep() {
    document.getElementById('otp-section').style.display  = 'none';
    document.getElementById('btn-login').style.display    = 'none';
    document.getElementById('btn-send-otp').style.display = 'block';
    document.getElementById('l-phone').disabled = false;
    document.getElementById('l-otp').value = '';
    clearAlert();
}

// ── Bước 2: Nhập OTP → Đăng nhập
document.getElementById('btn-login')?.addEventListener('click', async () => {
    clearAlert();
    const phone = document.getElementById('l-phone').value.replace(/\s/g, '');
    const otp   = document.getElementById('l-otp').value.trim();

    if (otp.length !== 6) {
        setErr('l-otp-err', true);
        return;
    }
    setErr('l-otp-err', false);
    setLoading('btn-login', 'spin-login', true);

    try {
        // Bước 1: Login lấy token
        const loginRes = await fetch(`${API}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone, otp_code: otp })
        });
        const loginData = await loginRes.json();
        if (!loginRes.ok) throw new Error(loginData.detail || 'OTP sai hoặc đã hết hạn');

        const token = loginData.access_token;

        // Bước 2: Lấy thông tin customer bằng token vừa nhận
        const meRes = await fetch(`${API}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        const meData = await meRes.json();
        if (!meRes.ok) throw new Error('Không lấy được thông tin tài khoản');

        // Lưu vào localStorage
        localStorage.setItem('aw_token', token);
        localStorage.setItem('aw_user', JSON.stringify(meData));

        showAlert(`Chào mừng ${meData.full_name}! 🎉`, 'ok');
        // Quay lại đúng trang khách đang muốn vào trước khi bị yêu cầu đăng nhập
        // (booking.html, loyalty.html...), thay vì luôn ép về loyalty.html
        setTimeout(() => { location.href = getNextUrl(); }, 800);

    } catch(e) {
        showAlert(e.message);
        setLoading('btn-login', 'spin-login', false);
    }
});

// ============================================================
// ĐĂNG KÝ — Bước 1: Gửi OTP
// ============================================================
document.getElementById('btn-send-otp-reg')?.addEventListener('click', async () => {
    clearAlert();
    const name  = document.getElementById('r-name').value.trim();
    const phone = document.getElementById('r-phone').value.replace(/\s/g, '');

    if (name.length < 2)  { setErr('r-name-err', true);  return; }
    if (!validPhone(phone)) { setErr('r-phone-err', true); return; }
    setErr('r-name-err', false);
    setErr('r-phone-err', false);

    setLoading('btn-send-otp-reg', 'spin-otp-reg', true);

    try {
        const res = await fetch(`${API}/api/auth/otp/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Gửi OTP thất bại');

        document.getElementById('otp-section-reg').style.display = 'block';
        document.getElementById('btn-reg').style.display         = 'block';
        document.getElementById('btn-send-otp-reg').style.display = 'none';
        document.getElementById('r-phone').disabled = true;
        document.getElementById('r-name').disabled  = true;
        showAlert(`Đã gửi OTP về ${phone}. Kiểm tra Terminal VS Code.`, 'ok');

    } catch(e) {
        showAlert(e.message);
    }

    setLoading('btn-send-otp-reg', 'spin-otp-reg', false);
});

// ── Bước 2: Nhập OTP → Tạo tài khoản
document.getElementById('btn-reg')?.addEventListener('click', async () => {
    clearAlert();
    const name  = document.getElementById('r-name').value.trim();
    const phone = document.getElementById('r-phone').value.replace(/\s/g, '');
    const otp   = document.getElementById('r-otp').value.trim();
    const plate = document.getElementById('r-plate').value.trim();
    const vtype = document.getElementById('r-vtype').value;

    if (otp.length !== 6) { setErr('r-otp-err', true); return; }
    setErr('r-otp-err', false);

    setLoading('btn-reg', 'spin-reg', true);

    try {
        // Đăng ký tài khoản
        const regRes = await fetch(`${API}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone_number: phone,
                otp_code:     otp,
                full_name:    name
            })
        });
        const regData = await regRes.json();
        if (!regRes.ok) throw new Error(regData.detail || 'Đăng ký thất bại');

        // Tự động login sau khi đăng ký
        // Request OTP mới để login
        await fetch(`${API}/api/auth/otp/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone })
        });

        showAlert('Đăng ký thành công! Đang chuyển sang đăng nhập...', 'ok');

        // Chuyển sang tab login với số điện thoại đã điền sẵn
        setTimeout(() => {
            switchTab('login');
            document.getElementById('l-phone').value = phone;
            showAlert('Vui lòng nhập OTP mới để đăng nhập. Kiểm tra Terminal VS Code.', 'ok');
            // Hiện bước 2 luôn
            document.getElementById('otp-section').style.display = 'block';
            document.getElementById('btn-login').style.display   = 'block';
            document.getElementById('btn-send-otp').style.display = 'none';
            document.getElementById('l-phone').disabled = true;
        }, 1500);

    } catch(e) {
        showAlert(e.message);
        setLoading('btn-reg', 'spin-reg', false);
    }
});

// ── Thêm biển số xe sau khi đăng ký (nếu có điền)
async function addVehicleAfterRegister(token, plate, vtype) {
    if (!plate) return;
    try {
        await fetch(`${API}/api/customers/me/vehicles`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                license_plate: plate,
                vehicle_type:  vtype || 'scooter',
                is_primary:    true
            })
        });
    } catch(e) {
        console.log('Thêm xe thất bại (không ảnh hưởng đăng ký):', e);
    }
}

// ── Eye button toggle password (giữ lại nếu có)
document.querySelectorAll('.eye-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.target);
        if (!target) return;
        target.type = target.type === 'password' ? 'text' : 'password';
        btn.textContent = target.type === 'password' ? '👁' : '🙈';
    });
});