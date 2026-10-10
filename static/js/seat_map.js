// State
let myTicket = null; // { id, seat_id, row, number, expires_at }
let timerInterval = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadSeatMap();
    // Auto-refresh every 5 seconds (if there is no active reservation)
    setInterval(() => { if (!myTicket) loadSeatMap(); }, 5000);
});

async function loadSeatMap() {
    try {
        const res = await fetch(`/sessions/${window.SESSION_ID}/seats`);
        const data = await res.json();
        renderSeatMap(data.seats);
    } catch (e) {
        console.error('Error loading schema:', e);
    }
}

function renderSeatMap(seats) {
    const map = document.getElementById('seat-map');
    map.innerHTML = '';

    // Group by rows
    const rows = {};
    seats.forEach(s => {
        if (!rows[s.row]) rows[s.row] = [];
        rows[s.row].push(s);
    });

    Object.keys(rows).sort((a, b) => a - b).forEach(rowNum => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'seat-row';

        const label = document.createElement('span');
        label.className = 'row-label';
        label.textContent = rowNum;
        rowDiv.appendChild(label);

        rows[rowNum].sort((a, b) => a.number - b.number).forEach(seat => {
            const btn = document.createElement('button');
            btn.className = 'seat';
            btn.textContent = seat.number;
            btn.dataset.seatId = seat.id;

            // Define the class
            if (seat.status === 'available') {
                btn.classList.add('available');
                btn.onclick = () => reserveSeat(seat);
            } else if (seat.status === 'reserved' && seat.is_mine) {
                btn.classList.add('mine');
                btn.onclick = () => releaseSeat();
                // Remember our reservation
                if (!myTicket || myTicket.seat_id !== seat.id) {
                    myTicket = {
                        seat_id: seat.id,
                        row: seat.row,
                        number: seat.number,
                        ttl: seat.ttl
                    };
                    showActionPanel();
                    startTimer(seat.ttl);
                }
            } else if (seat.status === 'reserved') {
                btn.classList.add('reserved-other');
                btn.title = 'Taken by another user';
            } else {
                btn.classList.add('taken');
                btn.title = 'Sold';
            }

            rowDiv.appendChild(btn);
        });

        // Mirror label on the right
        const label2 = label.cloneNode(true);
        rowDiv.appendChild(label2);

        map.appendChild(rowDiv);
    });
}

async function reserveSeat(seat) {
    const loader = document.getElementById('loader');
    loader.classList.remove('d-none');
    try {
        const res = await fetch(`/sessions/${window.SESSION_ID}/reserve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seat_id: seat.id })
        });
        const data = await res.json();
        if (!res.ok) {
            alert(data.error || 'Failed to reserve');
            await loadSeatMap();
            return;
        }
        // Success - update the schema
        myTicket = {
            id: data.ticket_id,
            seat_id: seat.id,
            row: seat.row,
            number: seat.number,
            ttl: data.ttl
        };
        showActionPanel();
        startTimer(data.ttl);
        await loadSeatMap();
    } catch (e) {
        alert('Network error');
    } finally {
        loader.classList.add('d-none');
    }
}

async function releaseSeat() {
    if (!myTicket || !myTicket.id) return;
    if (!confirm('Cancel reservation?')) return;
    try {
        await fetch(`/tickets/${myTicket.id}/release`, { method: 'POST' });
        myTicket = null;
        stopTimer();
        hideActionPanel();
        await loadSeatMap();
    } catch (e) {
        alert('Cancel error');
    }
}

function showActionPanel() {
    const panel = document.getElementById('action-panel');
    const info = document.getElementById('selected-info');
    const payBtn = document.getElementById('btn-pay');
    panel.classList.remove('d-none');
    info.textContent = `row ${myTicket.row}, place ${myTicket.number}`;
    payBtn.href = `/tickets/${myTicket.id}/payment`;
}

function hideActionPanel() {
    document.getElementById('action-panel').classList.add('d-none');
    document.getElementById('timer-box').classList.add('d-none');
}

function startTimer(seconds) {
    stopTimer();
    document.getElementById('timer-box').classList.remove('d-none');
    let left = seconds;
    const el = document.getElementById('timer');
    const tick = () => {
        if (left <= 0) {
            stopTimer();
            alert('Reservation time has expired. Seat is back on sale.');
            myTicket = null;
            hideActionPanel();
            loadSeatMap();
            return;
        }
        const m = Math.floor(left / 60), s = left % 60;
        el.textContent = `${m}:${s.toString().padStart(2, '0')}`;
        left--;
    };
    tick();
    timerInterval = setInterval(tick, 1000);
}

function stopTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = null;
}
