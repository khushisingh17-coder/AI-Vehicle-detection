const dropzone = document.getElementById('uploadDropzone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.querySelector('.browse-btn');
const progressWrapper = document.getElementById('progressWrapper');
const progressFill = document.getElementById('progressFill');
const imagePreview = document.getElementById('imagePreview');
const uploadStatus = document.getElementById('uploadStatus');

const toastWrapper = document.getElementById('toastWrapper');

const updateStatus = (text) => {
    uploadStatus.textContent = text;
};

const showToast = (message, variant = 'info') => {
    if (!toastWrapper) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${variant}`;
    toast.innerHTML = `
        <div class="toast-icon">${variant === 'success' ? '✓' : variant === 'warning' ? '!' : variant === 'error' ? '⨯' : 'ℹ'}</div>
        <div class="toast-body">
            <div class="toast-title">${variant === 'success' ? 'Success' : variant === 'warning' ? 'Warning' : variant === 'error' ? 'Error' : 'Info'}</div>
            <p class="toast-message">${message}</p>
        </div>
    `;

    toastWrapper.appendChild(toast);
    let hideTimeout = setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        toast.addEventListener('animationend', () => toast.remove());
    }, 3800);

    toast.addEventListener('mouseenter', () => clearTimeout(hideTimeout));
    toast.addEventListener('mouseleave', () => {
        hideTimeout = setTimeout(() => {
            toast.style.animation = 'toastOut 0.3s ease forwards';
            toast.addEventListener('animationend', () => toast.remove());
        }, 1800);
    });
};

const showPreview = (file) => {
    const reader = new FileReader();
    reader.onload = (event) => {
        imagePreview.innerHTML = `
            <img src="${event.target.result}" alt="Vehicle preview">
        `;
    };
    reader.readAsDataURL(file);
};

const simulateUpload = () => {
    progressWrapper.hidden = false;
    progressWrapper.classList.add('visible');
    progressFill.style.width = '0%';
    updateStatus('Uploading image...');
    showToast('Upload started — AI is analyzing your vehicle.', 'info');

    let progress = 0;
    const timer = setInterval(() => {
        progress += Math.floor(Math.random() * 12) + 6;
        if (progress >= 100) {
            progress = 100;
            clearInterval(timer);
            updateStatus('Image ready for analysis');
            showToast('Image upload complete. Ready for detection.', 'success');
        }
        progressFill.style.width = `${progress}%`;
    }, 180);
};

const handleFiles = (files) => {
    if (!files || !files.length) return;
    const file = files[0];
    if (!file.type.startsWith('image/')) {
        showToast('Please select a valid image file to continue.', 'error');
        return;
    }
    showToast('Image selected successfully.', 'success');
    showPreview(file);
    simulateUpload();
};

browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => handleFiles(fileInput.files));

dropzone.addEventListener('dragenter', (event) => {
    event.preventDefault();
    dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragover', (event) => {
    event.preventDefault();
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('drag-over');
});

dropzone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropzone.classList.remove('drag-over');
    if (event.dataTransfer.files.length) {
        handleFiles(event.dataTransfer.files);
    }
});

const cursorGlow = document.querySelector('.cursor-glow');
const countCards = document.querySelectorAll('.count-card');
const revealElements = document.querySelectorAll('.scroll-reveal');
const scrollTopBtn = document.getElementById('scrollTopBtn');
const detectBtn = document.querySelector('.detect');
const cameraBtn = document.querySelector('.camera');
const heroContent = document.querySelector('.hero-content');
const heroMedia = document.querySelector('.hero-media');

// ================= Hero cinematic parallax =================
if (heroContent && heroMedia) {
    const applyHeroParallax = () => {
        const rect = heroContent.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const scrollDistance = Math.max(0, (viewportHeight - rect.top) * 0.04);
        const offsetY = Math.max(-10, Math.min(10, scrollDistance - 25));
        heroMedia.style.transform = `translate3d(0, ${offsetY}px, 0) scale(1.05)`;
    };

    window.addEventListener('scroll', applyHeroParallax, { passive: true });
    window.addEventListener('resize', applyHeroParallax);
    applyHeroParallax();
}

const formatValue = (value) => {
    return Number.isInteger(value) ? value : value.toFixed(1);
};
const uploadForm = document.getElementById("uploadForm");

const renderDetectionResults = (data) => {
    const detailsGrid = document.querySelector('.details-grid');
    if (!detailsGrid) return;

    const detections = Array.isArray(data?.detections) ? data.detections : [];

    if (detections.length === 0) {
        detailsGrid.innerHTML = `
            <div class="info-card" style="grid-column: 1 / -1; text-align: center; padding: 32px 20px;">
                <i class="fa-solid fa-circle-info" style="font-size: 42px; opacity: 0.7; margin-bottom: 12px; display: block;"></i>
                <h4 style="margin: 0 0 8px 0;">No vehicles detected</h4>
                <p style="margin: 0; opacity: 0.7; font-size: 14px;">The uploaded image does not contain any recognizable vehicles.</p>
            </div>
        `;
        updateStatus("No vehicles found");
        showToast("No vehicles detected in the image.", 'warning');
        return;
    }

    const vehicleEmoji = {
        car: '🚗',
        truck: '🚚',
        bus: '🚌',
        motorcycle: '🏍️'
    };

    detailsGrid.innerHTML = `
        <div style="grid-column: 1 / -1; padding-bottom: 16px; border-bottom: 1px solid rgba(245, 158, 11, 0.2);">
            <h4 style="margin: 0; font-size: 16px;">
                <i class="fa-solid fa-check-circle" style="color: #10b981; margin-right: 8px;"></i>
                Detected Vehicles (${detections.length})
            </h4>
        </div>
        ${detections.map((detection, index) => {
            const vehicleType = detection.vehicle || 'vehicle';
            const label = vehicleType.charAt(0).toUpperCase() + vehicleType.slice(1);
            const confidence = Number(detection.confidence ?? 0);
            const displayConfidence = Number.isFinite(confidence) ? `${confidence.toFixed(2)}%` : '0.00%';
            const emoji = vehicleEmoji[vehicleType] || '🚙';

            return `
                <div class="info-card" style="animation: fadeIn 0.4s ease-out ${index * 0.08}s backwards;">
                    <i class="fa-solid fa-circle-check" style="color: #10b981;"></i>
                    <h4>${emoji} ${label}</h4>
                    <p style="font-size: 18px; font-weight: 600; color: #f59e0b;">${displayConfidence}</p>
                    <p style="font-size: 12px; opacity: 0.7; margin-top: 5px;">Confidence Score</p>
                </div>
            `;
        }).join('')}
    `;

    updateStatus("Detection complete");
    showToast(`Successfully detected ${detections.length} vehicle(s)!`, 'success');
};

const renderDetectionError = (message) => {
    const detailsGrid = document.querySelector('.details-grid');
    if (!detailsGrid) return;

    detailsGrid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 32px 20px; color: #ef4444;">
            <i class="fa-solid fa-exclamation-triangle" style="font-size: 42px; margin-bottom: 12px; display: block;"></i>
            <h4 style="margin: 0 0 8px 0;">Detection failed</h4>
            <p style="margin: 0; opacity: 0.7; font-size: 14px;">${message}</p>
        </div>
    `;
    updateStatus("Detection failed");
    showToast(message, 'error');
};

detectBtn?.addEventListener("click", async (e) => {

    e.preventDefault();

    const fileInput = document.getElementById("fileInput");

    if (fileInput.files.length === 0) {
        showToast("Please select an image first.", 'warning');
        return;
    }

    showToast("Uploading image...");
    updateStatus("Processing image with AI...");

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Detection results:", data);

        if (!data.success) {
            renderDetectionError(data.message || 'Upload was unsuccessful.');
            return;
        }

        document.getElementById("uploadedImage").src = "/uploads/" + data.filename;
        document.getElementById("processedImage").src = "/uploads/" + data.filename;
        renderDetectionResults(data);

    } catch (error) {
        console.error("Detection error:", error);
        renderDetectionError(error.message || 'An unexpected error occurred.');
    }

});
cameraBtn?.addEventListener('click', () => {
    showToast('Live camera mode is currently simulated for demo use.', 'warning');
});
const animateCount = (card) => {
    const target = parseFloat(card.dataset.target) || 0;
    const suffix = card.dataset.suffix || '';
    const display = card.querySelector('.count-number');
    let current = 0;
    const duration = 1200;
    const stepTime = 16;
    const increment = target / (duration / stepTime);

    const step = () => {
        current += increment;
        if (current >= target) {
            display.textContent = `${formatValue(target)}${suffix}`;
            return;
        }
        display.textContent = `${formatValue(current)}${suffix}`;
        requestAnimationFrame(step);
    };

    requestAnimationFrame(step);
};

const setRevealDelay = (element, index) => {
    const custom = Number(element.dataset.revealDelay || 0);
    const delay = custom || index * 120;
    element.style.setProperty('--reveal-delay', `${delay}ms`);
};

const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const element = entry.target;
        element.classList.add('in-view');
        if (element.classList.contains('count-card')) {
            animateCount(element);
        }
        observer.unobserve(element);
    });
}, { threshold: 0.2, rootMargin: '0px 0px -12% 0px' });

revealElements.forEach((element, index) => {
    setRevealDelay(element, index);
    revealObserver.observe(element);
});

window.addEventListener('mousemove', (event) => {
    if (!cursorGlow) return;
    cursorGlow.style.left = `${event.clientX}px`;
    cursorGlow.style.top = `${event.clientY}px`;
});

scrollTopBtn?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Initialize charts (vehicleChart: line, companyChart: doughnut)
const initCharts = () => {
    try {
        const vehicleCanvas = document.getElementById('vehicleChart');
        if (vehicleCanvas) {
            const ctx = vehicleCanvas.getContext('2d');
            // gradient for line area
            const grad = ctx.createLinearGradient(0, 0, 0, vehicleCanvas.height || 180);
            grad.addColorStop(0, 'rgba(59,130,246,0.22)');
            grad.addColorStop(0.6, 'rgba(59,130,246,0.08)');
            grad.addColorStop(1, 'rgba(59,130,246,0.02)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Detections',
                        data: [62, 78, 90, 72, 88, 94, 82],
                        borderColor: 'rgba(249,115,22,0.95)',
                        backgroundColor: grad,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgba(249,115,22,0.98)',
                        pointHoverRadius: 6,
                        borderWidth: 2.6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 900, easing: 'easeOutQuart' },
                    plugins: {
                        legend: { display: true, position: 'bottom', labels: { color: '#94a3b8' } },
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(2,6,23,0.95)',
                            titleColor: '#fff',
                            bodyColor: '#cbd5e1',
                            mode: 'index',
                            intersect: false,
                            padding: 10,
                            caretPadding: 6
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.03)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#94a3b8' },
                            grid: { color: 'rgba(255,255,255,0.03)' }
                        }
                    },
                    interaction: { mode: 'nearest', axis: 'x', intersect: false }
                }
            });
        }

        const companyCanvas = document.getElementById('companyChart');
        if (companyCanvas) {
            const cctx = companyCanvas.getContext('2d');
            // subtle gradient for segments (applied as solid colors for clarity)
            const colors = ['#3b82f6', '#f97316', '#f59e0b', '#7c3aed'];
            new Chart(cctx, {
                type: 'doughnut',
                data: {
                    labels: ['Hyundai', 'Tata', 'Mahindra', 'Others'],
                    datasets: [{
                        data: [34, 22, 18, 26],
                        backgroundColor: colors.map(c => c),
                        borderColor: 'rgba(6,8,20,0.6)',
                        borderWidth: 2,
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { animateRotate: true, duration: 900, easing: 'easeOutCubic' },
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8', usePointStyle: true } },
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(2,6,23,0.95)',
                            titleColor: '#fff',
                            bodyColor: '#cbd5e1'
                        }
                    }
                }
            });
        }
    } catch (err) {
        console.warn('Chart init failed:', err);
    }
};

// Run chart init after small delay to ensure Chart.js loaded
window.addEventListener('load', () => {
    setTimeout(initCharts, 120);
    const loader = document.getElementById('siteLoader');
    const loaderStatus = document.getElementById('loaderStatus');
    const progressFill = document.querySelector('.loader-progress-fill');
    let progress = 0;
    const steps = [
        'Preparing AI core...',
        'Loading camera feeds...',
        'Calibrating sensors...',
        'Applying detection models...',
        'Optimizing analytics...'
    ];

    const stepInterval = setInterval(() => {
        progress += Math.floor(Math.random() * 12) + 10;
        if (progress >= 100) progress = 100;
        if (progressFill) progressFill.style.width = `${progress}%`;
        if (loaderStatus) loaderStatus.textContent = steps[Math.min(steps.length - 1, Math.floor(progress / 20))];

        if (progress >= 100) {
            clearInterval(stepInterval);
            setTimeout(() => {
                document.body.classList.remove('loading');
                if (loader) loader.style.opacity = '0';
                setTimeout(() => loader?.remove(), 450);
            }, 650);
        }
    }, 140);
});

// NAVBAR: hamburger toggle, smooth scrolling, active link highlighting
(() => {
    const nav = document.querySelector('.navbar');
    const toggle = document.querySelector('.nav-toggle');
    const links = Array.from(document.querySelectorAll('.nav-link'));

    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            const open = nav.classList.toggle('nav-open');
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    // Smooth scroll for nav links
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const id = link.getAttribute('href')?.replace('#', '');
            const target = id ? document.getElementById(id) : null;
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
            // close mobile menu when navigating
            if (nav && nav.classList.contains('nav-open')) nav.classList.remove('nav-open');
        });
    });

    // Active link highlighting using IntersectionObserver
    const sections = links.map(l => document.getElementById(l.getAttribute('href')?.replace('#', ''))).filter(Boolean);
    if (sections.length) {
        const obs = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const id = entry.target.id;
                const link = document.querySelector(`.nav-link[href="#${id}"]`);
                if (entry.isIntersecting) {
                    links.forEach(l => l.classList.remove('active'));
                    if (link) link.classList.add('active');
                }
            });
        }, { threshold: 0.45 });
        sections.forEach(s => obs.observe(s));
    }

    // Add scrolled class to navbar when page scrolled
    const onScroll = () => {
        if (!nav) return;
        if (window.scrollY > 18) nav.classList.add('scrolled'); else nav.classList.remove('scrolled');
    };
    window.addEventListener('scroll', onScroll);
    onScroll();

})();
