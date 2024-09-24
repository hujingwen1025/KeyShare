//DM Root Process
document.addEventListener('DOMContentLoaded', () => {
    localStorage.setItem("buttonpressing", 0)

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

    const reportslot = document.getElementById("reportslot");
    var reportbutton = document.getElementById("reportbutton");
    reportbutton.addEventListener('click',function(){
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1);
            reportslot.insertAdjacentHTML("afterbegin", '<dialog open id="reportdialog" class="reportdiag"><center><img src="/static/resource/report.png"></center><br><center><h2>tinyurl.com/keysharers</h2><br><button class="reportclosebutton" id="reportclosebutton">Close</button></center></dialog>');
            var reportclosebutton = document.getElementById("reportclosebutton");
            reportclosebutton.addEventListener('click',function(){
                document.getElementById("reportdialog").remove();
                localStorage.setItem("buttonpressing", 0);
            })
        }
    })

    var borrowbutton = document.getElementById("borrowbutton");
    borrowbutton.addEventListener('click',function(){
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Identifacation PIN", alert)
        }
    },false)

    var adminbutton = document.getElementById("adminbutton");
    adminbutton.addEventListener('click',function(){
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Admin PIN", alert)
        }
    },false)

    var cardbutton = document.getElementById("cardbutton");
    cardbutton.addEventListener('click',function(){
        if (localStorage.getItem("buttonpressing") == 0) {
            localStorage.setItem("buttonpressing", 1)
            renderKeypad("Enter Card Bind Code", alert)
        }
    },false)
});
