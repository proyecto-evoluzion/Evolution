# -*- coding: utf-8 -*-
###############################################################################
#
#    BroadTech IT Solutions Pvt Ltd
#    Copyright (C) 2018 BroadTech IT Solutions Pvt Ltd 
#    (<http://broadtech-innovations.com>).
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


{
    'name': 'Clinica Doctor Datas',
    'version': '1.51',
    'license': 'Other proprietary',
    'category': 'custom',
    'description': """
     Clinica Doctor Datas
    """,
    'author' : 'BroadTech IT Solutions Pvt Ltd',
    'website' : 'http://www.broadtech-innovations.com',
    'depends': [
        'base','contacts','l10n_co_res_partner','product', 'l10n_co_tax_extension','account','web'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/doctor_sequence.xml',
        'data/doctor_surgical_technologist_element.xml',
        'data/self_doc_rule.xml',
        'data/localisation_province_data.xml',
        'wizard/create_health_professional_view.xml',
        'wizard/load_anesthesia_view.xml',
        'report/clinica_visualizer_report_template.xml',
        'report/clinica_visualizer_report.xml',
        'report/inherit_external_layout.xml',
        'views/doctor_details_view.xml',
        'views/res_config_settings_view.xml',
        'views/clinica_text_template_view.xml',
        'views/res_partner_view.xml',
        'views/doctor_product_view.xml',
        'views/doctor_attentions_view.xml',
        'views/quirurgic_sheet_view.xml',
        'views/nurse_sheet_view.xml',
        'views/recovery_sheet_view.xml',
        'views/nurse_chief_sheet.xml',
        'views/doctor_calendar_view.xml',
        'views/anhestesic_registry_view.xml',
        'views/post_anhestesic_care_view.xml',
        'views/plastic_surgery_sheet_view.xml',
        'views/medical_evolution_view.xml',
        'views/doctor_epicrisis_view.xml',
        'views/quirurgical_check_list_view.xml',
        'views/clinica_record_list_visualizer_view.xml',
        'views/account_invoice_view.xml',
        'views/doctor_surgical_technologist.xml',
        'views/doctor_clinica_prescription.xml',
        'views/assets.xml',
        'views/record_authenticate_views.xml',
        'views/base_localization_menu.xml',
        'views/clinica_calendar_cancelation.xml',
        'data/l10n_diseases_co_data.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    "external_dependencies": { # python pip packages
    #     'python': ['suds', 'dateutil'],
    },
    'installable': True,
    'auto_install': False,
 }


# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2: