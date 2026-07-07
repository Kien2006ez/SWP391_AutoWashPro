// ════════════════════════════════════════════════════════════
// BOOKING FLOW — đã sửa lỗi:
// 1. SyntaxError: await trong function không async (nextStep)
// 2. Không kiểm tra đăng nhập trước khi cho làm form
// 3. Khung giờ tĩnh (07:00 sai, thiếu 12:00) → giờ lấy động từ backend
// 4. serviceMap chỉ map 3/6 dịch vụ, chỉ gửi dịch vụ đầu tiên
// 5. Luôn lấy vehicles[0] thay vì xe đúng theo biển số khách nhập,
//    và bỏ phí thông tin "size xe" đã thu ở bước 1
// ════════════════════════════════════════════════════════════

// Bắt buộc đăng nhập mới cho đặt lịch (trước đây thiếu, khiến khách
// điền hết 6 bước mới biết chưa đăng nhập)
requireLogin();

let currentStep = 1;
const totalSteps = 6;
const bookingData = {
    size: '',
    branch: '',
    services: [],
    date: '',
    time: '',
    name: '',
    phone: '',
    plate: ''
};

const sizeLabels = {
    small: 'Small — Sedan nhỏ',
    medium: 'Medium — SUV/CUV',
    large: 'Large — Full-size'
};

const branchLabels = {
    tanphu: 'CarWash Tân Phú',
    quan9: 'CarWash Quận 9',
    phunhuan: 'CarWash Phú Nhuận'
};

const serviceLabels = {
    ruaxe: 'Rửa Xe Ô Tô',
    noithat: 'Vệ Sinh Nội Thất',
    khoangmay: 'Vệ Sinh Khoang Máy',
    danhbong: 'Đánh Bóng Xe',
    ceramic: 'Phủ Ceramic',
    danlanh: 'Vệ Sinh Dàn Lạnh'
};

// Backend (ServiceType enum) chỉ có 3 mức: Basic / Premium / Deluxe.
// Map đủ cả 6 dịch vụ hiển thị sang 1 trong 3 mức đó (trước đây thiếu
// 3 dịch vụ, bị âm thầm rơi về "Basic").
const serviceTierMap = {
    ruaxe: 'Basic',
    noithat: 'Premium',
    khoangmay: 'Premium',
    danlanh: 'Premium',
    danhbong: 'Deluxe',
    ceramic: 'Deluxe'
};
const TIER_RANK = { Basic: 0, Premium: 1, Deluxe: 2 };

// Giờ hoạt động phải khớp với backend (DAILY_TIME_SLOTS = 8h → 17h).
// Không còn hardcode danh sách giờ trong HTML nữa — nếu backend đổi
// giờ hoạt động, frontend tự cập nhật theo vì lấy trực tiếp từ API.

// SIZE CARDS
document.querySelectorAll('.size-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.size-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        bookingData.size = card.dataset.value;
    });
});

// BRANCH OPTIONS
// Lưu ý: backend hiện KHÔNG có cột lưu chi nhánh (branch) trong bảng
// bookings, nên giá trị này mới chỉ dùng để hiển thị lại cho khách xem
// ở bước xác nhận, chưa được gửi lên/lưu ở server. Muốn lưu thật cần
// bổ sung cột "branch" ở model Booking + schema + migration phía backend.
document.querySelectorAll('.branch-option').forEach(opt => {
    opt.addEventListener('click', () => {
        document.querySelectorAll('.branch-option').forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');
        bookingData.branch = opt.dataset.value;
    });
});

// SERVICE OPTIONS (multi select)
document.querySelectorAll('.service-option').forEach(opt => {
    opt.addEventListener('click', () => {
        opt.classList.toggle('selected');
        const val = opt.dataset.value;
        if (opt.classList.contains('selected')) {
            if (!bookingData.services.includes(val)) bookingData.services.push(val);
        } else {
            bookingData.services = bookingData.services.filter(s => s !== val);
        }
    });
});

// TIME SLOTS — giờ được render động, xem renderTimeSlots()
const timeGrid = document.getElementById('time-grid');

function timeToLabel(hhmmss) {
    // "08:00:00" -> "08:00"
    return hhmmss.slice(0, 5);
}

async function renderTimeSlots() {
    if (!bookingData.date) return;
    timeGrid.innerHTML = '<p class="slot-loading">Đang tải khung giờ còn trống...</p>';
    bookingData.time = '';

    try {
        const slots = await getAvailableSlots(bookingData.date);
        timeGrid.innerHTML = '';

        if (!slots.length) {
            timeGrid.innerHTML = '<p class="slot-empty">Không có khung giờ nào cho ngày này.</p>';
            return;
        }

        slots.forEach(slot => {
            const label = timeToLabel(slot.time_slot);
            const full = slot.capacity_remaining <= 0;

            const el = document.createElement('div');
            el.className = 'time-slot' + (full ? ' full' : '');
            el.dataset.time = label;
            el.textContent = full ? `${label} (Hết chỗ)` : label;

            if (!full) {
                el.addEventListener('click', () => {
                    document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                    el.classList.add('selected');
                    bookingData.time = label;
                });
            }
            timeGrid.appendChild(el);
        });
    } catch (e) {
        timeGrid.innerHTML = '<p class="slot-empty">Không tải được khung giờ. Vui lòng thử lại.</p>';
    }
}

// QUICK DATE
function setDate(daysAhead) {
    const d = new Date();
    d.setDate(d.getDate() + daysAhead);
    const formatted = d.toISOString().split('T')[0];
    document.getElementById('booking-date').value = formatted;
    bookingData.date = formatted;
    renderTimeSlots();
}

document.getElementById('booking-date').addEventListener('change', function () {
    bookingData.date = this.value;
    renderTimeSlots();
});

// VALIDATE từng bước
function validate(step) {
    if (step === 1) {
        if (!bookingData.size) {
            alert('Vui lòng chọn size xe!');
            return false;
        }
    }
    if (step === 2) {
        if (!bookingData.branch) {
            alert('Vui lòng chọn chi nhánh!');
            return false;
        }
    }
    if (step === 3) {
        if (bookingData.services.length === 0) {
            alert('Vui lòng chọn ít nhất một dịch vụ!');
            return false;
        }
    }
    if (step === 4) {
        if (!bookingData.date) {
            alert('Vui lòng chọn ngày!');
            return false;
        }
        if (!bookingData.time) {
            alert('Vui lòng chọn giờ!');
            return false;
        }
    }
    if (step === 5) {
        const name = document.getElementById('input-name').value.trim();
        const phone = document.getElementById('input-phone').value.trim();
        const plate = document.getElementById('input-plate').value.trim();
        if (!name) { alert('Vui lòng nhập họ và tên!'); return false; }
        if (!phone) { alert('Vui lòng nhập số điện thoại!'); return false; }
        if (!plate) { alert('Vui lòng nhập biển số xe!'); return false; }
        bookingData.name = name;
        bookingData.phone = phone;
        bookingData.plate = plate;
    }
    return true;
}

// UPDATE CONFIRM
function updateConfirm() {
    document.getElementById('confirm-size').textContent = sizeLabels[bookingData.size] || '—';
    document.getElementById('confirm-branch').textContent = branchLabels[bookingData.branch] || '—';
    document.getElementById('confirm-service').textContent = bookingData.services.map(s => serviceLabels[s]).join(', ') || '—';
    document.getElementById('confirm-datetime').textContent = bookingData.date && bookingData.time
        ? `${bookingData.date} lúc ${bookingData.time}`
        : '—';
    document.getElementById('confirm-name').textContent = bookingData.name || '—';
    document.getElementById('confirm-phone').textContent = bookingData.phone || '—';
    document.getElementById('confirm-plate').textContent = bookingData.plate || '—';
}

// GO TO STEP
function goToStep(step) {
    document.querySelectorAll('.step-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.step').forEach((el, i) => {
        el.classList.remove('active', 'done');
        if (i + 1 < step) el.classList.add('done');
        if (i + 1 === step) el.classList.add('active');
    });

    document.getElementById(`step-${step}`).classList.add('active');

    const btnBack = document.getElementById('btn-back');
    const btnNext = document.getElementById('btn-next');

    btnBack.style.display = step === 1 ? 'none' : 'flex';

    if (step === totalSteps) {
        btnNext.innerHTML = 'Xác Nhận Đặt Lịch <i class="fa-solid fa-check"></i>';
        updateConfirm();
    } else {
        btnNext.innerHTML = 'Tiếp theo <i class="fa-solid fa-arrow-right"></i>';
    }

    currentStep = step;

    // Scroll lên đầu form
    document.querySelector('.booking-wrapper').scrollIntoView({ behavior: 'smooth' });
}

// NEXT — sửa lỗi: phải khai báo async vì có dùng await bên trong
async function nextStep() {
    if (!validate(currentStep)) return;
    if (currentStep < totalSteps) {
        goToStep(currentStep + 1);
    } else {
        const btnNext = document.getElementById('btn-next');
        btnNext.disabled = true;
        await submitBooking();
        btnNext.disabled = false;
    }
}

// PREV
function prevStep() {
    if (currentStep > 1) goToStep(currentStep - 1);
}

// INIT
goToStep(1);

// Tìm xe theo biển số khách vừa nhập; nếu khách chưa có xe này trong
// hồ sơ thì tự thêm mới bằng size đã chọn ở bước 1 (trước đây "size"
// thu xong rồi bỏ luôn, không dùng vào việc gì).
async function resolveVehicleId() {
    const normalizedPlate = bookingData.plate.replace(/\s|-/g, '').toUpperCase();
    const vehicles = await getVehicles();
    const matched = vehicles.find(
        v => v.license_plate.replace(/\s|-/g, '').toUpperCase() === normalizedPlate
    );
    if (matched) return matched.vehicle_id;

    // Chưa có xe này trong hồ sơ -> tự liên kết xe mới với size đã chọn
    const created = await addVehicle(bookingData.plate, bookingData.size, null);
    return created.vehicle_id;
}

async function submitBooking() {
    try {
        const vehicle_id = await resolveVehicleId();

        // Nhiều dịch vụ có thể được chọn cùng lúc, nhưng backend chỉ
        // nhận 1 ServiceType — lấy mức cao nhất trong các dịch vụ đã
        // chọn thay vì chỉ lấy dịch vụ đầu tiên (tránh tính thiếu tiền/
        // ghi sai loại dịch vụ khi khách chọn dịch vụ cao cấp không
        // phải là dịch vụ đầu tiên được bấm).
        const service_type = bookingData.services.reduce((best, s) => {
            const tier = serviceTierMap[s] || 'Basic';
            return TIER_RANK[tier] > TIER_RANK[best] ? tier : best;
        }, 'Basic');

        await createBooking(
            vehicle_id,
            bookingData.date,
            bookingData.time + ':00', // format HH:MM:SS
            service_type
        );

        alert('🎉 Đặt lịch thành công! SMS xác nhận đã được gửi.');
        window.location.href = 'loyalty.html';

    } catch (e) {
        alert('Lỗi đặt lịch: ' + e.message);
    }
}