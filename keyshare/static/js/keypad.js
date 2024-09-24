document.addEventListener('DOMContentLoaded', () => {
    const keypad = document.querySelector('.keypad');
    const display = document.getElementById('display');
    const displayBox = document.getElementById('display');

    document.getElementById('ok').textContent = 'Cancel';

    function updateDisplay(value) {
        display.value += value;
    }

    function clearDisplay() {
        display.value = '';
    }

    function getdisplayContent() {
        return displayBox.value;
    }

    keypad.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON') {
            const value = event.target.value;

            if (value === 'clear') {
                clearDisplay();
                document.getElementById('ok').textContent = 'Cancel'
            } else if (value == 'ok') {
                parent.postMessage("doneinput" + getdisplayContent(), '*')
            } else {
                updateDisplay(value);
                document.getElementById('ok').textContent = 'OK'
            }
        }
    });
});

document.addEventListener('contextmenu', event => {
    event.preventDefault();
});