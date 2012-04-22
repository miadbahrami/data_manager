from osv import osv, fields
import base64
from lxml import etree
from tools.translate import _


class DeExportDataWizard(osv.osv_memory):
    _name = 'de.export.data.wizard'
    _inherit = 'ir.wizard.screen'

    def export_data(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)[0]
        ir_model_id = this.ir_model_id
        model_name = ir_model_id.model

        input_model_obj = self.pool.get(model_name)
        input_model_id_list = input_model_obj.search(cr, uid, [],
                                                     context=context)
        if not input_model_id_list:
            raise osv.except_osv((_('Warning')),
                ('There is no data for %s class' % model_name))

        input_model_list = input_model_obj.read(cr, uid, input_model_id_list,
                                                [], context=context)
        # Checking for iso_code field for main class
        if 'iso_code' not in input_model_list[0]:
            raise osv.except_osv((_('Warning')),
                                 (_("%s class does not have iso_code field" % model_name)))

        # Checking for duplication of iso_code content for main class
        iso_code_list = []
        for input_model in input_model_list:
            iso_code_list.append(input_model['iso_code'])

        if len(iso_code_list) > len(set(iso_code_list)):
            raise osv.except_osv(
                (_('Warning')),
                (_("iso_code field values of %s class must be unique" %
                   model_name)))

        # Creating XML
        openerp_tag = etree.Element('openerp')
        data_tag = etree.SubElement(openerp_tag, 'data')
        data_tag.attrib['noupdate'] = "1"

        for input_model in input_model_list:
            record_tag = etree.SubElement(data_tag, 'record')
            record_tag.attrib['id'] = "%s_%s" % (model_name.replace('.', '_'),
                                                 input_model['id'])
            record_tag.attrib['model'] = model_name

            for ir_model_field in ir_model_id.field_id:
                # Checking for existing model name in input model
                if ir_model_field.name in input_model:
                    field_tag = etree.SubElement(record_tag, 'field')
                    field_tag.attrib['name'] = ir_model_field.name

                    # data exporter doesn't support many2many field right now
                    if ir_model_field.ttype not in ['one2many', 'many2many']:
                        if ir_model_field.ttype == 'many2one':
                            temp_object_obj = self.pool.get(ir_model_field.model)

                            if input_model[ir_model_field.name]:
                                temp_object_id = input_model[ir_model_field.name][0]

                                temp_object = temp_object_obj.browse(cr, uid,
                                                                     temp_object_id,
                                                                     context=context)
                                temp_object_rel_name = temp_object._model._columns[ir_model_field.name]._obj
                                temp_object_rel_obj = self.pool.get(temp_object_rel_name)

                                ### Checking for Duplication of many2one field class iso_code content
                                iso_code_list = []
                                temp_object_rel_id_list = temp_object_rel_obj.search(cr, uid, [], context=context)
                                temp_object_rel_list = temp_object_rel_obj.browse(
                                    cr, uid, temp_object_rel_id_list,
                                    context=context)

                                for temp_object_rel in temp_object_rel_list:
                                    iso_code_list.append(temp_object_rel.iso_code)

                                if len(iso_code_list) > len(set(iso_code_list)):
                                    raise osv.except_osv(
                                        (_('Warning')),
                                        (_("iso_code field values of %s class must be unique" % ir_model_field.model)))
                                ###

                                ### check iso_code of many2one field class
                                temp_object_rel = temp_object_rel_obj.browse(
                                    cr, uid, input_model[ir_model_field.name][0])

                                try:
                                    temp_iso_code = temp_object_rel.iso_code

                                except AttributeError:
                                    raise osv.except_osv(
                                        (_('Warning')),
                                        (_("%s class doesn't have iso_code field!" %
                                           ir_model_field.model)))
                                ###

                                field_tag.attrib['search'] = "[('iso_code', '=', %s)]" % temp_iso_code
                                field_tag.attrib['model'] = temp_object_rel_name

                        else:
                            try:
                                # False field should not set, except boolean fields and integers
                                if not input_model[ir_model_field.name] and ir_model_field.ttype not in ('boolean', 'integer'):
                                    raise KeyError

                                field_tag.text = unicode(input_model[ir_model_field.name])

                            except KeyError:
                                field_tag.text = ''

        out = base64.encodestring(etree.tostring(openerp_tag))

        return self.write(cr, uid, ids, {
            'state': 'done', 'de_export_data_wizard_data': out,
            'name': "%s_data.xml" % model_name.replace('.', '_')
        }, context=context)

    _columns = {
        'name': fields.char('Filename', size=128, readonly=True),
        'ir_model_id': fields.many2one('ir.model', 'IR Model'),
        'de_export_data_wizard_data': fields.binary('Export Data Wizard Data',
                                                 readonly=True),
        'state': fields.selection([('init', 'init'), ('done', 'done')],
                                  'state', readonly=True),
    }

    _defaults = {'state': 'init'}

DeExportDataWizard()
