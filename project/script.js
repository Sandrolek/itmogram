document.addEventListener('DOMContentLoaded', () => {
    const rooms = document.querySelectorAll('.room-item');
    const roomsPerPage = 4;
    const totalPages = Math.ceil(rooms.length / roomsPerPage);
    let currentPage = 1;

    function showPage(page) {
        const start = (page - 1) * roomsPerPage;
        const end = start + roomsPerPage;
        rooms.forEach((room, index) => {
            room.style.display = (index >= start && index < end) ? 'block' : 'none';
        });
        document.getElementById('current-page').textContent = page;
        document.getElementById('total-pages').textContent = totalPages;
        document.getElementById('prev-page').disabled = (page === 1);
        document.getElementById('next-page').disabled = (page === totalPages);
    }

    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    });

    showPage(currentPage);
});