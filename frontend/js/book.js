
window.Grimorio = window.Grimorio || {};

Grimorio.Book = (function () {
    const TOTAL_PAGES = 5;
    const pages = []; // { el, canvas, ctx }
    let currentIndex = 0;

    function init(stackElementId) {
        const stack = document.getElementById(stackElementId);

        for (let i = 0; i < TOTAL_PAGES; i++) {
            const pageEl = document.createElement('div');
            pageEl.className = 'page';
            pageEl.style.zIndex = TOTAL_PAGES - i;

            const canvas = document.createElement('canvas');
            canvas.width = 720;
            canvas.height = 480;
            pageEl.appendChild(canvas);

            const pn = document.createElement('div');
            pn.className = 'page-number';
            pn.textContent = 'fólio ' + (i + 1);
            pageEl.appendChild(pn);

            stack.appendChild(pageEl);
            pages.push({ el: pageEl, canvas, ctx: canvas.getContext('2d') });
        }
    }

    function goToPage(newIndex) {
        if (newIndex < 0 || newIndex >= pages.length || newIndex === currentIndex) return;

        if (newIndex > currentIndex) {
            pages[currentIndex].el.classList.add('flipped');
        } else {
            pages[newIndex].el.classList.remove('flipped');
        }
        currentIndex = newIndex;
    }

    function nextPage() { goToPage(currentIndex + 1); }
    function prevPage() { goToPage(currentIndex - 1); }

    function getCurrentPage() { return pages[currentIndex]; }

    function clearCurrentPage() {
        const p = getCurrentPage();
        p.ctx.clearRect(0, 0, p.canvas.width, p.canvas.height);
    }

    function getPages() { return pages; }
    function getCurrentIndex() { return currentIndex; }

    return {
        init,
        goToPage,
        nextPage,
        prevPage,
        getCurrentPage,
        clearCurrentPage,
        getPages,
        getCurrentIndex,
    };
})();