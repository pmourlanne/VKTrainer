var point_radius = 5;

var drawPoint = function(canvas, x, y) {
    var context = canvas.getContext("2d");

    context.beginPath();
    context.arc(x, y, point_radius, 0, 2 * Math.PI, false);
    context.fillStyle = '#00FF00';
    context.fill();
    context.closePath();
};


var clearPoint = function(canvas, x, y) {
    // We cheat and clear a rectangle around the point
    var context = canvas.getContext("2d");
    var radius = point_radius + 1;

    context.clearRect(
        x - radius,
        y - radius,
        radius * 2,
        radius * 2
    );
}
