
window.Grimorio = window.Grimorio || {};

Grimorio.Drawing = (function (Book) {
    let drawing = false;
    let lastPoint = null;

    function inkStroke(ctx, from, to) {
        ctx.save();
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        ctx.shadowColor = 'rgba(217,143,63,0.85)';
        ctx.shadowBlur = 10;
        ctx.strokeStyle = 'rgba(90,55,20,0.9)';
        ctx.lineWidth = 2.6;

        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
        ctx.restore();
    }

    function drawAt(normX, normY) {
        const page = Book.getCurrentPage();
        const x = normX * page.canvas.width;
        const y = normY * page.canvas.height;
        if (lastPoint) {
            inkStroke(page.ctx, lastPoint, { x, y });
        }
        lastPoint = { x, y };
    }

    function releasePen() { lastPoint = null; }

    function enableMouseTesting() {
        Book.getPages().forEach((p, idx) => {
            p.canvas.addEventListener('mousedown', e => {
                if (idx !== Book.getCurrentIndex()) return;
                drawing = true;
                const r = p.canvas.getBoundingClientRect();
                drawAt((e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height);
            });
            p.canvas.addEventListener('mousemove', e => {
                if (!drawing || idx !== Book.getCurrentIndex()) return;
                const r = p.canvas.getBoundingClientRect();
                drawAt((e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height);
            });
        });
        window.addEventListener('mouseup', () => { drawing = false; releasePen(); });
    }

    return {
        drawAt,
        releasePen,
        enableMouseTesting,
    };
})(Grimorio.Book);