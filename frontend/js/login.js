// ============================================================
// AutoWash Pro — js/login.js
// ============================================================

document.addEventListener('DOMContentLoaded', () => {

    // Nếu đã đăng nhập → về trang chủ
    if (localStorage.getItem('aw_token')) {
        const next = new URLSearchParams(location.search).get('next');
        location.href = next ? decodeURIComponent(next) : 'index.html';
        return;
    }

    // Đọc ?tab=register từ URL
    const urlTab = new URLSearchParams(location.search).get('tab');
    if (urlTab === 'register') switchTab('register');

    // ── Elements ───────────────────────────────────────────
    const alertBox  = document.getElementById('alert-box');
    const btnLogin  = document.getElementById('btn-login');
    const btnReg    = document.getElementById('btn-reg');
    const spinLogin = document.getElementById('spin-login');
    const spinReg   = document.getElementById('spin-reg');

    // ── Tab switch ─────────────────────────────────────────
    window.switchTab = function (tab) {
        const isLogin = tab === 'login';
        document.getElementById('tab-login').classList.toggle('active',  isLogin);
        document.getElementById('tab-reg').classList.toggle('active',   !isLogin);
        document.getElementById('panel-login').classList.toggle('active', isLogin);
        document.getElementById('panel-reg').classList.toggle('active', !isLogin);
        clearAlert();
    };

    document.getElementById('tab-login').addEventListener('click', () => switchTab('login'));
    document.getElementById('tab-reg').addEventListener('click',   () => switchTab('register'));

    // ── Alert ──────────────────────────────────────────────
    function showAlert(msg, type = 'err') {
        alertBox.textContent = msg;
        alertBox.className   = `alert-box show ${type}`;
    }
    function clearAlert() {
        alertBox.className   = 'alert-box';
        alertBox.textContent = '';
    }

    // ── Field helpers ──────────────────────────────────────
    function setErr(id, show) {
        const el = document.getElementById(id);
        if (el) el.className = 'ferr' + (show ? ' show' : '');
    }
    function markInput(id, valid) {
        const el = document.getElementById(id);
        if (!el) return;
        el.classList.toggle('err', !valid);
        el.classList.toggle('ok',   valid && el.value.length > 0);
    }

    // ── Validators ─────────────────────────────────────────
    const validPhone = v => /^0[3-9][0-9]{8}$/.test(v.replace(/\s/g, ''));
    const validPw    = v => v.length >= 6;
    const validName  = v => v.trim().length >= 2;

    // ── Eye toggle ─────────────────────────────────────────
    document.querySelectorAll('.eye-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const inp = document.getElementById(btn.dataset.target);
            if (!inp) return;
            inp.type        = inp.type === 'password' ? 'text' : 'password';
            btn.textContent = inp.type === 'password' ? '👁' : '🙈';
        });
    });

    // ── Password strength ──────────────────────────────────
    document.getElementById('r-pw')?.addEventListener('input', e => {
        const pw = e.target.value;
        let score = 0;
        if (pw.length >= 8)           score++;
        if (/[A-Z]/.test(pw))        score++;
        if (/[0-9]/.test(pw))        score++;
        if (/[^A-Za-z0-9]/.test(pw)) score++;
        const cfg = [
            { w: '0%',   bg: 'transparent', label: '' },
            { w: '25%',  bg: '#EF4444',     label: 'Yếu' },
            { w: '55%',  bg: '#F97316',     label: 'Trung bình' },
            { w: '80%',  bg: '#3B82F6',     label: 'Khá mạnh' },
            { w: '100%', bg: '#16A34A',     label: 'Mạnh' },
        ][score];
        const bar  = document.getElementById('pw-bar');
        const hint = document.getElementById('pw-hint');
        if (bar)  { bar.style.width = cfg.w; bar.style.background = cfg.bg; }
        if (hint) hint.textContent = cfg.label;
    });

    // ── Live blur validation ───────────────────────────────
    [
        ['l-phone', 'l-phone-err', validPhone],
        ['l-pw',    'l-pw-err',    validPw],
        ['r-name',  'r-name-err',  validName],
        ['r-phone', 'r-phone-err', validPhone],
        ['r-pw',    'r-pw-err',    validPw],
    ].forEach(([id, errId, fn]) => {
        document.getElementById(id)?.addEventListener('blur', () => {
            const el = document.getElementById(id);
            const v  = fn(el.value);
            setErr(errId, !v);
            markInput(id, v);
        });
    });

    // ── Loading state ──────────────────────────────────────
    function setLoading(btnEl, spinEl, on, label = '') {
        btnEl.disabled = on;
        btnEl.querySelector('.btn-text').textContent = on ? 'Đang xử lý...' : label;
        spinEl.className = on ? 'btn-spin show' : 'btn-spin';
    }

    // ── Save session ───────────────────────────────────────
    function saveSession(data) {
        localStorage.setItem('aw_token',  data.token);
        localStorage.setItem('aw_user',   JSON.stringify(data.user));
        localStorage.setItem('aw_expire', (Date.now() + (data.expiresIn || 86400) * 1000).toString());
    }

    // ── API calls ──────────────────────────────────────────
    // Thay 2 hàm fake bên dưới bằng fetch thật khi có backend

    async function apiLogin(phone, password) {
        // ── Thật: bỏ comment dưới đây, xoá phần fake ──
        // const res  = await fetch('https://api.autowashpro.vn/v1/auth/login', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ phone, password })
        // });
        // const data = await res.json();
        // if (!res.ok) throw new Error(data.message || 'Đăng nhập thất bại');
        // return data;

        // ── Fake (demo) ──
        await new Promise(r => setTimeout(r, 900));
        if (phone === '0000000000') throw new Error('Số điện thoại chưa được đăng ký.');
        return {
            token: 'demo_' + Date.now(),
            expiresIn: 86400,
            user: { fullName: 'Nguyễn Demo', phone, tier: 'gold', points: 1240, monthlySpend: 1800000 }
        };
    }

    async function apiRegister(payload) {
        // ── Thật ──
        // const res  = await fetch('https://api.autowashpro.vn/v1/auth/register', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(payload)
        // });
        // const data = await res.json();
        // if (!res.ok) throw new Error(data.message || 'Đăng ký thất bại');
        // return data;

        // ── Fake (demo) ──
    await new Promise(r => setTimeout(r, 1100));
        if (payload.phone === '0999999999') throw new Error('Số điện thoại đã được đăng ký.');
        return {
            token: 'demo_' + Date.now(),
            expiresIn: 86400,
            user: { fullName: payload.fullName, phone: payload.phone, tier: 'member', points: 0, monthlySpend: 0 }
        };
    }

    // ── ĐĂNG NHẬP ──────────────────────────────────────────
    btnLogin?.addEventListener('click', async () => {
        clearAlert();
        const phone = document.getElementById('l-phone').value.trim();
        const pw    = document.getElementById('l-pw').value;

        let ok = true;
        if (!validPhone(phone)) { setErr('l-phone-err', true);  markInput('l-phone', false); ok = false; }
        else                    { setErr('l-phone-err', false); markInput('l-phone', true); }
        if (!validPw(pw))       { setErr('l-pw-err', true);    markInput('l-pw', false);    ok = false; }
        else                    { setErr('l-pw-err', false);   markInput('l-pw', true); }
        if (!ok) return;

        setLoading(btnLogin, spinLogin, true);
        try {
            const data = await apiLogin(phone, pw);
            saveSession(data);

            if (document.getElementById('l-remember').checked)
                localStorage.setItem('aw_remember', phone);
            else
                localStorage.removeItem('aw_remember');

            showAlert(`Chào mừng trở lại, ${data.user.fullName}! 🎉`, 'ok');
            setTimeout(() => {
                const next = new URLSearchParams(location.search).get('next');
                location.href = next ? decodeURIComponent(next) : 'index.html';
            }, 900);
        } catch (e) {
            showAlert(e.message || 'Sai số điện thoại hoặc mật khẩu.');
            setLoading(btnLogin, spinLogin, false, 'Đăng nhập');
        }
    });

    // Điền lại số điện thoại đã ghi nhớ
    const remembered = localStorage.getItem('aw_remember');
    if (remembered) {
        const el = document.getElementById('l-phone');
        if (el) el.value = remembered;
        const rm = document.getElementById('l-remember');
        if (rm) rm.checked = true;
    }

// ── ĐĂNG KÝ ────────────────────────────────────────────
    btnReg?.addEventListener('click', async () => {
        clearAlert();
        const name  = document.getElementById('r-name').value.trim();
        const phone = document.getElementById('r-phone').value.trim();
        const pw    = document.getElementById('r-pw').value;
        const pw2   = document.getElementById('r-pw2').value;
        const plate = document.getElementById('r-plate').value.trim().toUpperCase();
        const vtype = document.getElementById('r-vtype').value;
        const terms = document.getElementById('r-terms').checked;

        let ok = true;

        // Validate từng field
        [
            [name,  validName,  'r-name',  'r-name-err'],
            [phone, validPhone, 'r-phone', 'r-phone-err'],
            [pw,    validPw,    'r-pw',    'r-pw-err'],
        ].forEach(([val, fn, inputId, errId]) => {
            const v = fn(val);
            setErr(errId, !v);
            markInput(inputId, v);
            if (!v) ok = false;
        });

        // Confirm password
        const pwMatch = pw === pw2 && pw.length > 0;
        setErr('r-pw2-err', !pwMatch);
        markInput('r-pw2', pwMatch);
        if (!pwMatch) ok = false;

        // Biển số (nếu có nhập)
        if (plate) {
            const plateOk = /^[0-9]{2}[A-Z]-?[0-9]{3}\.?[0-9]{2}$/i.test(plate)
                         || /^[0-9]{2}[A-Z][0-9]-?[0-9]{4,5}$/i.test(plate);
            setErr('r-plate-err', !plateOk);
            markInput('r-plate', plateOk);
            if (!plateOk) ok = false;
        }

        if (!terms) { showAlert('Vui lòng đồng ý với điều khoản sử dụng.'); return; }
        if (!ok)    return;

        setLoading(btnReg, spinReg, true);
        try {
            const payload = { fullName: name, phone, password: pw, vehicleType: vtype };
            if (plate) payload.licensePlate = plate;

            const data = await apiRegister(payload);
            saveSession(data);
            showAlert(`Đăng ký thành công! Chào mừng ${data.user.fullName} 🎉`, 'ok');
            setTimeout(() => { location.href = 'booking.html'; }, 1200);
        } catch (e) {
            showAlert(e.message || 'Đăng ký thất bại. Vui lòng thử lại.');
            setLoading(btnReg, spinReg, false, 'Tạo tài khoản');
        }
    });

    // ── Enter key ──────────────────────────────────────────
    document.addEventListener('keydown', e => {
        if (e.key !== 'Enter') return;
        if (document.getElementById('panel-login').classList.contains('active')) btnLogin?.click();
        else btnReg?.click();
    });
});