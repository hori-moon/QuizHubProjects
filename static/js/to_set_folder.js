document.addEventListener("DOMContentLoaded", function () {
    // 送信ボタンとローディング画面要素
    const submitButton = document.getElementById("submit-quiz-btn");
    const loadingOverlay = document.getElementById("loading-overlay");

    // ローディング表示の関数
    function showLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "flex";
    }
    function hideLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "none";
    }

    const createBtn = document.getElementById("create-folder-btn");
    const newFolderInput = document.getElementById("new-folder-name");
    const folderRadioInputs = document.getElementsByName("selected_folder");
    const form = document.getElementById("add-to-folder-form");

    // 新しいフォルダーの作成処理（デモ用：本番はfetchでPOSTなど）
    createBtn.addEventListener("click", () => {
        const folderName = newFolderInput.value.trim();
        if (!folderName) {
            alert("フォルダー名を入力してください。");
            return;
        }
        // ここにfetchなどでフォルダー作成APIを呼び出す処理を記述
        alert(`フォルダー "${folderName}" を作成しました（デモ）`);
        newFolderInput.value = "";
    });

    // 問題を送信する際、フォルダーが選ばれているかチェック
    form.addEventListener("submit", (e) => {
        const selected = Array.from(folderRadioInputs).some(
            (input) => input.checked
        );
        if (!selected) {
            e.preventDefault();
            alert("フォルダーを選択してください。");
        }
    });
});
