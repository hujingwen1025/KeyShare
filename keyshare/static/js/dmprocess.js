//DM Root Process
document.addEventListener('DOMContentLoaded', () => {
    localStorage.setItem("buttonpressing", 0)
    localStorage.setItem("loaderpresent", 0)

    function renderKeypad(inputlabel, callfunction) {
        const keypadslot = document.getElementById("keypadslot");
        const iframecode = `<iframe src="./keypad.html?inputlabel=${inputlabel}" id="keypadiframe"></iframe>`;
        keypadslot.insertAdjacentHTML("afterbegin", iframecode);
        const keypadiframe = document.getElementById('keypadiframe');
        window.onmessage = function(event) {
            if (event.data.startsWith("doneinput")) {
                document.getElementById("keypadiframe").remove();
                callfunction(event.data.replace('doneinput', ''));
                localStorage.setItem("buttonpressing", 0)
            }
        }
    }


    function renderDialog(title, body) {
        const diagslot = document.getElementById("diagslot");
        localStorage.setItem("buttonpressing", 1);
        diagslot.insertAdjacentHTML("afterbegin", `<dialog open id="dialog" class="diag"><h1>${title}</h1><p>${body}</p><center><button class="diagclosebutton" id="diagclosebutton">Close</button></center></dialog>`)
        var diagclosebutton = document.getElementById("diagclosebutton");
        diagclosebutton.addEventListener('click', function() {
            diagslot.removeChild(diagslot.children[0]);
            localStorage.setItem("buttonpressing", 0);
        })
    }

    function renderLoader() {
        const loaderslot = document.getElementById("loaderslot")
        if (localStorage.getItem("loaderpresent") == 0) {
            localStorage.setItem("loaderpresent", 1)
            loaderslot.insertAdjacentHTML("afterbegin", '<div class="loader"></div>')
        }
    }

    function removeLoader() {
        const loaderslot = document.getElementById("loaderslot")
        if (localStorage.getItem("loaderpresent") == 1) {
            loaderslot.removeChild(loaderslot.children[0]);
            localStorage.setItem("loaderpresent", 0)
        }
    }

    async function checkPin(pin) {
        if (pin == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/checkpin", {
                method: 'POST',
                body: JSON.stringify({
                    pin: pin
                }),
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const responseJson = await response.json();


            switch (responseJson.status) {
                case "transmiterr":
                    renderDialog("Error", "An error occurred while trying to reach data server");
                    break;
                case "ok":
                    renderDialog("OK", `username: ${responseJson.user}| userid: ${responseJson.userid}`);
                    break;
                case "hasherr":
                    renderDialog("Error", "An error occurred while trying to authenticate with the server");
                    break;
                case "err":
                    renderDialog("Error", `error: ${responseJson.errinfo}`);
                    break;
                case "unknownerr":
                    renderDialog("Error", "An unknown error occurred");
                    break;
                default:
                    renderDialog("Error", "Unit webserver encountered an error");
            }
            removeLoader()
        } catch (error) {
            console.error('Error:', error);
            renderDialog("Error", "An error occurred while requesting for pin check");
            removeLoader()
        }
        removeLoader()
    }


    const diagslot = document.getElementById("diagslot");
    var reportbutton = document.getElementById("reportbutton");
    reportbutton.addEventListener('click', function() {
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1);
            diagslot.insertAdjacentHTML("afterbegin", '<dialog open id="reportdialog" class="reportdiag"><center><img src="/static/resource/report.png"></center><br><center><h2>tinyurl.com/keysharers</h2><br><p>If you are reporting a broken borrowed item, please first scan the item</p><br><button class="diagclosebutton" id="diagclosebutton">Close</button></center></dialog>');
            var diagclosebutton = document.getElementById("diagclosebutton");
            diagclosebutton.addEventListener('click', function() {
                var diagslot = document.getElementById("diagslot");
                diagslot.removeChild(diagslot.children[0]);
                localStorage.setItem("buttonpressing", 0);
            })
        }
    })

    var borrowbutton = document.getElementById("borrowbutton");
    borrowbutton.addEventListener('click', function() {
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Identifacation PIN", checkPin)
        }
    }, false)

    var adminbutton = document.getElementById("adminbutton");
    adminbutton.addEventListener('click', function() {
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Admin PIN", alert)
        }
    }, false)

    var cardbutton = document.getElementById("cardbutton");
    cardbutton.addEventListener('click', function() {
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Card Bind Code", alert)
        }
    }, false)
});