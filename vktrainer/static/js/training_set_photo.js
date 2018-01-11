var _getBaseUrl = function() {
    var url = window.location.pathname;
    return url.substring(0, url.indexOf('/photo/'));
};


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


Vue.component('img-responsive', {
    delimiters: ['[[', ']]'],
    template: '#template_img_responsive',
    props: ['img_url'],
    data: function() {
        return {
            canvasStyle: {
                position: 'absolute',
                width: 0,
                height: 0
            },
            canvasClass: {
                hidden: true
            },
        };
    },
    watch: {
        img_url: function(new_url) {
            // Fit canvas on image load
            var self = this;
            var img = self.$refs['img'];
            var canvas = self.$refs['canvas'];

            self.$data.canvasClass.hidden = true;
            img.onload = function() {
                self.$data.canvasStyle.width = img.width + 'px';
                self.$data.canvasStyle.height = img.height + 'px';
                self.$data.canvasClass.hidden = false;
            };
        }
    }
});

Vue.component('progress-bar', {
    delimiters: ['[[', ']]'],
    template: '#template_progress_bar',
    props: ['percentage']
});

Vue.component('small-text', {
    delimiters: ['[[', ']]'],
    template: '#template_small_text',
    props: ['text']
});

Vue.component('features', {
    delimiters: ['[[', ']]'],
    props: ['photo_pk'],
    template: '#template_features',
    data: function() {
        return {
            'patterns': [],
            'active_index': 0,
            'training_done': false
        };
    },
    methods: {
        // Actual training
        _disableActivePattern: function() {
            this.$data.patterns[this.$data.active_index].active = false;
            this.removeClickOnImageListener();
        },
        _enablePattern: function(index) {
            var pattern = this.$data.patterns[index];

            this.resetPattern(pattern);
            pattern.active = true;
            this.$data.active_index = index;

            // Give focus to the input if there is one
            var input = this.$refs[pattern.name + '_input'];
            if (input) {
                this.$nextTick(() => input[0].focus())
            }

            // Add click on image listener if relevant
            if (pattern.input === 'point') {
                this.addClickOnImageListener();
            }
        },
        enableNextPattern: function() {
            var active_index = this.$data.active_index;

            // We're all done
            if (active_index === this.$data.patterns.length - 1) {
                this._disableActivePattern();
                this.$data.training_done = true;
                return;
            }

            this._disableActivePattern();
            this._enablePattern(active_index + 1);
        },
        enablePreviousPattern: function() {
            var active_index = this.$data.active_index;
            // We're already at the first pattern
            if (active_index === 0) {
                return;
            }

            // We were done, we enable the last pattern
            if (this.$data.training_done) {
                this.$data.training_done = false;
                this._enablePattern(this.$data.patterns.length - 1);
                return;
            }

            // We're done with edge cases :o
            this._disableActivePattern();
            this.resetPattern(this.$data.patterns[active_index])
            this._enablePattern(active_index - 1);
        },
        setActivePatternResult: function(result) {
            this.$data.patterns[this.$data.active_index].result = result;
            this.enableNextPattern();
        },
        submitResult: function() {
            var data, i, pattern;
            var training_result = {};

            for (i = 0; i < this.$data.patterns.length; i++) {
                pattern = this.$data.patterns[i];
                training_result[pattern.name] = pattern.result;
            }

            data = {
                'training_result': JSON.stringify(training_result),
                'photo': this.photo_pk
            };

            var url = _getBaseUrl() + '/result/';

            var self = this;
            $.post(url, data, function(data) {
                self.resetPatterns();
                self.$emit('result_posted');
            });
        },

        // Fetch and reset
        fetchPatterns: function() {
            var url = _getBaseUrl() + '/patterns/';

            var self = this;
            $.get(url, function(data) {
                self.$data.patterns = data.patterns;
                self._enablePattern(0);
            });
        },
        resetPattern: function(pattern) {
            if (pattern.input === 'point' && pattern.result) {
                // We need to remove the actual point
                var canvas = $('#training_img canvas')[0];
                var x = pattern.result.x_abs;
                var y = pattern.result.y_abs;
                clearPoint(canvas, x, y);
            }

            pattern.result = '';
        },
        resetPatterns: function() {
            var pattern, i;
            // Clean the patterns (result and active)
            for (i = 0; i < this.$data.patterns.length; i++) {
                pattern = this.$data.patterns[i];
                this.resetPattern(pattern)
                pattern.active = false;
            }
            this.$data.training_done = false;
            // Enable the first pattern
            this._enablePattern(0);
        },

        // Global keyboard bindings
        addKeyEventListeners: function() {
            var self = this;

            window.addEventListener('keyup', function(e) {
                // Handle enter press
                if (e.keyCode === 13) {
                    // If we're done, submit the result
                    if (self.$data.training_done) {
                        self.submitResult();
                    }
                    // Otherwise we skip to the next pattern
                    else {
                        self.enableNextPattern();
                    }
                }

                // Select 'choice' on numeric key (not 0)
                if ((e.keyCode >= 49 && e.keyCode <= 57) || (e.keyCode >= 97 && e.keyCode <= 105)) {
                    // If we're done training we ignore the key press
                    if (self.$data.training_done) {
                        return;
                    }

                    // If the active pattern is not a select, we ignore the key press
                    var pattern = self.$data.patterns[self.$data.active_index];
                    if (pattern.input !== 'select') {
                        return;
                    }

                    var idx;
                    if (e.keyCode >= 49 && e.keyCode <= 57) {
                        idx = e.keyCode - 49;
                    } else {
                        idx = e.keyCode - 97;
                    }
                    self.setActivePatternResult(pattern.choices[idx]);
                }
            });
        },
        // Click on image listeners
        // This code should not be in this component, improve :O
        addClickOnImageListener: function() {
            var self = this;

            $('#training_img canvas').bind('click.pattern', function(e) {
                var offset = $(this).offset();
                var x = e.pageX - offset.left;
                var y = e.pageY - offset.top;
                var imgX = $(this).width();
                var imgY = $(this).height();

                // Draw the point
                drawPoint($(this)[0], x, y);
                // Log the result
                self.setActivePatternResult({
                    x_abs: x,
                    y_abs: y,
                    x_rel: x / imgX,
                    y_rel: y / imgY
                });
            });
        },
        removeClickOnImageListener: function() {
            $('#training_img canvas').unbind('click.pattern');
        }
    },
    mounted: function() {
        this.fetchPatterns();
        this.addKeyEventListeners();
    }
});

new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        'photo_pk': '',
        'photo_url': '',
        'photo_name': '',
        'percentage_done': 0
    },
    methods: {
        // Photo fetch and load
        fetchNextPhoto: function() {
            var url = window.location.pathname + 'next/';
            if (this.photo_pk !== '') {
                url += '?photo=' + this.photo_pk;
            }
            this.fetchPhoto(url);
        },
        fetchPhoto: function(url) {
            var self = this;
            $.get(url, function(data) {
                self.loadPhoto(data);
            });
        },
        loadPhoto: function(data) {
            // Load the photo
            this.$data.photo_pk = data.pk;
            this.$data.photo_url = data.url;
            this.$data.photo_name = data.name;

            // Update the url
            window.location.hash = '#/' + this.$data.photo_pk;
        },
        fetchPhotoFromHash: function() {
            // We try to get the photo pk from the hash
            var regex = /#\/(\d)/g;
            var match = regex.exec(window.location.hash);
            if (match) {
                // If there is one, we use it
                var pk = match[1];
                var url = window.location.pathname + pk;
                this.fetchPhoto(url);
            } else {
                // Otherwise we load the next photo
                this.fetchNextPhoto();
            }
        },

        // Percentage display
        fetchPercentageDone: function() {
            var url = _getBaseUrl() + '/percentage_done/';
            var self = this;

            $.get(url, function(data) {
                self.$data.percentage_done = data.percentage_done;
            });
        },

        handleResultPosted: function() {
            this.fetchNextPhoto();
            this.fetchPercentageDone();
        }
    },
    mounted: function() {
        // Fetch data
        this.fetchPhotoFromHash();
        this.fetchPercentageDone();
    }
});
