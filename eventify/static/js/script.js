document.addEventListener('DOMContentLoaded', function() {
    // Sidenav initialization
    let sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav);

    // Initialize select elements
    let selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);

    // Initialize datepicker
    var dateElems = document.querySelectorAll('.datepicker');
    if (dateElems.length > 0) {
        console.log('Datepicker elements:', dateElems);  // Debugging log
        M.Datepicker.init(dateElems, {
            format: 'dd-mm-yyyy',
            autoClose: true,
            onClose: function() {
                console.log("Selected date:", dateElems[0].value);
            }
        });
    } else {
        console.error("Datepicker elements not found.");
    }

    // Initialize timepicker
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

    // Collapsible initialization
    let collapsibles = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibles);
});
