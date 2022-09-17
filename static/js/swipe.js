var touchstartX = 0
var touchendX = 0
var touchstartY = 0
var touchendY = 0
var threshold = 75; // empirical value. TODO: finetune 

function isHorizontalSwipe() {
    return Math.abs(touchendX - touchstartX) > threshold && Math.abs(touchendX - touchstartX) > Math.abs(touchendY - touchstartY);
}

function changeProblem(swipe_left, swipe_right, current_id, list_id, is_user_list, sort_by, is_ascending, to_show) {
    if (touchendX < touchstartX && isHorizontalSwipe()) {
        // Here we should load previous problem from list
        swipe_right(current_id, list_id, is_user_list, sort_by, is_ascending, to_show);
    }
    if (touchendX > touchstartX && isHorizontalSwipe()) {
        // Here we should load next problem from list
        swipe_left(current_id, list_id, is_user_list, sort_by, is_ascending, to_show);
    }
};

function swipeInit(swipe_left, swipe_right, current_id, list_id, is_user_list, sort_by, is_ascending, to_show) {

    document.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].screenX;
        touchstartY = e.changedTouches[0].screenY;
    });

    document.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].screenX;
        touchendY = e.changedTouches[0].screenY;
        changeProblem(swipe_left, swipe_right, current_id, list_id, is_user_list, sort_by, is_ascending, to_show);
    });
};

function loadNext(problem_id, list_id, is_user_list, sort_by, is_ascending, to_show) {
    loadProblem(problem_id, list_id, is_user_list, "load_next", sort_by, is_ascending, to_show);
}

function loadPrevious(problem_id, list_id, is_user_list, sort_by, is_ascending, to_show) {
    loadProblem(problem_id, list_id, is_user_list, "load_previous", sort_by, is_ascending, to_show);
}

function loadProblem(problem_id, list_id, is_user_list, endpoint, sort_by, is_ascending, to_show) {
    var path = build_query_url(
        problem_id, 
        list_id, 
        is_user_list, 
        endpoint,
        sort_by,
        is_ascending,
        to_show
    );

    // Add more params to query: any filter options
    // path = endpoint + "?list_id=" + list_id + "&is_user_list=" + is_user_list + "&id=" + problem_id + "&scroll=" + window.scrollY.toFixed(2);
    
    // TODO: we should keep the state of the filters
    fetch(path, {})
        .then(resp => resp.text())
        .then(body => {
            // Hacky Whacky
            document.open();
            document.write(body);
            document.close();
        });

}

function build_query_url(problem_id, list_id, is_user_list, endpoint, sort_by, is_ascending, to_show) {
    // base
    var base_path = endpoint + "?list_id=" + list_id + "&is_user_list=" + is_user_list + "&id=" + problem_id;
    // add scroll status
    base_path = base_path + "&scroll=" + window.scrollY.toFixed(2);
    // add additional params
    base_path = base_path + "&sort_by=" + sort_by + "&is_ascending=" + is_ascending + "&to_show=" + to_show;
    return base_path;
} 

window.touchstartX = touchstartX;
window.touchendX = touchendX;
window.touchstartY = touchstartY;
window.touchendY = touchendY;
window.swipeInit = swipeInit;
window.loadPrevious = loadPrevious;
window.loadNext = loadNext;