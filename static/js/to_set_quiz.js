document.addEventListener("DOMContentLoaded", function () {
    const totalQuestions = parseInt(document.getElementById("question-count").value, 10);
    const submitButton = document.getElementById("submit-quiz-btn");

    // 初期状態で問題作成ボタンを非表示にする
    submitButton.style.display = "none";

    // ローディング表示制御（必要に応じて使用）
    const loadingOverlay = document.getElementById("loading-overlay");
    function showLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "flex";
    }
    function hideLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "none";
    }

    // --- スライダー形式の問題表示制御 ---
    const slides = document.querySelectorAll(".quiz-slide");
    let current = 0;

    // 指定されたindexのスライドだけを表示する
    function showSlide(index) {
        slides.forEach((s, i) => s.style.display = i === index ? "block" : "none");
    }

    // 「前へ」ボタン処理
    document.getElementById("prev-quiz").addEventListener("click", () => {
        if (current > 0) current--;
        showSlide(current);
    });

    // 「次へ」ボタン処理
    document.getElementById("next-quiz").addEventListener("click", () => {
        if (current < slides.length - 1) current++;
        showSlide(current);
    });

    showSlide(current);  // 最初のスライドを表示

    // --- 解答欄の形式を選択肢形式に応じて切り替える ---
    function switchAnswerInput(questionIndex, type) {
        const container = document.getElementById(`answer_container_${questionIndex}`);
        if (!container) return;

        // 解答欄を一度リセット
        container.innerHTML = `<label for="answer_${questionIndex}">解答:</label><br>`;

        if (type === "text" || type === "image") {
            // 選択肢がある形式 → input（番号入力）
            const input = document.createElement("input");
            input.type = "text";
            input.id = `answer_${questionIndex}`;
            input.name = `answer_${questionIndex}`;
            input.placeholder = "例: 1,3";
            input.pattern = "[0-9,]+";
            input.required = true;
            container.appendChild(input);
        } else {
            // 記述式 → textarea
            const textarea = document.createElement("textarea");
            textarea.id = `answer_${questionIndex}`;
            textarea.name = `answer_${questionIndex}`;
            textarea.rows = 2;
            textarea.cols = 50;
            textarea.required = true;
            container.appendChild(textarea);
        }
    }

    // --- 各問題に対して選択肢入力欄の生成やイベント処理をセット ---
    for (let i = 1; i <= totalQuestions; i++) {
        const radios = document.querySelectorAll(`input[name="choice_type_${i}"]`);
        const textGroup = document.getElementById(`text_choices_group_${i}`);
        const imageGroup = document.getElementById(`image_choices_group_${i}`);

        // 選択肢形式が切り替えられたときの処理
        radios.forEach(rb => {
            rb.addEventListener("change", () => {
                const value = document.querySelector(`input[name="choice_type_${i}"]:checked`).value;
                switchAnswerInput(i, value);  // 解答欄を切り替える

                // 選択肢入力欄の表示制御
                if (value === "text") {
                    textGroup.style.display = "block";
                    imageGroup.style.display = "none";
                } else if (value === "image") {
                    textGroup.style.display = "none";
                    imageGroup.style.display = "block";
                } else {
                    textGroup.style.display = "none";
                    imageGroup.style.display = "none";
                }

                validateForm();  // 入力内容をチェック
            });
        });

        // 初期状態で「選択肢なし」の解答欄を表示
        switchAnswerInput(i, "none");

        // 選択肢の数に応じて入力欄を動的に生成
        const renderChoices = (type) => {
            const numInput = document.getElementById(`${type}_num_choices_${i}`);
            const container = document.getElementById(`dynamic_${type}_choices_${i}`);
            if (!numInput || !container) return;

            const num = parseInt(numInput.value, 10) || 2;
            container.innerHTML = "";  // 既存の選択肢をクリア

            for (let j = 0; j < num; j++) {
                const wrapper = document.createElement("div");
                wrapper.style.display = "flex";
                wrapper.style.alignItems = "center";
                wrapper.style.marginBottom = "8px";

                const label = document.createElement("span");
                label.textContent = `${j + 1}.`;
                label.style.marginRight = "8px";

                if (type === "text") {
                    const textarea = document.createElement("textarea");
                    textarea.name = `choices_${i}`;
                    textarea.rows = 2;
                    textarea.cols = 50;
                    textarea.required = true;
                    wrapper.appendChild(label);
                    wrapper.appendChild(textarea);
                } else {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.name = `image_choices_${i}`;
                    input.accept = "image/*";
                    input.required = true;
                    wrapper.appendChild(label);
                    wrapper.appendChild(input);
                }

                container.appendChild(wrapper);
            }
        };

        // テキスト選択肢数の入力欄と動的生成
        const textInput = document.getElementById(`text_num_choices_${i}`);
        if (textInput) {
            textInput.addEventListener("input", () => renderChoices("text"));
            renderChoices("text");  // 初期化
        }

        // 画像選択肢数の入力欄と動的生成
        const imageInput = document.getElementById(`image_num_choices_${i}`);
        if (imageInput) {
            imageInput.addEventListener("input", () => renderChoices("image"));
            renderChoices("image");  // 初期化
        }
    }

    // --- フォーム検証（問題文と解答がすべて入力されているか） ---
    function validateForm() {
        let allValid = true;

        for (let i = 1; i <= totalQuestions; i++) {
            const questionField = document.getElementById(`question_${i}`);
            const answerField = document.getElementById(`answer_${i}`);

            if (!questionField || questionField.value.trim() === "") allValid = false;
            if (!answerField || answerField.value.trim() === "") allValid = false;
        }

        // 全ての問題に必要項目が入力されていれば表示、それ以外は非表示
        submitButton.style.display = allValid ? "block" : "none";
    }

    // 入力欄に入力があるたびにvalidateFormを呼び出す
    for (let i = 1; i <= totalQuestions; i++) {
        const questionField = document.getElementById(`question_${i}`);
        const answerField = document.getElementById(`answer_${i}`);

        if (questionField) {
            questionField.addEventListener("input", validateForm);
        }
        if (answerField) {
            answerField.addEventListener("input", validateForm);
        }
    }

    // ページロード時に一度検証して初期状態を設定
    validateForm();
});
