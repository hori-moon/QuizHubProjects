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

    // textarea の初期高さを設定
    answerTextarea.addEventListener("input", function () {
        autoResizeTextarea(answerTextarea);
    });

    // 選択肢の種類に応じて表示する入力欄を切り替える関数
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


    // 選択肢がある場合の動的な選択肢入力欄の生成（文字）
    const numChoicesInput = document.getElementById('text_num_choices');
    const dynamicChoicesDiv = document.getElementById('dynamic_text_choices');

    // 選択肢入力欄を numChoicesInput の値だけ生成
    function renderChoices() {
        dynamicChoicesDiv.innerHTML = '';
        const num = parseInt(numChoicesInput.value, 10) || 2;
        for (let i = 0; i < num; i++) {
            const textarea = document.createElement('textarea');
            textarea.id = `choice_${i + 1}`;
            textarea.name = 'choices';
            textarea.rows = 2;
            textarea.cols = 50;
            textarea.placeholder = `選択肢${i + 1}：選択肢番号等は入力しないでください。`;
            textarea.style.display = 'block';
            textarea.style.marginBottom = '8px';
            // 高さ自動調整
            textarea.addEventListener('input', function () {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            });
            dynamicChoicesDiv.appendChild(textarea);
        }
    }

    numChoicesInput.addEventListener('input', renderChoices);
    renderChoices();

    // 選択肢がある場合の動的な選択肢入力欄の生成（画像）
    const numImageChoicesInput = document.getElementById('image_num_choices');
    const dynamicImageChoicesDiv = document.getElementById('dynamic_image_choices');
    // 選択肢入力欄を numChoicesInput の値だけ生成
    function renderImageChoices() {
        dynamicImageChoicesDiv.innerHTML = '';
        const num = parseInt(numImageChoicesInput.value, 10) || 2;
        for (let i = 0; i < num; i++) {
            const input = document.createElement('input');
            input.type = 'file';
            input.id = `image_choice_${i + 1}`;
            input.name = 'image_choices';
            input.accept = 'image/*';
            input.style.display = 'block';
            input.style.marginBottom = '8px';
            dynamicImageChoicesDiv.appendChild(input);
        }
    }
    numImageChoicesInput.addEventListener('input', renderImageChoices);
    renderImageChoices();
});
