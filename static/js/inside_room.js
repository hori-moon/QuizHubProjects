document.addEventListener("DOMContentLoaded", function () {
  // コピー機能（IDで指定）
  document.querySelectorAll(".dli-copy").forEach(function (copyBtn) {
    copyBtn.addEventListener("click", function () {
      const targetId = copyBtn.getAttribute("data-copy-target");

      let text;
      if (targetId === "room-password") {
        text = document.getElementById("real-password")?.value;
      } else {
        const input = document.getElementById(targetId);
        text = input?.value || input?.textContent;
      }

      if (text) {
        navigator.clipboard.writeText(text)
          .then(() => showToast())
          .catch(() => showToast("コピーに失敗しました"));
      }
    });
  });
});

function togglePassword() {
  const field = document.getElementById("room-password");
  const realPassword = document.getElementById("real-password").value;

  if (field.textContent === "*****") {
    field.textContent = realPassword;
  } else {
    field.textContent = "*****";
  }
}

function showToast(message = "Copied!") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");

  // 一定時間後に非表示にする
  setTimeout(() => {
    toast.classList.remove("show");
  }, 2000);
}

function showAddFolderPrompt() {
}

function showDeleteOptions(folderId) {
}

