var touchstartX = 0
var touchendX = 0

function changeProblem(swipe_left, swipe_right, current_id, gym_code) {
    if (touchendX < touchstartX) {
        // Here we should load previous problem from list
        swipe_right(current_id, gym_code);
    }
    if (touchendX > touchstartX) {
        // Here we should load next problem from list
        swipe_left(current_id, gym_code);
    }
};

function swipeInit(swipe_left, swipe_right, current_id, gym_code) {

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX
        changeProblem(swipe_left, swipe_right, current_id, gym_code);
    });
};

function loadNext(problem_id, gym_code) {
    loadProblem(problem_id, gym_code, "load_next");
}

function loadPrevious(problem_id, gym_code) {
    loadProblem(problem_id, gym_code, "load_previous");
}

function loadProblem(problem_id, gym_code, endpoint) {
    fetch(endpoint + "?gym=" + gym_code + "&id=" + problem_id, {})
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
window.swipeInit = swipeInit;
window.loadNext = loadNext;
window.loadPrevious = loadPrevious;