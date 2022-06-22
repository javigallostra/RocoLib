var touchstartX = 0
var touchendX = 0

function checkDirection() {
    // if (touchendX < touchstartX) alert('swiped left!')
    // if (touchendX > touchstartX) alert('swiped right!')
}

function swipeInit() {

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX
    })

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX
        checkDirection()
    })
}

window.touchstartX = touchstartX;
window.touchendX = touchendX;
window.swipeInit = swipeInit;