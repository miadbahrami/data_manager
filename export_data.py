from osv import osv, fields
import base64
from lxml import etree
from tools.translate import _


class ExportDataWizard(osv.osv_memory):
    _name = 'export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        model_name = this.ir_model_id.model

        input_model_obj = self.pool.get(model_name)
        input_model_id_list = input_model_obj.search(cr, uid, [],
                                                     context=context)
        input_model_list = input_model_obj.read(cr, uid, input_model_id_list,
                                                [], context=context)

        # Creating XML
        openerp_tag = etree.Element('openerp')
        data_tag = etree.SubElement(openerp_tag, 'data')
        data_tag.attrib['noupdate'] = "1"

        for input_model in input_model_list:
            record_tag = etree.SubElement(data_tag, 'record')
            record_tag.attrib['id'] = "%s_%s" % (model_name.replace('.', '_'),
                                                 input_model['id'])
            record_tag.attrib['model'] = model_name

            for ir_model_field in this.ir_model_id.field_id:
                field_tag = etree.SubElement(record_tag, 'field')
                field_tag.attrib['name'] = ir_model_field.name

                if ir_model_field.ttype not in ['one2many', 'many2many']:
                    if ir_model_field.ttype == 'many2one':
                        temp_object_obj = self.pool.get(ir_model_field.model)
                        temp_object_id = input_model[ir_model_field.name][0]
                        temp_object = temp_object_obj.browse(cr, uid,
                                                             temp_object_id,
                                                             context=context)
                        temp_object_rel_name = temp_object._model._columns[ir_model_field.name]._obj
                        temp_object_rel_obj = self.pool.get(temp_object_rel_name)
                        temp_object_rel = temp_object_rel_obj.browse(
                            cr, uid, input_model[ir_model_field.name][0])

                        try:
                            temp_iso_code = temp_object_rel.iso_code

                        except AttributeError:
                            raise osv.except_osv(
                                (_('Warning')),
                                (_("%s class doesn't have iso_code field!" %
                                   ir_model_field.model)))

                        field_tag.attrib['search'] = "[('iso_code', '=', %s)]" % temp_iso_code
                        field_tag.attrib['model'] = temp_object_rel_name

                    else:
                        field_tag.text = unicode(input_model[ir_model_field.name])

        out = base64.encodestring(etree.tostring(openerp_tag))

        return self.write(cr, uid, ids, {
            'state': 'done', 'export_data_wizard_data': out,
            'name': "%s_data.xml" % model_name.replace('.', '_')
        }, context=context)

    _columns = {
        'name': fields.char('Filename', size=128, readonly=True),
        'ir_model_id': fields.many2one('ir.model', 'IR Model'),
        'export_data_wizard_data': fields.binary('Export Data Wizard Data',
                                                 readonly=True),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

ExportDataWizard()
