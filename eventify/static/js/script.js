document.addEventListener('DOMContentLoaded', function() {
    // Sidenav initialization
    let sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav);

    // Initialize select elements
    let selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);

    // Initialize datepicker (for event creation and search filters)
    var dateElems = document.querySelectorAll('.datepicker');
    if (dateElems.length > 0) {
        console.log('Datepicker elements:', dateElems);  // Debugging log
        M.Datepicker.init(dateElems, {
            format: 'dd-mm-yyyy',  // U.K. date format
            autoClose: true,
            onClose: function() {
                console.log("Selected date:", dateElems[0].value);
            }
        });
    } else {
        console.error("Datepicker elements not found.");
    }

    // Initialize timepicker (for event creation)
    var timeElems = document.querySelectorAll('.timepicker');
    if (timeElems.length > 0) {
        console.log('Timepicker elements:', timeElems);  // Debugging log
        M.Timepicker.init(timeElems, {
            twelveHour: false,
            defaultTime: 'now',
            showClearBtn: true,
            onCloseEnd: function() {
                console.log("Selected time:", timeElems[0].value);
            }
        });
    } else {
        console.error("Timepicker elements not found.");
    }

    // Collapsible initialization (for any collapsible UI elements in the app)
    let collapsibles = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibles);
});
