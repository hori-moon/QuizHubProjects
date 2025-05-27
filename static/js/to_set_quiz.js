document.addEventListener("DOMContentLoaded", function () {
    const totalQuestions = parseInt(document.getElementById("question-count").value, 10);
    const submitButton = document.getElementById("submit-quiz-btn");

    const loadingOverlay = document.getElementById("loading-overlay");
    function showLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "flex";
    }
    function hideLoading() {
        if (loadingOverlay) loadingOverlay.style.display = "none";
    }

    const slides = document.querySelectorAll(".quiz-slide");
    let current = 0;

    function showSlide(index) {
        slides.forEach((s, i) => s.style.display = i === index ? "block" : "none");
    }

    document.getElementById("prev-quiz").addEventListener("click", () => {
        if (current > 0) current--;
        showSlide(current);
        validateForm();
    });

    document.getElementById("next-quiz").addEventListener("click", () => {
        if (current < slides.length - 1) current++;
        showSlide(current);
        validateForm();
    });

    showSlide(current);
    validateForm();

    function switchAnswerInput(questionIndex, type) {
        const container = document.getElementById(`answer_container_${questionIndex}`);
        if (!container) return;

        container.innerHTML = `<label for="answer_${questionIndex}">解答:</label><br>`;

        if (type === "text" || type === "image") {
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
            const textarea = document.createElement("textarea");
            textarea.id = `answer_${questionIndex}`;
            textarea.name = `answer_${questionIndex}`;
            textarea.rows = 2;
            textarea.cols = 50;
            textarea.required = true;
            textarea.addEventListener("input", validateForm);
            container.appendChild(textarea);
        }
    }

    for (let i = 1; i <= totalQuestions; i++) {
        const radios = document.querySelectorAll(`input[name="choice_type_${i}"]`);
        const textGroup = document.getElementById(`text_choices_group_${i}`);
        const imageGroup = document.getElementById(`image_choices_group_${i}`);

        radios.forEach(rb => {
            rb.addEventListener("change", () => {
                const value = document.querySelector(`input[name="choice_type_${i}"]:checked`).value;
                switchAnswerInput(i, value);

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

                validateForm();
            });
        });

        switchAnswerInput(i, "none");

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
                else {
                    const input = document.createElement("input");
                    input.type = "file";
                    input.name = `image_choices_${i}`;
                    input.accept = "image/*";
                    input.addEventListener("change", validateForm);
                    wrapper.appendChild(label);
                    wrapper.appendChild(input);
                }

                container.appendChild(wrapper);
            }
        };

        const textInput = document.getElementById(`text_num_choices_${i}`);
        if (textInput) {
            textInput.addEventListener("input", () => renderChoices("text"));
            renderChoices("text");
        }

        const imageInput = document.getElementById(`image_num_choices_${i}`);
        if (imageInput) {
            imageInput.addEventListener("input", () => renderChoices("image"));
            renderChoices("image");
        }
    }

    function validateForm() {
        let allValid = true;

        for (let i = 1; i <= totalQuestions; i++) {
            const questionField = document.getElementById(`question_${i}`);
            const answerField = document.getElementById(`answer_${i}`);

            if (questionField) {
                questionField.addEventListener("input", validateForm);
            }

            if (!questionField || questionField.value.trim() === "") allValid = false;
            if (!answerField || answerField.value.trim() === "") allValid = false;

            const choiceType = document.querySelector(`input[name="choice_type_${i}"]:checked`)?.value;

            if (choiceType === "text") {
                const choices = document.querySelectorAll(`#dynamic_text_choices_${i} textarea`);
                const textGroup = document.getElementById(`text_choices_group_${i}`);
                if (textGroup && textGroup.style.display !== "none") {
                    choices.forEach(choice => {
                        if (choice.value.trim() === "") allValid = false;
                    });
                }
            } else if (choiceType === "image") {
                const choices = document.querySelectorAll(`#dynamic_image_choices_${i} input[type="file"]`);
                const imageGroup = document.getElementById(`image_choices_group_${i}`);
                if (imageGroup && imageGroup.style.display !== "none") {
                    choices.forEach(choice => {
                        if (!choice.files || choice.files.length === 0) allValid = false;
                    });
                }
            }
            // choiceType が none のときは選択肢チェックはスキップ
        }

        submitButton.style.display = allValid ? "block" : "none";
    }


    validateForm();

    document.getElementById("quiz-form").addEventListener("submit", (e) => {
        slides.forEach(slide => {
            if (slide.style.display === "none") {
                slide.querySelectorAll("[required]").forEach(input => {
                    input.dataset.originalRequired = "true";
                    input.required = false;
                });
            }
        });

        showLoading();
    });
});
