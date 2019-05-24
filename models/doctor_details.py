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


import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo import tools
import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError
import base64

class AssurancePlan(models.Model):
    _name = "assurance.plan"
    
    name = fields.Char(string='Plan')
    code = fields.Char(string='Plan Code')
    assurance_partner_id = fields.Many2one('res.partner',string='Assurance Company')
    
class DoctorPatientOccupation(models.Model):
    _name = "doctor.patient.occupation"
    
    code = fields.Char(string='Code', copy=False)
    name = fields.Char(string='Description')
    
class DoctorDiseases(models.Model):
    _name = "doctor.diseases"

    code = fields.Char('Code', size=4, required=True)
    name = fields.Char('Disease', size=256, required=True)

    _sql_constraints = [('code_uniq', 'unique (code)', 'The Medical Diseases code must be unique')]
    
class Doctor(models.Model):
    _name = "doctor.doctor"
    _rec_name = "partner_id"
    
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    first_name = fields.Char(string='First Name')
    first_last_name = fields.Char(string='First Last Name')
    second_name = fields.Char(string='Second Name')
    second_last_name = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    partner_id = fields.Many2one('res.partner', copy=False, ondelete='restrict', string='Related Partner', 
                                    help='Partner-related data of doctor ')
    
    def _check_email(self, email):
        if not tools.single_email_re.match(email):
            raise ValidationError(_('Invalid Email ! Please enter a valid email address.'))
        else:
            return True
    
    @api.multi
    def _get_related_partner_vals(self, vals):
        ## code for updating partner with change in administrative data
        ## administrative data will not get updated with partner changes
        for data in self:
            partner_vals = {}
            if 'first_name' in vals or 'first_last_name' in vals or 'second_name' in vals or 'second_last_name' in vals:
                first_name = data.first_name or ''
                first_last_name = data.first_last_name or ''
                second_name = data.second_name or ''
                second_last_name = data.second_last_name or ''
                if 'first_name' in vals:
                    first_name = vals.get('first_name', False) or ''
                    partner_vals.update({'x_name1': vals.get('first_name', False)})
                if 'first_last_name' in vals:
                    first_last_name = vals.get('first_last_name', False) or ''
                    partner_vals.update({'x_name2': vals.get('first_last_name', False)})
                if 'second_name' in vals:
                    second_name = vals.get('second_name', False) or ''
                    partner_vals.update({'x_lastname1': vals.get('second_name', False)})
                if 'second_last_name' in vals:
                    second_last_name = vals.get('second_last_name', False) or ''
                    partner_vals.update({'x_lastname2': vals.get('second_last_name', False)})
                nameList = [
                    first_name.strip(),
                    first_last_name.strip(),
                    second_name.strip(),
                    second_last_name.strip()
                    ]
                formatedList = []
                name = ''
                for item in nameList:
                    if item is not '':
                        formatedList.append(item)
                    name = ' ' .join(formatedList).title()
                partner_vals.update({'name': name})
            if 'email' in vals:
                partner_vals.update({'email': vals.get('email', False)})
            if 'phone' in vals:
                partner_vals.update({'phone': vals.get('phone', False)})
            return partner_vals
      
    @api.model
    def create(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        res = super(Doctor, self).create(vals)
        partner_vals = res._get_related_partner_vals(vals)
        partner_vals.update({'doctype': 1})
        partner = self.env['res.partner'].create(partner_vals)
        res.partner_id = partner.id 
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        res = super(Doctor, self).write(vals)
        if 'first_name' in vals or 'first_last_name' in vals or 'second_name' in vals or 'second_last_name' in vals\
                 or 'email' in vals or 'phone' in vals :
            for doctor in self:
                if doctor.partner_id:
                    partner_vals = doctor._get_related_partner_vals(vals)
                    doctor.partner_id.write(partner_vals)
        return res
    

class DoctorAdministrativeData(models.Model):
    _name = "doctor.administrative.data"
    _rec_name='patient_name'
    
    @api.model
    def _default_image(self):
        image_path = get_module_resource('clinica_doctor_data', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    
    name = fields.Char(string='Number ID')
    patient_name = fields.Char(string='Patient Name', compute='_compute_patient_name', store=True)
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    image = fields.Binary("Image", attachment=True, default=_default_image,
        help="This field holds the image used as avatar for this contact, limited to 1024x1024px", copy=False)
    image_medium = fields.Binary("Medium-sized image", attachment=True, 
        help="Medium-sized image of this contact. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views.", copy=False)
    image_small = fields.Binary("Small-sized image", attachment=True, 
        help="Small-sized image of this contact. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required.", copy=False)
    first_name = fields.Char(string='First Name')
    first_last_name = fields.Char(string='First Last Name')
    second_name = fields.Char(string='Second Name')
    second_last_name = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    birth_country_id = fields.Many2one('res.country', string='Country of Birth')
#     birth_department_id = fields.Many2one('res.country.state', string='Department of Birth Place')
    birth_city_id = fields.Many2one('res.country.state.city', string='Location/City/Town of Birth')
#     birth_district = fields.Char(string='Districts/localties/areas of Birth Place')
#     birth_neighborhood = fields.Char(string='Neighborhood of Birth Place')
#     birth_address = fields.Text(string="Address of Birth Place")
    residence_country_id = fields.Many2one('res.country', string='Residence Country')
    residence_department_id = fields.Many2one('res.country.state', string='Residence Department')
    residence_city_id = fields.Many2one('res.country.state.city', string='Residence Location/City/Town')
#     residence_district = fields.Char(string='Residence Districts/localties/areas')
#     residence_neighborhood = fields.Char(string='Residence Neighborhood')
    residence_address = fields.Text(string="Residence Address")
    civil_state = fields.Selection([('separated','Separada/o'),('single','Soltera/o'),('married','Casada/o'),
                                   ('free_union','Unión libre'),('widow','Viuda/o')], string='Civil Status')
#     beliefs = fields.Text(string="Beliefs")
    occupation_id = fields.Many2one('doctor.patient.occupation', string='Occupation')
#     profession_id = fields.Char(string='Profession')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
#     mobile = fields.Char('Mobile Number')
    accompany_name = fields.Char("Name of the companion")
    accompany_relationship = fields.Selection([('mother','Mother'),('father','Father'),('grand_father','Grand Father'),
                                 ('grand_mother','Grand Mother'),('uncle','Uncle'),('aunt','Aunt'),
                                 ('friend','Friend'),('other','Other')], string="Accompany Person's Relationship")
    other_accompany_relationship = fields.Char(string="Other Accompany Person's Relationship")
    accompany_phone = fields.Char("Accompany Person's Phone Number")
    responsible_name = fields.Char("Responsible Person's Name")
    responsible_relationship = fields.Selection([('mother','Mother'),('father','Father'),('grand_father','Grand Father'),
                                     ('grand_mother','Grand Mother'),('uncle','Uncle'),('aunt','Aunt'),
                                     ('friend','Friend'),('other','Other')], string="Responsible Person's Relationship")
    other_responsible_relationship = fields.Char(string="Other Responsible Person's Relationship")
    responsible_phone = fields.Char("Responsible Person's Phone Number")
#     father_name = fields.Char(string="Father's Name")
#     father_occupation = fields.Char(string="Father's Occupation")
#     father_address = fields.Text(string="Father's Address")
#     father_phone = fields.Char(string="Father's Phone Number")
#     mother_name = fields.Char(string="Mother's Name")
#     mother_occupation = fields.Char(string="Mother's Occupation")
#     mother_address = fields.Text(string="Mother's Address")
#     mother_phone = fields.Char(string="Mother's Phone Number")
    user_type =  fields.Selection([('contributory','Contributivo'),('subsidized','Subsidiado'),('linked','Vinculado')], string="User Type")
#     primary_payer =  fields.Selection([('private_user','Usuario Particular'),('eps','EPS'),
#                                        ('another_insurer','Otra Aseguradora'),('mixed','Pago Mixto')], string="Primary Payer")
    assurance_partner_id = fields.Many2one('res.partner',string='Assurance Company')
#     assurance_plan_id = fields.Many2one('assurance.plan', string='Assurer Plans')
#     other_assurance_partner_id = fields.Many2one('res.partner',string='Other Assurance Company')
#     other_assurance_plan_id = fields.Many2one('assurance.plan', string='Other Assurer Plans')
    doctor_id = fields.Many2one('doctor.doctor', ondelete='restrict', string='Treating Doctor')
    partner_id = fields.Many2one('res.partner', copy=False, ondelete='restrict', string='Related Partner', 
                                    help='Partner-related data of administrative data ')
    
    
    @api.multi
    @api.depends('first_name', 'first_last_name', 'second_name', 'second_last_name')
    def _compute_patient_name(self):
        for data in self:
            first_name = data.first_name or ''
            first_last_name = data.first_last_name or ''
            second_name = data.second_name or ''
            second_last_name = data.second_last_name or ''
            nameList = [
                first_name.strip(),
                first_last_name.strip(),
                second_name.strip(),
                second_last_name.strip()
                ]
            formatedList = []
            name = ''
            for item in nameList:
                if item is not '':
                    formatedList.append(item)
                name = ' ' .join(formatedList).title()
            data.patient_name = name
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for data in self:
            if data.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(data.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    data.age_meassure_unit = '3'
                    data.age = int(date_diff.days)
                elif difference < 365:
                    data.age_meassure_unit = '2'
                    data.age = int(date_diff.months)
                else:
                    data.age_meassure_unit = '1'
                    data.age = int(date_diff.years)
                    
    def _check_birth_date(self, birth_date):
        warn_msg = '' 
        today_datetime = datetime.today()
        today_date = today_datetime.date()
        birth_date_format = datetime.strptime(birth_date, DF).date()
        date_difference = today_date - birth_date_format
        difference = int(date_difference.days)    
        if difference < 0: 
            warn_msg = _('Invalid birth date!')
        return warn_msg
            
    @api.onchange('birth_date','age_meassure_unit')
    def onchange_birth_date(self):
        if self.age_meassure_unit == '3':
            self.document_type = 'rc'
        if self.birth_date:
            warn_msg = self._check_birth_date(self.birth_date)
            if warn_msg:
                warning = {
                        'title': _('Warning!'),
                        'message': warn_msg,
                    }
                return {'warning': warning}
                 
            
    @api.onchange('numberid_integer', 'document_type')
    def onchange_numberid_integer(self):
        if self.numberid_integer:
            self.name = str(self.numberid_integer) 
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer == 0:
            self.name = str(0)
    
    def _check_email(self, email):
        if not tools.single_email_re.match(email):
            raise ValidationError(_('Invalid Email ! Please enter a valid email address.'))
        else:
            return True
        
    def _check_assign_numberid(self, numberid_integer):
        if numberid_integer == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(numberid_integer)
            return numberid
    
    @api.multi
    def _check_document_types(self):
        for data in self:
            if data.age_meassure_unit == '3' and data.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if data.age > 17 and data.age_meassure_unit == '1' and data.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if data.age_meassure_unit in ['2','3'] and data.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if data.document_type == 'ms' and data.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if data.document_type == 'as' and data.age_meassure_unit == '1' and data.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
        
    @api.multi
    def _get_related_partner_vals(self, vals):
        ## code for updating partner with change in administrative data
        ## administrative data will not get updated with partner changes
        for data in self:
            partner_vals = {}
            if 'first_name' in vals or 'first_last_name' in vals or 'second_name' in vals or 'second_last_name' in vals:
                first_name = data.first_name or ''
                first_last_name = data.first_last_name or ''
                second_name = data.second_name or ''
                second_last_name = data.second_last_name or ''
                if 'first_name' in vals:
                    first_name = vals.get('first_name', False) or ''
                    partner_vals.update({'x_name1': vals.get('first_name', False)})
                if 'first_last_name' in vals:
                    first_last_name = vals.get('first_last_name', False) or ''
                    partner_vals.update({'x_name2': vals.get('first_last_name', False)})
                if 'second_name' in vals:
                    second_name = vals.get('second_name', False) or ''
                    partner_vals.update({'x_lastname1': vals.get('second_name', False)})
                if 'second_last_name' in vals:
                    second_last_name = vals.get('second_last_name', False) or ''
                    partner_vals.update({'x_lastname2': vals.get('second_last_name', False)})
                nameList = [
                    first_name.strip(),
                    first_last_name.strip(),
                    second_name.strip(),
                    second_last_name.strip()
                    ]
                formatedList = []
                name = ''
                for item in nameList:
                    if item is not '':
                        formatedList.append(item)
                    name = ' ' .join(formatedList).title()
                partner_vals.update({'name': name})
            if 'birth_date' in vals:
                partner_vals.update({'xbirthday': vals.get('birth_date', False)})
            if 'email' in vals:
                partner_vals.update({'email': vals.get('email', False)})
            if 'phone' in vals:
                partner_vals.update({'phone': vals.get('phone', False)})
            if 'mobile' in vals:
                partner_vals.update({'mobile': vals.get('mobile', False)})
            if 'image' in vals:
                partner_vals.update({'image': vals.get('image', False)})
            if 'residence_district' in vals:
                partner_vals.update({'street2': vals.get('residence_district', False)})
            if 'residence_department_id' in vals:
                partner_vals.update({'state_id': vals.get('residence_department_id', False)})
            if 'residence_country_id' in vals:
                partner_vals.update({'country_id': vals.get('residence_country_id', False)})
            if 'residence_address' in vals:
                partner_vals.update({'street': vals.get('residence_address', False)})
            return partner_vals
    
    @api.model
    def create(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        if vals.get('document_type', False) and vals['document_type'] in ['cc','ti']:
            numberid_integer = 0
            if vals.get('numberid_integer', False):
                numberid_integer = vals['numberid_integer']
            numberid = self._check_assign_numberid(numberid_integer)
            vals.update({'name': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        tools.image_resize_images(vals)
        res = super(DoctorAdministrativeData, self).create(vals)
        res._check_document_types()
        partner_vals = res._get_related_partner_vals(vals)
        partner_vals.update({'doctype': 1})
        partner = self.env['res.partner'].create(partner_vals)
        res.partner_id = partner.id 
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('email', False):
            self._check_email(vals.get('email'))
        tools.image_resize_images(vals)
        if vals.get('document_type', False) or vals.get('numberid_integer', False):
            if vals.get('document_type', False):
                document_type = vals['document_type']
            else:
                document_type = self.document_type
            if document_type in ['cc','ti']:
                if vals.get('numberid_integer', False):
                    numberid_integer = vals['numberid_integer']
                else:
                    numberid_integer = self.numberid_integer
                numberid = self._check_assign_numberid(numberid_integer)
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        tools.image_resize_images(vals)
        res = super(DoctorAdministrativeData, self).write(vals)
        self._check_document_types()
        if 'first_name' in vals or 'first_last_name' in vals or 'second_name' in vals or 'second_last_name' in vals\
                 or 'birth_date' in vals or 'email' in vals or 'phone' in vals or 'mobile' in vals or 'image' in vals \
                 or 'residence_district' in vals or 'residence_department_id' in vals or 'residence_country_id' in vals or 'residence_address' in vals:
            for data in self:
                if data.partner_id:
                    partner_vals = data._get_related_partner_vals(vals)
                    data.partner_id.write(partner_vals)
        return res

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
