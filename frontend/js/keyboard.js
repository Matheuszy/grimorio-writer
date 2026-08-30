window.Grimorio = window.Grimorio || {};

Grimorio.Keyboard = (function (Book) {
    function enable() {
        window.addEventListener('keydown', e => {
            if (e.key === 'ArrowRight') Book.nextPage();
            if (e.key === 'ArrowLeft') Book.prevPage();
            if (e.key.toLowerCase() === 'c') Book.clearCurrentPage();
        });
    }

    return { enable };
})(Grimorio.Book);