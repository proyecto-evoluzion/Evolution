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

from odoo import tools
import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.exceptions import ValidationError

class PresurgicalRecord(models.Model):
    _name = "doctor.presurgical.record"
    _rec_name = 'number'
    
    number = fields.Char('Attention number', readonly=True)
    attention_code_id = fields.Many2one('doctor.cups.code', string="Attention Code", ondelete='restrict')
    date_attention = fields.Date('Date of attention', required=True, default=fields.Date.context_today)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.administrative.data', 'Patient', ondelete='restrict')
    first_name = fields.Char(string='First Name')
    first_last_name = fields.Char(string='First Last Name')
    second_name = fields.Char(string='Second Name')
    second_last_name = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    
    consultation_reason = fields.Text(string="Reason for Consultation")
    pathological = fields.Text(string="Pathological")
    surgical = fields.Text(string="Surgical")
    relatives = fields.Text(string="Relatives")
    smoke = fields.Boolean(string="Smoke")
    cigarate_daily = fields.Integer(string="Cigarettes / Day")
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks")
    alcohol_frequency = fields.Integer(string="Frequency")
    marijuana = fields.Boolean(string="Marijuana")
    cocaine = fields.Boolean(string="Cocaine")
    ecstasy = fields.Boolean(string="Ecstasy")
    body_background_others = fields.Text(string="Body Background Others")
    pharmacological = fields.Text(string="Pharmacological")
    allergic = fields.Text(string="Allergic")
    pregnancy_number = fields.Integer(string="Number of Pregnancies")
    child_number = fields.Integer(string="Number of Children")
    abortion_number = fields.Integer(string="Number of Abortions")
    last_birth_date = fields.Date(string="Date of Last Birth")
    last_menstruation_date = fields.Date(string="Date of Last Menstruation")
    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods")
    
    physical_sistolic_arteric_presure = fields.Integer(string="Sistolic Arteric Pressure")
    physical_diastolic_artery_presure = fields.Integer(string="Diastolic Artery Pressure")
    physical_fc = fields.Integer(string="FC")
    physical_fr = fields.Integer(string="FR")
    physical_weight = fields.Float(string="Weight")
    physical_size = fields.Float(string="Size")
    physical_body_mass_index = fields.Float(string="IMC (Body Mass Index)")
    physical_exam = fields.Text(string="Physical Exam")
    
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
    paraclinical_goldman = fields.Selection([('class_1','0-5 Points: Class I 1% Complications'),
                                             ('class_2','6-12 Points: Class II 7% Complications'),
                                             ('class_3','13-25 Points: Class III 14% Complications'),
                                             ('class_4','26-53 Points: Class IV 78% Complications')],
                                            string="GOLDMAN", default='class_1')
    
    disease_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease2_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease3_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease_type = fields.Selection([('principal', 'Principal'),('related', 'Relacionado')], string='Kind')
    disease_state = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'confirmado repetido')], string='Disease Status')
    disease_state2 = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'confirmado repetido')], string='Disease Status')
    disease_state3 = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'confirmado repetido')], string='Disease Status')
    process_id = fields.Many2one('product.product', string='Process', ondelete='restrict')
    plan_analysis = fields.Text(string="Plan, Analysis and Conduct")
    medical_recipe = fields.Text(string="Medical Orders and Recipe")
    
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
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.first_name = self.patient_id.first_name
            self.first_last_name = self.patient_id.first_last_name
            self.second_name = self.patient_id.second_name
            self.second_last_name = self.patient_id.second_last_name
            
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
            self.numberid = str(self.numberid_integer) 
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer == 0:
            self.numberid = str(0)
            
    def _check_assign_numberid(self, numberid_integer):
        if numberid_integer == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(numberid_integer)
            return numberid
    
    @api.multi
    def _check_document_types(self):
        for record in self:
            if record.age_meassure_unit == '3' and record.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if record.age > 17 and record.age_meassure_unit == '1' and record.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if record.age_meassure_unit in ['2','3'] and record.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if record.document_type == 'ms' and record.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if record.document_type == 'as' and record.age_meassure_unit == '1' and record.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
            
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('doctor.presurgical.record') or '/'
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
        
        res = super(PresurgicalRecord, self).create(vals)
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
        
        res = super(PresurgicalRecord, self).write(vals)
        self._check_document_types()
        return res
    
    
    
    
    