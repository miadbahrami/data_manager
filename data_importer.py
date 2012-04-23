from osv import osv, fields
import base64
import json
from tools.translate import _


class DmImportDataWizard(osv.osv_memory):
    _name = 'dm.import.data.wizard'
    _inherit = 'ir.wizard.screen'

    def import_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        data_json = base64.decodestring(this.dm_import_data_wizard_data)
        data_json = json.dumps(data_json)
        data_json = eval(json.loads(data_json))

        model_list = set([data_record['model'] for data_record in data_json])

        # Reset table
        for model in model_list:
            cr.execute("delete from %s" % model.replace('.', '_'))
            cr.execute("select setval('%s_id_seq', 1)" % model.replace('.', '_'))

        for data_record in data_json:
            v_list = []
            k_str = ''

            for k, v in data_record['fields'].iteritems():
                k_str += "%s, " % str(k)
                v_list.append(v)

            k_str = k_str[:-2]
            k_str = "(%s)" % k_str

            cr.execute("insert into %s %s values %s" % (
                data_record['model'].replace('.', '_'),
                k_str,
                str(tuple(v_list))
            ))

        return {}

    _columns = {
        'dm_import_data_wizard_data': fields.binary(
            'DM Import Data Wizard Data'),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

DmImportDataWizard()
