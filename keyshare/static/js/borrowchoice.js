function getParameterByName(name) {
    return new URLSearchParams(window.location.search).get(name);
}

function parseJSON(str) {
    return str ? JSON.parse(str) : {};
}

function createButtons(jsonData) {
    const container = document.getElementById('buttonContainer');
    
    if (!container) {
        console.error('Button container element not found');
        return;
    }

    Object.entries(jsonData).forEach(([key, value]) => {
        const [displayText, buttonId, isEnabled] = value.split(',');
        
        const button = document.createElement('button');
        button.textContent = displayText;
        button.id = buttonId;
        if (isEnabled == 1) {
            button.disabled = false;
        } else {
            button.disabled = true;
        }

        button.addEventListener('click', () => {
            parent.postMessage("doneselect" + button.id, '*')
        });

        // Create a new div for each button
        const buttonWrapper = document.createElement('div');
        buttonWrapper.className = 'button-wrapper';
        container.appendChild(buttonWrapper);

        buttonWrapper.appendChild(button);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const textValue = getParameterByName('buttonjson').replaceAll("'", '"');

    const username = getParameterByName('username');

    document.getElementById('usernameslot').textContent = username;

    const jsonData = parseJSON(textValue);

    if (Object.keys(jsonData).length > 0) {
        createButtons(jsonData);
    } else {
        console.log('No valid JSON data provided');
    }
});
