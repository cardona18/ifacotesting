odoo.define('ireport.report', function (require) {
"use strict";

var Context = require('web.Context');
var core = require('web.core');
var pyeval = require('web.pyeval');
var Widget = require('web.Widget');
var Sidebar = require('web.Sidebar');

Sidebar.include({
    /**
     * @override
     */
    _addToolbarActions: function (toolbarActions) {

        this._super.apply(this, arguments);
        var self = this;

        self._rpc({
            model: 'ireport.report',
            method: 'check_print_templates',
            args: [0, self.env.model]
        }).then(function(data){

            _.each(data[1], function(template){
                self.items['print'].push({ label: template.name, action: data[0], tid: template.id });
            });

            self._redraw();

        });

    },
    /**
     * @override
     */
    _onItemActionClicked: function (item) {

        var self = this;
        this.trigger_up('sidebar_data_asked', {
            callback: function (env) {
                self.env = env;
                var activeIdsContext = {
                    active_id: item.tid ? item.tid : env.activeIds[0],
                    active_ids: env.activeIds,
                    active_model: env.model,
                };
                if (env.domain) {
                    activeIdsContext.active_domain = env.domain;
                }

                var context = pyeval.eval('context', new Context(env.context, activeIdsContext));

                self._rpc({
                    route: '/web/action/load',
                    params: {
                        action_id: item.action.id,
                        context: context,
                    },
                }).done(function (result) {

                    result.context = new Context(
                        result.context || {}, activeIdsContext)
                            .set_eval_context(context);

                    result.flags = result.flags || {};
                    result.flags.new_window = true;
                    self.do_action(result, {
                        on_close: function () {
                            self.trigger_up('reload');
                        },
                    });
                });
            }
        });

    }
});

});