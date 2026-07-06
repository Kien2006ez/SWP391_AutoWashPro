// ============================================================
// api.js — Kết nối Frontend với Backend AutoWash Pro
// Tất cả trang đều import file này
// URL backend: http://localhost:8000
// ============================================================

const API_BASE = 'http://localhost:8000';

// ── Lấy token từ localStorage ────────────────────────────────
function getToken() {
    return localStorage.getItem('aw_token');
}

// ── Header mặc định cho mọi request cần auth ────────────────
function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
    };
}

// ── Xử lý lỗi chung ─────────────────────────────────────────
async function handleResponse(res) {
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || 'Có lỗi xảy ra');
    }
    return data;
}

// ════════════════════════════════════════════════════════════
// AUTH APIs
// ════════════════════════════════════════════════════════════

// Bước 1: Yêu cầu OTP (dùng cho cả đăng ký và đăng nhập)
async function requestOtp(phone_number) {
    const res = await fetch(`${API_BASE}/api/auth/otp/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number })
    });
    return handleResponse(res);
}

// Bước 2: Đăng ký
async function register(phone_number, otp_code, full_name, date_of_birth = null) {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number, otp_code, full_name, date_of_birth })
    });
    return handleResponse(res);
}

// Bước 2: Đăng nhập
async function login(phone_number, otp_code) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number, otp_code })
    });
    return handleResponse(res);
}

// Lấy thông tin bản thân
async function getMe() {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

// ════════════════════════════════════════════════════════════
// BOOKING APIs
// ════════════════════════════════════════════════════════════

// Lấy slot còn trống theo ngày
async function getAvailableSlots(date) {
    const res = await fetch(
        `${API_BASE}/api/bookings/available-slots?target_date=${date}`,
        { headers: authHeaders() }
    );
    return handleResponse(res);
}

// Tạo booking mới
async function createBooking(vehicle_id, booking_date, time_slot, service_type) {
    const res = await fetch(`${API_BASE}/api/bookings`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ vehicle_id, booking_date, time_slot, service_type })
    });
    return handleResponse(res);
}

// Xem lịch sắp tới
async function getUpcomingBookings() {
    const res = await fetch(`${API_BASE}/api/bookings/upcoming`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

// Xem lịch sử rửa xe
async function getWashHistory() {
    const res = await fetch(`${API_BASE}/api/bookings/history`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

// Hủy booking
async function cancelBooking(booking_id) {
    const res = await fetch(`${API_BASE}/api/bookings/${booking_id}/cancel`, {
        method: 'PATCH',
        headers: authHeaders()
    });
    return handleResponse(res);
}

// ════════════════════════════════════════════════════════════
// LOYALTY APIs
// ════════════════════════════════════════════════════════════

// Lịch sử điểm
async function getPointHistory() {
    const res = await fetch(`${API_BASE}/api/loyalty/points`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

// Đổi điểm
async function redeemPoints(points_cost, reward_description) {
    const res = await fetch(`${API_BASE}/api/loyalty/redeem`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ points_cost, reward_description })
    });
    return handleResponse(res);
}

// Xem promotions đang áp dụng cho tier của mình
async function getMyPromotions() {
    const res = await fetch(`${API_BASE}/api/admin/promotions/my-promotions`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

// ════════════════════════════════════════════════════════════
// VEHICLES APIs
// ════════════════════════════════════════════════════════════

async function getVehicles() {
    const res = await fetch(`${API_BASE}/api/customers/me/vehicles`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

async function addVehicle(license_plate, vehicle_type, brand) {
    const res = await fetch(`${API_BASE}/api/customers/me/vehicles`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ license_plate, vehicle_type, brand })
    });
    return handleResponse(res);
}

// ════════════════════════════════════════════════════════════
// SESSION HELPERS
// ════════════════════════════════════════════════════════════

function saveSession(token, user) {
    localStorage.setItem('aw_token', token);
    localStorage.setItem('aw_user', JSON.stringify(user));
}

function getUser() {
    const u = localStorage.getItem('aw_user');
    return u ? JSON.parse(u) : null;
}

function logout() {
    localStorage.removeItem('aw_token');
    localStorage.removeItem('aw_user');
    window.location.href = 'login.html';
}

function requireLogin() {
    if (!getToken()) {
        window.location.href = 'login.html?next=' + encodeURIComponent(location.href);
    }
}