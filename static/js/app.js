// SIGOA - Sistema de Gerenciamento de Organização Acadêmica
// Lógica de visualização, calendário, CRUD e integração com Google & Arquivos

let currentDate = new Date();
let currentView = 'month'; // 'month', 'week', 'day'
let allEvents = [];
let activeFilter = 'all';

// Restaura última data e visualização do usuário para não perder contexto
try {
    const savedDate = localStorage.getItem('sigoa_current_date');
    if (savedDate) {
        const parsed = new Date(savedDate);
        if (!isNaN(parsed.getTime())) currentDate = parsed;
    }
    const savedView = localStorage.getItem('sigoa_current_view');
    if (savedView && ['month', 'week', 'day'].includes(savedView)) {
        currentView = savedView;
    }
} catch (e) {}

function saveCurrentState() {
    try {
        localStorage.setItem('sigoa_current_date', currentDate.toISOString());
        localStorage.setItem('sigoa_current_view', currentView);
    } catch (e) {}
}

function showToast(message, type = 'success') {
    let toast = document.getElementById('sigoa-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'sigoa-toast';
        document.body.appendChild(toast);
    }
    
    const bgColor = type === 'success' ? 'bg-emerald-600 text-white' : 'bg-rose-600 text-white';
    toast.className = `fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-2xl shadow-2xl text-xs font-bold transition-all duration-300 transform translate-y-0 opacity-100 ${bgColor}`;
    toast.textContent = message;
    
    setTimeout(() => {
        toast.className = 'fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-2xl shadow-2xl text-xs font-bold transition-all duration-300 transform translate-y-8 opacity-0 pointer-events-none';
    }, 3500);
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[char]);
}

function safeColor(value) {
    return /^#[0-9a-fA-F]{6}$/.test(value || '') ? value : '#2563eb';
}

const MONTH_NAMES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

const WEEK_DAYS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
const WEEK_DAYS_SHORT = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

// Mapeamento padrão de cores do Design Sprint
const TYPE_COLORS = {
    'prova': '#dc2626',    // Vermelho
    'aula': '#2563eb',     // Azul
    'trabalho': '#9333ea', // Roxo
    'entrega': '#16a34a',  // Verde
    'outro': '#f59e0b'     // Âmbar
};

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    loadEvents();
    loadStats();
    
    // Fechar dropdown de lembretes ao clicar fora
    document.addEventListener('click', (e) => {
        const bell = document.getElementById('btnReminderBell');
        const dropdown = document.getElementById('reminderDropdown');
        if (dropdown && !dropdown.contains(e.target) && !bell.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
});

// ==================== CONTROLE DE DATA E NAVEGAÇÃO ====================

function updatePeriodHeader() {
    const label = document.getElementById('currentPeriodLabel');
    if (!label) return;

    const y = currentDate.getFullYear();
    const m = MONTH_NAMES[currentDate.getMonth()];

    if (currentView === 'month') {
        label.textContent = `${m} de ${y}`;
    } else if (currentView === 'week') {
        const weekStart = getWeekStart(currentDate);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekEnd.getDate() + 6);
        label.textContent = `${weekStart.getDate()} de ${MONTH_NAMES[weekStart.getMonth()]} - ${weekEnd.getDate()} de ${MONTH_NAMES[weekEnd.getMonth()]} (${y})`;
    } else if (currentView === 'day') {
        label.textContent = `${WEEK_DAYS[currentDate.getDay()]}, ${currentDate.getDate()} de ${m} de ${y}`;
    }
}

function prevPeriod() {
    if (currentView === 'month') {
        currentDate.setMonth(currentDate.getMonth() - 1);
    } else if (currentView === 'week') {
        currentDate.setDate(currentDate.getDate() - 7);
    } else if (currentView === 'day') {
        currentDate.setDate(currentDate.getDate() - 1);
    }
    saveCurrentState();
    renderCurrentView();
}

function nextPeriod() {
    if (currentView === 'month') {
        currentDate.setMonth(currentDate.getMonth() + 1);
    } else if (currentView === 'week') {
        currentDate.setDate(currentDate.getDate() + 7);
    } else if (currentView === 'day') {
        currentDate.setDate(currentDate.getDate() + 1);
    }
    saveCurrentState();
    renderCurrentView();
}

function goToToday() {
    currentDate = new Date();
    saveCurrentState();
    renderCurrentView();
}

function switchView(view) {
    currentView = view;
    saveCurrentState();
    
    // Atualiza botões
    ['Day', 'Week', 'Month'].forEach(v => {
        const btn = document.getElementById(`viewBtn${v}`);
        if (!btn) return;
        if (v.toLowerCase() === view) {
            btn.className = "px-3 py-1 rounded-lg text-xs font-semibold bg-white text-blue-600 shadow-xs transition";
        } else {
            btn.className = "px-3 py-1 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 transition";
        }
    });

    renderCurrentView();
}

function filterEvents() {
    activeFilter = document.getElementById('typeFilter').value;
    renderCurrentView();
}

// ==================== CARREGAMENTO DE DADOS ====================

async function loadEvents() {
    try {
        const res = await fetch('/api/events', { cache: 'no-store' });
        if (res.ok) {
            allEvents = await res.json();
            renderCurrentView();
            checkUpcomingReminders();
        }
    } catch (err) {
        console.error("Erro ao carregar eventos:", err);
    }
}

async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('statProvas').textContent = data.provas_pendentes;
            document.getElementById('statEntregas').textContent = data.entregas_pendentes;
            document.getElementById('statTotal').textContent = data.total_eventos;
            document.getElementById('statArquivos').textContent = data.total_arquivos;
        }
    } catch (err) {
        console.error("Erro ao carregar estatísticas:", err);
    }
}

function getFilteredEvents() {
    if (activeFilter === 'all') return allEvents;
    return allEvents.filter(e => e.event_type === activeFilter);
}

// ==================== RENDERIZAÇÃO DAS VISÕES ====================

function renderCurrentView() {
    updatePeriodHeader();
    const container = document.getElementById('calendarContainer');
    if (!container) return;

    if (currentView === 'month') {
        renderMonthView(container);
    } else if (currentView === 'week') {
        renderWeekView(container);
    } else if (currentView === 'day') {
        renderDayView(container);
    }

    if (window.lucide) lucide.createIcons();
}

// 1. VISÃO MENSAL (Especificação do PDF: Grade com Marcadores Coloridos)
function renderMonthView(container) {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDayIndex = new Date(year, month, 1).getDay();
    const totalDaysInMonth = new Date(year, month + 1, 0).getDate();
    const totalDaysInPrevMonth = new Date(year, month, 0).getDate();

    const today = new Date();
    const todayStr = formatDateYMD(today);

    const filtered = getFilteredEvents();

    let html = `
        <!-- Cabeçalho dos Dias da Semana -->
        <div class="grid grid-cols-7 border-b border-slate-200 bg-slate-50/80 text-center text-[11px] font-bold uppercase tracking-wider text-slate-500 py-2.5">
            ${WEEK_DAYS_SHORT.map(d => `<div>${d}</div>`).join('')}
        </div>
        <!-- Grade do Mês -->
        <div class="calendar-grid flex-grow border-b border-r border-slate-200 bg-slate-200 gap-px">
    `;

    // Dias do mês anterior
    for (let i = firstDayIndex - 1; i >= 0; i--) {
        const dayNum = totalDaysInPrevMonth - i;
        html += `
            <div class="calendar-day-cell is-other-month bg-white/70 p-2 flex flex-col justify-between opacity-50">
                <span class="text-xs font-semibold text-slate-400">${dayNum}</span>
            </div>
        `;
    }

    // Dias do mês atual
    for (let day = 1; day <= totalDaysInMonth; day++) {
        const cellDate = new Date(year, month, day);
        const cellDateStr = formatDateYMD(cellDate);
        const isToday = (cellDateStr === todayStr);

        // Eventos deste dia
        const dayEvents = filtered.filter(e => e.event_date === cellDateStr);

        html += `
            <div class="calendar-day-cell ${isToday ? 'is-today' : 'bg-white'} p-2 flex flex-col justify-between group cursor-pointer hover:bg-blue-50/30 relative"
                 onclick="handleCellClick('${cellDateStr}', event)">
                
                <div class="flex items-center justify-between">
                    <span class="text-xs font-bold ${isToday ? 'w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center -ml-1 -mt-1 shadow-sm' : 'text-slate-700'}">
                        ${day}
                    </span>
                    <button onclick="openCreateModal('${cellDateStr}'); event.stopPropagation();" 
                            class="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-200/70 rounded-md text-slate-400 hover:text-slate-700 transition" 
                            title="Adicionar evento neste dia">
                        <i data-lucide="plus" class="w-3 h-3"></i>
                    </button>
                </div>

                <!-- Lista de Marcadores / Pílulas Coloridas -->
                <div class="space-y-1 mt-1 overflow-hidden">
                    ${dayEvents.slice(0, 3).map(ev => `
                        <div onclick="openEditModal(${ev.id}); event.stopPropagation();"
                             class="event-pill text-[11px] px-2 py-0.5 rounded-md truncate font-medium flex items-center gap-1.5 shadow-2xs border border-black/5"
                             style="background-color: ${safeColor(ev.color)}15; color: ${safeColor(ev.color)}; border-left: 3px solid ${safeColor(ev.color)};"
                             title="${escapeHtml(ev.title)} (${escapeHtml(ev.start_time || 'Sem horário')})">
                            <span class="w-1.5 h-1.5 rounded-full shrink-0" style="background-color: ${safeColor(ev.color)}"></span>
                            <span class="truncate">${escapeHtml(ev.title)}</span>
                            ${ev.files_count > 0 ? '<i data-lucide="paperclip" class="w-2.5 h-2.5 shrink-0"></i>' : ''}
                        </div>
                    `).join('')}

                    ${dayEvents.length > 3 ? `
                        <span class="text-[10px] text-slate-500 font-semibold block px-1">
                            +${dayEvents.length - 3} mais
                        </span>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Dias do próximo mês para completar grade (7 colunas)
    const totalRendered = firstDayIndex + totalDaysInMonth;
    const remaining = (7 - (totalRendered % 7)) % 7;
    for (let day = 1; day <= remaining; day++) {
        html += `
            <div class="calendar-day-cell is-other-month bg-white/70 p-2 flex flex-col justify-between opacity-50">
                <span class="text-xs font-semibold text-slate-400">${day}</span>
            </div>
        `;
    }

    html += `</div>`;
    container.innerHTML = html;
}

// 2. VISÃO SEMANAL
function renderWeekView(container) {
    const weekStart = getWeekStart(currentDate);
    const filtered = getFilteredEvents();
    const todayStr = formatDateYMD(new Date());

    let html = `
        <div class="grid grid-cols-7 border-b border-slate-200 bg-slate-50 text-center text-xs font-bold text-slate-700 py-3">
    `;

    const weekDaysArr = [];
    for (let i = 0; i < 7; i++) {
        const d = new Date(weekStart);
        d.setDate(d.getDate() + i);
        weekDaysArr.push(d);
        const isToday = formatDateYMD(d) === todayStr;
        html += `
            <div class="${isToday ? 'text-blue-600' : ''}">
                <div class="text-[11px] uppercase tracking-wider text-slate-400">${WEEK_DAYS_SHORT[i]}</div>
                <div class="text-base font-bold ${isToday ? 'w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center mx-auto mt-0.5' : ''}">
                    ${d.getDate()}
                </div>
            </div>
        `;
    }
    html += `</div><div class="grid grid-cols-7 divide-x divide-slate-100 flex-grow p-2">`;

    weekDaysArr.forEach(d => {
        const dateStr = formatDateYMD(d);
        const dayEvents = filtered.filter(e => e.event_date === dateStr);

        html += `
            <div class="p-2 space-y-2 min-h-[350px] hover:bg-slate-50/50 rounded-xl transition cursor-pointer"
                 onclick="handleCellClick('${dateStr}', event)">
                <div class="flex justify-between items-center mb-1">
                    <button onclick="openCreateModal('${dateStr}'); event.stopPropagation();" 
                            class="w-full text-center py-1 text-[11px] font-semibold text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition">
                        + Evento
                    </button>
                </div>
                <div class="space-y-2">
                    ${dayEvents.map(ev => `
                        <div onclick="openEditModal(${ev.id}); event.stopPropagation();"
                             class="p-2.5 rounded-xl border border-slate-200/80 shadow-2xs hover:shadow-xs transition cursor-pointer"
                             style="border-left: 4px solid ${safeColor(ev.color)}; background: #ffffff;">
                            <span class="text-[10px] font-bold uppercase tracking-wider block" style="color: ${safeColor(ev.color)}">
                                ${escapeHtml(ev.event_type)} ${ev.start_time ? '• ' + escapeHtml(ev.start_time) : ''}
                            </span>
                            <h4 class="text-xs font-bold text-slate-800 line-clamp-1 mt-0.5">${escapeHtml(ev.title)}</h4>
                            ${ev.discipline ? `<p class="text-[10px] text-slate-500 truncate">${escapeHtml(ev.discipline)}</p>` : ''}
                            ${ev.files_count > 0 ? `
                                <div class="mt-1 flex items-center gap-1 text-[10px] text-slate-400">
                                    <i data-lucide="paperclip" class="w-3 h-3"></i>
                                    <span>${ev.files_count} anexo(s)</span>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;
}

// 3. VISÃO DIÁRIA
function renderDayView(container) {
    const dateStr = formatDateYMD(currentDate);
    const filtered = getFilteredEvents().filter(e => e.event_date === dateStr);

    let html = `
        <div class="p-6">
            <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                <div>
                    <h3 class="text-lg font-bold text-slate-800">
                        Compromissos para ${currentDate.getDate()} de ${MONTH_NAMES[currentDate.getMonth()]}
                    </h3>
                    <p class="text-xs text-slate-500">${filtered.length} evento(s) agendado(s)</p>
                </div>
                <button onclick="openCreateModal('${dateStr}')" 
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5">
                    <i data-lucide="plus" class="w-4 h-4"></i>
                    <span>Adicionar Neste Dia</span>
                </button>
            </div>

            <div class="space-y-3">
                ${filtered.length === 0 ? `
                    <div class="text-center py-16">
                        <div class="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-2">
                            <i data-lucide="calendar-x" class="w-6 h-6"></i>
                        </div>
                        <p class="text-xs font-semibold text-slate-600">Nenhum compromisso marcado para este dia.</p>
                        <p class="text-[11px] text-slate-400 mt-0.5">Aproveite para adiantar suas leituras ou criar uma nova tarefa.</p>
                    </div>
                ` : filtered.map(ev => `
                    <div onclick="openEditModal(${ev.id})"
                         class="p-4 rounded-2xl border border-slate-200/80 hover:border-slate-300 shadow-2xs hover:shadow-xs transition cursor-pointer flex items-center justify-between gap-4"
                         style="border-left: 5px solid ${safeColor(ev.color)};">
                        
                        <div class="space-y-1">
                            <div class="flex items-center gap-2">
                                <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md" 
                                      style="background-color: ${safeColor(ev.color)}20; color: ${safeColor(ev.color)};">
                                    ${escapeHtml(ev.event_type)}
                                </span>
                                ${ev.start_time ? `
                                    <span class="text-xs font-semibold text-slate-500">
                                        ⏰ ${escapeHtml(ev.start_time)} ${ev.end_time ? 'às ' + escapeHtml(ev.end_time) : ''}
                                    </span>
                                ` : '<span class="text-xs text-slate-400">Dia Inteiro</span>'}
                            </div>

                            <h4 class="text-sm font-bold text-slate-800">${escapeHtml(ev.title)}</h4>
                            ${ev.discipline ? `<p class="text-xs text-slate-600 font-medium">Matéria: ${escapeHtml(ev.discipline)}</p>` : ''}
                            ${ev.description ? `<p class="text-xs text-slate-500">${escapeHtml(ev.description)}</p>` : ''}
                        </div>

                        <div class="flex items-center gap-2">
                            <a href="${escapeHtml(ev.google_calendar_url)}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation()"
                               class="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-600" title="Google Calendar">
                                <i data-lucide="calendar" class="w-4 h-4"></i>
                            </a>
                            <button class="p-2 rounded-xl bg-slate-100 text-slate-600 hover:bg-blue-50 hover:text-blue-600">
                                <i data-lucide="chevron-right" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// ==================== LEMBRETES INTERNOS & ALERTAS ====================

function checkUpcomingReminders() {
    const now = new Date();
    const offsetMinutes = { at_time: 0, '1h': 60, '1d': 1440, '2d': 2880, '1w': 10080 };
    const due = allEvents.filter((event) => {
        if (Number(event.is_completed) === 1 || !(event.reminder_type in offsetMinutes)) return false;
        const [year, month, day] = (event.event_date || '').split('-').map(Number);
        if (!year || !month || !day) return false;
        const [hour, minute] = (event.start_time || '09:00').split(':').map(Number);
        const eventAt = new Date(year, month - 1, day, hour || 0, minute || 0);
        const reminderAt = new Date(eventAt.getTime() - offsetMinutes[event.reminder_type] * 60000);
        const visibleUntil = new Date(eventAt.getTime() + 24 * 60 * 60000);
        return now >= reminderAt && now <= visibleUntil;
    }).sort((a, b) => a.event_date.localeCompare(b.event_date));

    const banner = document.getElementById('urgentAlertBanner');
    const bannerText = document.getElementById('urgentAlertText');
    const badge = document.getElementById('reminderBadge');
    const reminderList = document.getElementById('reminderList');
    const reminderCountLabel = document.getElementById('reminderCountLabel');

    reminderList.replaceChildren();
    if (due.length) {
        badge.classList.remove('hidden');
        reminderCountLabel.textContent = `${due.length} lembrete(s) ativo(s)`;
        const first = due[0];
        const title = document.createElement('strong');
        title.textContent = first.title;
        bannerText.replaceChildren(title, document.createTextNode(
            ` (${String(first.event_type || 'evento').toUpperCase()}) está marcado para ${first.event_date}. Verifique materiais e requisitos.`
        ));
        banner.classList.remove('hidden');

        due.forEach((event) => {
            const card = document.createElement('button');
            card.type = 'button';
            card.className = 'block w-full text-left p-2.5 rounded-xl bg-slate-50 hover:bg-blue-50 border border-slate-200/80 cursor-pointer transition';
            card.addEventListener('click', () => openEditModal(event.id));
            const meta = document.createElement('div');
            meta.className = 'flex items-center justify-between mb-0.5';
            const type = document.createElement('span');
            type.className = 'text-[10px] font-bold uppercase tracking-wider text-rose-600';
            type.textContent = event.event_type || 'evento';
            const date = document.createElement('span');
            date.className = 'text-[10px] text-slate-400';
            date.textContent = event.event_date;
            meta.append(type, date);
            const titleText = document.createElement('span');
            titleText.className = 'block text-xs font-semibold text-slate-800 truncate';
            titleText.textContent = event.title;
            card.append(meta, titleText);
            reminderList.append(card);
        });
    } else {
        badge.classList.add('hidden');
        banner.classList.add('hidden');
        bannerText.replaceChildren();
        const empty = document.createElement('p');
        empty.className = 'text-slate-400 text-center py-4 text-[11px]';
        empty.textContent = 'Nenhum lembrete ativo no momento.';
        reminderList.append(empty);
        reminderCountLabel.textContent = '0 ativos';
    }

    if (window.lucide) lucide.createIcons();
}
function toggleReminderDropdown() {
    const dropdown = document.getElementById('reminderDropdown');
    dropdown.classList.toggle('hidden');
}

// ==================== MODAL DE CRIAÇÃO (RF02) ====================

function openCreateModal(datePrefill = null) {
    const modal = document.getElementById('createEventModal');
    const form = document.getElementById('createEventForm');
    form.reset();

    const dateInput = document.getElementById('createDate');
    if (datePrefill) {
        dateInput.value = datePrefill;
    } else {
        dateInput.value = formatDateYMD(currentDate);
    }

    autoAssignColor(document.getElementById('createEventType').value, 'createColor');
    modal.classList.remove('hidden');
}

function closeCreateModal() {
    document.getElementById('createEventModal').classList.add('hidden');
}

async function handleCreateEvent(e) {
    e.preventDefault();
    const form = document.getElementById('createEventForm');
    const formData = new FormData(form);

    try {
        const res = await fetch('/api/events', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            closeCreateModal();
            await loadEvents();
            await loadStats();
            showToast('Compromisso criado e salvo com sucesso!');
        } else {
            const err = await res.json();
            alert(err.error || 'Erro ao criar evento.');
        }
    } catch (err) {
        alert('Erro ao conectar com o servidor.');
    }
}

function updateSchedulePdfLabel(inputId, labelId) {
    const input = document.getElementById(inputId);
    const label = document.getElementById(labelId);
    const file = input.files && input.files[0];
    label.textContent = file ? file.name : (inputId === 'calendarPdf'
        ? 'Selecione o PDF do calendario' : 'Selecione o PDF dos horarios');
    label.title = file ? `${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)` : '';
    label.classList.toggle('text-slate-500', !file);
    label.classList.toggle('text-emerald-700', !!file);
    resetSchedulePdfRead();
}

function resetSchedulePdfRead() {
    document.getElementById('schedulePhaseControls').classList.add('hidden');
    const phaseSelect = document.getElementById('schedulePhase');
    phaseSelect.value = '';
    document.getElementById('importScheduleButton').classList.add('hidden');
}

async function lerHorarioPdf() {
    const calendarPdf = document.getElementById('calendarPdf').files[0];
    const schedulePdf = document.getElementById('courseSchedulePdf').files[0];
    const phaseSelect = document.getElementById('schedulePhase');
    const readButton = document.getElementById('inspectScheduleButton');
    document.getElementById('schedulePhaseControls').classList.add('hidden');
    document.getElementById('importScheduleButton').classList.add('hidden');
    if (!calendarPdf || !schedulePdf) {
        showToast('Selecione o calendario academico e o horario do curso em PDF.', 'error');
        return;
    }
    const formData = new FormData();
    formData.append('calendar_pdf', calendarPdf);
    formData.append('schedule_pdf', schedulePdf);
    readButton.disabled = true;
    readButton.textContent = 'Lendo PDFs...';
    try {
        const res = await fetch('/api/events/inspect-schedule', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok) throw new Error(result.error || 'Nao foi possivel ler os PDFs.');
        phaseSelect.innerHTML = '<option value="">Selecione a fase</option>' + result.phases
            .map(phase => `<option value="${phase}">${phase}a fase</option>`).join('');
        document.getElementById('schedulePhaseControls').classList.remove('hidden');
        document.getElementById('importScheduleButton').classList.remove('hidden');
        document.getElementById('importScheduleButton').classList.add('flex');
        showToast(`PDFs lidos. Periodo ${result.start_date} a ${result.end_date}; agora selecione sua fase.`);
    } catch (err) {
        showToast(err.message || 'Erro ao ler os PDFs.', 'error');
    } finally {
        readButton.disabled = false;
        readButton.textContent = 'Ler PDFs';
    }
}

async function importarHorarioSelecionado() {
    const calendarPdf = document.getElementById('calendarPdf').files[0];
    const schedulePdf = document.getElementById('courseSchedulePdf').files[0];
    const phase = document.getElementById('schedulePhase').value;
    if (!calendarPdf || !schedulePdf) {
        showToast('Selecione o calendario academico e o horario do curso em PDF.', 'error');
        return;
    }
    if (!phase) {
        showToast('Selecione sua fase depois de ler os PDFs.', 'error');
        return;
    }
    if (!confirm(`Ler os PDFs e importar as aulas da ${phase}a fase nos dias letivos do calendario?`)) return;

    const formData = new FormData();
    formData.append('calendar_pdf', calendarPdf);
    formData.append('schedule_pdf', schedulePdf);
    formData.append('phase', phase);
    try {
        const res = await fetch('/api/events/import-schedule', { method: 'POST', body: formData });
        const result = await res.json();
        if (!res.ok) throw new Error(result.error || 'Nao foi possivel importar os PDFs.');
        await loadEvents();
        await loadStats();
        showToast(`${result.created} aulas importadas; ${result.skipped} ja existiam. Periodo ${result.start_date} a ${result.end_date}.`);
    } catch (err) {
        showToast(err.message || 'Erro ao ler os PDFs.', 'error');
    }
}

// ==================== MODAL DE EDIÇÃO ====================

async function openEditModal(eventId) {
    const modal = document.getElementById('editEventModal');
    try {
        const res = await fetch(`/api/events/${eventId}`);
        if (!res.ok) return;

        const event = await res.json();

        document.getElementById('editEventId').value = event.id;
        document.getElementById('editTitle').value = event.title;
        document.getElementById('editDiscipline').value = event.discipline || '';
        document.getElementById('editDate').value = event.event_date;
        document.getElementById('editStartTime').value = event.start_time || '';
        document.getElementById('editEndTime').value = event.end_time || '';
        document.getElementById('editEventType').value = event.event_type;
        document.getElementById('editColor').value = event.color;
        document.getElementById('editReminder').value = event.reminder_type || 'none';
        document.getElementById('editStatus').value = event.is_completed || '0';
        document.getElementById('editDescription').value = event.description || '';

        // Botão Google Calendar Sync
        const btnGoogle = document.getElementById('btnSyncGoogleEvent');
        btnGoogle.href = event.google_calendar_url;

        // Lista de Arquivos Anexados
        const filesContainer = document.getElementById('editFilesList');
        if (event.files && event.files.length > 0) {
            filesContainer.innerHTML = event.files.map(f => `
                <div class="flex items-center justify-between p-2 rounded-xl bg-slate-50 border border-slate-200/70 text-xs">
                    <div class="flex items-center gap-2 truncate">
                        <i data-lucide="file" class="w-3.5 h-3.5 text-blue-600 shrink-0"></i>
                        <span class="truncate text-slate-700 font-medium">${escapeHtml(f.original_filename)}</span>
                    </div>
                    <a href="/api/files/${f.id}/download" class="text-blue-600 hover:text-blue-800 p-1 font-semibold" title="Baixar Arquivo">
                        <i data-lucide="download" class="w-3.5 h-3.5"></i>
                    </a>
                </div>
            `).join('');
        } else {
            filesContainer.innerHTML = `<p class="text-[11px] text-slate-400">Nenhum anexo para este compromisso.</p>`;
        }

        modal.classList.remove('hidden');
        if (window.lucide) lucide.createIcons();
    } catch (err) {
        console.error("Erro ao abrir detalhes:", err);
    }
}

function closeEditModal() {
    document.getElementById('editEventModal').classList.add('hidden');
}

async function handleUpdateEvent(e) {
    e.preventDefault();
    const eventId = document.getElementById('editEventId').value;
    const form = document.getElementById('editEventForm');
    const formData = new FormData(form);

    try {
        const res = await fetch(`/api/events/${eventId}`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            closeEditModal();
            await loadEvents();
            await loadStats();
            showToast('Alterações salvas com sucesso no banco!');
        } else {
            const err = await res.json();
            alert(err.error || 'Erro ao atualizar evento.');
        }
    } catch (err) {
        alert('Erro ao conectar com o servidor.');
    }
}

async function handleDeleteEvent() {
    const eventId = document.getElementById('editEventId').value;
    if (!confirm('Deseja realmente excluir este compromisso acadêmico?')) {
        return;
    }

    try {
        const res = await fetch(`/api/events/${eventId}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            closeEditModal();
            await loadEvents();
            await loadStats();
            showToast('Compromisso excluído com sucesso.');
        } else {
            alert('Erro ao excluir compromisso.');
        }
    } catch (err) {
        alert('Erro ao conectar com o servidor.');
    }
}

// ==================== GERENCIADOR DE ARQUIVOS (DB POR USUÁRIO) ====================

async function openFilesModal() {
    const modal = document.getElementById('filesModal');
    modal.classList.remove('hidden');
    await loadUserFiles();
}

function closeFilesModal() {
    document.getElementById('filesModal').classList.add('hidden');
}

async function loadUserFiles() {
    const container = document.getElementById('userFilesContainer');
    try {
        const res = await fetch('/api/files');
        if (!res.ok) return;

        const files = await res.json();
        if (files.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <div class="w-12 h-12 rounded-full bg-amber-50 text-amber-500 flex items-center justify-center mx-auto mb-2">
                        <i data-lucide="folder-open" class="w-6 h-6"></i>
                    </div>
                    <p class="text-xs font-semibold text-slate-600">Nenhum arquivo enviado até o momento.</p>
                    <p class="text-[11px] text-slate-400 mt-0.5">Envie PDFs, slides ou enunciados usando o formulário acima.</p>
                </div>
            `;
        } else {
            container.innerHTML = files.map(f => `
                <div class="p-3 rounded-xl bg-white border border-slate-200/80 hover:border-slate-300 shadow-2xs flex items-center justify-between gap-3">
                    <div class="flex items-center gap-3 truncate">
                        <div class="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                            <i data-lucide="file-text" class="w-4 h-4"></i>
                        </div>
                        <div class="truncate">
                            <h5 class="text-xs font-bold text-slate-800 truncate">${escapeHtml(f.original_filename)}</h5>
                            <p class="text-[10px] text-slate-400">
                                ${(f.file_size / 1024).toFixed(1)} KB • ${escapeHtml((f.uploaded_at || '').substring(0, 16))}
                                ${f.event_title ? `• Vinculado a: <em>${escapeHtml(f.event_title)}</em>` : ''}
                            </p>
                        </div>
                    </div>
                    <div class="flex items-center gap-1.5 shrink-0">
                        <a href="/api/files/${f.id}/download" 
                           class="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 hover:text-blue-600 transition" 
                           title="Baixar Arquivo">
                            <i data-lucide="download" class="w-4 h-4"></i>
                        </a>
                        <button onclick="handleDeleteFile(${f.id})" 
                                class="p-1.5 rounded-lg border border-rose-200 hover:bg-rose-50 text-rose-500 transition" 
                                title="Excluir Arquivo">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }

        if (window.lucide) lucide.createIcons();
    } catch (err) {
        container.innerHTML = `<p class="text-xs text-rose-600 text-center py-4">Erro ao carregar arquivos.</p>`;
    }
}

async function handleDirectFileUpload(e) {
    e.preventDefault();
    const input = document.getElementById('directFileInput');
    if (!input.files || input.files.length === 0) return;

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res = await fetch('/api/files/upload', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            input.value = '';
            await loadUserFiles();
            await loadStats();
        } else {
            const err = await res.json();
            alert(err.error || 'Erro ao enviar arquivo.');
        }
    } catch (err) {
        alert('Erro ao enviar arquivo.');
    }
}

async function handleDeleteFile(fileId) {
    if (!confirm('Tem certeza que deseja remover este arquivo?')) return;

    try {
        const res = await fetch(`/api/files/${fileId}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            await loadUserFiles();
            await loadStats();
        } else {
            alert('Erro ao excluir arquivo.');
        }
    } catch (err) {
        alert('Erro ao excluir arquivo.');
    }
}

// ==================== HELPERS ====================

function handleCellClick(dateStr, e) {
    openCreateModal(dateStr);
}

function autoAssignColor(type, colorInputId) {
    const input = document.getElementById(colorInputId);
    if (input && TYPE_COLORS[type]) {
        input.value = TYPE_COLORS[type];
    }
}

function formatDateYMD(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function getWeekStart(d) {
    const date = new Date(d);
    const day = date.getDay();
    const diff = date.getDate() - day; // Domingo como início
    return new Date(date.setDate(diff));
}

// ==================== MODAL DE PRIVACIDADE E DIREITOS LGPD ====================

function openLgpdModal() {
    const modal = document.getElementById('lgpdModal');
    if (modal) {
        modal.classList.remove('hidden');
        if (window.lucide) lucide.createIcons();
    }
}

function closeLgpdModal() {
    const modal = document.getElementById('lgpdModal');
    if (modal) modal.classList.add('hidden');
}

async function handleDeleteAccountLgpd() {
    const confirmed = window.confirm('Excluir permanentemente sua conta, todos os seus compromissos e todos os seus arquivos? Esta a\u00e7\u00e3o n\u00e3o pode ser desfeita.');
    if (!confirmed) return;

    try {
        const res = await fetch('/api/user/delete-account', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        const data = await res.json().catch(() => ({}));

        if (res.ok && data.success) {
            alert(data.message || 'Sua conta e seus dados foram exclu\u00eddos.');
            window.location.href = '/login';
        } else {
            alert(data.error || `N\u00e3o foi poss\u00edvel excluir a conta (erro ${res.status}). Tente novamente.`);
        }
    } catch (err) {
        alert('N\u00e3o foi poss\u00edvel conectar ao servidor. Verifique sua conex\u00e3o e tente novamente.');
    }
}
