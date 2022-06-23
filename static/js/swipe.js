var touchstartX = 0
var touchendX = 0

function changeProblem(swipe_left, swipe_right) {
    if (touchendX < touchstartX) {
        // Here we should load previous problem from list
        swipe_right();
    }
    if (touchendX > touchstartX) {
        // Here we should load next problem from list
        swipe_left();
    }
};

function swipeInit(swipe_left, swipe_right) {

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX
        changeProblem(swipe_left, swipe_right);
    });
};

window.touchstartX = touchstartX;
window.touchendX = touchendX;
window.swipeInit = swipeInit;