const userInputSkill = document.querySelector("#skills")

let timer;
userInputSkill.addEventListener("input", function(){
    clearTimeout(timer);
    timer = setTimeout(async function(){
        const skillText = userInputSkill.value.trim();

        if (skillText.length < 2){
            return;
        }

        const requestUrl = "/api/skills?q=" + encodeURIComponent(skillText);
        const response = await fetch(requestUrl);
        const suggestions = await response.json();

        }, 300);
});


