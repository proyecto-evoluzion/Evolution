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
import html2text

class MedicalOrderEvolution(models.Model):
    _name = "clinica.medical.evolution"
    _order = 'id desc'
    _description = 'Medical orders and Evolution'
    
    @api.model
    def _get_signature(self):
        user = self.env.user
        signature = html2text.html2text(user.signature)
        return signature

    def _default_doctor(self):
        ctx = self._context
        user_id = self._context.get('uid')
        professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_id)])
        return professional_obj.id
    
    name = fields.Char(string="Name", copy=False)
    procedure_date = fields.Datetime(string='Procedure Date', default=fields.Datetime.now, copy=False)
    tdoc = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                             ('pa','PA - Passport'),('rc','RC - Civil Registry'),
                             ('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),
                             ('ms','MS - Unidentified Minor')], string='Type of Document', related="patient_id.tdoc")
    numberid = fields.Char(string='Number ID', compute="_compute_numberid", store="true")
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', compute="_compute_numberid_integer", store="true")
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    sex = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon', default=_default_doctor)
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
                                        string='Type of Anesthesia')
    procedure = fields.Text(string="Procedure")
    sign_stamp = fields.Text(string='Sign and médical stamp', default=_get_signature)
    user_id = fields.Many2one('res.users', string='Medical registry number', default=lambda self: self.env.user)
    evolution_note_ids = fields.One2many('clinica.medical.evolution.note', 'medical_evolution_id', string='Orders and Evolutions Notes', copy=False)
    
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    smoke = fields.Boolean(string="Smoke", related='patient_id.smoke')
    cigarate_daily = fields.Integer(string="Cigarettes / Day", related='patient_id.cigarate_daily')
    smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),('month','per Month'), 
                                  ('year','per Year')], string="Smoke Unit of Measure", default='day', related='patient_id.smoke_uom')
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks", related='patient_id.is_alcoholic')
    alcohol_frequency = fields.Integer(string="Frequency", related='patient_id.alcohol_frequency')
    alcohol_frequency_uom = fields.Selection([('day','per Day'), ('week','per Week'), ('month','per Month'), 
                                              ('year','per Year')], string="Alcoholic Frequency Unit of Measure", default='day', 
                                             related='patient_id.alcohol_frequency_uom')
    marijuana = fields.Boolean(string="Marijuana", related='patient_id.marijuana')
    cocaine = fields.Boolean(string="Cocaine", related='patient_id.cocaine')
    ecstasy = fields.Boolean(string="Ecstasy", related='patient_id.ecstasy')
    body_background_others = fields.Text(string="Body Background Others", related='patient_id.body_background_others')
    pharmacological = fields.Text(string="Pharmacological", related='patient_id.pharmacological')
    allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    pregnancy_number = fields.Integer(string="Number of Pregnancies", related='patient_id.pregnancy_number')
    child_number = fields.Integer(string="Number of Children", related='patient_id.child_number')
    abortion_number = fields.Integer(string="Number of Abortions", related='patient_id.abortion_number')
    last_birth_date = fields.Date(string="Date of Last Birth", related='patient_id.last_birth_date')
    last_menstruation_date = fields.Date(string="Date of Last Menstruation", related='patient_id.last_menstruation_date')
    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related='patient_id.contrtaceptive_methods')
    diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    medical_record = fields.Char(string='Medical record')
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
    review_note = fields.Text('Review Note')
    review_active = fields.Boolean('Is Review Note?')
    review_readonly = fields.Boolean('set to readonly')
    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    @api.depends('patient_id')
    def _compute_numberid_integer(self):
        for rec in self:
            try:
                rec.numberid_integer = int(rec.patient_id.name) if rec.patient_id else False
            except:
                rec.numberid_integer = 0

    @api.depends('patient_id')
    def _compute_numberid(self):
        for rec in self:
            rec.numberid = rec.patient_id.name if rec.patient_id else False
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for evolution in self:
            if evolution.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(evolution.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    evolution.age_meassure_unit = '3'
                    evolution.age = int(date_diff.days)
                elif difference < 365:
                    evolution.age_meassure_unit = '2'
                    evolution.age = int(date_diff.months)
                else:
                    evolution.age_meassure_unit = '1'
                    evolution.age = int(date_diff.years)
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.sex = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.tdoc = self.patient_id.tdoc
            self.numberid = self.patient_id.name
            self.numberid_integer = int(self.patient_id.name)
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh
            self.medical_record = self.patient_id.doctor_id.medical_record
            
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
    
    @api.model
    def create(self, vals):
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(MedicalOrderEvolution, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('review_note', False):
            self.review_readonly = True
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
         
        res = super(MedicalOrderEvolution, self).write(vals)
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.surgeon_id and self.surgeon_id.id or False,
            'default_view_model': 'medical_evolution',
            }
        return vals
           
    @api.multi
    def action_view_clinica_record_history(self):
        context = self._set_visualizer_default_values()
        return {
                'name': _('Historial de Registros'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'clinica.record.list.visualizer',
                'view_id': self.env.ref('clinica_doctor_data.clinica_record_list_visualizer_form').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
        
    @api.multi
    def action_set_close(self):
        for record in self:
            record.state = 'closed'

    def review_note_trigger(self):
        if not self.review_active:
            self.write({'review_active': True})


class MedicalOrderEvolutionNotes(models.Model):
    _name = "clinica.medical.evolution.note"  
    
    medical_evolution_id = fields.Many2one('clinica.medical.evolution', 'Medical Evolution', ondelete='cascade')
    note = fields.Text(string='Evolution')
    date_hour = fields.Datetime(string='Date and Hour', default=fields.Datetime.now)
    
    
        
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


