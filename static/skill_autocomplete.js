const userInputSkill = document.querySelector("#skills")
const selectedSkillsBox = document.querySelector("#selected-skills");
const selectedSkillIds = new Set();

let timer;
userInputSkill.addEventListener("input", function(){
    clearTimeout(timer);
    const delay = userInputSkill.value.trim().length === 1 ? 400 : 300;
    timer = setTimeout(async function(){
        const skillText = userInputSkill.value.trim();

        if (skillText.length === 0){
            return;
        }

        const requestUrl = "/api/skills?q=" + encodeURIComponent(skillText);
        const response = await fetch(requestUrl)
        const suggestions = await response.json();

        const suggestionsBox = document.querySelector("#skill-suggestions");
        suggestionsBox.replaceChildren();
        for (const suggestion of suggestions) {
            const button = document.createElement("button");
            button.type = "button"
            button.textContent = suggestion.display_text;
            button.dataset.skill_id = suggestion.skill_id;

        button.addEventListener("click", function () {
            const skillId = String(suggestion.skill_id);

            if (selectedSkillIds.has(skillId)) {
                return;
            }

            const tag = document.createElement("span");
            tag.className = "skill-tag";

            const label = document.createElement("span");
            label.textContent = suggestion.display_text;

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.textContent = "×";

            const hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "skill_ids";
            hiddenInput.value = skillId;

            removeButton.addEventListener("click", function () {
                tag.remove();
                selectedSkillIds.delete(skillId);
            });

            tag.append(label, removeButton, hiddenInput);
            selectedSkillsBox.append(tag);
            selectedSkillIds.add(skillId);

            userInputSkill.value = "";
            suggestionsBox.replaceChildren();
            userInputSkill.focus();
        });

            suggestionsBox.appendChild(button);
        }
    }, delay);
});


