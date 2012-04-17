from osv import osv, fields


class ExportDataWizard(osv.osv_memory):
    _name = 'export.data.wizard'
    _inherit = 'ir.wizard.screen'

    _columns = {
        'export_data_wizard_class_name': fields.char(
            'Export Data Wizard Class Name', size=64),
        'export_data_wizard_data': fields.binary('Export Data Wizard Data'),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

    def export_data(self, cr, uid, ids, context=None):
        print "hello world"

        self.write(cr, uid, ids, {
            'state': 'done', 'export_data_wizard_data': 'durud'
        }, context=context)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'export.data.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids and ids[0] or False,
        }
ExportDataWizard()
