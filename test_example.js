// JavaScript example
const greeting = "Hello, World!";
let counter = 0;

function displayMessage() {
    // This is a comment
    console.log(greeting);

    for (let i = 0; i < 10; i++) {
        if (i % 2 === 0) {
            console.log(`Even number: ${i}`);
        }
    }
}

async function fetchData() {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    return data;
}

displayMessage();
