document.addEventListener("DOMContentLoaded", function () {
    const upForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const previewImage = document.getElementById("preview-image");
    const okButton = document.getElementById("crop-ok");
    const resultBox = document.querySelector(".result-box");
    const placeholderText = document.getElementById("placeholder-text");
    const textarea = document.getElementById("ocr-result");
    const loadingOverlay = document.getElementById("loading-overlay");
    let cropper;

    function showLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "flex";
    }
    function hideLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "none";
    }

    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const fileType = file.type;
        if (fileType === "application/pdf") {
            const fileReader = new FileReader();
            fileReader.onload = function () {
                const typedarray = new Uint8Array(this.result);
                pdfjsLib.getDocument(typedarray).promise.then(function (pdf) {
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

    okButton.addEventListener("click", function () {
        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas();
        const croppedImage = canvas.toDataURL("image/png");

        textarea.value = "";
        showLoading();
        sendImageToServer(croppedImage);
    });

    function sendImageToServer(imageBase64) {
        function base64ToBlob(base64) {
            const byteString = atob(base64.split(',')[1]);
            const mimeString = base64.split(',')[0].split(':')[1].split(';')[0];
            const ab = new ArrayBuffer(byteString.length);
            const ia = new Uint8Array(ab);
            for (let i = 0; i < byteString.length; i++) {
                ia[i] = byteString.charCodeAt(i);
            }
            return new Blob([ab], { type: mimeString });
        }

        const blob = base64ToBlob(imageBase64);
        const formData = new FormData();
        formData.append("image", blob, "cropped.png");

        fetch("/ocr/", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
        })
            .then((response) => response.json())
            .then((data) => {
                textarea.value = data.text || "認識できませんでした";
                autoResizeTextarea(textarea);
                placeholderText.style.display = "none";
                hideLoading();
            })
            .catch((error) => {
                console.error("送信エラー:", error);
                hideLoading();
            });
    }

    function autoResizeTextarea(textarea) {
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    }

    textarea.addEventListener("input", function () {
        autoResizeTextarea(textarea);
        placeholderText.style.display = textarea.value.trim() === "" ? "block" : "none";
    });

    function getCsrfToken() {
        const cookie = document.cookie.match("(^|;)\\s*csrftoken\\s*=\\s*([^;]+)");
        return cookie ? cookie.pop() : "";
    }
});
