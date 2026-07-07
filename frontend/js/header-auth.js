// ============================================================
// header-auth.js — Đồng bộ trạng thái đăng nhập trên header
// Dùng chung cho MỌI trang khách hàng (index, booking, loyalty,
// stores, service, aboutus) để tránh lặp code như cách admin
// đang lặp doLogout() ở từng file.
//
// Yêu cầu: load file này SAU js/api.js, và header phải có:
//   <div class="header-auth" id="header-auth-wrap">
//       <a href="login.html" id="header-auth-btn" class="booking-btn">
//           Đăng Nhập <i class="fa-solid fa-arrow-right"></i>
//       </a>
//   </div>
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    const wrap = document.getElementById('header-auth-wrap');
    const btn  = document.getElementById('header-auth-btn');
    if (!wrap || !btn) return;

    const token = typeof getToken === 'function'
        ? getToken()
        : localStorage.getItem('aw_token');
    const user = typeof getUser === 'function'
        ? getUser()
        : JSON.parse(localStorage.getItem('aw_user') || 'null');

    // Chưa đăng nhập → giữ nguyên nút "Đăng Nhập" mặc định, không làm gì thêm
    if (!token || !user) return;

    // Đã đăng nhập → đổi nút thành tên khách hàng, trỏ tới trang Thành Viên
    btn.href = 'loyalty.html';
    btn.innerHTML = `<i class="fa-solid fa-user"></i> ${user.full_name || 'Tài khoản'}`;

    // Thêm nút Đăng xuất (chỉ thêm 1 lần, tránh lặp nếu script chạy lại)
    if (!document.getElementById('header-logout-btn')) {
        const logoutBtn = document.createElement('a');
        logoutBtn.href = '#';
        logoutBtn.id = 'header-logout-btn';
        logoutBtn.className = 'header-logout-btn';
        logoutBtn.title = 'Đăng xuất';
        logoutBtn.innerHTML = '<i class="fa-solid fa-right-from-bracket"></i>';
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Bạn có chắc muốn đăng xuất?')) {
                // logout() được định nghĩa sẵn trong api.js:
                // xoá aw_token + aw_user rồi chuyển về login.html
                logout();
            }
        });
        wrap.appendChild(logoutBtn);
    }
});