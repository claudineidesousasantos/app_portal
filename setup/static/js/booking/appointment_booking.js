$(document).ready(function() {
    // Função para atualizar os horários disponíveis
    function updateAvailableSlots() {
        var employeeId = $('#id_employee').val();
        var date = $('#id_date').val();
        var barbershopName = $('#barbershop-name').data('name');

        // Limpar e desabilitar o select de horários enquanto carrega
        var timeSelect = $('#id_time');
        timeSelect.empty().prop('disabled', true);
        timeSelect.append('<label value="">Carregando horários...</label>');

        if (employeeId && date) {
            $.ajax({
                url: `/booking/${barbershopName}/get-available-slots/${employeeId}/${date}/`,
                method: 'GET',
                success: function(data) {
                    timeSelect.empty().prop('disabled', false);
                    timeSelect.append('<label id="id_time">Selecione um horário</label>');
                    
                    if (data.available_slots && data.available_slots.length > 0) {
                        data.available_slots.forEach(function(slot) {
                            timeSelect.append(`<label id="id_time">${slot}</label>`);
                        });
                    } else {
                        timeSelect.append('<label id="id_time" disabled>' + (data.message || 'Nenhum horário disponível') + '</label>');
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.error("AJAX error:", textStatus, errorThrown);
                    console.log("Response:", jqXHR.responseText);
                    alert('Erro ao carregar horários disponíveis. Por favor, tente novamente.');
                }
            });
        } else {
            timeSelect.empty().prop('disabled', true);
            timeSelect.append('<label id="">Selecione um funcionário e uma data</label>');
        }
    }
    // Atualizar horários disponíveis quando o funcionário ou a data mudar
    $('#id_employee, #id_date').change(updateAvailableSlots);
    // Manipular o envio do formulário de agendamento
    $('#booking-form').submit(function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        
        $.ajax({
            url: $(this).attr('action'),
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    alert(response.message || 'Agendamento realizado com sucesso!');
                    // Redirecionar ou atualizar a página conforme necessário
                    // window.location.href = '/pagina-de-confirmacao/';
                } else {
                    if (response.errors) {
                        // Exibir erros de validação do formulário
                        var errorMessage = "Erros no formulário:\n";
                        for (var field in response.errors) {
                            errorMessage += field + ": " + response.errors[field] + "\n";
                        }
                        alert(errorMessage);
                    } else {
                        alert(response.message || 'Não foi possível realizar o agendamento. Por favor, tente novamente.');
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("AJAX error:", textStatus, errorThrown);
                console.log("Response:", jqXHR.responseText);
                alert('Erro ao realizar o agendamento. Por favor, tente novamente.');
            }
        });
    });
    // Inicializar o estado do select de horários
    updateAvailableSlots();
});
