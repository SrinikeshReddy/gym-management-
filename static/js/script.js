/**
 * GYM MANAGEMENT SYSTEM
 * Client-Side JavaScript Utilities
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-calculate Membership Duration (Days)
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const durationInput = document.getElementById('duration_days');

    function calculateMembershipDuration() {
        if (startDateInput && endDateInput && durationInput) {
            const startVal = startDateInput.value;
            const endVal = endDateInput.value;
            if (startVal && endVal) {
                const start = new Date(startVal);
                const end = new Date(endVal);
                const diffTime = end - start;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                if (diffDays >= 0) {
                    durationInput.value = diffDays;
                } else {
                    durationInput.value = 0;
                }
            }
        }
    }

    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', calculateMembershipDuration);
        endDateInput.addEventListener('change', calculateMembershipDuration);
    }

    // 2. Auto-calculate Attendance Workout Duration (Minutes)
    const checkInInput = document.getElementById('check_in_time');
    const checkOutInput = document.getElementById('check_out_time');
    const workoutDurationInput = document.getElementById('workout_duration');

    function calculateWorkoutDuration() {
        if (checkInInput && checkOutInput && workoutDurationInput) {
            const inVal = checkInInput.value;
            const outVal = checkOutInput.value;
            if (inVal && outVal) {
                const today = '2000-01-01 ';
                const inTime = new Date(today + inVal);
                const outTime = new Date(today + outVal);
                const diffMs = outTime - inTime;
                const diffMins = Math.floor(diffMs / 60000);
                if (diffMins >= 0) {
                    workoutDurationInput.value = diffMins;
                } else {
                    workoutDurationInput.value = 0;
                }
            }
        }
    }

    if (checkInInput && checkOutInput) {
        checkInInput.addEventListener('change', calculateWorkoutDuration);
        checkOutInput.addEventListener('change', calculateWorkoutDuration);
    }

    // 3. Dynamic Address Inputs for Member Form
    const addAddressBtn = document.getElementById('add-address-btn');
    const addressContainer = document.getElementById('address-fields-container');

    if (addAddressBtn && addressContainer) {
        addAddressBtn.addEventListener('click', function () {
            const div = document.createElement('div');
            div.className = 'input-group mb-2 address-row';
            div.innerHTML = `
                <input type="text" name="addresses[]" class="form-control" placeholder="Enter additional address" required>
                <button type="button" class="btn btn-outline-danger remove-address-btn">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            addressContainer.appendChild(div);
        });

        addressContainer.addEventListener('click', function (e) {
            if (e.target.closest('.remove-address-btn')) {
                e.target.closest('.address-row').remove();
            }
        });
    }

    // 4. Dynamic Certification Inputs for Trainer Form
    const addCertBtn = document.getElementById('add-cert-btn');
    const certContainer = document.getElementById('cert-fields-container');

    if (addCertBtn && certContainer) {
        addCertBtn.addEventListener('click', function () {
            const div = document.createElement('div');
            div.className = 'input-group mb-2 cert-row';
            div.innerHTML = `
                <input type="text" name="certifications[]" class="form-control" placeholder="e.g. CPR/AED or ACE Certified" required>
                <button type="button" class="btn btn-outline-danger remove-cert-btn">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            certContainer.appendChild(div);
        });

        certContainer.addEventListener('click', function (e) {
            if (e.target.closest('.remove-cert-btn')) {
                e.target.closest('.cert-row').remove();
            }
        });
    }

    // 5. Auto Calculate Age from Date of Birth
    const dobInput = document.getElementById('date_of_birth');
    const ageInput = document.getElementById('age');

    if (dobInput && ageInput) {
        dobInput.addEventListener('change', function () {
            const dobVal = dobInput.value;
            if (dobVal) {
                const dob = new Date(dobVal);
                const today = new Date();
                let age = today.getFullYear() - dob.getFullYear();
                const m = today.getMonth() - dob.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
                    age--;
                }
                if (age > 0) {
                    ageInput.value = age;
                }
            }
        });
    }
});

// Confirmation helper for delete actions
function confirmDelete(entityName) {
    return confirm(`Are you sure you want to permanently delete this ${entityName}? This action cannot be undone.`);
}
