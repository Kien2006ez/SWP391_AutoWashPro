// Highlight pill nav khi scroll đến section tương ứng
const sections = document.querySelectorAll('.sv-block');
const pills    = document.querySelectorAll('.sv-hero-pills a');

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.id;
            pills.forEach(pill => {
                pill.style.background   = '';
                pill.style.borderColor  = '';
                pill.style.color        = '';
            });
            const active = document.querySelector(`.sv-hero-pills a[href="#${id}"]`);
            if (active) {
                active.style.background  = '#ff6200';
                active.style.borderColor = '#ff6200';
                active.style.color       = '#fff';
            }
        }
    });
}, { threshold: 0.35 });

sections.forEach(sec => observer.observe(sec));