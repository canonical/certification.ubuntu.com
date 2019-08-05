jQuery(document).ready(function($) {
    $('.model .device_summary').addClass('closed').each(function() {
        var self = $(this),
            naturalHeight = self.height();
        
        self.css('height', 0).parents('.model').on({
            mouseenter: function() {
                self.stop().animate({
                    height: naturalHeight,
                    opacity: 1
                }, 500);
            },
            mouseleave: function() {
                self.stop().animate({
                    height: 0,
                    opacity: 0	
                }, 500);
            }
        }); 
    });
});