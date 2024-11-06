const user_input = $("#search-box")
const show_selector = $("#show-selector")
const results_div = $('#search-results')
const endpoint = '/'
const delay_by_in_ms = 700
let scheduled_function = false

let ajax_call = function (endpoint, request_parameters) {
    $.getJSON(endpoint, request_parameters)
        .done(response => {
            // fade out the artists_div, then:
                results_div.promise().then(() => {
                // replace the HTML contents
                results_div.html(response['html_from_view'])
                // fade-in the div with new contents
            })
        })
}


show_selector.on('input', function (e) {
    const request_parameters = {
        q: user_input.val(), // value of user_input: the HTML element with ID user-input
        show: $(this).val()
    }
    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})

user_input.on('keyup', function () {

    const request_parameters = {
        q: $(this).val(), // value of user_input: the HTML element with ID user-input
        show: show_selector.val()
    }

    // start animating the search icon with the CSS class
    //search_icon.addClass('blink')

    // if scheduled_function is NOT false, cancel the execution of the function
    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }

    // setTimeout returns the ID of the function to be executed
    scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
})
