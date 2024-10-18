//DM Root Process
document.addEventListener('DOMContentLoaded', () => {
    localStorage.setItem("buttonpressing", 0)
    localStorage.setItem("loaderpresent", 0)

    var cardBindNFC = false;
    var newCardNFC = "";

    function renderKeypad(inputlabel, callfunction) {
        const interactslot = document.getElementById("interactslot");
        const iframecode = `<iframe src="./keypad?inputlabel=${inputlabel}" id="keypadiframe"></iframe>`;
        interactslot.insertAdjacentHTML("afterbegin", iframecode);
        const keypadiframe = document.getElementById('keypadiframe');
        window.onmessage = function(event) {
            if (event.data.startsWith("doneinput")) {
                keypadiframe.remove();
                callfunction(event.data.replace('doneinput', ''));
                localStorage.setItem("buttonpressing", 0)
            }
        }
    }

    function closeDiag(){
        try {
            var diagclosebutton = document.getElementById("diagclosebutton");
            diagclosebutton.click();
        } catch (error) {
            console.log('nodiag');
        }
    }

    function renderBorrowChoice(username, borrowInfo, callfunction) {
        const interactslot = document.getElementById("interactslot");
        const iframecode = `<iframe src="./borrowchoice?buttonjson=${borrowInfo}&username=${username}" id="borrowchoiceiframe"></iframe>`;
        interactslot.insertAdjacentHTML("afterbegin", iframecode);
        const borrowchoiceiframe = document.getElementById('borrowchoiceiframe');
        window.onmessage = function(event) {
            if (event.data.startsWith("doneselect")) {
                borrowchoiceiframe.remove();
                callfunction(event.data.replace('doneselect', ''));
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

    async function checkAdminPin(pin) {
        if (pin == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/checkadminpin", {
                method: 'POST',
                body: JSON.stringify({
                    "pin": pin
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
                    renderDialog("OK", `admin auth ok`);
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
            renderDialog("Error", "An error occurred while requesting for admin pin check");
            removeLoader()
        }
        removeLoader()
    }

    async function checkPin(pin) {
        if (pin == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/auth", {
                method: 'POST',
                body: JSON.stringify({
                    "authmethod": "pin",
                    "pin": pin
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
                    var usern = responseJson.user;
                    var borrowinf = responseJson.borrowinfo;
                    renderBorrowChoice(usern, borrowinf, alert)
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

    async function checkCard(cardid) {
        if (cardid == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/auth", {
                method: 'POST',
                body: JSON.stringify({
                    "authmethod": "card",
                    "cardid": cardid
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
                    var usern = responseJson.user;
                    var borrowinf = responseJson.borrowinfo;
                    renderBorrowChoice(usern, borrowinf, alert)
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

    async function bindCard(cardid) {
        if (cardid == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/cardregister", {
                method: 'POST',
                body: JSON.stringify({
                    "operation": "checkpin",
                    "cardid": cardid
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
                    renderDialog("Success", "Card has been binded to your account");
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
                case "operror":
                    renderDialog("Error", "Operation choice error")
                    break;
                default:
                    renderDialog("Error", "Unit webserver encountered an error");
            }
            removeLoader()
        } catch (error) {
            console.error('Error:', error);
            renderDialog("Error", "An error occurred while requesting for item check");
            removeLoader()
        }
        removeLoader()
    }

    async function checkCardBindingPin(pin) {
        if (pin == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/cardregister", {
                method: 'POST',
                body: JSON.stringify({
                    "operation": "checkpin",
                    "pin": pin
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
                    renderDialog(`Welcome ${responseJson.username}`, "Please tap card to bind...");
                    var diagclosebutton = document.getElementById("diagclosebutton");
                    diagclosebutton.addEventListener('click', function() {
                        bindCard(newCardNFC);
                    });
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
                case "operror":
                    renderDialog("Error", "Operation choice error")
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

    async function checkItem(itemid) {
        if (itemid == "") {
            return 0
        }
        renderLoader()
        try {
            const response = await fetch("/checkitem", {
                method: 'POST',
                body: JSON.stringify({
                    "itemid": itemid
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
                    renderDialog("OK", "Item valid");
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
                case "operror":
                    renderDialog("Error", "Operation choice error")
                    break;
                default:
                    renderDialog("Error", "Unit webserver encountered an error");
            }
            removeLoader()
        } catch (error) {
            console.error('Error:', error);
            renderDialog("Error", "An error occurred while requesting for item check");
            removeLoader()
        }
        removeLoader()
    }


    function handleNfcInput(nfcInput) {
        if (nfcInput.startsWith('03')) {
            checkItem(nfcInput)
        } else {
            if (cardBindNFC) {
                newCardNFC = nfcInput;
                closeDiag()
            } else {
                checkCard(nfcInput)
            }
        }
    }

    const nfcInputSocket = new io();

    nfcInputSocket.onopen = function(e) {
        console.log("Socket Opened");
    };

    nfcInputSocket.on('contentupdate', function(msg) {
        handleNfcInput(msg);
    });

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
            renderKeypad("Enter Admin PIN", checkAdminPin)
        }
    }, false)

    var cardbutton = document.getElementById("cardbutton");
    cardbutton.addEventListener('click', function() {
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Card Bind Code", checkCardBindingPin)
        }
    }, false)
});