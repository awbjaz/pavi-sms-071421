from odoo import api, models, fields, _
from lxml import etree
from odoo.addons.base_address_city.models.res_partner import Partner as OriginalPartner
import logging

_logger = logging.getLogger(__name__)


@api.model
def _fields_view_get_address(self, arch):
    _logger.debug(f"_FIELDS_VIEW_GET_ADDRESS")
    arch = super(OriginalPartner, self)._fields_view_get_address(arch)
    # render the partner address accordingly to address_view_id
    doc = etree.fromstring(arch)
    if doc.xpath("//field[@name='city_id']"):
        return arch

    replacement_xml = """
        <div>
            <field name="country_enforce_cities" invisible="1"/>
            <field name="parent_id" invisible="1"/>
            <field name='city' placeholder="%(placeholder)s" class="o_address_city"
                attrs="{
                    'invisible': [('country_enforce_cities', '=', True), '|', ('city_id', '!=', False), ('city', 'in', ['', False ])],
                    'readonly': [('salesforce_id','!=', False)]
                }"
            />
            <field name='city_id' placeholder="%(placeholder)s" string="%(placeholder)s" class="o_address_city"
                context="{'default_country_id': country_id,
                          'default_name': city,
                          'default_zipcode': zip,
                          'default_state_id': state_id}"
                domain="[('country_id', '=', country_id)]"
                attrs="{
                    'invisible': [('country_enforce_cities', '=', False)],
                    'readonly': [('salesforce_id','!=', False)]
                }"
            />
        </div>
    """

    replacement_data = {
        'placeholder': _('City'),
    }

    def _arch_location(node):
        in_subview = False
        view_type = False
        parent = node.getparent()
        while parent is not None and (not view_type or not in_subview):
            if parent.tag == 'field':
                in_subview = True
            elif parent.tag in ['list', 'tree', 'kanban', 'form']:
                view_type = parent.tag
            parent = parent.getparent()
        return {
            'view_type': view_type,
            'in_subview': in_subview,
        }

    for city_node in doc.xpath("//field[@name='city']"):
        location = _arch_location(city_node)
        replacement_data['parent_condition'] = ''
        if location['view_type'] == 'form' or not location['in_subview']:
            replacement_data['parent_condition'] = ", ('parent_id', '!=', False)"

        replacement_formatted = replacement_xml % replacement_data
        for replace_node in etree.fromstring(replacement_formatted).getchildren():
            city_node.addprevious(replace_node)
        parent = city_node.getparent()
        parent.remove(city_node)

    arch = etree.tostring(doc, encoding='unicode')
    return arch


OriginalPartner._fields_view_get_address = _fields_view_get_address