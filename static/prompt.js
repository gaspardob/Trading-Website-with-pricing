const promptForm = document.getElementById("prompt-form");
const submitButton = document.getElementById("submit-button");
const questionButton = document.getElementById("question-button");
const messagesContainer = document.getElementById("messages-container");
const mainContainer = document.getElementById("main-container");
const prompto = document.getElementById("prompt");
const resetButton = document.getElementById("reset-button");
const aboutusContent = document.getElementById("about-us-content");


const appendHumanMessage = (message) => {
  const humanMessageElement = document.createElement("div");
  humanMessageElement.classList.add("message", "message-human");
  humanMessageElement.innerHTML = message;
  messagesContainer.appendChild(humanMessageElement);
};


// les suggestions 
function getStockSuggestions(input) {
  fetch(`/get_stock_suggestions?input=${input}`)
    .then(response => response.json())
    .then(suggestions => {
      const datalist = document.getElementById('stockSuggestions');
      datalist.innerHTML = "";

      for (const suggestion of suggestions.slice(0, 5)) {
        const option = document.createElement("option");
        option.value = suggestion;
        datalist.appendChild(option);
      }
    });
}

function getStockSuggestionsNoms(input){
  fetch(`/get_stock_suggestions_noms?input=${input}`)
    .then(response => response.json())
    .then(suggestions => {
      const datalist = document.getElementById('nomsSuggestions');
      datalist.innerHTML = "";

      for (const suggestion of suggestions.slice(0, 5)) {
        const option = document.createElement("option");
        option.value = suggestion;
        datalist.appendChild(option);
      }
    });

}
function getBuySuggestionsNoms(input){
  fetch(`/get_stock_suggestions?input=${input}`)
    .then(response => response.json())
    .then(suggestions => {
      const datalist = document.getElementById('buyStockSuggestions');
      datalist.innerHTML = "";

      for (const suggestion of suggestions.slice(0, 5)) {
        const option = document.createElement("option");
        option.value = suggestion;
        datalist.appendChild(option);
      }
    });

}

const inputText = document.getElementById("inputText");
const inputText2 = document.getElementById("inputText2");
const stock_name_buy = document.getElementById("stock_name_buy")

inputText.addEventListener('input', function() {
  const inputValue = inputText.value;
  getStockSuggestions(inputValue);
});

stock_name_buy.addEventListener('input', function() {
  const inputValue = stock_name_buy.value;
  getBuySuggestionsNoms(inputValue);
});

inputText2.addEventListener('input', function() {
  const inputValue = inputText2.value;
  getStockSuggestionsNoms(inputValue);
});



inputText2.addEventListener('blur', function () {
  const inputValue = inputText2.value;
  const suggestions = Array.from(document.getElementById('nomsSuggestions').options).map(option => option.value);
  
  if (inputValue !=="" && !suggestions.includes(inputValue)) {
    alert("Le nom n'est pas dans la liste des suggestions.");
    // Vous pouvez également ajouter du code pour réinitialiser la valeur du champ ou prendre d'autres mesures nécessaires.
  }
});

inputText.addEventListener('blur', function () {
  const inputValue = inputText.value;
  const suggestions = Array.from(document.getElementById('stockSuggestions').options).map(option => option.value);
  if (inputValue !=="" && !suggestions.includes(inputValue)) {
    alert("Le symbole n'est pas dans la liste des suggestions.");
    // Vous pouvez également ajouter du code pour réinitialiser la valeur du champ ou prendre d'autres mesures nécessaires.
  }
});


stock_name_buy.addEventListener('blur', function () {
  const inputValue = stock_name_buy.value;
  const suggestions = Array.from(document.getElementById('buyStockSuggestions').options).map(option => option.value);
  if (inputValue !=="" && !suggestions.includes(inputValue)) {
    alert("Le symbole n'est pas dans la liste des suggestions.");
    // Vous pouvez également ajouter du code pour réinitialiser la valeur du champ ou prendre d'autres mesures nécessaires.
  }
});
