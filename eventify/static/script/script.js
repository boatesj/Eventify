document.addEventListener('DOMContentLoaded', function() {
    // Sidenav initialization
    let sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav);

    // Initialize select elements
    let selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);

    // Initialize datepicker
    var dateElems = document.querySelectorAll('.datepicker');
    M.Datepicker.init(dateElems, {
        format: 'dd-mm-yyyy',  // Set your desired format
        autoClose: true,
    });

    // Initialize timepicker
    var timeElems = document.querySelectorAll('.timepicker');
    M.Timepicker.init(timeElems, {
        twelveHour: false, // Use 24-hour format
        defaultTime: 'now',
        showClearBtn: true, // Show clear button
        onSelect: function(time) {
            console.log("Selected time: ", time); // Debugging log
        }
    });

    // Collapsible initialization
    let collapsibles = document.querySelectorAll('.collapsible');
    M.Collapsible.init(collapsibles);
});

// Form submission handling
document.querySelector('form').addEventListener('submit', function(event) {
    const dateInput = document.getElementById('date');
    let dateValue = dateInput.value;

    // Perform client-side validation here if needed

    // Optionally: Modify the input value to fit the desired format before submission
    // Example: If users enter in ISO format, convert it to dd-mm-yyyy format
});
