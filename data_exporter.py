from osv import osv, fields
import base64
import json
from tools.translate import _


class DmExportDataWizard(osv.osv_memory):
    _name = 'dm.export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        # Getting Input values
        export_type_input = this.dm_export_data_wizard_type
        ir_model_id_input = this.ir_model_id
        ir_module_module_input = this.ir_module_module_id

        data_json = []

        ir_model_list = []

        # Check for based on module
        if export_type_input == 'b':
            ir_model_obj = self.pool.get('ir.model')
            ir_model_id_list = ir_model_obj.search(cr, uid,
                [('modules', '=', ir_module_module_input.name)],
                context=context)
            ir_model_list = ir_model_obj.browse(cr, uid, ir_model_id_list,
                                                context=context)

        # Check for based on model
        elif export_type_input == 'a':
            ir_model_list.append(ir_model_id_input)

        for ir_model in ir_model_list:
            ### Getting Export model
            input_model_obj = self.pool.get(ir_model.model)
            input_model_id_list = input_model_obj.search(cr, uid, [],
                                                         context=context)
            # Checking for Empty data
            if not input_model_id_list:
                raise osv.except_osv((_('Warning')),
                    ('There is no data for %s class' % ir_model.model))

            # Select * from ...
            input_model_list = input_model_obj.read(cr, uid, input_model_id_list,
                                                    [], context=context)
            ###

            # Iterating export model data
            for input_model in input_model_list:
                record_dict = {}
                field_dict = {}
                record_dict['pk'] = input_model['id']
                record_dict['model'] = ir_model.model

                # Iterating model fields
                for ir_model_field in ir_model_id_input.field_id:
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
#            'name': "%s_data.json" % model_name.replace('.', '_')
            'name': "harchi"
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
