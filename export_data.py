from osv import osv, fields
import cStringIO
import base64


class ExportDataWizard(osv.osv_memory):
    _name = 'export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        this.name = '%s.json' % this.export_data_wizard_class_name
        buf = cStringIO.StringIO()
        buf.write("durud bar to bad")
        out = base64.encodestring(buf.getvalue())
        buf.close()
        return self.write(cr, uid, ids, {
            'state': 'done', 'export_data_wizard_data': out,
            'name': this.name
        }, context=context)

    _columns = {
        'name': fields.char('Filename', size=16, readonly=True),
        'export_data_wizard_class_name': fields.char(
            'Export Data Wizard Class Name', size=64),
        'export_data_wizard_data': fields.binary('Export Data Wizard Data',
                                                 readonly=True),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

ExportDataWizard()
