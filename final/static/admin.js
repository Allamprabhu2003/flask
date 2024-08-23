document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form.admin-form');
    const errorMessages = document.getElementById('error-messages');

    if (form) {
        const inputs = form.querySelectorAll('input[type="text"], input[type="password"], input[type="email"]');
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateInput(input);
            });
        });

        form.addEventListener('submit', function(event) {
            let isValid = true;
            errorMessages.innerHTML = '';
            errorMessages.style.display = 'none';

            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                event.preventDefault();
                errorMessages.style.display = 'block';
            }
        });
    }

    function validateInput(input) {
        const errorElement = input.nextElementSibling;
        if (!errorElement || !errorElement.classList.contains('error-message')) {
            const newErrorElement = document.createElement('div');
            newErrorElement.classList.add('error-message');
            input.parentNode.insertBefore(newErrorElement, input.nextSibling);
        }

        let isValid = true;
        let errorMessage = '';

        switch(input.id) {
            case 'email':
                if (!isValidEmail(input.value)) {
                    errorMessage = 'Please enter a valid email address.';
                    isValid = false;
                }
                break;
            case 'password':
                if (input.value.length < 8) {
                    errorMessage = 'Password must be at least 8 characters long.';
                    isValid = false;
                }
                break;
            case 'first_name':
            case 'last_name':
                if (input.value.length < 2) {
                    errorMessage = 'Must be at least 2 characters long.';
                    isValid = false;
                }
                break;
        }

        if (!isValid) {
            showError(errorElement, errorMessage);
            addErrorMessage(errorMessage);
        } else {
            hideError(errorElement);
        }

        return isValid;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }

    function hideError(element) {
        element.style.display = 'none';
    }

    function addErrorMessage(message) {
        const li = document.createElement('li');
        li.textContent = message;
        errorMessages.appendChild(li);
    }
});