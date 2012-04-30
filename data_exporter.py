from osv import osv, fields
import base64
import json
from tools.translate import _


class DmExportDataWizard(osv.osv_memory):
    _name = 'dm.export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        ir_model_id = this.ir_model_id
        model_name = ir_model_id.model

        ### Getting Export model
        input_model_obj = self.pool.get(model_name)
        input_model_id_list = input_model_obj.search(cr, uid, [],
                                                     context=context)
        # Checking for Empty data
        if not input_model_id_list:
            raise osv.except_osv((_('Warning')),
                ('There is no data for %s class' % model_name))

        # Select * from ...
        input_model_list = input_model_obj.read(cr, uid, input_model_id_list,
                                                [], context=context)
        ###

        data_json = []

        # Iterating export model data
        for input_model in input_model_list:
            record_dict = {}
            field_dict = {}
            record_dict['pk'] = input_model['id']
            record_dict['model'] = model_name

            # Iterating model fields
            for ir_model_field in ir_model_id.field_id:
                # Checking for existing model name in input model
                if ir_model_field.name in input_model:
                    if ir_model_field.ttype == 'many2one':
                        field_dict[ir_model_field.name] = \
                            input_model[ir_model_field.name][0]
                    else:
                        field_dict[ir_model_field.name] = \
                            input_model[ir_model_field.name]

            record_dict['fields'] = field_dict
            data_json.append(record_dict)

        out = base64.encodestring(json.dumps(data_json, indent=4))

        return self.write(cr, uid, ids, {
            'state': 'done', 'dm_export_data_wizard_data': out,
            'name': "%s_data.json" % model_name.replace('.', '_')
        }, context=context)

    EXPORT_TYPE = (('a', 'based on model'), ('b', 'based on module'))

    _columns = {
        'name': fields.char('Filename', size=128, readonly=True),
        'dm_export_data_wizard_type': fields.selection(EXPORT_TYPE,
            'DM Export Data Wizard Type'),
        'ir_model_id': fields.many2one('ir.model', 'IR Model'),
        'ir_module_module_id': fields.many2one('ir.module.module',
                                               'IR Module Module'),
        'dm_export_data_wizard_data': fields.binary('Export Data Wizard Data',
                                                 readonly=True),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init', 'dm_export_data_wizard_type': 'b'}

DmExportDataWizard()
