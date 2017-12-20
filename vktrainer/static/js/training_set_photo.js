new Vue({
    delimiters: ['[[', ']]'],
    el: '#body_container',
    data: {
        'photo_pk': '',
        'photo_url': '',
        'photo_name': '',
    },
    methods: {
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
        loadPhoto(data) {
            // Load the photo
            this.$data.photo_pk = data.pk;
            this.$data.photo_url = data.url;
            this.$data.photo_name = data.name;

            // Update the url
            window.location.hash = '#/' + this.$data.photo_pk;
        },
        fetchPhotoFromHash() {
            // We try to get the photo pk from the hash
            var regex = /#\/(\d)/g;
            var match = regex.exec(window.location.hash);
            if (match !== undefined) {
                // If there is one, we use it
                var pk = match[1];
                var url = window.location.pathname + pk;
                this.fetchPhoto(url);
            } else {
                // Otherwise we load the next photo
                this.fetchNextPhoto();
            }
        }
    },
    mounted: function() {
        this.fetchPhotoFromHash();
    }
});
