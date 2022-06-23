var touchstartX = 0
var touchendX = 0

function changeProblem(swipe_left, swipe_right, prev_id, next_id) {
    if (touchendX < touchstartX) {
        // Here we should load previous problem from list
        swipe_right(next_id);
    }
    if (touchendX > touchstartX) {
        // Here we should load next problem from list
        swipe_left(prev_id);
    }
};

function swipeInit(swipe_left, swipe_right, prev_id, next_id) {

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX
        changeProblem(swipe_left, swipe_right, prev_id, next_id);
    });
};

window.touchstartX = touchstartX;
window.touchendX = touchendX;
window.swipeInit = swipeInit;