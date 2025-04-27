// ページ読み込み完了後にイベントをセット
document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('file-input');
    
    // ファイルが選択されたときの処理
    fileInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            alert(`選択されたファイル名: ${file.name}`); // ファイル名をアラート表示
        }
    });
});
