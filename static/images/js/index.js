document.addEventListener('alpine:init', () => {
    Alpine.data('scrollControls', () => ({
        scrollX: 0,
        init() {
            this.$watch('scrollX', (value) => {
                const container = this.$refs.container;
                container.scrollLeft = value;
            });
        }
    }));
});