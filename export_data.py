from osv import osv, fields
import base64


class ExportDataWizard(osv.osv_memory):
    _name = 'export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        generated_content = []
        generated_dict = {}
        generated_fields = {}
        this = self.browse(cr, uid, ids, context=context)[0]
        model_name = this.ir_model_id.model
        model_field_list = this.ir_model_id.field_id

        for model_field in model_field_list:
            if model_field.ttype in ['char', 'integer', 'many2one', 'float', 'date', 'time', 'datetime']:
                generated_fields[model_field.name] = None

        current_obj = self.pool.get(model_name)
        current_obj_id_list = current_obj.search(cr, uid, [], context=context)
        current_list = current_obj.browse(cr, uid, current_obj_id_list, context=context)
        this.name = "%s.py" % model_name

        for current in current_list:
            generated_dict['pk'] = current.id
            generated_dict['model'] = model_name
            generated_dict['fields'] = generated_fields

        generated_content.append(generated_dict)

        out = base64.encodestring(str(generated_content))

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
