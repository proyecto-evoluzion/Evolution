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
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
from odoo.exceptions import ValidationError

class PlasticSurgerySheet(models.Model):
    _name = "clinica.plastic.surgery2"
    _rec_name = 'number'

    @api.depends('size','weight')
    def _comp_imc(self):
        for imc in self:
            if imc.size != 0:
                imc.imc = imc.weight / pow(imc.size,2)    
    
    number = fields.Char('Attention number', readonly=True)
    attention_code_id = fields.Many2one('doctor.cups.code', string="Attention Code", ondelete='restrict')
    date_attention = fields.Date('Date of attention', required=True, default=fields.Date.context_today)
    type_id = fields.Selection([('fist_time','First Time'),('control','Control')], string='Consultation Type', default='fist_time')
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document', related="patient_id.tdoc")
    numberid = fields.Char(string='Number ID', related='patient_id.name')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', related='patient_id.ref')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender', related="patient_id.sex")
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    
    consultation_reason = fields.Text(string="Reason for Consultation", related="patient_id.consultation_reason")
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    toxic = fields.Text(string="Toxic")
    allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    gyneco_obst = fields.Text(string="Gyneco-Obstetricians")
    relatives = fields.Text(string="Relatives")
    others = fields.Text(string="Others")

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
    pregnancy_number = fields.Integer(string="Number of Pregnancies", related='patient_id.pregnancy_number')
    child_number = fields.Integer(string="Number of Children", related='patient_id.child_number')
    
    gestations = fields.Integer(string="G", help="Gestations")
    births = fields.Integer(string="B",  help="Births")
    cesarean = fields.Integer(string="C", help="Cesarean")
    abortion_number = fields.Integer(string="A", related='patient_id.abortion_number', help="Abortions")
    last_menstruation_date = fields.Date(string="LMD", related='patient_id.last_menstruation_date', help="Last menstruation date")
    last_birth_date = fields.Date(string="LBD", related='patient_id.last_birth_date', help="Last birth date")
    mature_promoting_factor = fields.Char(string="MPF",  help="Mature Promoting Factor")

    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related='patient_id.contrtaceptive_methods')
    diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
    
    physical_sistolic_arteric_presure = fields.Integer(string="Sistolic Arteric Pressure")
    physical_diastolic_artery_presure = fields.Integer(string="Diastolic Artery Pressure")
    physical_fc = fields.Integer(string="FC")
    physical_fr = fields.Integer(string="FR")
    physical_weight = fields.Float(string="Weight")
    physical_size = fields.Float(string="Size")
    physical_body_mass_index = fields.Float(string="IMC (Body Mass Index)")
    physical_exam = fields.Text(string="Physical Exam Observations")
    
    disease_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease2_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease3_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease_type = fields.Selection([('principal', 'Principal'),('related', 'Relacionado')], string='Kind')
    disease_state = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status')
    disease_state2 = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status')
    disease_state3 = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status')
    process_id = fields.Many2one('product.product', string='Process', ondelete='restrict')
    treatment = fields.Text(string="Treatment")
    medical_recipe = fields.Text(string="Medical Orders and Recipe")
    medical_recipe_template_id = fields.Many2one('clinica.text.template', string='Template')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    physical_examination_ids = fields.One2many('clinica.physical.examination', 'plastic_surgery_id', string="Physical Examination")
    doctor_id = fields.Many2one('doctor.professional', string='Professional')
    prescription_id = fields.Many2one('doctor.prescription', string='Prescription')
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')    
    systolic_blood_pressure = fields.Float(string="Systolic blood pressure")
    diastolic_blood_pressure = fields.Float(string="Diastolic blood pressure")
    heart_rate = fields.Integer(string="Heart rate")
    breathing_frequency = fields.Integer(string="Breathing frequency")    
    size = fields.Float(string="Size")
    weight = fields.Float(string="Weight")
    imc = fields.Float(string="IMC", compute=_comp_imc)    

    @api.multi
    def action_set_close(self):
        for record in self:
            record.state = 'closed'    
    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
    
    @api.onchange('patient_id')
    def onchange_consultation_reason(self):
        if self.patient_id:
            self.consultation_reason = self.patient_id.consultation_reason

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
            
    @api.onchange('physical_size')
    def onchange_imc(self):
        if self.physical_size and self.physical_weight:
            self.physical_body_mass_index = float(self.physical_weight/(self.physical_size/100)**2)

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
            
    @api.onchange('medical_recipe_template_id')
    def onchange_medical_recipe_template_id(self):
        if self.medical_recipe_template_id:
            self.medical_recipe = self.medical_recipe_template_id.template_text
            
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

        ctx = self._context
        if ctx.get('uid'):
            create_uid = self.env['res.users'].search([('id','=',ctx.get('uid'))])
            professional_obj = self.env['doctor.professional'].search([('res_user_id','=',create_uid.id)])
            if professional_obj:
                vals['doctor_id'] = professional_obj.id
        
        res = super(PlasticSurgerySheet, self).create(vals)
        if res.room_id:
            res.room_id.patient_state = 'attended'
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
        
        res = super(PlasticSurgerySheet, self).write(vals)
        self._check_document_types()
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_view_model': 'plastic_surgery',
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

class PhysicalExamination(models.Model):
    _name = "clinica.physical.examination"

    plastic_surgery_id = fields.Many2one('clinica.plastic.surgery2', string='Plastic Surgery')
    element = fields.Many2one('clinica.physical.item', string='Tipo Exámen Físico')
    physical_examination = fields.Char(string="Exámen Físico")

class PhysicalExaminationType(models.Model):
    _name = "clinica.physical.item"

    name = fields.Char(string="Name", required=True)
    professional_id = fields.Many2one('doctor.professional', string='Professional')
    active = fields.Boolean(string="Active", default="True")

class DoctorWaitingRoom(models.Model):
    _name = "doctor.waiting.room2"
    _description= 'Doctor Waiting Room2'
    
    name = fields.Char(string='Name', copy=False)
    room_type = fields.Selection([('surgery','Surgery Room'),('waiting','Waiting Room')], string='Room Type')
    surgery_room_id = fields.Many2one('clinica.surgery.room', string='Surgery Room', copy=False)
    schedule_id = fields.Many2one('doctor.schedule', string='Schedule', copy=False)
    procedure_date = fields.Datetime(string='Procedure Date', default=fields.Datetime.now, copy=False)
    procedure_end_date = fields.Datetime(string='Procedure End Date', copy=False)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    middlename = fields.Char(string='Second Name')
    email_from = fields.Char(string='Email From CRM')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    phone = fields.Char(string='Telephone')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], string='Type of Anesthesia')
    circulating_id = fields.Many2one('doctor.professional', string='Circulating')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    nurse_boss_id = fields.Many2one('doctor.professional', string='Nurse Boss')
    technologist_id = fields.Many2one('doctor.professional', string='Surgical Technologists')
    procedure = fields.Text(string='Procedure')
    notes = fields.Text(string='Observations or Notes')
    programmer_id = fields.Many2one('res.users', string='Programmer', default=lambda self: self.env.user)
    procedure_ids = fields.One2many('doctor.waiting.room.procedures', 'room_id', string='Helath Procedures', copy=False)
    state = fields.Selection([('new','New'),('confirmed','Confirmed'),('ordered','SO Created')], 
                                        string='Status', default='new')
    patient_state = fields.Selection([('dated','Citado'),('attended','Atendido'),('not_attended','No asistio'),('in_room','En sala de espera')], 
                                        string='Estado paciente', default='not_attended')
    nurse_sheet_created = fields.Boolean(string='Nurse Sheet Created', compute='_compute_nurse_sheet_creation')
    anhestesic_registry_created = fields.Boolean(string='Anhestesic Registry Created', compute='_compute_anhestesic_registry_creation')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
    
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
    assigned_professional_ids = fields.Many2many('doctor.professional', 'waiting_room_professional_rel', 'room_id', 'professional_id', 
                                                string="Responsible Professionals", copy=False)
    from_surgery_procedure = fields.Boolean(string='Created from Surgery Room Procedure', copy=False)
    user_type =  fields.Selection([('contributory','Contributory'),('subsidized','Subsidized'),('linked','Linked'),
                                   ('particular','Particular'),('other','Other'),('victim_contributive','Victim - Contributive'),
                                   ('victim_subsidized','Victim - Subsidized'),('victim_linked','Victim - Linked')], string="User Type", default='particular')
    appointment_type_id = fields.Many2one('clinica.appointment.type', string='Appointment Type')
    insurer_id = fields.Many2one('res.partner',string='Assurance Company')
    assurance_plan_id = fields.Many2one('doctor.insurer.plan', string='Assurer Plan')
    schedule_allocation_id = fields.Many2one('doctor.schedule.time.allocation', string='Schedule Time Allocation')
    
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for room in self:
            if room.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(room.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    room.age_meassure_unit = '3'
                    room.age = int(date_diff.days)
                elif difference < 365:
                    room.age_meassure_unit = '2'
                    room.age = int(date_diff.months)
                else:
                    room.age_meassure_unit = '1'
                    room.age = int(date_diff.years)
                    
    @api.multi
    def _compute_nurse_sheet_creation(self):
        for room in self:
            nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('room_id','=',room.id)])
            if nurse_sheet_ids:
                room.nurse_sheet_created = True           
                     
    @api.multi
    def _compute_anhestesic_registry_creation(self):
        for room in self:
            anhestesic_registry_ids = self.env['clinica.anhestesic.registry'].search([('room_id','=',room.id)])
            if anhestesic_registry_ids:
                room.anhestesic_registry_created = True
                
    @api.onchange('room_type')
    def onchange_room_type(self):
        if self.room_type and self.room_type == 'surgery':
            self.from_surgery_procedure = True
        else:
            self.from_surgery_procedure = False
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.phone = self.patient_id.phone
            self.document_type = self.patient_id.tdoc
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.ref
            
    @api.onchange('schedule_id')
    def onchange_schedule_id(self):
        if self.schedule_id:
            self.surgeon_id = self.schedule_id.professional_id and self.schedule_id.professional_id.id or False
            if self.schedule_id.time_allocation_ids:
                start_date = self.schedule_id.get_next_appointment_start_date()
                self.procedure_date = start_date
            
    @api.onchange('document_type','numberid_integer','numberid')
    def onchange_numberid(self):
        if self.document_type and self.document_type not in ['cc','ti']:
            self.numberid_integer = 0
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
            self.numberid = self.numberid_integer
            
    @api.onchange('procedure_date','appointment_type_id')
    def onchange_procedure_date(self):
        if self.procedure_date:
            if self.appointment_type_id:
                duration = self.appointment_type_id.duration
            else: 
                duration = 4
            procedure_date = datetime.strptime(self.procedure_date, DEFAULT_SERVER_DATETIME_FORMAT)
            self.procedure_end_date = procedure_date + timedelta(hours=duration)
    
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
        for room in self:
            if room.age_meassure_unit == '3' and room.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if room.age > 17 and room.age_meassure_unit == '1' and room.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if room.age_meassure_unit in ['2','3'] and room.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if room.document_type == 'ms' and room.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if room.document_type == 'as' and room.age_meassure_unit == '1' and room.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
      
    @api.multi
    def _validate_surgeon_room(self):
        for room in self:
            if self.surgeon_id:
                start_date = self.procedure_date
                end_date = self.procedure_end_date
                if end_date and start_date:
                    if end_date <= start_date:
                        raise ValidationError(_("End date should be greater than start date!"))
                    start_time_between_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','<=',start_date),
                                                ('procedure_end_date','>',start_date),
                                                ])
                    if len(start_time_between_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                    end_time_between_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','<',end_date),
                                                ('procedure_end_date','>=',end_date),
                                                ])
                    if len(end_time_between_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                    
                    overlap_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','>=',start_date),
                                                ('procedure_end_date','<=',end_date),
                                                ])
                    if len(overlap_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
    
    @api.multi
    def _validate_surgery_room_alocation(self):   
        for room in self:  
            start_date = self.procedure_date
            end_date = self.procedure_end_date
            if end_date and start_date:
                start_time_between_rooms = self.search([('surgery_room_id','=',self.surgery_room_id.id),
                                            ('procedure_date','<=',start_date),
                                            ('procedure_end_date','>',start_date),
                                            ])
                if len(start_time_between_rooms) > 1:
                    raise ValidationError(_("%s is already allocated for this date! Please choose another. ") % self.surgery_room_id.name)
                end_time_between_rooms = self.search([('surgery_room_id','=',self.surgery_room_id.id),
                                            ('procedure_date','<',end_date),
                                            ('procedure_end_date','>=',end_date),
                                            ])
                if len(end_time_between_rooms) > 1:
                    raise ValidationError(_("%s is already allocated for this date! Please choose another. ") % self.surgery_room_id.name)
                
                overlap_rooms = self.search([('surgery_room_id','=',self.surgery_room_id.id),
                                            ('procedure_date','>=',start_date),
                                            ('procedure_end_date','<=',end_date),
                                            ])
                if len(overlap_rooms) > 1:
                    raise ValidationError(_("%s is already allocated for this date! Please choose another. ") % self.surgery_room_id.name)
    
    @api.multi
    def _add_assigned_professionals(self,):
        professional_ids = []
        if self.surgeon_id:
            professional_ids.append(self.surgeon_id.id)
        if self.anesthesiologist_id:
            professional_ids.append(self.anesthesiologist_id.id)
        if self.circulating_id:
            professional_ids.append(self.circulating_id.id)
        if self.nurse_boss_id:
            professional_ids.append(self.nurse_boss_id.id)
        if self.technologist_id:
            professional_ids.append(self.technologist_id.id)
        self.assigned_professional_ids = [(6, 0, professional_ids)]
        
    @api.multi
    def _allocate_in_schedule_time(self):
        schedule_alloc_pool = self.env['doctor.schedule.time.allocation']
        time_space_domain = [('schedule_id','=',self.schedule_id.id),'|', '|',
                             '&', ('start_time','>=', self.procedure_date), ('end_time','<=', self.procedure_end_date),
                             '&', ('start_time','<=', self.procedure_date), ('end_time','<=', self.procedure_date),
                             '&', ('start_time','<=', self.procedure_end_date), ('end_time','>=', self.procedure_end_date),]
        
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','>=', self.procedure_date), ('end_time','<=', self.procedure_end_date),
                             ('start_time','!=', self.procedure_end_date), ('end_time','!=', self.procedure_date)]
        between_allocation_objs = schedule_alloc_pool.search(time_space_domain)
        
        if between_allocation_objs:
            between_allocation_objs.unlink()
            
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','<', self.procedure_date), ('end_time','>', self.procedure_date)]
        start_overlap_allocation_objs =  schedule_alloc_pool.search(time_space_domain, limit=1)
        if start_overlap_allocation_objs:
            start_overlap_allocation_objs.end_time = self.procedure_date
        
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','<', self.procedure_end_date), ('end_time','>', self.procedure_end_date)]
        end_overlap_allocation_objs = schedule_alloc_pool.search(time_space_domain, limit=1)
        if end_overlap_allocation_objs:
            end_overlap_allocation_objs.start_time = self.procedure_end_date
        
        time_space_domain = [('schedule_id','=',self.schedule_id.id),
                             ('start_time','<', self.procedure_date), ('end_time','>', self.procedure_end_date)]
        start_end_overlap_objs = schedule_alloc_pool.search(time_space_domain, limit=1)
        if start_end_overlap_objs:
            aloc_end = start_end_overlap_objs.end_time
            start_end_overlap_objs.end_time = self.procedure_date
            end_new_alloc = schedule_alloc_pool.create({'start_time': self.procedure_end_date,
                                                        'end_time': self.aloc_end,
                                                        'schedule_id': self.schedule_id.id})
        
        new_allocation_vals = {
            'start_time': self.procedure_date,
            'end_time': self.procedure_end_date,
            'patient_id': self.patient_id and self.patient_id.id or False,
            'state': 'assigned',
            'schedule_id': self.schedule_id.id
            }
        new_allocation = schedule_alloc_pool.create(new_allocation_vals)
        self.schedule_allocation_id = new_allocation.id
        
    @api.multi
    def _reallocate_schedule_time(self, vals):
        new_start = vals.get('procedure_date', False)
        new_end = vals.get('procedure_end_date', False)
        schedule_alloc_pool = self.env['doctor.schedule.time.allocation']
        if new_start:
            time_space_domain = [('schedule_id','=',self.schedule_id.id), ('state','!=', 'assigned'),
                                 ('start_time','<=',new_start),('end_time','>=', new_start)]
            before_start_allocs = schedule_alloc_pool.search(time_space_domain, order='start_time desc', limit=1)
            if before_start_allocs and before_start_allocs.id != self.schedule_allocation_id.id:
                before_start_allocs.end_time = new_start
            self.schedule_allocation_id.start_time = new_start
        if new_end:
            time_space_domain = [('schedule_id','=',self.schedule_id.id),('state','!=', 'assigned'),
                                 ('start_time','<=',new_end), ('end_time','>=', new_end)]
            after_start_allocs = schedule_alloc_pool.search(time_space_domain, order='start_time desc', limit=1)
            if after_start_allocs and after_start_allocs.id != self.schedule_allocation_id.id:
                after_start_allocs.start_time = new_end
            self.schedule_allocation_id.end_time = new_end
            
        
        if new_start:
            start_time = new_start
        else:
            start_time = self.procedure_date
        if new_end:
            end_time = new_end
        else:
            end_time = self.procedure_end_date
            
        time_space_domain = [('schedule_id','=',self.schedule_id.id), ('state','!=', 'assigned'),
                             ('start_time','>=',start_time),('end_time','<=',end_time)]
            
        between_allocs = schedule_alloc_pool.search(time_space_domain)
        if between_allocs:
            between_allocs.unlink()
            
    
    @api.model
    def create(self, vals):
        if vals.get('room_type', False) and vals['room_type'] == 'surgery':
            vals['name'] = self.env['ir.sequence'].next_by_code('doctor.surgery.room.procedure') or 'Consulta'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('doctor.waiting.room2') or 'Consulta'
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
        if not vals.get('procedure_ids', False):
            warn_msg = _('Error! Plase add at least one procedure.')
            raise ValidationError(warn_msg)
        
        res = super(DoctorWaitingRoom, self).create(vals)
        res._check_document_types()
        res._validate_surgeon_room()
        if vals.get('room_type', False) and vals['room_type'] == 'surgery':
            if vals.get('surgery_room_id', False):
                res._validate_surgery_room_alocation()
                
        if vals.get('surgeon_id', False) or vals.get('anesthesiologist_id', False) \
            or vals.get('circulating_id', False) or vals.get('nurse_boss_id', False) \
            or vals.get('technologist_id', False):
            res._add_assigned_professionals()
        if vals.get('schedule_id', False):
            res._allocate_in_schedule_time()
        res.state = 'confirmed'
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
            
        if vals.get('procedure_date', False) or vals.get('procedure_end_date', False):
            if self.schedule_id and self.schedule_allocation_id:
                self._reallocate_schedule_time(vals)
                
        res = super(DoctorWaitingRoom, self).write(vals)
        self._check_document_types()
        self._validate_surgeon_room()
        if vals.get('room_type', False) and vals['room_type'] == 'surgery':
            if vals.get('surgery_room_id', False):
                self._validate_surgery_room_alocation()
        if 'surgeon_id' in vals or 'anesthesiologist_id' in vals or 'circulating_id' in vals \
            or 'nurse_boss_id' in vals or 'technologist_id' in vals:
            self._add_assigned_professionals()
        return res
    
    @api.multi
    def action_confirm(self):
        for room in self:
            room.state = 'confirmed'
            
    @api.multi
    def _set_nurse_sheet_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_room_id' : self.id,
        }
        anhestesic_registry = self.env['clinica.anhestesic.registry'].search([('room_id','=',self.id)], limit=1)
        if anhestesic_registry:
            vals.update({'default_anhestesic_registry_id': anhestesic_registry.id})
        if self.sale_order_id and self.sale_order_id.picking_ids:
            procedure_list = []
            for picking in self.sale_order_id.picking_ids:
                for move in picking.move_lines:
                    procedure_list.append((0,0,{'product_id': move.product_id and move.product_id.id or False,
                                                'product_uom_qty': move.product_uom_qty,
                                                'quantity_done': move.quantity_done,
                                                'move_id': move.id}))
            if procedure_list:
                vals.update({'default_procedure_ids': procedure_list})
        return vals
            
    @api.multi
    def action_view_nurse_sheet(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_nurse_sheet')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_nurse_sheet_values()
        nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(nurse_sheet_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(nurse_sheet_ids.ids) + ")]"
        elif len(nurse_sheet_ids) == 1:
            res = self.env.ref('clinica_doctor_data.view_clinica_nurse_sheet_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = nurse_sheet_ids.id
        return result
    
    @api.multi
    def _create_so(self):
        for room in self:
            so_vals = {
                    'partner_id': room.patient_id and room.patient_id.partner_id and room.patient_id.partner_id.id or False
                }
            sale_order = self.env['sale.order'].create(so_vals)
            for procedure in room.procedure_ids:
                so_line_vals = {
                    'product_id': procedure.product_id and procedure.product_id.id or False,
                    'product_uom_qty': procedure.quantity,
                    'order_id': sale_order.id,
                    }
                self.env['sale.order.line'].create(so_line_vals)
        return sale_order
    
    @api.multi
    def action_create_so(self):
        for room in self:
            room.sale_order_id = room._create_so().id
            room.state = 'ordered'
        return self.action_view_sale_order()
            
    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        res = self.env.ref('sale.view_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.sale_order_id.id
        return result
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.surgeon_id and self.surgeon_id.id or False,
            }
        if self.room_type == 'waiting':
            vals.update({'default_view_model': 'waiting_room'})
        elif self.room_type == 'surgery':
            vals.update({'default_view_model': 'surgery_room'})
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
        
    @api.multi
    def _set_clinica_form_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_room_id' : self.id
        }
        return vals
            
    @api.multi
    def action_view_anhestesic_registry(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_anhestesic_registry')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        anhestesic_registry_ids = self.env['clinica.anhestesic.registry'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(anhestesic_registry_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(anhestesic_registry_ids.ids) + ")]"
        elif len(anhestesic_registry_ids) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_anhestesic_registry_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = anhestesic_registry_ids.id
        return result
    
    @api.multi
    def action_view_presurgical_record(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_presurgical_record')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        pre_surgical_ids = self.env['doctor.presurgical.record'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(pre_surgical_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(pre_surgical_ids.ids) + ")]"
        elif len(pre_surgical_ids) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_presurgical_record_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pre_surgical_ids.id
        return result

    @api.multi
    def action_not_attended(self):
        for record in self:
            record.patient_state = 'not_attended'
    
    @api.multi
    def action_view_quirurgic_sheet(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_quirurgic_sheet')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        quirurgic_sheets = self.env['doctor.quirurgic.sheet'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(quirurgic_sheets) != 1:
            result['domain'] = "[('id', 'in', " + str(quirurgic_sheets.ids) + ")]"
        elif len(quirurgic_sheets) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_quirurgic_sheet_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = quirurgic_sheets.id
        return result
    
    @api.multi
    def action_view_quirurgical_check_list(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_quirurgical_check_list')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        quirurgic_check_lists = self.env['clinica.quirurgical.check.list'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(quirurgic_check_lists) != 1:
            result['domain'] = "[('id', 'in', " + str(quirurgic_check_lists.ids) + ")]"
        elif len(quirurgic_check_lists) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_quirurgical_check_list_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = quirurgic_check_lists.id
        return result
    
    @api.multi
    def action_view_post_anhestesic_care(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_post_anhestesic_care')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        post_anhestesic_care_ids = self.env['clinica.post.anhestesic.care'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(post_anhestesic_care_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(post_anhestesic_care_ids.ids) + ")]"
        elif len(post_anhestesic_care_ids) == 1:
            res = self.env.ref('clinica_doctor_data.view_clinica_post_anhestesic_care_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = post_anhestesic_care_ids.id
        return result
    
    @api.multi
    def action_view_plastic_surgery(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_plastic_surgery2')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        plastic_surgery_ids = self.env['clinica.plastic.surgery2'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(plastic_surgery_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(plastic_surgery_ids.ids) + ")]"
        elif len(plastic_surgery_ids) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_plastic_surgery_form2', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = plastic_surgery_ids.id
        return result
    
    @api.multi
    def action_view_medical_evolution(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_medical_evolution')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        evolution_ids = self.env['clinica.medical.evolution'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(evolution_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(evolution_ids.ids) + ")]"
        elif len(evolution_ids) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_medical_evolution_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = evolution_ids.id
        return result
    
    @api.multi
    def action_view_epicrisis(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_doctor_epicrisis')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_clinica_form_default_values()
        epicrisis_ids = self.env['doctor.epicrisis'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(epicrisis_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(epicrisis_ids.ids) + ")]"
        elif len(epicrisis_ids) == 1:
            res = self.env.ref('clinica_doctor_data.clinica_doctor_epicrisis_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = epicrisis_ids.id
        return result    