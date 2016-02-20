function position_canvas() {
    var img = $('.img-training');
    var $canvas = $('.canvas-training');
    var canvas = $canvas[0];

    $canvas.css('position', 'absolute');
    $canvas.css('left', img.offset().left + 'px');
    $canvas.css('top', img.offset().top + 'px');
    canvas.width = img.width();
    canvas.height = img.height();
    $canvas.removeClass('hidden');
}


function draw_point(canvas, x, y) {
    var radius = 5;
    var context = canvas.getContext("2d");

    context.beginPath();
    context.arc(x, y, radius, 0, 2 * Math.PI, false);
    context.fillStyle = '#00FF00';
    context.fill();
    context.closePath();
}


function draw_canvas_from_state(canvas, state) {
    var picture = new Image();
    picture.src = state;
    picture.onload = function () {
        var context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(picture, 0, 0);
    };
}
