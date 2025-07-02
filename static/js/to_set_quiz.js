document.addEventListener("DOMContentLoaded", function () {
    // 総問題数の取得
    const totalQuestions = parseInt(document.getElementById("question-count").value, 10);

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

    // スライド形式のUI制御
    const slides = document.querySelectorAll(".quiz-slide");
    let current = 0;

    function showSlide(index) {
        slides.forEach((s, i) => s.style.display = i === index ? "block" : "none");
    }

    // 前へボタンの挙動
    document.getElementById("prev-quiz").addEventListener("click", () => {
        if (current > 0) current--;
        showSlide(current);
        validateForm();
    });

    // 次へボタンの挙動
    document.getElementById("next-quiz").addEventListener("click", () => {
        if (current < slides.length - 1) current++;
        showSlide(current);
        validateForm();
    });

    // 最初のスライドを表示
    showSlide(current);
    validateForm();

    // 解答欄を選択肢形式に応じて切り替える関数
    function switchAnswerInput(questionIndex, type) {
        const container = document.getElementById(`answer_container_${questionIndex}`);
        if (!container) return;

        // 中身を初期化し、ラベルを挿入
        container.innerHTML = `<label for="answer_${questionIndex}">解答:</label><br>`;

        // 選択肢ありの場合（テキストまたは画像）
        if (type === "text") {
            const input = document.createElement("input");
            input.type = "text";
            input.id = `answer_${questionIndex}`;
            input.name = `answer_${questionIndex}`;
            input.placeholder = "例: 1,3";
            input.pattern = "[0-9,]+";
            input.required = true;
            input.addEventListener("input", validateForm);
            container.appendChild(input);
        } else {
            // 記述式など（選択肢なし）の場合
            const textarea = document.createElement("textarea");
            textarea.id = `answer_${questionIndex}`;
            textarea.name = `answer_${questionIndex}`;
            textarea.rows = 2;
            textarea.cols = 50;
            textarea.required = true;
            textarea.addEventListener("input", validateForm);
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = `is_answer_${questionIndex}`;
            checkbox.name = `is_answer_${questionIndex}`;
            checkbox.checked = true; // デフォルトでチェック
            const span = document.createElement("span");
            span.textContent = "この回答は完答ですか？";
            container.appendChild(textarea);
            container.appendChild(document.createElement("br"));
            container.appendChild(checkbox);
            container.appendChild(span);
        }
    }

    // 各設問ごとの初期設定
    for (let i = 1; i <= totalQuestions; i++) {
        const radios = document.querySelectorAll(`input[name="choice_type_${i}"]`);
        const textGroup = document.getElementById(`text_choices_group_${i}`);

        // ラジオボタンの変更に応じて入力欄切り替え
        radios.forEach(rb => {
            rb.addEventListener("change", () => {
                const value = document.querySelector(`input[name="choice_type_${i}"]:checked`).value;
                switchAnswerInput(i, value);

                // 選択肢の表示切り替え
                if (value === "text") {
                    textGroup.style.display = "block";
                    imageGroup.style.display = "none";
                } else {
                    textGroup.style.display = "none";
                    imageGroup.style.display = "none";
                }

                validateForm();
            });
        });

        // 初期状態では選択肢なし
        switchAnswerInput(i, "none");

        // 選択肢を描画する関数（テキスト or 画像）
        const renderChoices = (type) => {
            const numInput = document.getElementById(`${type}_num_choices_${i}`);
            const container = document.getElementById(`dynamic_${type}_choices_${i}`);
            if (!numInput || !container) return;

            const num = parseInt(numInput.value, 10) || 2;
            container.innerHTML = "";

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
                    textarea.addEventListener("input", validateForm);
                    wrapper.appendChild(label);
                    wrapper.appendChild(textarea);
                }

                container.appendChild(wrapper);
            }
        };

        // 選択肢数の変更に応じて描画
        const textInput = document.getElementById(`text_num_choices_${i}`);
        if (textInput) {
            textInput.addEventListener("input", () => renderChoices("text"));
            renderChoices("text");
        }
    }

    // フォーム全体のバリデーションチェック
    function validateForm() {
        let allValid = true;

        for (let i = 1; i <= totalQuestions; i++) {
            const questionField = document.getElementById(`question_${i}`);
            const answerField = document.getElementById(`answer_${i}`);

            // 問題文の変更に合わせて再度validateFormを呼ぶようにする
            if (questionField) {
                questionField.addEventListener("input", validateForm);
            }

            // 問題文・解答欄の中身が空ならNG
            if (!questionField || questionField.value.trim() === "") allValid = false;
            if (!answerField || answerField.value.trim() === "") allValid = false;

            // 選択肢の内容もチェック（選択されていない場合は無視）
            const choiceType = document.querySelector(`input[name="choice_type_${i}"]:checked`)?.value;

            if (choiceType === "text") {
                const choices = document.querySelectorAll(`#dynamic_text_choices_${i} textarea`);
                const textGroup = document.getElementById(`text_choices_group_${i}`);
                if (textGroup && textGroup.style.display !== "none") {
                    choices.forEach(choice => {
                        if (choice.value.trim() === "") allValid = false;
                    });
                }
            }
        }

        // 全ての問題が有効な場合のみ送信ボタンを表示
        submitButton.style.display = allValid ? "block" : "none";
    }

    // 最終確認としてもう一度呼ぶ
    validateForm();

    // フォーム送信時、非表示スライドのrequired属性を一時的に解除
    document.getElementById("quiz-form").addEventListener("submit", (e) => {
        slides.forEach(slide => {
            if (slide.style.display === "none") {
                slide.querySelectorAll("[required]").forEach(input => {
                    input.dataset.originalRequired = "true";
                    input.required = false;
                });
            }
        });

        // ローディング画面を表示
        showLoading();
    });
});
