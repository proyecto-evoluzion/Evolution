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
from odoo.exceptions import ValidationError

class AnhestesicRegistry(models.Model):
    _name = "clinica.anhestesic.registry"
    _order = 'id desc'
    _description = 'Anhestesic Registry'
    
    name = fields.Char(string="Name")
    intervention_date = fields.Datetime(string='Intervention Date', default=fields.Datetime.now, copy=False)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
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
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    product_id = fields.Many2one('product.product', 'Process', ondelete='restrict')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
                                        string='Type of Anesthesia')
    start_time = fields.Datetime(string='Start Time', default=fields.Datetime.now, copy=False)
    end_time = fields.Datetime(string='End Time', copy=False)
    preoperative_note = fields.Text(string='Preoperative Note')
    
    paraclinical_exam_date = fields.Date(string="Paraclinical Exam Date")
    paraclinical_hb = fields.Float(string="HB")
    paraclinical_hto = fields.Float(string="Hto (Hematocrit)")
    paraclinical_leukocytes = fields.Float(string="Leukocytes")
    paraclinical_differential = fields.Text(string="Differential")
    paraclinical_vsg = fields.Integer(string="VSG")
    paraclinical_pt = fields.Float(string="PT")
    paraclinical_ptt = fields.Float(string="PTT")
    paraclinical_platelets = fields.Float(string="Platelets")
    paraclinical_tc = fields.Float(string="TC")
    paraclinical_glycemia = fields.Float(string="Glycemia")
    paraclinical_creatinine = fields.Float(string="Creatinine")
    paraclinical_albumin = fields.Float(string="Albumin")
    paraclinical_glob = fields.Text(string="Glob")
    paraclinical_ecg = fields.Text(string="E.C.G")
    paraclinical_rx_chest = fields.Text(string="Rx. Chest")
    paraclinical_others = fields.Text(string="Paraclinical Others")
    paraclinical_asa = fields.Selection([('1','ASA 1'),('2','ASA 2'),('3','ASA 3'),
                                         ('4','ASA 4'), ('5','ASA 5') ], string="A.S.A")
    paraclinical_goldman = fields.Text(string="GOLDMAN")
    
    monitor = fields.Text(string="Monitor")
    crystalloids = fields.Float(string="Crystalloids")
    blood = fields.Float(string="Blood")
    colloids = fields.Float(string="Colloids")
    infiltrated = fields.Float(string="Infiltrated")
    bleeding = fields.Float(string="Bleeding")
    diuresis = fields.Float(string="Diuresis")
    liposuction = fields.Float(string="Liposuction")
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for anhestesic in self:
            if anhestesic.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(anhestesic.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    anhestesic.age_meassure_unit = '3'
                    anhestesic.age = int(date_diff.days)
                elif difference < 365:
                    anhestesic.age_meassure_unit = '2'
                    anhestesic.age = int(date_diff.months)
                else:
                    anhestesic.age_meassure_unit = '1'
                    anhestesic.age = int(date_diff.years)
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.document_type = self.patient_id.tdoc
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.ref
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh
            
    @api.onchange('document_type','numberid_integer','numberid')
    def onchange_numberid(self):
        if self.document_type and self.document_type not in ['cc','ti']:
            self.numberid_integer = 0
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
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
    def _check_document_types(self):
        for anhestesic in self:
            if anhestesic.age_meassure_unit == '3' and anhestesic.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if anhestesic.age > 17 and anhestesic.age_meassure_unit == '1' and anhestesic.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if anhestesic.age_meassure_unit in ['2','3'] and anhestesic.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if anhestesic.document_type == 'ms' and anhestesic.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if anhestesic.document_type == 'as' and anhestesic.age_meassure_unit == '1' and anhestesic.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('anhestesic.registry') or '/'
        if vals.get('document_type', False) and vals['document_type'] in ['cc','ti']:
            numberid_integer = 0
            if vals.get('numberid_integer', False):
                numberid_integer = vals['numberid_integer']
            numberid = self._check_assign_numberid(numberid_integer)
            vals.update({'numberid': numberid})
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(AnhestesicRegistry, self).create(vals)
        res._check_document_types()
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('document_type', False) or 'numberid_integer' in  vals:
            if vals.get('document_type', False):
                document_type = vals['document_type']
            else:
                document_type = self.document_type
            if document_type in ['cc','ti']:
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
         
        res = super(AnhestesicRegistry, self).write(vals)
        self._check_document_types()
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.surgeon_id and self.surgeon_id.id or False,
            'default_view_model': 'anhestesic_registry',
            }
        return vals
           
    @api.multi
    def action_view_clinica_record_history(self):
        context = self._set_visualizer_default_values()
        return {
                'name': _('Clinica Record History'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'clinica.record.list.visualizer',
                'view_id': self.env.ref('clinica_doctor_data.clinica_record_list_visualizer_form').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:




