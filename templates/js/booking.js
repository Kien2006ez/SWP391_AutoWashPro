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

// SIZE CARDS
document.querySelectorAll('.size-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.size-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        bookingData.size = card.dataset.value;
    });
});

// BRANCH OPTIONS
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

// TIME SLOTS
document.querySelectorAll('.time-slot').forEach(slot => {
    slot.addEventListener('click', () => {
        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
        slot.classList.add('selected');
        bookingData.time = slot.dataset.time;
    });
});

// QUICK DATE
function setDate(daysAhead) {
    const d = new Date();
    d.setDate(d.getDate() + daysAhead);
    const formatted = d.toISOString().split('T')[0];
    document.getElementById('booking-date').value = formatted;
    bookingData.date = formatted;
}

document.getElementById('booking-date').addEventListener('change', function () {
    bookingData.date = this.value;
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

// NEXT
function nextStep() {
    if (!validate(currentStep)) return;
    if (currentStep < totalSteps) {
        goToStep(currentStep + 1);
    } else {
        // Gửi dữ liệu — hiện tại chỉ alert, sau gắn backend vào đây
        alert('Đặt lịch thành công! Chúng tôi sẽ liên hệ bạn trong vòng 30 phút.');
    }
}

// PREV
function prevStep() {
    if (currentStep > 1) goToStep(currentStep - 1);
}

// INIT
goToStep(1);