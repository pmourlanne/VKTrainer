new Vue({
    delimiters: ['[[', ']]'],
    el: '#body_container',
    data: {
        'photo_pk': '',
        'photo_url': '',
        'photo_name': '',
        'patterns': [],
        'active_index': 0,
        'training_done': false
    },
    methods: {
        // Actual training
        _disableActivePattern: function() {
            this.$data.patterns[this.$data.active_index].active = false;
        },
        _enablePattern: function(index) {
            this.$data.patterns[index].active = true;
            this.$data.patterns[index].result = '';
            this.$data.active_index = index;
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
            // We were done, we enable the last pattern
            if (this.$data.training_done) {
                this.$data.training_done = false;
                this._enablePattern(this.$data.patterns.length - 1);
                return;
            }

            var active_index = this.$data.active_index;
            // We're already at the first pattern
            if (active_index === 0) {
                return;
            }

            // We're done with edge cases :o
            this._disableActivePattern();
            this.$data.patterns[active_index].result = '';
            this._enablePattern(active_index - 1);
        },
        setActivePatternResult: function(choice) {
            this.$data.patterns[this.$data.active_index].result = choice;
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
                'photo': this.$data.photo_pk
            };

            var url = window.location.pathname;
            url = url.substring(0, url.indexOf('/photo/'));
            url += '/result/';

            var self = this;
            $.post(url, data, function(data) {
                self.resetPatterns();
                self.fetchNextPhoto();
            });
        },

        // Patterns fetch and load
        fetchPatterns: function() {
            var url = window.location.pathname;
            url = url.substring(0, url.indexOf('/photo/'));
            url += '/patterns/';

            var self = this;
            $.get(url, function(data) {
                self.$data.patterns = data.patterns;
                self._enablePattern(0);
            });
        },
        resetPatterns: function() {
            var pattern, i;
            // Clean the patterns (result and active)
            for (i = 0; i < this.$data.patterns.length; i++) {
                pattern = this.$data.patterns[i];
                pattern.result = '';
                pattern.active = false;
            }
            this.$data.training_done = false;
            // Enable the first pattern
            this._enablePattern(0);
        },

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

        // Global keyboard bindings
        addKeyEventListeners: function() {
            var self = this;

            window.addEventListener('keyup', function(e) {
                // Submit on enter when training done
                if (e.keyCode === 13) {
                    if (self.$data.training_done) {
                        self.submitResult();
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
        }
    },
    mounted: function() {
        // Fetch data
        this.fetchPhotoFromHash();
        this.fetchPatterns();
        // Add global keybindings
        this.addKeyEventListeners();
    }
});
