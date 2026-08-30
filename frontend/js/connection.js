
window.Grimorio = window.Grimorio || {};

Grimorio.Connection = (function (Book, Drawing) {
    const WS_URL = 'ws://localhost:8765';
    const RECONNECT_DELAY_MS = 1500;

    let statusDot, statusText, camFeed, camIdleText, penIndicator;

    function cacheElements() {
        statusDot = document.getElementById('statusDot');
        statusText = document.getElementById('statusText');
        camFeed = document.getElementById('camFeed');
        camIdleText = document.getElementById('camIdleText');
        penIndicator = document.getElementById('penIndicator');
    }

    function setConnected(isConnected) {
        statusDot.classList.toggle('on', isConnected);
        statusText.textContent = isConnected
            ? 'Conectado ao grimório — comece a escrever'
            : 'Sem conexão com o backend Python — reconectando...';

        if (!isConnected) {
            camFeed.classList.remove('live');
            camIdleText.style.display = 'flex';
        }
    }

    function handleUpdate(msg) {
        if (msg.frame) {
            camFeed.src = 'data:image/jpeg;base64,' + msg.frame;
            camFeed.classList.add('live');
            camIdleText.style.display = 'none';
        }

        penIndicator.classList.toggle('active', !!msg.pen_mode);

        if (msg.pen_mode && msg.fingertip) {
            Drawing.drawAt(msg.fingertip.x, msg.fingertip.y);
        } else {
            Drawing.releasePen();
        }
    }

    function handleGesture(msg) {
        if (msg.action === 'next_page') Book.nextPage();
        if (msg.action === 'prev_page') Book.prevPage();
        if (msg.action === 'clear_page') Book.clearCurrentPage();
    }

    function connect() {
        const ws = new WebSocket(WS_URL);

        ws.onopen = () => setConnected(true);
        ws.onclose = () => {
            setConnected(false);
            setTimeout(connect, RECONNECT_DELAY_MS);
        };
        ws.onerror = () => ws.close();

        ws.onmessage = (ev) => {
            const msg = JSON.parse(ev.data);
            if (msg.type === 'update') handleUpdate(msg);
            if (msg.type === 'gesture') handleGesture(msg);
        };
    }

    function init() {
        cacheElements();
        connect();
    }

    return { init };
})(Grimorio.Book, Grimorio.Drawing);