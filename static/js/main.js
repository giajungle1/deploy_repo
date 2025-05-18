// Flash message auto-hide
document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            setTimeout(function () {
                message.remove();
            }, 500);
        }, 3000);
    });
});

// Form validation
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Prediction form handling
const predictionForm = document.getElementById('prediction-form');
if (predictionForm) {
    predictionForm.addEventListener('submit', function (event) {
        const textInput = document.getElementById('text');
        if (!textInput.value.trim()) {
            event.preventDefault();
            alert('Please enter some text to analyze');
        }
    });
}

// Download history button
const downloadBtn = document.getElementById('download-history');
if (downloadBtn) {
    downloadBtn.addEventListener('click', function () {
        this.classList.add('disabled');
        setTimeout(() => {
            this.classList.remove('disabled');
        }, 2000);
    });
} 