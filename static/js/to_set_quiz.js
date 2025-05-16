document.addEventListener("DOMContentLoaded", function () {
    const loadingOverlay = document.getElementById("loading-overlay");

    // ロード画面の表示・非表示を制御する関数
    function showLoading() {
        loadingOverlay.style.display = "flex";
    }
    function hideLoading() {
        loadingOverlay.style.display = "none";
    }

    const questionTextarea = document.getElementById("question");
    const choicesTextarea = document.getElementById("choices");
    const answerTextarea = document.getElementById("answer");


    // textarea の高さを自動調整する関数
    function autoResizeTextarea(textarea) {
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    }

    // questionTextarea の初期高さを設定
    questionTextarea.addEventListener("input", function () {
        autoResizeTextarea(questionTextarea);
    });

    // choicesTextarea の初期高さを設定
    choicesTextarea.addEventListener("input", function () {
        autoResizeTextarea(choicesTextarea);
    });

    // textarea の初期高さを設定
    answerTextarea.addEventListener("input", function () {
        autoResizeTextarea(answerTextarea);
    });

    const radioButtons = document.getElementsByName('choice_type');
    const textGroup = document.getElementById('text_choices_group');
    const imageGroup = document.getElementById('image_choices_group');

    function updateChoiceInput() {
        const selected = document.querySelector('input[name="choice_type"]:checked').value;

        if (selected === 'none') {
            textGroup.style.display = 'none';
            imageGroup.style.display = 'none';
        } else if (selected === 'text') {
            textGroup.style.display = 'block';
            imageGroup.style.display = 'none';
        } else if (selected === 'image') {
            textGroup.style.display = 'none';
            imageGroup.style.display = 'block';
        }
    }

    // 初期状態設定＋イベントリスナー登録
    radioButtons.forEach(btn => btn.addEventListener('change', updateChoiceInput));
    updateChoiceInput();  // 初期化

});
