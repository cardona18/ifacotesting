openerp.help_custom = function(instance) {
    instance.web.UserMenu.include({
        on_menu_gi_help: function(param) {
            window.open('/web/help/user', '_blank');
        },
    })
}