document.addEventListener("DOMContentLoaded", function () {
    // HTML要素を取得
    const upForm = document.getElementById("upload-form");            // アップロードフォーム
    const fileInput = document.getElementById("file-input");          // 画像ファイル選択用
    const previewImage = document.getElementById("preview-image");    // プレビュー表示用の画像タグ
    const okButton = document.getElementById("crop-ok");              // トリミング確定ボタン
    const resultBox = document.querySelector(".result-box");          // OCR結果表示用ボックス
    const textarea = document.getElementById("ocr-result");           // OCR結果表示用テキストエリア
    const loadingOverlay = document.getElementById("loading-overlay");
    let cropper; // Cropper.js インスタンス

    // ロード画面の表示・非表示を制御する関数
    function showLoading() {
        loadingOverlay.style.display = "flex";
    }
    function hideLoading() {
        loadingOverlay.style.display = "none";
    }

    // ファイル選択時の処理
    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const fileType = file.type;

        if (fileType === "application/pdf") {
            // PDF処理
            const fileReader = new FileReader();
            fileReader.onload = function () {
                const typedarray = new Uint8Array(this.result);

                pdfjsLib.getDocument(typedarray).promise.then(function (pdf) {
                    // 1ページ目だけを対象
                    pdf.getPage(1).then(function (page) {
                        const scale = 1.5;
                        const viewport = page.getViewport({ scale: scale });

                        const canvas = document.createElement("canvas");
                        const context = canvas.getContext("2d");
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;

                        const renderContext = {
                            canvasContext: context,
                            viewport: viewport
                        };

                        page.render(renderContext).promise.then(function () {
                            const imageDataUrl = canvas.toDataURL("image/png");
                            previewImage.src = imageDataUrl;
                            previewImage.style.display = "block";
                            okButton.style.display = "inline-block";

                            if (cropper) cropper.destroy();
                            cropper = new Cropper(previewImage, {
                                viewMode: 1,
                                aspectRatio: NaN,
                                autoCropArea: 1.0,
                            });

                            upForm.style.display = "none";
                        });
                    });
                });
            };
            fileReader.readAsArrayBuffer(file);
        } else if (fileType.startsWith("image/")) {
            // 画像処理
            const reader = new FileReader();
            reader.onload = function (event) {
                previewImage.src = event.target.result;
                previewImage.style.display = "block";
                okButton.style.display = "inline-block";

                if (cropper) cropper.destroy();
                cropper = new Cropper(previewImage, {
                    viewMode: 1,
                    aspectRatio: NaN,
                    autoCropArea: 1.0,
                });

                upForm.style.display = "none";
            };
            reader.readAsDataURL(file);
        } else {
            alert("対応していないファイル形式です。画像またはPDFを選択してください。");
        }
    });


    // 「OK」ボタンがクリックされたときの処理
    okButton.addEventListener("click", function () {
        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas();
        const croppedImage = canvas.toDataURL();

        textarea.value = ""; // テキストエリアをクリア
        showLoading(); // ロード画面表示
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
                hideLoading(); // ロード画面非表示
            })
            .catch((error) => {
                console.error("エラー:", error);
                resultBox.textContent = "エラーが発生しました";
                hideLoading(); // ロード画面非表示
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
