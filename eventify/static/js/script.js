document.addEventListener('DOMContentLoaded', function() {
    // Sidenav initialization
    let sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav);

    // Initialize select elements
    let selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);

    // Initialize datepicker only if present on the page
    var dateElems = document.querySelectorAll('.datepicker');
    if (dateElems.length > 0) {
        console.log('Initializing datepicker...');
        M.Datepicker.init(dateElems, {
            format: 'dd-mm-yyyy',  // Adjusted format to match the desired format (dd-mm-yyyy)
            autoClose: true,
            onClose: function() {
                console.log("Selected date:", dateElems[0].value);
            }
        });
    }

    // Initialize timepicker only if present on the page
    var timeElems = document.querySelectorAll('.timepicker');
    if (timeElems.length > 0) {
        console.log('Initializing timepicker...');
        M.Timepicker.init(timeElems, {
            twelveHour: false,
            defaultTime: 'now',
            showClearBtn: true,
            onCloseEnd: function() {
                console.log("Selected time:", timeElems[0].value);
            }
        });
    }

    // Collapsible initialization (for collapsible UI elements)
    let collapsibles = document.querySelectorAll('.collapsible');
    if (collapsibles.length > 0) {
        M.Collapsible.init(collapsibles);
    }

     // Log the admin dashboard link to ensure it is rendered
     let adminLink = document.querySelector('a[href="/admin_dashboard"]');
     if (adminLink) {
         console.log("Admin Dashboard link is rendered:", adminLink);
     } else {
         console.log("Admin Dashboard link not found");
     }
});
