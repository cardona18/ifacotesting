openerp.gi_base = function(instance) {
    instance.web.UserMenu.include({
        on_menu_help: function(param) {
            window.open('http://192.168.168.211:4567', '_blank');
        },
    })
}