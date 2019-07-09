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


from odoo import models, fields, api, _

import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.exceptions import ValidationError
import html2text

class DoctorEpicrisis(models.Model):
    _name = "doctor.epicrisis"
    _order = 'id desc'
    
    @api.model
    def _get_signature(self):
        user = self.env.user
        signature = html2text.html2text(user.signature)
        return signature
    
    name = fields.Char(string='Name', copy=False)
    patient_in_date = fields.Datetime(string='In Date', copy=False)
    patient_out_date = fields.Datetime(string='Out Date', copy=False)
    tdoc = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                             ('pa','PA - Passport'),('rc','RC - Civil Registry'),
                             ('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),
                             ('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    disease_id = fields.Many2one('doctor.diseases', 'Diseases', ondelete='restrict')
    procedure_id = fields.Many2one('product.product', 'Procedure', ondelete='restrict')
    sign_stamp = fields.Text(string='Sign and médical stamp', default=_get_signature)
    user_id = fields.Many2one('res.users', string='Medical registry number', default=lambda self: self.env.user)
    epicrisis_note = fields.Text(string='Epicrisis')
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for epicrisis in self:
            if epicrisis.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(epicrisis.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    epicrisis.age_meassure_unit = '3'
                    epicrisis.age = int(date_diff.days)
                elif difference < 365:
                    epicrisis.age_meassure_unit = '2'
                    epicrisis.age = int(date_diff.months)
                else:
                    epicrisis.age_meassure_unit = '1'
                    epicrisis.age = int(date_diff.years)
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.tdoc = self.patient_id.tdoc
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.ref
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh
            
    @api.onchange('tdoc','numberid_integer','numberid')
    def onchange_numberid(self):
        if self.tdoc and self.tdoc not in ['cc','ti']:
            self.numberid_integer = 0
        if self.tdoc and self.tdoc in ['cc','ti'] and self.numberid_integer:
            self.numberid = self.numberid_integer
            
    def _check_assign_numberid(self, numberid_integer):
        if numberid_integer == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(numberid_integer)
            return numberid
    
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
    
    @api.multi
    def _check_tdocs(self):
        for epicrisis in self:
            if epicrisis.age_meassure_unit == '3' and epicrisis.tdoc not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if epicrisis.age > 17 and epicrisis.age_meassure_unit == '1' and epicrisis.tdoc in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if epicrisis.age_meassure_unit in ['2','3'] and epicrisis.tdoc in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if epicrisis.tdoc == 'ms' and epicrisis.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if epicrisis.tdoc == 'as' and epicrisis.age_meassure_unit == '1' and epicrisis.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('doctor.epicrisis') or '/'
        if vals.get('tdoc', False) and vals['tdoc'] in ['cc','ti']:
            numberid_integer = 0
            if vals.get('numberid_integer', False):
                numberid_integer = vals['numberid_integer']
            numberid = self._check_assign_numberid(numberid_integer)
            vals.update({'numberid': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(DoctorEpicrisis, self).create(vals)
        res._check_tdocs()
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('tdoc', False) or 'numberid_integer' in  vals:
            if vals.get('tdoc', False):
                tdoc = vals['tdoc']
            else:
                tdoc = self.tdoc
            if tdoc in ['cc','ti']:
                if 'numberid_integer' in  vals:
                    numberid_integer = vals['numberid_integer']
                else:
                    numberid_integer = self.numberid_integer
                numberid = self._check_assign_numberid(numberid_integer)
                vals.update({'numberid': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
         
        res = super(DoctorEpicrisis, self).write(vals)
        self._check_tdocs()
        return res
            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


