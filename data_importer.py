from osv import osv, fields
import base64
import json


class DmImportDataWizard(osv.osv_memory):
    _name = 'dm.import.data.wizard'
    _inherit = 'ir.wizard.screen'

    def import_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        data_json = base64.decodestring(this.dm_import_data_wizard_data)
        data_json = json.loads(data_json)

        model_list = set([data_record['model'] for data_record in data_json])

        # Reset table
        for model in model_list:
            cr.execute("delete from %s" % model.replace('.', '_'))
            cr.execute("select setval('%s_id_seq', 1)" %
                       model.replace('.', '_'))

        data_field = {}

        for data_record in data_json:
            my_object_obj = self.pool.get(data_record['model'])
            data_field['id'] = data_record['pk']

            for k, v in data_record['fields'].iteritems():
                if isinstance(v, list):
                    data_field[k] = [(6, 0, v)]

                else:
                    data_field[k] = v

            my_object_obj.create(cr, uid, data_field, context=context)

        return {}

    _columns = {
        'dm_import_data_wizard_data': fields.binary(
            'DM Import Data Wizard Data'),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

DmImportDataWizard()
