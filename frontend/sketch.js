// Sources and collaborator: P5.js library, ChatGPT, AJ

let printerReady = true;
let cooldown = 45;

// DOM elements.
let pageNumber = 1; // start with first page (or another page when testing!).

let pages = [];
let pagesLoaded = false;
let displayedPage = null;

let myName = "";
let currentInput = "";
let myCountry = "";

let answers = {};

let pageElements = [];

// Load page text from JSON
async function loadPages() {
  const response = await fetch("/questions_WSF.json");

  if (!response.ok)
    throw new Error(`Could not load questions json: ${response.status}`);

  return await response.json();
}

// Replace ${variable} with the matching value
function interpolate(text) {
  const replacements = {
    myName,
    currentInput,
    myCountry
  };

  return text.replace(/\$\{(\w+)\}/g, (_, variable) => {
    return replacements[variable] ?? "...";
  });
}

// Remove the current page from the screen
function clearPage() {
  for (const element of pageElements)
    element.remove();

  pageElements = [];
}

// Draw a normal text page
function drawTextPage(page) {
  clearPage();

  const styledText = createP(interpolate(page.text));

  styledText.position(
    width / 2 - 300,
    height / 2 - 100
  );

  styledText.class("lowlight");

  pageElements.push(styledText);

  if (page.input) {
    const styledInput = createP(interpolate(page.input));

    styledInput.position(
      width / 2 - 200,
      550
    );

    styledInput.class("lowlightSmall");

    pageElements.push(styledInput);
  }
}

// Draw the waiting page
function drawWaitingPage() {
  clearPage();

  const styledText = createP(
    `De printer is nog niet klaar om je bon uit te printen. ` +
    `Wacht nog even, dit duurt ongeveer ${cooldown} seconden.`
  );

  styledText.position(width / 2 - 200, 550);
  styledText.class("lowlightSmall");

  pageElements.push(styledText);
}

// Draw the error page
function drawErrorPage() {
  clearPage();

  const styledText = createP(
    `Er is iets verkeerd gegaan, waarschijnlijk is de printer ` +
    `vastgelopen :( <br><br>` +
    `Druk op Enter om naar de startpagina te gaan`
  );

  styledText.position(width / 2 - 200, 550);
  styledText.class("lowlightSmall");

  pageElements.push(styledText);
}

// Create all pages
function createPages(data) {
  pages = data.pages;

  // Add waiting and error pages
  pages.push({
    waiting: true
  });

  pages.push({
    error: true,
    next: 1
  });

  pagesLoaded = true;

  console.log("Pages loaded:", pages);
}

// Go to page n, with obvershoot prevention
function goToPage(n) {
  pageNumber = constrain(n, 1, pages.length - 2);
}

//p5
function setup() {
  console.log("SETUP RUNNING");

  createCanvas(900, 700);

  loadPages()
    .then(data => {
      createPages(data);
    })
    .catch(error => {
      console.error("Failed to load pages:", error);
    });
}

//p5
function draw() {
  background(0);

  if (!pagesLoaded) {
    fill(255);
    textAlign(CENTER, CENTER);
    textSize(32);
    text("Loading...", width / 2, height / 2);
    return;
  }

  drawPageNavigation();

  // Only redraw the page when the page changes
  if (displayedPage !== pageNumber) {
    displayedPage = pageNumber;

    const page = pages[pageNumber - 1];

    if (!page) {
      console.error("Page not found:", pageNumber);

      textAlign(CENTER, CENTER);
      textSize(24);
      text("Page Not Found", width / 2, height / 2);

      return;
    }

    if (page.waiting) {
      drawWaitingPage();
    }
    else if (page.error) {
      drawErrorPage();
    }
    else {
      drawTextPage(page);
    }
  }

  fill(255);
  text(`mouseX:${mouseX}, mouseY:${mouseY}`, 200, 20);
}

// Instructions for navigation
function drawPageNavigation() {
  fill(255);
  textSize(16);
  textAlign(LEFT, BOTTOM);
  textAlign(RIGHT, BOTTOM);
}

// Handle special key inputs
function handlePageWithProperty(key, page) {
  if (!page?.property) {
    return;
  }

  const property = page.property;

  const allowedInputs = {
    oneTwoThreeInput: ['1', '2', '3'],
    abcInput: ['a', 'b', 'c'],
    zeroNineInput: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
  };

  // Handle Backspace
  if (key === 'Backspace') {
    currentInput = currentInput.slice(0, -1);
    if (page.input)
      drawTextPage(page);

    return;
  }

  // Handle restricted single-character inputs
  if (allowedInputs[property]) {
    if (allowedInputs[property].includes(key)) {
      if (property === "zeroNineInput") {
        currentInput += key;
      }
      else {
        currentInput = key;
      }
      answers[`Q${pageNumber}`] = currentInput;

      drawTextPage(page);
    }
    return;
  }

  // Ignore keys that aren't valid text characters
  if (
    !['enterName', 'enterCountry', 'stringInput'].includes(property) ||
    key.length !== 1 ||
    key === 'Enter' ||
    key === 'Shift'
  ) {
    return;
  }

  // Add character and capitalize first letter
  currentInput += key;
  currentInput = currentInput.charAt(0).toUpperCase() + currentInput.slice(1);
  answers[`Q${pageNumber}`] = currentInput;

  if (page.input) {
    if (property === "enterName")
      myName = currentInput;

    if (property === "enterCountry")
      myCountry = currentInput;
  }
}

// Hanlde keypress
document.addEventListener("keydown", function (event) {
  const key = event.key;
  const page = pages[pageNumber - 1];

  // Previous page
  if (key === 'ArrowLeft') {
    goToPage(pageNumber - 1);
    event.preventDefault();
    return;
  }

  // Next / confirm
  if (key === 'Enter') {
    handleEnter(page, event);
    return;
  }

  // Printing
  if (page?.property === "final" && key.toLowerCase() === 'p') {
    if (sendAnswers() === false) {
      console.log("Tried to print while printer wasn't ready");
      pageNumber = pages.length - 1;
      displayedPage = null;
    }
    else {
      pageNumber = 1;
      displayedPage = null;
    }
    return;
  }

  // Input
  if (page?.property) {
    handlePageWithProperty(key, page);
  }
});

let randomQueue = [];
let randomNext = null;

function handleEnter(page, event) {
  event.preventDefault();

  // Start a random sequence
  if (page?.random) {
    randomQueue = [...page.random].sort(() => Math.random() - 0.5);
    randomNext = page.next ?? pageNumber + 1;

    goToPage(randomQueue.shift());
    currentInput = '';
    return;
  }

  // Continue random sequence
  if (randomQueue.length > 0) {
    goToPage(randomQueue.shift());
    currentInput = '';
    return;
  }

  // Random sequence finished
  if (randomNext !== null) {
    goToPage(randomNext);
    randomNext = null;
    currentInput = '';
    return;
  }

  // Normal navigation
  goToPage(page?.next ?? pageNumber + 1);
  currentInput = '';
}

function sendAnswers() {
  const payload = {
    flow: "festival",
    myName: myName,
    projectCountry: myCountry,
    answers: answers
  };

  console.log("payload: ", payload);

  if (printerReady === false)
    return false;

  printerReady = false;

  fetch("http://127.0.0.1:5000/submit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  }
  ).then(response => response.json()
  ).then(data => {
    console.log("Printer response:", data);

    cooldown = data.cooldown

    if (data.error === "FATAL") {
      console.error("FATAL: printer server needs manual restart");

      printerReady = false;
      pageNumber = pages.length - 1;
      displayedPage = null;
      return;
    }

    if (data.ready) {
      printerReady = true;
      myName = '';
      answers = {};

      console.log("Printer is ready again.");
    }
  })

    .catch(error => {
      console.error("Printer error:", error);

      printerReady = true;
      pageNumber = pages.length - 1;
      displayedPage = null;

      return;
    });

  return true;
}
