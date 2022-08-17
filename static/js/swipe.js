var touchstartX = 0
var touchendX = 0
var touchstartY = 0
var touchendY = 0
var threshold = 75; // empirical value. TODO: finetune 

function isHorizontalSwipe() {
    return Math.abs(touchendX - touchstartX) > threshold && Math.abs(touchendX - touchstartX) > Math.abs(touchendY - touchstartY);
}

function changeProblem(swipe_left, swipe_right, current_id, list_id, is_user_list) {
    if (touchendX < touchstartX && isHorizontalSwipe()) {
        // Here we should load previous problem from list
        swipe_right(current_id, list_id, is_user_list);
    }
    if (touchendX > touchstartX && isHorizontalSwipe()) {
        // Here we should load next problem from list
        swipe_left(current_id, list_id, is_user_list);
    }
};

function swipeInit(swipe_left, swipe_right, current_id, list_id, is_user_list) {

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
        touchstartY = e.changedTouches[0].screenY;
    });

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        touchendY = e.changedTouches[0].screenY;
        changeProblem(swipe_left, swipe_right, current_id, list_id, is_user_list);
    });
};

function loadNext(problem_id, list_id, is_user_list) {
    loadProblem(problem_id, list_id, is_user_list, "load_next");
}

function loadPrevious(problem_id, list_id, is_user_list) {
    loadProblem(problem_id, list_id, is_user_list, "load_previous");
}

function loadProblem(problem_id, list_id, is_user_list, endpoint) {
    var path = endpoint + "?list_id=" + list_id + "&is_user_list=" + is_user_list + "&id=" + problem_id + "&scroll=" + window.scrollY.toFixed(2);
    // Add more params to query: list_id, and any filter options
    fetch(path, {})
        .then(resp => resp.text())
        .then(body => {
            // Hacky Whacky
            document.open();
            document.write(body);
            document.close();
        });

}

window.touchstartX = touchstartX;
window.touchendX = touchendX;
window.touchstartY = touchstartY;
window.touchendY = touchendY;
window.swipeInit = swipeInit;
window.loadPrevious = loadPrevious;
window.loadNext = loadNext;