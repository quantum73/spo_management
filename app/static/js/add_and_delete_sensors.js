let add_btn = $("#add-sensor-btn");
let remove_btn = $("#remove-sensor-btn");

$(add_btn).click(function () {
    let sensors_rows = $(".sensor-row");
    let length = sensors_rows.length;
    if (length < 5) {
        $(this).removeClass("disabled");
        $(this).prop('disabled', false);
        let clone_sensor = $(".sensor-row:first").clone();
        clone_sensor.find(":input").attr("id", $(":input", clone_sensor).attr("id").replace(/-\d-/, `-${length}-`) );
        clone_sensor.find(":input").attr("name", $(":input", clone_sensor).attr("name").replace(/-\d-/, `-${length}-`) );
        clone_sensor.find("label").attr("for", $("label", clone_sensor).attr("for").replace(/-\d-/, `-${length}-`) );
        clone_sensor.insertAfter(".sensor-row:last");
    }
});

$(remove_btn).click(function () {
    let sensors_rows = $(".sensor-row");
    if (sensors_rows.length > 1) {
        let remove_idx = sensors_rows.length - 1;
        sensors_rows[remove_idx].remove();
    }
});