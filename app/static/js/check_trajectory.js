function check_trajectory_select(select_element) {
    let glyssade_block = $(".glyssade-block");
    let ellipse_block = $(".ellipse-block");
    if (select_element.value === "glissade") {
        glyssade_block.show();
        ellipse_block.hide();
        glyssade_block.find(':input').prop("required", true);
        ellipse_block.find(':input').prop("required", false);
    } else {
        ellipse_block.show();
        glyssade_block.hide();
        ellipse_block.find(':input').prop("required", true);
        glyssade_block.find(':input').prop("required", false);
    }
}

let trajectory = $(".trajectory-select");
$(".glyssade-block").find(':input').prop("required", true);
$(".ellipse-block").hide();
trajectory.change(function () {
    check_trajectory_select(this);
});