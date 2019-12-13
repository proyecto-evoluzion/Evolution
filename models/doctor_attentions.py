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
from datetime import datetime, date, time, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.exceptions import ValidationError

class PresurgicalRecord(models.Model):
    _name = "doctor.presurgical.record"
    _rec_name = 'number'

    def _first_attention(self):
        product_id_rec = self.env['product.product'].search([('name','in',['CONSULTA DE PRIMERA VEZ POR ESPECIALISTA EN ANESTESIOLOGIA'])], limit=1)
        cups_obj = self.env['doctor.cups.code'].search([('product_id','=', product_id_rec.id)])
        return cups_obj.id

    def _auto_load_diasease(self):
    	product_id_rec = self.env['doctor.diseases'].search([('name','in',['OTRAS CONSULTAS ESPECIFICADAS'])], limit=1)
    	return product_id_rec.id

    def _default_professional(self):
        ctx = self._context
        user_id = self._context.get('uid')
        user_obj = self.env['res.users'].search([('id','=',user_id)])
        # professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_obj.id)])
        # if professional_obj:
        return user_obj.id
    
    number = fields.Char('Attention number', readonly=True)
    attention_code_id = fields.Many2one('doctor.cups.code', string="Attention Code", ondelete='restrict', default=_first_attention)
    date_attention = fields.Date('Date of attention', required=True, default=fields.Date.context_today)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], related="patient_id.tdoc", string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    professional_id = fields.Many2one('res.users', 'Professional', default=_default_professional)
    background_edit_flag = fields.Boolean('Background Flag', default=False)
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
    
    consultation_reason = fields.Text(string="Reason for Consultation")
    
    pathological = fields.Text(string="Pathological")
    surgical = fields.Text(string="Surgical")
    relatives = fields.Text(string="Relatives")
    smoke = fields.Boolean(string="Smoke")
    cigarate_daily = fields.Integer(string="Cigarettes / Day")
    smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),('month','per Month'), 
                                  ('year','per Year')], string="Smoke Unit of Measure", default='day')
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks")
    alcohol_frequency = fields.Integer(string="Frequency")
    alcohol_frequency_uom = fields.Selection([('day','per Day'), ('week','per Week'), ('month','per Month'), 
                                              ('year','per Year')], string="Alcoholic Frequency Unit of Measure", default='day')
    marijuana = fields.Boolean(string="Marijuana")
    cocaine = fields.Boolean(string="Cocaine")
    ecstasy = fields.Boolean(string="Ecstasy")
    body_background_others = fields.Text(string="Body Background Others")
    pharmacological = fields.Text(string="Pharmacological")
    allergic = fields.Text(string="Allergic")
    pregnancy_number = fields.Integer(string="Number of Pregnancies", related="patient_id.pregnancy_number")
    child_number = fields.Integer(string="Number of Children", related="patient_id.child_number")
    abortion_number = fields.Integer(string="Number of Abortions", related="patient_id.abortion_number")
    last_birth_date = fields.Date(string="Date of Last Birth", related="patient_id.last_birth_date")
    last_menstruation_date = fields.Date(string="Date of Last Menstruation", related="patient_id.last_menstruation_date")
    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related="patient_id.contrtaceptive_methods")
    diabetes = fields.Boolean(string="Diabetes")
    hypertension = fields.Boolean(string="Hypertension")
    arthritis = fields.Boolean(string="Arthritis")
    thyroid_disease = fields.Boolean(string="Thyroid Disease")
    
    physical_sistolic_arteric_presure = fields.Integer(string="Sistolic Arteric Pressure")
    physical_diastolic_artery_presure = fields.Integer(string="Diastolic Artery Pressure")
    physical_fc = fields.Integer(string="FC")
    physical_fr = fields.Integer(string="FR")
    physical_weight = fields.Float(string="Weight", required=True)
    physical_size = fields.Float(string="Size", required=True)
    physical_body_mass_index = fields.Float(string="IMC (Body Mass Index)")
    physical_exam = fields.Text(string="Physical Exam")
    dental_prostheses = fields.Boolean(string='Dental Prostheses')
    prostheses_type = fields.Selection([('fixed','Fixed'),('removable','Removable')], string='Prostheses Type', default='fixed')
    prostheses_type_fixed = fields.Boolean(string='Fixed', default=False)
    prostheses_type_removable = fields.Boolean(string='Removable', default=False)
    prostheses_location = fields.Selection([('above','Above'),('below','Below')], string='Prostheses Location', default='above')
    prostheses_location_above = fields.Boolean(string='Above', default=False)
    prostheses_location_below = fields.Boolean(string='Below', default=False)
    
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
    paraclinical_goldman = fields.Selection([('class_1','Class I'),
                                             ('class_2','Class II'),
                                             ('class_3','Class III'),
                                             ('class_4','Class IV')],
                                            string="GOLDMAN", default='class_1')
    mallampati_scale = fields.Selection([('class1', 'Clase I'),('class2', 'Clase II'),
                                       ('class3', 'Clase III'),('class4','Clase IV')], string='Mallampati Scale')
    caprini_scale = fields.Selection([('1', '1'),('2', '2'),
                                       ('3', '3'),('4','4'),
                                       ('5', '5'),('6','6'),
                                       ('7', '7'),('8','8'),
                                       ('9', '9'),('10','10'),], string='Caprini Scale')
    suitable_surgery = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes')
    
    disease_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict', default=_auto_load_diasease)
    other_diseases = fields.Boolean(string="Other Diseases")
    disease2_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease3_id = fields.Many2one('doctor.diseases', string='Diagnosis', ondelete='restrict')
    disease_type = fields.Selection([('principal', 'Principal'),('related', 'Relacionado')], string='Kind')
    disease_state = fields.Selection([('diagnostic_impresson', 'Impresión Diagnóstica'),
                                       ('new_confirmed', 'Confirmado Nuevo'),
                                       ('repeat_confirmed', 'Confirmado repetido')], string='Disease Status', default='new_confirmed')
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
    mallampati_scale = fields.Selection([('class1', 'Clase I'),('class2', 'Clase II'),
                                       ('class3', 'Clase III'),('class4','Clase IV')], string='Mallampati Scale')
    lead_id = fields.Many2one('doctor.waiting.room', string='Lead', copy=False) # this is the related Proced. Schedule attached to the lead
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
    review_note = fields.Text('Review Note')
    review_active = fields.Boolean('Is Review Note?')
    review_readonly = fields.Boolean('set to readonly')
    
    @api.onchange('professional_id')
    def onchange_professional_id(self):
        if self.professional_id:
            user_groups_list = []
            for user_groups in self.professional_id.groups_id:
                user_groups_list.append(user_groups.id)
            print (user_groups_list)
            anhestesic_group = self.env.ref('clinica_doctor_data.anesthesiologist')
            print(anhestesic_group)
            if anhestesic_group.id in user_groups_list:
                self.background_edit_flag = True

    @api.onchange('lead_id')
    def onchange_lead_id(self):
        if self.lead_id:
            self.patient_id = self.lead_id.patient_id and self.lead_id.patient_id.id or False
            # nurse_obj = self.env['clinica.nurse_sheet'].search([('room_id','=',self.lead_id.id),('patient_id','=',self.patient_id.id)],limit=1)
            # self.diabetes = nurse_obj.diabetes
    
    @api.onchange('patient_id')
    def onchange_consultation_reason(self):
        if self.patient_id:
            self.consultation_reason = self.patient_id.consultation_reason
            self.document_type = self.patient_id.tdoc
            hc_object = self.env['clinica.plastic.surgery'].search([('patient_id','=',self.patient_id.id)], limit=1)
            if hc_object:
                print(hc_object)
                print(hc_object.others)
                self.relatives = hc_object.relatives
                self.diabetes = hc_object.diabetes
                self.hypertension = hc_object.hypertension
                self.arthritis = hc_object.arthritis
                self.thyroid_disease = hc_object.thyroid_disease
                self.smoke = hc_object.smoke
                self.is_alcoholic = hc_object.is_alcoholic
                self.marijuana = hc_object.marijuana
                self.cocaine = hc_object.cocaine
                self.ecstasy = hc_object.ecstasy
                self.pathological = hc_object.pathological
                self.surgical = hc_object.surgical
                self.cigarate_daily = hc_object.cigarate_daily
                self.body_background_others = hc_object.others
                self.pharmacological = hc_object.pharmacological
                self.allergic = hc_object.allergic
                self.alcohol_frequency = hc_object.alcohol_frequency
            lead_obj = self.lead_id.search([('patient_id','=',self.patient_id.id)])
            lead_list = [x.id for x in lead_obj]
            if lead_list:
                pivot = lead_list[len(lead_list)-1]
                self.lead_id = pivot
            #DevFARK: adding 60 days rule for put same exams values from last attention
            last_att_obj = self.search([('patient_id','=',self.patient_id.id)])
            if last_att_obj:
                get_last_id = 0
                for last_id in last_att_obj:
                    get_last_id = last_id.id
                last_att_obj = self.search([('id','=',get_last_id)])
                last_date = last_att_obj.date_attention
                last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
                date_attention = dt.datetime.strptime(self.date_attention, '%Y-%m-%d')
                since_sixty_days = date_attention - last_date
                if since_sixty_days.days > 60:
                    self.paraclinical_hb = 0.00
                    self.paraclinical_hto = 0.00
                    self.paraclinical_leukocytes = 0.00
                    self.paraclinical_glycemia = 0.00
                    self.paraclinical_creatinine = 0.00
                    self.paraclinical_albumin = 0.00
                    self.paraclinical_differential = ''
                    self.paraclinical_pt = ''
                    self.paraclinical_ptt = ''
                    self.paraclinical_platelets = ''
                    self.paraclinical_glob = ''
                    self.paraclinical_ecg = ''
                    self.paraclinical_rx_chest = ''
                    self.paraclinical_others = ''
                    self.paraclinical_tc = ''
                    self.plan_analysis = ''
                    self.medical_recipe = ''
                    self.paraclinical_vsg = 0
                    self.other_diseases = False
                else:
                    # if not self.diabetes:
                    #     self.diabetes = last_att_obj.diabetes
                    # if not self.hypertension:
                    #     self.hypertension = last_att_obj.hypertension
                    # if not self.arthritis:
                    #     self.arthritis = last_att_obj.arthritis
                    # if not self.thyroid_disease:
                    #     self.thyroid_disease = last_att_obj.thyroid_disease
                    # if not self.smoke:
                    #     self.smoke = last_att_obj.smoke
                    # if not self.is_alcoholic:
                    #     self.is_alcoholic = last_att_obj.is_alcoholic
                    # if not self.marijuana:
                    #     self.marijuana = last_att_obj.marijuana
                    # if not self.cocaine:
                    #     self.cocaine = last_att_obj.cocaine
                    # if not self.ecstasy:
                    #     self.ecstasy = last_att_obj.ecstasy
                    # if not self.pathological:
                    #     self.pathological = last_att_obj.pathological
                    # if not self.surgical:
                    #     self.surgical = last_att_obj.surgical
                    # if not self.cigarate_daily:
                    #     self.cigarate_daily = last_att_obj.cigarate_daily
                    # if not self.body_background_others:
                    #     self.body_background_others = last_att_obj.body_background_others
                    # if not self.pharmacological:
                    #     self.pharmacological = last_att_obj.pharmacological
                    # if not self.allergic:
                    #     self.allergic = last_att_obj.allergic
                    # if not self.alcohol_frequency:
                    #     self.alcohol_frequency = last_att_obj.alcohol_frequency

                    self.paraclinical_hb = last_att_obj.paraclinical_hb
                    self.paraclinical_hto = last_att_obj.paraclinical_hto
                    self.paraclinical_leukocytes = last_att_obj.paraclinical_leukocytes
                    self.paraclinical_glycemia = last_att_obj.paraclinical_glycemia
                    self.paraclinical_creatinine = last_att_obj.paraclinical_creatinine
                    self.paraclinical_albumin = last_att_obj.paraclinical_albumin
                    self.paraclinical_differential = last_att_obj.paraclinical_differential
                    self.paraclinical_pt = last_att_obj.paraclinical_pt
                    self.paraclinical_ptt = last_att_obj.paraclinical_ptt
                    self.paraclinical_platelets = last_att_obj.paraclinical_platelets
                    self.paraclinical_glob = last_att_obj.paraclinical_glob
                    self.paraclinical_ecg = last_att_obj.paraclinical_ecg
                    self.paraclinical_rx_chest = last_att_obj.paraclinical_rx_chest
                    self.paraclinical_others = last_att_obj.paraclinical_others
                    self.paraclinical_tc = last_att_obj.paraclinical_tc
                    self.plan_analysis = last_att_obj.plan_analysis
                    self.medical_recipe = last_att_obj.medical_recipe
                    self.paraclinical_vsg = last_att_obj.paraclinical_vsg
                    self.other_diseases = last_att_obj.other_diseases

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

            
    @api.onchange('medical_recipe_template_id')
    def onchange_medical_recipe_template_id(self):
        if self.medical_recipe_template_id:
            self.medical_recipe = self.medical_recipe_template_id.template_text
            
            
    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('doctor.presurgical.record') or '/'
        res = super(PresurgicalRecord, self).create(vals)
#         res._check_document_types()
        return res
    
    
    @api.multi
    def write(self, vals):
        if vals.get('review_note', False):
            self.review_readonly = True
        res = super(PresurgicalRecord, self).write(vals)
#         self._check_document_types()
        return res
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_view_model': 'presurgical',
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
    
    @api.onchange('physical_size')
    def onchange_imc(self):
        if self.physical_size and self.physical_weight:
            self.physical_body_mass_index = float(self.physical_weight/(self.physical_size/100)**2)
            
    @api.multi
    def action_set_close(self):
        for record in self:
            record.state = 'closed'

    def review_note_trigger(self):
        if not self.review_active:
            self.write({'review_active': True})
    
    
    