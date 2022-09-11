let add_btn = $("#add-sensor-btn");
let remove_btn = $("#remove-sensor-btn");

function populate(frm, data, prefix) {
    $.each(data, function (key, value) {
        $(':input[name=' + prefix + key + ']', frm).val(value);
    });
}

function send_json_data(json_field, form_field) {
    let fd = new FormData();
    let json_file = $(json_field).prop('files')[0];
    let name_prefix = $(json_field).attr("name").replace("from_json", "");
    fd.append('from_json', json_file);
    $.ajax({
        url: 'http://127.0.0.1:7373/check-json/',
        type: "POST",
        data: fd,
        success: function (data) {
            populate(form_field, data, name_prefix);
        },
        error: function (data) {
            alert("Некорректный запрос или JSON");
        },
        cache: false,
        contentType: false,
        processData: false,
    });

}

function change_json_field(clone) {
    clone.find(':input').not(':input[type=button], select').val(null);
    clone.find(':input.from-json-field').change(function () {
        send_json_data($(this), clone);
        $(this).parent().hide();
        $(this).parent().parent().find(":input.clear-sensor-btn").show();
    });
}

function click_clear_button(clone) {
    clone.find(':input.clear-sensor-btn').click(function () {
        $(this).parent().find(':input').not(':input[type=button], select').val(null);
        $(this).hide();
        $(this).parent().find(":input.from-json-field").parent().show();
    });
}

$(".clear-sensor-btn:first").hide();
let first_sensor_row = $(".sensor-row:first");
change_json_field(first_sensor_row);
click_clear_button(first_sensor_row);


$(add_btn).click(function () {
    let sensors_rows = $(".sensor-row");
    let length = sensors_rows.length;
    if (length < 5) {
        $(this).removeClass("disabled");
        $(this).prop('disabled', false);
        let clone_sensor = $(".sensor-row:first").clone(true, true);

        // Rename id and name attributes into inputs
        clone_sensor.find(":input").each(function (i, v) {
            let new_id_value = $(v).attr("id").replace(/-\d-/, `-${length}-`);
            let new_name_value = $(v).attr("name").replace(/-\d-/, `-${length}-`);
            $(v).attr("id", new_id_value);
            $(v).attr("name", new_name_value);
        });
        // Rename for attribute into labels
        clone_sensor.find("label").each(function (i, v) {
            let new_id_value = $(v).attr("for").replace(/-\d-/, `-${length}-`);
            $(v).attr("for", new_id_value);
        });
        // Hide clear button and show input for json autofill
        clone_sensor.find(":input.clear-sensor-btn").hide();
        clone_sensor.find(":input.from-json-field").parent().show();

        change_json_field(clone_sensor);
        click_clear_button(clone_sensor);
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