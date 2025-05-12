document.addEventListener("DOMContentLoaded", function () {
    // HTML要素を取得
    const fileInput = document.getElementById("file-input");          // 画像ファイル選択用
    const previewImage = document.getElementById("preview-image");    // プレビュー表示用の画像タグ
    const okButton = document.getElementById("crop-ok");              // トリミング確定ボタン
    const resultBox = document.querySelector(".result-box");          // OCR結果表示用ボックス
    let cropper; // Cropper.js インスタンス

    // ファイル選択時の処理
    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0]; // 選択されたファイルを取得
        if (!file) return; // ファイルが選択されていなければ処理しない

        const reader = new FileReader();

        // ファイル読み込み完了時の処理
        reader.onload = function (event) {
            // 読み込んだ画像をプレビュー表示
            previewImage.src = event.target.result;
            previewImage.style.display = "block";
            okButton.style.display = "inline-block";

            // 既にCropperがある場合は破棄して新規作成
            if (cropper) cropper.destroy();
            cropper = new Cropper(previewImage, {
                viewMode: 1,         // 画像全体が表示されるモード
                aspectRatio: NaN,    // 縦横比は固定しない
                autoCropArea: 0.8,   // 初期選択範囲は画像の80%
            });
        };

        reader.readAsDataURL(file); // ファイルをBase64形式に読み込む
    });

    // 「OK」ボタンがクリックされたときの処理
    okButton.addEventListener("click", function () {
        if (!cropper) return; // Cropperが無ければ処理しない

        // トリミングされた画像をCanvasに変換
        const canvas = cropper.getCroppedCanvas();
        // Base64形式の画像データとして取得
        const croppedImage = canvas.toDataURL();

        // サーバーへ送信してOCR処理
        sendImageToServer(croppedImage);
    });

    // 画像をサーバーへ送信する関数
    function sendImageToServer(imageBase64) {
        fetch("/ocr/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(), // CSRFトークンを取得してヘッダーに追加
            },
            body: JSON.stringify({ image: imageBase64 }), // JSON形式で画像を送信
        })
            .then((response) => response.json()) // レスポンスをJSONとして解析
            .then((data) => {
                // OCR結果をテキストエリアに表示
                const textarea = document.getElementById("ocr-result");
                textarea.value = data.text || "認識できませんでした";
            })
            .catch((error) => {
                // 通信エラーなどが発生した場合
                console.error("エラー:", error);
                resultBox.textContent = "エラーが発生しました";
            });
    }

    // CookieからCSRFトークンを取得する関数（Django対策）
    function getCsrfToken() {
        const cookie = document.cookie.match("(^|;)\\s*csrftoken\\s*=\\s*([^;]+)");
        return cookie ? cookie.pop() : "";
    }
});
