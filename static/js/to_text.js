document.addEventListener("DOMContentLoaded", function () {
    // HTML要素を取得
    const upForm = document.getElementById("upload-form");            // アップロードフォーム
    const fileInput = document.getElementById("file-input");          // 画像ファイル選択用
    const previewImage = document.getElementById("preview-image");    // プレビュー表示用の画像タグ
    const okButton = document.getElementById("crop-ok");              // トリミング確定ボタン
    const resultBox = document.querySelector(".result-box");          // OCR結果表示用ボックス
    const textarea = document.getElementById("ocr-result");           // OCR結果表示用テキストエリア
    let cropper; // Cropper.js インスタンス

    // ファイル選択時の処理
    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0]; // 選択されたファイルを取得
        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (event) {
            previewImage.src = event.target.result;
            previewImage.style.display = "block";
            okButton.style.display = "inline-block";

            if (cropper) cropper.destroy();
            cropper = new Cropper(previewImage, {
                viewMode: 1,
                aspectRatio: NaN,
                autoCropArea: 0.8,
            });
        };

        reader.readAsDataURL(file);

        // upFormを見えないようにする
        upForm.style.display = "none";
    });

    // 「OK」ボタンがクリックされたときの処理
    okButton.addEventListener("click", function () {
        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas();
        const croppedImage = canvas.toDataURL();

        alert("文字起こし中です。しばらくお待ちください。");
        textarea.value = ""; // テキストエリアをクリア
        textarea.disabled = false; // テキストエリアを有効化
        sendImageToServer(croppedImage);
    });

    // 画像をサーバーへ送信する関数
    function sendImageToServer(imageBase64) {
        fetch("/ocr/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify({ image: imageBase64 }),
        })
            .then((response) => response.json())
            .then((data) => {
                textarea.value = data.text || "認識できませんでした";
                const placeholder = document.getElementById("placeholder-text");
                if (data.text) {
                    placeholder.style.display = "none";
                }
                autoResizeTextarea(textarea); // 高さを自動調整
            })
            .catch((error) => {
                console.error("エラー:", error);
                resultBox.textContent = "エラーが発生しました";
            });
    }

    // textarea の高さを自動調整する関数
    function autoResizeTextarea(textarea) {
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    }

    // ユーザーの手入力にも対応
    textarea.addEventListener("input", function () {
        autoResizeTextarea(textarea);
    });

    // CookieからCSRFトークンを取得する関数（Django対策）
    function getCsrfToken() {
        const cookie = document.cookie.match("(^|;)\\s*csrftoken\\s*=\\s*([^;]+)");
        return cookie ? cookie.pop() : "";
    }
});
