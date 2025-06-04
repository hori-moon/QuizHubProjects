document.addEventListener("DOMContentLoaded", function () {
    const usePasswordCheckbox = document.getElementById("use_password");
    const passwordField = document.getElementById("password_field");

    // チェックボックスの状態に応じてパスワード入力欄を表示/非表示
    usePasswordCheckbox.addEventListener("change", function () {
        if (usePasswordCheckbox.checked) {
            passwordField.style.display = "block";
        } else {
            passwordField.style.display = "none";
        }
    });

    // 初期状態で非表示
    if (!usePasswordCheckbox.checked) {
        passwordField.style.display = "none";
    }
});