document.addEventListener('DOMContentLoaded', () => {
    // Current state variables
    const urlParams = new URLSearchParams(window.location.search);
    const currentDateISO = urlParams.get('data') || document.getElementById('selectedDateISO')?.value || getTodayISO();
    
    let calendarDate = new Date(currentDateISO + 'T00:00:00');

    // DOM Elements
    const dateSelectorBtn = document.getElementById('dateSelectorBtn');
    const calendarDropdown = document.getElementById('calendarDropdown');
    const btnHoje = document.getElementById('btnHoje');
    const calendarDaysGrid = document.getElementById('calendarDaysGrid');
    const currentMonthYearLabel = document.getElementById('currentMonthYear');
    const prevMonthBtn = document.getElementById('prevMonthBtn');
    const nextMonthBtn = document.getElementById('nextMonthBtn');

    // Modals
    const userProfileBtn = document.getElementById('userProfileBtn');
    const userProfileModal = document.getElementById('userProfileModal');
    const btnCadastrarCliente = document.getElementById('btnCadastrarCliente');
    const clienteModal = document.getElementById('clienteModal');
    const btnCadastrarAtendimento = document.getElementById('btnCadastrarAtendimento');
    const atendimentoModal = document.getElementById('atendimentoModal');
    const detalhesModal = document.getElementById('detalhesModal');

    // Filter Form
    const filterForm = document.getElementById('filterForm');

    // Helper: Get local computer date formatted as YYYY-MM-DD
    function getTodayISO() {
        const d = new Date();
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Toggle Calendar Dropdown
    if (dateSelectorBtn && calendarDropdown) {
        dateSelectorBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            calendarDropdown.classList.toggle('active');
            renderCalendar(calendarDate);
        });

        document.addEventListener('click', (e) => {
            if (!calendarDropdown.contains(e.target) && !dateSelectorBtn.contains(e.target)) {
                calendarDropdown.classList.remove('active');
            }
        });
    }

    // "Hoje" Button: Redirects immediately to user's computer today date
    if (btnHoje) {
        btnHoje.addEventListener('click', () => {
            const todayISO = getTodayISO();
            const currentRisco = urlParams.get('risco') || 'todos';
            window.location.href = `/?data=${todayISO}&risco=${currentRisco}`;
        });
    }

    // Calendar Navigation (Previous & Next Month)
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            calendarDate.setMonth(calendarDate.getMonth() - 1);
            renderCalendar(calendarDate);
        });
    }

    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            calendarDate.setMonth(calendarDate.getMonth() + 1);
            renderCalendar(calendarDate);
        });
    }

    // Render Calendar Days Grid
    function renderCalendar(dateObj) {
        if (!calendarDaysGrid || !currentMonthYearLabel) return;

        const year = dateObj.getFullYear();
        const month = dateObj.getMonth();

        const monthNames = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ];

        currentMonthYearLabel.textContent = `${monthNames[month]} ${year}`;

        // Clear grid (keep day headers)
        calendarDaysGrid.innerHTML = `
            <div class="calendar-weekday">Dom</div>
            <div class="calendar-weekday">Seg</div>
            <div class="calendar-weekday">Ter</div>
            <div class="calendar-weekday">Qua</div>
            <div class="calendar-weekday">Qui</div>
            <div class="calendar-weekday">Sex</div>
            <div class="calendar-weekday">Sáb</div>
        `;

        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const totalDaysInMonth = new Date(year, month + 1, 0).getDate();

        // Empty cells before first day
        for (let i = 0; i < firstDayOfMonth; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'calendar-day-cell empty';
            calendarDaysGrid.appendChild(emptyCell);
        }

        const todayISO = getTodayISO();

        // Days of month
        for (let day = 1; day <= totalDaysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'calendar-day-cell';
            dayCell.textContent = day;

            const dayString = String(day).padStart(2, '0');
            const monthString = String(month + 1).padStart(2, '0');
            const cellDateISO = `${year}-${monthString}-${dayString}`;

            if (cellDateISO === currentDateISO) {
                dayCell.classList.add('selected');
            }

            if (cellDateISO === todayISO) {
                dayCell.classList.add('today');
            }

            dayCell.addEventListener('click', () => {
                const currentRisco = urlParams.get('risco') || 'todos';
                window.location.href = `/?data=${cellDateISO}&risco=${currentRisco}`;
            });

            calendarDaysGrid.appendChild(dayCell);
        }
    }

    // Modal Control Utility
    function setupModal(triggerBtn, modalElement) {
        if (!triggerBtn || !modalElement) return;

        triggerBtn.addEventListener('click', () => {
            modalElement.classList.add('active');
        });

        const closeBtns = modalElement.querySelectorAll('.close-modal-btn');
        closeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                modalElement.classList.remove('active');
            });
        });

        modalElement.addEventListener('click', (e) => {
            if (e.target === modalElement) {
                modalElement.classList.remove('active');
            }
        });
    }

    setupModal(userProfileBtn, userProfileModal);
    setupModal(btnCadastrarCliente, clienteModal);
    setupModal(btnCadastrarAtendimento, atendimentoModal);

    // Quick Add Button inside slot row
    document.querySelectorAll('.btn-add-quick').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const slotTime = btn.getAttribute('data-time');
            const horarioSelect = document.getElementById('atendimentoHorario');
            if (horarioSelect) {
                horarioSelect.value = slotTime;
            }
            if (atendimentoModal) {
                atendimentoModal.classList.add('active');
            }
        });
    });

    // Event Card Click -> Open Detalhes Atendimento Modal
    document.querySelectorAll('.event-card').forEach(card => {
        card.addEventListener('click', () => {
            const atendimentoId = card.getAttribute('data-id');
            fetch(`/atendimento/${atendimentoId}/detalhes/`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('detalhesCliente').textContent = data.cliente;
                    document.getElementById('detalhesDataHora').textContent = `${data.data} às ${data.horario}`;
                    document.getElementById('detalhesRisco').textContent = data.risco_display;
                    document.getElementById('detalhesRisco').className = `badge-risk ${data.risco}`;
                    document.getElementById('detalhesDescricao').textContent = data.descricao;

                    const arquivosContainer = document.getElementById('detalhesArquivos');
                    arquivosContainer.innerHTML = '';

                    if (data.arquivos && data.arquivos.length > 0) {
                        data.arquivos.forEach(arq => {
                            const li = document.createElement('li');
                            li.className = 'file-item';
                            li.innerHTML = `
                                <span>📄 ${arq.nome}</span>
                                <a href="${arq.url}" target="_blank" download>Baixar/Ver</a>
                            `;
                            arquivosContainer.appendChild(li);
                        });
                    } else {
                        arquivosContainer.innerHTML = '<li class="text-muted" style="font-size:0.85rem;">Nenhum arquivo anexado.</li>';
                    }

                    if (detalhesModal) {
                        detalhesModal.classList.add('active');
                    }
                })
                .catch(err => console.error('Erro ao carregar detalhes:', err));
        });
    });

    const closeDetalhesBtns = detalhesModal?.querySelectorAll('.close-modal-btn');
    closeDetalhesBtns?.forEach(btn => {
        btn.addEventListener('click', () => {
            detalhesModal.classList.remove('active');
        });
    });
    detalhesModal?.addEventListener('click', (e) => {
        if (e.target === detalhesModal) {
            detalhesModal.classList.remove('active');
        }
    });

    // Submit Forms via AJAX for responsive UX
    const formCadastrarCliente = document.getElementById('formCadastrarCliente');
    if (formCadastrarCliente) {
        formCadastrarCliente.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(formCadastrarCliente);
            
            fetch('/cliente/cadastrar/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('Cliente registrado com sucesso!');
                    // Update client select in atendimento form dynamically
                    const selectCliente = document.getElementById('atendimentoCliente');
                    if (selectCliente && data.cliente) {
                        const opt = document.createElement('option');
                        opt.value = data.cliente.id;
                        opt.textContent = `${data.cliente.nome} (${data.cliente.risco_display})`;
                        opt.selected = true;
                        selectCliente.appendChild(opt);
                    }
                    clienteModal.classList.remove('active');
                    formCadastrarCliente.reset();
                } else {
                    alert(data.message || 'Erro ao cadastrar cliente.');
                }
            })
            .catch(err => {
                console.error(err);
                formCadastrarCliente.submit();
            });
        });
    }

    const formCadastrarAtendimento = document.getElementById('formCadastrarAtendimento');
    if (formCadastrarAtendimento) {
        formCadastrarAtendimento.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(formCadastrarAtendimento);

            fetch('/atendimento/cadastrar/', {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('Atendimento agendado com sucesso!');
                    atendimentoModal.classList.remove('active');
                    // Reload home view for the selected date
                    const selectedDate = formData.get('data') || currentDateISO;
                    const currentRisco = urlParams.get('risco') || 'todos';
                    window.location.href = `/?data=${selectedDate}&risco=${currentRisco}`;
                } else {
                    alert(data.message || 'Erro ao cadastrar atendimento.');
                }
            })
            .catch(err => {
                console.error(err);
                formCadastrarAtendimento.submit();
            });
        });
    }
});
