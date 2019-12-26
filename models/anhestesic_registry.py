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

    def all_procedures(self):
        return self.env['product.product'].search([('is_health_procedure','=',1)]).ids
    
    name = fields.Char(string="Name")
    intervention_date = fields.Datetime(string='Intervention Date', default=fields.Datetime.now, copy=False)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document', related="patient_id.tdoc")
    numberid = fields.Char(string='Number ID', compute="_compute_numberid", store="true")
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', compute="_compute_numberid_integer", store="true")
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
    product_id = fields.Many2one('product.product', 'Process', ondelete='restrict')
    product_ids = fields.Many2many('product.product',ondelete='restrict', domain=[('is_health_procedure','=', True)])
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
                                        string='Type of Anesthesia')
    start_time = fields.Float(string='Surgery Starting Hour')
    end_time = fields.Float(string='Surgery Ending Hour')
    preoperative_note = fields.Text(string='Preoperative Note')
    
    paraclinical_exam_date = fields.Date(string="Paraclinical Exam Date")
    paraclinical_hb = fields.Float(string="HB")
    paraclinical_hto = fields.Float(string="Hto (Hematocrit)")
    paraclinical_leukocytes = fields.Float(string="Leukocytes")
    paraclinical_differential = fields.Text(string="Differential")
    paraclinical_vsg = fields.Integer(string="VSG")
    paraclinical_pt = fields.Char(string="PT")
    paraclinical_ptt = fields.Char(string="PTT")
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
    paraclinical_goldman = fields.Selection([('class1', 'Clase I'),('class2', 'Clase II'),
                                       ('class3', 'Clase III'),('class4','Clase IV')], string='GOLDMAN')
    mallampati_scale = fields.Selection([('class1', 'Clase I'),('class2', 'Clase II'),
                                       ('class3', 'Clase III'),('class4','Clase IV')], string='Mallampati Scale')
    dental_prostheses = fields.Boolean(string='Dental Prostheses')
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
    plan_analysis = fields.Text(string="Plan, Analysis and Conduct")
    medical_recipe = fields.Text(string="Medical Orders and Recipe")
    medical_recipe_template_id = fields.Many2one('clinica.text.template', string='Template')
    
    monitor_ids = fields.One2many('clinica.anhestesic.registry.monitor', 'anhestesic_registry_id', 
                                         string='Orders and Evolutions Notes', copy=False)

    heart_noises = fields.Boolean(string="Heart Noises")
    ind_blood_pressure = fields.Boolean(string="Automatic Indirect Blood Pressure") # Automatic Indirect Blood Pressure
    dir_blood_pressure = fields.Boolean(string="Direct Blood Pressure") # Direct Blood Pressure
    ekg = fields.Boolean(string="EKG")
    oxymetry = fields.Boolean(string="Oximetry")
    capnometry = fields.Boolean(string="Capnometry")
    capnography = fields.Boolean(string="Capnography")
    respirometer = fields.Boolean(string="Respirometer")
    spirometry = fields.Boolean(string="Spirometry")
    cent_venous_pressure = fields.Boolean(string="Central venous pressure") #central venous pressure
    intermitt_venous_pressure = fields.Boolean(string="Intermittent venous pressure")  #intermittent venous pressure
    diuresis_bool = fields.Boolean(string="Diuresis")
    temperature = fields.Boolean(string="Temperature")
    other_monitor = fields.Char(string='Other Monitor')
    #ocular protection
    occlusion_protection = fields.Boolean(string="Oclusión")
    gel_protection = fields.Boolean(string="Gel")
    #laryngeal mask
    number_mask =  fields.Integer(string='Número')
    air_mask = fields.Float(string='Aire (cm)')
    difficulty_mask = fields.Selection([('easy', 'Fácil'), ('difficult', 'Difícil')], string="Dificultad", default='easy')

    facial_mask = fields.Boolean(string="Máscara Facial")
    other_facial_mask = fields.Char(string='Otra')
    nasal_cannula = fields.Boolean(string="Cánula Nasal")
    venturi = fields.Boolean(string="Venturi")
    percentage = fields.Char(string="%")

    tube_type = fields.Selection([('regular', 'Normal'), ('ringed', 'Anillado')], string="Tipo Tubo", default='regular')
    tube_number = fields.Char(string='Número Tubo')
    distance = fields.Float(string='Distancia (cm)')
    pneumotapon = fields.Float(string='Neumotapón (cm)')

    orotracheal = fields.Boolean(string="Orotracheal")
    nasotracheal = fields.Boolean(string="Nasotracheal")
    tracheostomy = fields.Boolean(string="Tracheostomy")
    attemps = fields.Integer(string="Attemps")
    used_laryngoscope = fields.Boolean(string="Used Laryngoscope")
    intubation = fields.Selection([('easy', 'Easy'), ('hard', 'Hard')], string="Intubation", default='easy')

    intravenous = fields.Boolean(string="Intravenous")
    inhalation = fields.Boolean(string="Inhalation")
    sellick = fields.Boolean(string="Sellick")
    fast_sequence = fields.Boolean(string="Fast Sequence")
    mixed = fields.Boolean(string="Mixed")
    pre_induction = fields.Text(string="Pre-induction")
    induction = fields.Text(string="Induction")
    maintenance = fields.Text(string="Maintenance")
    reversion = fields.Text(string="Reversion")
    analgesics = fields.Text(string="Analgesics")
    antiemetics = fields.Text(string="Antiemetics")
    
    crystalloids = fields.Float(string="Crystalloids")
    blood = fields.Float(string="Blood")
    colloids = fields.Float(string="Colloids")
    infiltrated = fields.Float(string="Infiltrated")
    bleeding = fields.Float(string="Bleeding")
    diuresis = fields.Float(string="Diuresis")
    liposuction = fields.Float(string="Liposuction")
    motor_lock = fields.Boolean(string="Motor Lock")
    coma = fields.Boolean(string="Coma")
    awake = fields.Boolean(string="Awake")
    asleep = fields.Boolean(string="Asleep")
    intubated = fields.Boolean(string="Intubated")
    reagent = fields.Boolean(string="Reagent")
    shock = fields.Boolean(string="Shock")
    uci = fields.Boolean(string="UCI")
    recovery = fields.Boolean(string="Recovery")
    
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    smoke = fields.Boolean(string="Smoke", related='patient_id.smoke')
    cigarate_daily = fields.Integer(string="Cigarettes", related='patient_id.cigarate_daily')
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
    
    anesthesia_start_time = fields.Float(string="Anesthesia Start Time")
    intubation_time = fields.Float(string="Intubation Time")
    extubation_time = fields.Float(string="Extubation Time")
    anesthesia_end_time = fields.Float(string="Anesthesia End Time")
    recovery_transfer_time = fields.Float(string="Transfer Time to Recovery")
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery', copy=False)
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
    review_note = fields.Text('Review Note')
    review_active = fields.Boolean('Is Review Note?')
    review_readonly = fields.Boolean('set to readonly')
    caprini_scale = fields.Selection([('1', '1'),('2', '2'),
                                       ('3', '3'),('4','4'),
                                       ('5', '5'),('6','6'),
                                       ('7', '7'),('8','8'),
                                       ('9', '9'),('10','10'),], string='Caprini Scale')    

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
                    
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            list_ids = []
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
            self.surgeon_id = self.room_id.surgeon_id and self.room_id.surgeon_id.id or False
            self.anesthesiologist_id = self.room_id.anesthesiologist_id and self.room_id.anesthesiologist_id.id or False
            self.anesthesia_type = self.room_id.anesthesia_type
            for procedure_ids in self.room_id.procedure_ids:
                for products in procedure_ids.product_id:
                    list_ids.append(products.id)
            self.product_ids = [(6, 0, list_ids)]

                    
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
            self.numberid_integer = int(self.patient_id.name) if self.document_type in ['cc','ti'] else 0
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh
            if self.room_id:
                presurgical_obj = self.env['doctor.presurgical.record'].search([('patient_id','=',self.patient_id.id), ('lead_id','=',self.room_id.id)], limit=1)
                if presurgical_obj:
                    if presurgical_obj.paraclinical_goldman:
                        cad = presurgical_obj.paraclinical_goldman
                        cad = cad[0:5]+''+cad[6:]
                        self.paraclinical_goldman = cad
                    # Background
                    if not self.body_background_others:
                        self.body_background_others = presurgical_obj.body_background_others
                    self.diabetes = presurgical_obj.diabetes
                    self.arthritis = presurgical_obj.arthritis
                    self.hypertension = presurgical_obj.hypertension
                    self.thyroid_disease = presurgical_obj.thyroid_disease
                    self.pathological = presurgical_obj.pathological
                    self.surgical = presurgical_obj.surgical
                    self.smoke = presurgical_obj.smoke
                    self.cigarate_daily = presurgical_obj.cigarate_daily
                    self.is_alcoholic = presurgical_obj.is_alcoholic
                    self.alcohol_frequency = presurgical_obj.alcohol_frequency
                    self.marijuana = presurgical_obj.marijuana
                    self.cocaine = presurgical_obj.cocaine
                    self.ecstasy = presurgical_obj.ecstasy
                    self.pharmacological = presurgical_obj.pharmacological
                    self.allergic = presurgical_obj.allergic
                    self.pregnancy_number = presurgical_obj.pregnancy_number
                    self.child_number = presurgical_obj.child_number
                    self.abortion_number = presurgical_obj.abortion_number
                    self.last_birth_date = presurgical_obj.last_birth_date
                    self.last_menstruation_date = presurgical_obj.last_menstruation_date
                    self.contrtaceptive_methods = presurgical_obj.contrtaceptive_methods
                    # Paraclinical
                    self.paraclinical_exam_date = presurgical_obj.paraclinical_exam_date
                    self.caprini_scale = presurgical_obj.caprini_scale
                    self.paraclinical_hb = presurgical_obj.paraclinical_hb
                    self.paraclinical_hto = presurgical_obj.paraclinical_hto
                    self.paraclinical_leukocytes = presurgical_obj.paraclinical_leukocytes
                    self.paraclinical_differential = presurgical_obj.paraclinical_differential
                    self.paraclinical_vsg = presurgical_obj.paraclinical_vsg
                    self.paraclinical_tc = presurgical_obj.paraclinical_tc
                    self.paraclinical_pt = presurgical_obj.paraclinical_pt
                    self.paraclinical_ptt = presurgical_obj.paraclinical_ptt
                    self.paraclinical_platelets = presurgical_obj.paraclinical_platelets
                    self.paraclinical_glycemia = presurgical_obj.paraclinical_glycemia
                    self.paraclinical_creatinine = presurgical_obj.paraclinical_creatinine
                    self.paraclinical_albumin = presurgical_obj.paraclinical_albumin
                    self.paraclinical_glob = presurgical_obj.paraclinical_glob
                    self.paraclinical_ecg = presurgical_obj.paraclinical_ecg
                    self.paraclinical_others = presurgical_obj.paraclinical_others
                    self.dental_prostheses = presurgical_obj.dental_prostheses
                    self.disease_id = presurgical_obj.disease_id
                    self.disease_state = presurgical_obj.disease_state
                    self.disease2_id = presurgical_obj.disease2_id
                    self.disease_state2 = presurgical_obj.disease_state2
                    self.disease3_id = presurgical_obj.disease3_id
                    self.disease_state3 = presurgical_obj.disease_state3
                    self.plan_analysis = presurgical_obj.plan_analysis
                    self.medical_recipe = presurgical_obj.medical_recipe
                    self.paraclinical_rx_chest = presurgical_obj.paraclinical_rx_chest
                    self.paraclinical_asa = presurgical_obj.paraclinical_asa
                    self.mallampati_scale = presurgical_obj.mallampati_scale
            
            
    @api.onchange('medical_recipe_template_id')
    def onchange_medical_recipe_template_id(self):
        if self.medical_recipe_template_id:
            self.medical_recipe = self.medical_recipe_template_id.template_text
            
    
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
        vals['name'] = self.env['ir.sequence'].next_by_code('anhestesic.registry') or '/'
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(AnhestesicRegistry, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('review_note', False):
            self.review_readonly = True
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
         
        res = super(AnhestesicRegistry, self).write(vals)
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
        
class AnhestesicRegistryMonitor(models.Model):
    _name = "clinica.anhestesic.registry.monitor"  
    
    anhestesic_registry_id = fields.Many2one('clinica.anhestesic.registry', 'Anhestesic Registry', ondelete='cascade')
    monitor = fields.Text(string='Monitor')
    date_hour = fields.Datetime(string='Date and hopeur', default=fields.Datetime.now)
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:




