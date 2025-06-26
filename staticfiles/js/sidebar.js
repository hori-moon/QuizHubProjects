// サイドバーを開閉する関数
function toggleSidebar() {
    const sidebar = document.getElementById("mySidebar");
    const toggleBtn = document.querySelector(".toggle-btn");

    if (sidebar.classList.contains('open')) {
        // サイドバーが開いている場合、閉じる
        sidebar.classList.remove('open');
        toggleBtn.textContent = "☰"; // ボタンのアイコンを「三本線」に戻す
    } else {
        // サイドバーが閉じている場合、開く
        sidebar.classList.add('open');
        toggleBtn.textContent = "✖"; // ボタンのアイコンを「バツ」にする
    }
}
