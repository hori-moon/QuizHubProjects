document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('file-input');
    const previewImage = document.getElementById('preview-image');
    const okButton = document.getElementById('crop-ok');
    const resultBox = document.querySelector('.result-box');
    let cropper;

    fileInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (event) {
            previewImage.src = event.target.result;
            previewImage.style.display = 'block';
            okButton.style.display = 'inline-block';

            if (cropper) cropper.destroy();  // 既存Cropperの破棄
            cropper = new Cropper(previewImage, {
                viewMode: 1,
                aspectRatio: NaN,
                autoCropArea: 0.8,
            });
        };
        reader.readAsDataURL(file);
    });

    okButton.addEventListener('click', function () {
        if (!cropper) return;
        const canvas = cropper.getCroppedCanvas();
        const croppedImage = canvas.toDataURL();

        sendImageToServer(croppedImage);
    });

    function sendImageToServer(imageBase64) {
        fetch('/ocr/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ image: imageBase64 })
        })
        .then(response => response.json())
        .then(data => {
            resultBox.textContent = data.text || '認識できませんでした';
        })
        .catch(error => {
            console.error('エラー:', error);
            resultBox.textContent = 'エラーが発生しました';
        });
    }

    function getCsrfToken() {
        const cookie = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return cookie ? cookie.pop() : '';
    }
});
