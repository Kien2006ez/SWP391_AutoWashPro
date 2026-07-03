// ============================================================
// AutoWash Pro — js/loyalty.js
// Trang Khách Hàng Thân Thiết: điểm, hạng, đổi thưởng, lịch sử
// ============================================================

// ── Cấu hình hạng thành viên (đồng bộ với backend: models/customer.py) ──
const TIER_CONFIG = {
    member: {
        key: 'member', name: 'Member', color: '#94a3b8', icon: 'fa-id-card',
        bookingWindowDays: 7, pointMultiplier: 1.0, minPoints3m: 0,
        birthdayBonus: 0, freeWashPerMonth: 0, priorityLabel: 'Tiêu chuẩn',
    },
    silver: {
        key: 'silver', name: 'Silver', color: '#8ea0b3', icon: 'fa-medal',
        bookingWindowDays: 10, pointMultiplier: 1.2, minPoints3m: 500,
        birthdayBonus: 100, freeWashPerMonth: 0, priorityLabel: 'Ưu tiên khá',
    },
    gold: {
        key: 'gold', name: 'Gold', color: '#e0a72e', icon: 'fa-trophy',
        bookingWindowDays: 12, pointMultiplier: 1.5, minPoints3m: 1500,
        birthdayBonus: 200, freeWashPerMonth: 1, priorityLabel: 'Ưu tiên cao',
    },
    platinum: {
        key: 'platinum', name: 'Platinum', color: '#a78bfa', icon: 'fa-crown',
        bookingWindowDays: 14, pointMultiplier: 2.0, minPoints3m: 3000,
        birthdayBonus: 500, freeWashPerMonth: 2, priorityLabel: 'Ưu tiên cao nhất',
    },
};
const TIER_ORDER = ['member', 'silver', 'gold', 'platinum'];

// Danh sách quyền lợi hiển thị trên thẻ hạng (tier-card)
function tierPerksList(cfg) {
    const perks = [
        `Đặt lịch trước tối đa <strong>${cfg.bookingWindowDays} ngày</strong>`,
        `${cfg.priorityLabel} trong hàng chờ`,
        `Nhân điểm x${cfg.pointMultiplier.toFixed(1)} mỗi lần rửa xe`,
    ];
    if (cfg.freeWashPerMonth > 0) perks.push(`${cfg.freeWashPerMonth} lượt rửa xe miễn phí / tháng`);
    if (cfg.birthdayBonus > 0) perks.push(`Tặng ${cfg.birthdayBonus} điểm vào sinh nhật`);
    return perks;
}

// ── Các gói đổi điểm (Redemption) ──
const REDEMPTION_OPTIONS = [
    { id: 'r_disc50',  icon: 'fa-tag',        title: 'Giảm 50.000đ',           cost: 500,  type: 'Discount' },
    { id: 'r_disc100', icon: 'fa-tags',       title: 'Giảm 100.000đ',          cost: 1000, type: 'Discount' },
    { id: 'r_freewash',icon: 'fa-car',        title: 'Rửa xe miễn phí',        cost: 1500, type: 'FreeWash' },
    { id: 'r_addon',   icon: 'fa-spray-can',  title: 'Vệ sinh nội thất miễn phí', cost: 1200, type: 'AddOn' },
];

document.addEventListener('DOMContentLoaded', () => {

    // ── 1. Kiểm tra đăng nhập ──────────────────────────────
    const token = localStorage.getItem('aw_token');
    if (!token) {
        location.href = 'login.html?next=' + encodeURIComponent('loyalty.html');
        return;
    }

    let user = JSON.parse(localStorage.getItem('aw_user') || '{}');
    // Chuẩn hoá dữ liệu demo nếu thiếu field (tài khoản cũ / mới đăng ký)
    user.tier         = user.tier || 'member';
    user.points       = user.points ?? 0;
    user.monthlySpend = user.monthlySpend ?? 0;
    user.visitCount   = user.visitCount ?? 0;

    document.getElementById('header-auth-btn').innerHTML =
        `<i class="fa-solid fa-user"></i> ${user.fullName || 'Tài khoản'}`;
    document.getElementById('header-auth-btn').href = 'loyalty.html';

    // ── 2. API layer ───────────────────────────────────────
    // Thay các hàm fake bên dưới bằng fetch thật khi backend sẵn sàng
    // (loyalty router: GET /v1/loyalty/me, GET /v1/loyalty/history, POST /v1/loyalty/redeem)

    async function apiGetLoyaltyProfile() {
        //const res = await fetch('https://api.autowashpro.vn/v1/loyalty/me', {
        //     headers: { Authorization: `Bearer ${token}` }
        // });
        // return res.json();

        // ── Fake (demo) ──
        await new Promise(r => setTimeout(r, 300));
        return { ...user };
    }

    async function apiGetHistory() {
        // const res = await fetch('https://api.autowashpro.vn/v1/loyalty/history', {
        //     headers: { Authorization: `Bearer ${token}` }
        // });
        // return res.json();

        // ── Fake (demo) — dữ liệu mẫu ──
        await new Promise(r => setTimeout(r, 300));
        const today = new Date();
        const daysAgo = n => new Date(today.getTime() - n * 86400000).toISOString().split('T')[0];
        const monthsFromNow = n => new Date(today.getFullYear(), today.getMonth() + n, today.getDate())
            .toISOString().split('T')[0];

        return {
            washHistory: [
                { date: daysAgo(3),  plate: '30A-123.45', service: 'Rửa Xe + Phủ Ceramic', amount: 450000, pointsEarned: 45, status: 'completed' },
                { date: daysAgo(15), plate: '30A-123.45', service: 'Rửa Xe Tiêu Chuẩn',      amount: 150000, pointsEarned: 15, status: 'completed' },
                { date: daysAgo(28), plate: '30A-123.45', service: 'Vệ Sinh Nội Thất',       amount: 250000, pointsEarned: 25, status: 'completed' },
                { date: daysAgo(1),  plate: '30A-123.45', service: 'Rửa Xe + Hút Bụi',       amount: 200000, pointsEarned: 0,  status: 'pending' },
            ],
            pointsHistory: [
                { date: daysAgo(3),  type: 'Earn',   delta: +45,  balanceAfter: user.points,        expiry: monthsFromNow(12), note: 'Rửa xe #AWP-118' },
                { date: daysAgo(15), type: 'Earn',   delta: +15,  balanceAfter: user.points - 45,    expiry: monthsFromNow(11), note: 'Rửa xe #AWP-104' },
                { date: daysAgo(28), type: 'Earn',   delta: +25,  balanceAfter: user.points - 60,    expiry: monthsFromNow(10), note: 'Rửa xe #AWP-091' },
                { date: daysAgo(60), type: 'Bonus',  delta: +100, balanceAfter: user.points - 85,    expiry: monthsFromNow(8),  note: 'Chúc mừng lên hạng Silver' },
                { date: daysAgo(90), type: 'Redeem', delta: -500, balanceAfter: user.points - 185,   expiry: null,              note: 'Đổi voucher giảm 50.000đ' },
            ],
        };
    }

    async function apiRedeemPoints(option) {
        // const res = await fetch('https://api.autowashpro.vn/v1/loyalty/redeem', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        //     body: JSON.stringify({ optionId: option.id })
        // });
        // if (!res.ok) throw new Error((await res.json()).message);
        // return res.json();

        // ── Fake (demo) ──
        await new Promise(r => setTimeout(r, 500));
        if (user.points < option.cost) throw new Error('Bạn không đủ điểm để đổi ưu đãi này.');
        user.points -= option.cost;
        localStorage.setItem('aw_user', JSON.stringify(user));
        return { success: true, newBalance: user.points };
    }

    // ── 3. Render: Hero / Tier badge / Progress ─────────────
    function renderHero(profile) {
        document.getElementById('loy-username').textContent = profile.fullName || 'Khách hàng';
        document.getElementById('loy-points-balance').textContent = profile.points.toLocaleString('vi-VN');
        document.getElementById('loy-spent-3m').textContent = profile.monthlySpend.toLocaleString('vi-VN') + 'đ';
        document.getElementById('loy-visit-count').textContent = profile.visitCount;

        const cfg = TIER_CONFIG[profile.tier] || TIER_CONFIG.member;
        const card = document.getElementById('tier-badge-card');
        card.style.setProperty('--tier-color', cfg.color);
        document.getElementById('tier-badge-name').textContent = cfg.name;
        card.querySelector('.tier-badge-icon i').className = `fa-solid ${cfg.icon}`;

        // Tiến độ lên hạng tiếp theo dựa trên chi tiêu 3 tháng
        const idx = TIER_ORDER.indexOf(cfg.key);
        const fill = document.getElementById('tier-progress-fill');
        const text = document.getElementById('tier-progress-text');

        if (idx === TIER_ORDER.length - 1) {
            fill.style.width = '100%';
            text.textContent = 'Bạn đang ở hạng cao nhất — Platinum 🎉';
        } else {
            const nextCfg = TIER_CONFIG[TIER_ORDER[idx + 1]];
            const curMin  = cfg.minPoints3m;
            const nextMin = nextCfg.minPoints3m;
            const progress = Math.min(100, Math.max(0,
                ((profile.monthlySpend / 1000 - curMin) / (nextMin - curMin)) * 100
            ));
            // Ghi chú: demo quy đổi tạm 1.000đ chi tiêu ≈ 1 điểm xếp hạng, thay bằng field thật khi có API
            fill.style.width = `${isFinite(progress) ? progress : 0}%`;
            const remain = Math.max(0, nextMin - Math.round(profile.monthlySpend / 1000));
            text.innerHTML = remain > 0
                ? `Còn thiếu <strong>${remain.toLocaleString('vi-VN')} điểm chi tiêu</strong> (3 tháng gần nhất) để lên hạng ${nextCfg.name}`
                : `Đủ điều kiện lên hạng ${nextCfg.name} — hạng sẽ cập nhật vào kỳ đánh giá tháng tới`;
        }
    }

    // ── 4. Render: Bảng hạng & quyền lợi ─────────────────────
    function renderTierCards(currentTierKey) {
        const grid = document.getElementById('tiers-grid');
        grid.innerHTML = TIER_ORDER.map(key => {
            const cfg = TIER_CONFIG[key];
            const isCurrent = key === currentTierKey;
            return `
                <div class="tier-card ${isCurrent ? 'current' : ''}" style="--tier-color:${cfg.color}">
                    <div class="tier-card-name">${cfg.name}</div>
                    <div class="tier-card-req">${cfg.minPoints3m === 0 ? 'Không yêu cầu' : `Từ ${cfg.minPoints3m.toLocaleString('vi-VN')} điểm chi tiêu / 3 tháng`}</div>
                    <ul>
                        ${tierPerksList(cfg).map(p => `<li><i class="fa-solid fa-check"></i> ${p}</li>`).join('')}
                    </ul>
                </div>`;
        }).join('');
    }

    // ── 5. Render: Đổi điểm thưởng ────────────────────────────
    function renderRedeemGrid(points) {
        const grid = document.getElementById('redeem-grid');
        grid.innerHTML = REDEMPTION_OPTIONS.map(opt => `
            <div class="redeem-card">
                <div class="redeem-icon"><i class="fa-solid ${opt.icon}"></i></div>
                <div class="redeem-title">${opt.title}</div>
                <div class="redeem-cost">${opt.cost.toLocaleString('vi-VN')} điểm</div>
                <button class="redeem-btn" data-id="${opt.id}" ${points < opt.cost ? 'disabled' : ''}>
                    ${points < opt.cost ? 'Không đủ điểm' : 'Đổi ngay'}
                </button>
            </div>`).join('');

        grid.querySelectorAll('.redeem-btn').forEach(btn => {
            btn.addEventListener('click', () => handleRedeem(btn.dataset.id));
        });
    }

    async function handleRedeem(optionId) {
        const option = REDEMPTION_OPTIONS.find(o => o.id === optionId);
        if (!option) return;
        if (!confirm(`Đổi ${option.cost.toLocaleString('vi-VN')} điểm lấy "${option.title}"?`)) return;

        try {
            const result = await apiRedeemPoints(option);
            alert(`Đổi thưởng thành công! Điểm còn lại: ${result.newBalance.toLocaleString('vi-VN')}`);
            const profile = await apiGetLoyaltyProfile();
            renderHero(profile);
            renderRedeemGrid(profile.points);
        } catch (e) {
            alert(e.message || 'Đổi thưởng thất bại, vui lòng thử lại.');
        }
    }

    // ── 6. Render: Lịch sử rửa xe / điểm ──────────────────────
    const STATUS_LABEL = { completed: 'Đã hoàn thành', pending: 'Đang xử lý', cancelled: 'Đã huỷ' };
    const TX_LABEL = { Earn: 'Tích điểm', Redeem: 'Đổi thưởng', Expire: 'Hết hạn', Bonus: 'Thưởng', Adjust: 'Điều chỉnh' };
    const TX_CLASS = { Earn: 'pts-earn', Redeem: 'pts-redeem', Expire: 'pts-expire', Bonus: 'pts-bonus', Adjust: '' };

    function renderWashHistory(rows) {
        document.getElementById('wash-history-body').innerHTML = rows.map(r => `
            <tr>
                <td>${r.date}</td>
                <td>${r.plate}</td>
                <td>${r.service}</td>
                <td>${r.amount.toLocaleString('vi-VN')}đ</td>
                <td>${r.pointsEarned > 0 ? '+' + r.pointsEarned : '—'}</td>
                <td><span class="status-pill status-${r.status}">${STATUS_LABEL[r.status]}</span></td>
            </tr>`).join('');
    }

    function renderPointsHistory(rows) {
        document.getElementById('points-history-body').innerHTML = rows.map(r => `
            <tr>
                <td>${r.date}</td>
                <td>${TX_LABEL[r.type]}</td>
                <td class="${TX_CLASS[r.type]}">${r.delta > 0 ? '+' + r.delta : r.delta}</td>
                <td>${r.balanceAfter.toLocaleString('vi-VN')}</td>
                <td>${r.expiry || '—'}</td>
                <td>${r.note}</td>
            </tr>`).join('');

        // Banner cảnh báo điểm sắp hết hạn trong 30 ngày tới
        const soon = rows.filter(r => r.type === 'Earn' && r.expiry &&
            (new Date(r.expiry) - new Date()) / 86400000 <= 30);
        if (soon.length > 0) {
            const totalExpiring = soon.reduce((s, r) => s + r.delta, 0);
            document.getElementById('expiry-banner-text').textContent =
                `Bạn có ${totalExpiring.toLocaleString('vi-VN')} điểm sắp hết hạn trong 30 ngày tới (điểm hết hạn sau 12 tháng kể từ ngày tích). Hãy đổi thưởng trước khi điểm bị mất!`;
            document.getElementById('expiry-banner').style.display = 'block';
        }
    }

    // ── 7. Tabs ────────────────────────────────────────────
    document.querySelectorAll('.history-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.history-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.history-panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`panel-${tab.dataset.tab}`).classList.add('active');
        });
    });

    // ── 8. Khởi chạy ───────────────────────────────────────
    (async function init() {
        const profile = await apiGetLoyaltyProfile();
        renderHero(profile);
        renderTierCards(profile.tier);
        renderRedeemGrid(profile.points);

        const { washHistory, pointsHistory } = await apiGetHistory();
        renderWashHistory(washHistory);
        renderPointsHistory(pointsHistory);
    })();
});