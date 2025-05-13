// Script principal para o webapp Safa Barbeiros CIASC

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers do Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Efeito de fade-out para mensagens flash
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const alertInstance = new bootstrap.Alert(alert);
            if (alertInstance) {
                setTimeout(() => {
                    alert.classList.add('fade');
                    setTimeout(() => {
                        alertInstance.close();
                    }, 500);
                }, 3000);
            }
        });
    }, 3000);
    
    // Formatação de campos de valores monetários
    const moneyInputs = document.querySelectorAll('.money-input');
    
    moneyInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            // Remove qualquer caractere que não seja número ou ponto
            let value = e.target.value.replace(/[^0-9.]/g, '');
            
            // Garante que só exista um ponto decimal
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            // Limita a duas casas decimais
            if (parts.length > 1 && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            
            e.target.value = value;
        });
    });
    
    // Confirmação para ações destrutivas
    const confirmForms = document.querySelectorAll('.confirm-form');
    
    confirmForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = form.getAttribute('data-confirm') || 'Você tem certeza que deseja realizar esta ação?';
            
            if (confirm(message)) {
                form.submit();
            }
        });
    });
    
    // Inicializa selecione com busca 
    const selects = document.querySelectorAll('.select2');
    if (selects.length > 0 && typeof $.fn.select2 !== 'undefined') {
        $(selects).select2({
            theme: 'bootstrap-5',
            width: '100%'
        });
    }
    
    // Formatação de datas para inputs
    const dateInputs = document.querySelectorAll('.date-input');
    
    dateInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            
            if (value.length > 5) {
                value = value.substring(0, 5) + '/' + value.substring(5, 9);
            }
            
            e.target.value = value;
        });
    });
    
    // Formatação de números de telefone
    const phoneInputs = document.querySelectorAll('.phone-input');
    
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 0) {
                value = '(' + value;
            }
            
            if (value.length > 3) {
                value = value.substring(0, 3) + ') ' + value.substring(3);
            }
            
            if (value.length > 10) {
                value = value.substring(0, 10) + '-' + value.substring(10, 14);
            }
            
            e.target.value = value;
        });
    });
    
    // Toggle para exibir/ocultar senha
    const togglePassword = document.querySelectorAll('.toggle-password');
    
    togglePassword.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const target = document.getElementById(targetId);
            
            if (target.type === 'password') {
                target.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                target.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
    
    // Atualização de contadores de caracteres para textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counterId = textarea.getAttribute('data-counter');
        
        if (counterId) {
            const counter = document.getElementById(counterId);
            
            if (counter) {
                // Atualizar contador inicial
                counter.textContent = `${textarea.value.length}/${maxLength}`;
                
                // Atualizar ao digitar
                textarea.addEventListener('input', function() {
                    counter.textContent = `${textarea.value.length}/${maxLength}`;
                });
            }
        }
    });
    
    // Inicializar seletor de horários na página de agendamento
    const timeSlots = document.querySelectorAll('.time-slot');
    
    timeSlots.forEach(function(slot) {
        slot.addEventListener('click', function() {
            // Remove seleção anterior
            timeSlots.forEach(s => s.classList.remove('selected'));
            
            // Adiciona seleção ao slot atual
            this.classList.add('selected');
            
            // Atualiza campo oculto com o horário selecionado
            const dateTimeValue = this.getAttribute('data-datetime');
            const hiddenInput = document.getElementById('data_hora');
            
            if (hiddenInput) {
                hiddenInput.value = dateTimeValue;
            }
            
            // Ativa o botão de agendar
            const agendarBtn = document.getElementById('btn-agendar');
            if (agendarBtn) {
                agendarBtn.disabled = false;
            }
        });
    });
});
