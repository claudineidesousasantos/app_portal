document.addEventListener('DOMContentLoaded', function() {
    const employeeCards = document.querySelectorAll('.employee-card');
    const modalElement = document.getElementById('employeeScheduleModal');
    const modal = new bootstrap.Modal(modalElement);
    const scheduleContainer = document.getElementById('employeeSchedule');

    employeeCards.forEach(card => {
        card.addEventListener('click', function() {
            const employeeId = this.dataset.employeeId;
            fetchEmployeeSchedule(employeeId);
        });
    });

    function fetchEmployeeSchedule(employeeId) {
        fetch(`/booking/barbershop/employee/${employeeId}/schedule/`)
            .then(response => response.json())
            .then(data => {
                displaySchedule(data);
                modal.show();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erro ao carregar a agenda. Por favor, tente novamente.');
            });
    }

    function displaySchedule(scheduleData) {
        let scheduleHtml = '<table class="table"><thead><tr><th>Data</th><th>Horário</th><th>Serviço</th></tr></thead><tbody>';
        
        if (scheduleData.length === 0) {
            scheduleHtml += '<tr><td colspan="3">Nenhum agendamento encontrado.</td></tr>';
        } else {
            scheduleData.forEach(appointment => {
                scheduleHtml += `
                    <tr>
                        <td>${appointment.date}</td>
                        <td>${appointment.time}</td>
                        <td>${appointment.service}</td>
                    </tr>
                `;
            });
        }

        scheduleHtml += '</tbody></table>';
        scheduleContainer.innerHTML = scheduleHtml;
    }
});
