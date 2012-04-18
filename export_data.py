from osv import osv, fields
import base64


class ExportDataWizard(osv.osv_memory):
    _name = 'export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        this.name = '%s.json' % this.export_data_wizard_class_name
        out = base64.encodestring("durud bar to sds")
        return self.write(cr, uid, ids, {
            'state': 'done', 'export_data_wizard_data': out,
            'name': this.name
        }, context=context)

    _columns = {
        'name': fields.char('Filename', size=16, readonly=True),
        'ir_model_id': fields.many2one('ir.model', 'IR Model'),
        'export_data_wizard_data': fields.binary('Export Data Wizard Data',
                                                 readonly=True),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

ExportDataWizard()
