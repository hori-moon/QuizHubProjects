function jumpToPage() {
    const input = document.getElementById("page-input");
    const page = parseInt(input.value);
    if (!isNaN(page) && page >= 1) {
        const url = new URL(window.location.href);
        url.searchParams.set("page", page);
        window.location.href = url.toString();
    }
    return false;
}