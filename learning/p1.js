const userInput = "pyt";
console.log(userInput);

const hippo = "pycharm"
console.log(hippo.length);

const ar = ["Flask", "Python", "MySQL"]
console.log(ar[1])

const skill = {
    skillId : 102,
    skillName : "PyTorch"
    };
console.log(skill.skillName)

function showInput(text) {
    console.log(text);
}

showInput("pyt");



if (userInput === "") {
    console.log("No input");
} else {
    console.log("Search skills");
}

const II = "pyt";
function show(II){
    if (II === "ii"){
        console.log("IIF")
    }
    else {
        console.log("III")
    }
}

const skills = ["Python", "Pytest", "PyTorch"];

for (const skill of skills) {
    console.log(skill);
}

const hippo = document.querySelector("#skill-input");

hippo.addEventListener("input", function () {
    const userInput = hippo.value;
    console.log(userInput);
});

const suggestion = document.querySelector("#suggestion");

suggestion.textContent = "Python";

let timer;

input.addEventListener("input", function () {
    clearTimeout(timer);

    timer = setTimeout(function () {
        console.log(input.value);
    }, 250);
});

let hi;
input.addEventListener("input", function(){
    clearTimeout(hi)
    hi = setTimeout(function(){
        console.log("hippo");
    }, 250)

})


async function searchSkills(userInput) {
    const safeInput = encodeURIComponent(userInput);

    const response = await fetch(`/api/skills?q=${safeInput}`);

    const skills = await response.json();

    console.log(skills);
}

const skills = [
    { skill_id: 1, skill_name: "Python" },
    { skill_id: 2, skill_name: "Pytest" },
    { skill_id: 3, skill_name: "PyTorch" }
];

const suggestions = document.querySelector("#suggestions");

for (const skill of skills) {
    const button = document.createElement("button");

    button.textContent = skill.skill_name;

    suggestions.appendChild(button);
}

for (const skill of skills){
    const hip = document.createElement("button")
    button.textContent = skill.skill_name;
    suggestions.appendChild(hip)
}




const skill = {
    skill_id: 1,
    skill_name: "Python"
};

const button = document.createElement("button");
button.textContent = skill.skill_name;

button.addEventListener("click", function () {
    const selectedBox = document.querySelector("#selected-skills");

    const selectedSkill = document.createElement("span");
    selectedSkill.textContent = skill.skill_name;

    selectedSkill.dataset.skillId = skill.skill_id;

    selectedBox.append(selectedSkill);
});
































