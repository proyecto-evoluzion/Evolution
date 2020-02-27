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

import datetime as dt
from datetime import datetime
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import calendar
from odoo.exceptions import ValidationError

class ClinicaPostAnhestesicCare(models.Model):
	_name = "clinica.post.anhestesic.care"
	_order = 'id desc'
	_description = 'Post-Anhestesic care'

	@api.model
	def _default_professional(self):
		ctx = self._context
		user_id = self._context.get('uid')
		user_obj = self.env['res.users'].search([('id','=',user_id)])
		# professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_obj.id)])
		# if professional_obj:
		return user_obj.id

	document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document', related="patient_id.tdoc")
	patient_id = fields.Many2one('doctor.patient', 'Paciente', ondelete='restrict')
	numberid = fields.Char(string='Number ID')
	name = fields.Char(string='name', default="Cuidado Post-Anestésico")
	medical_record= fields.Char(string='HC')
	bed = fields.Char(string='Cama')
	date = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	# procedure = fields.Char(string='Procedimiento')
	procedure = fields.Many2many('product.product',ondelete='restrict', domain=[('is_health_procedure','=', True)])
	duration = fields.Float(string='Duración (en horas)')
	surgeon_id = fields.Many2one('doctor.professional', string='Cirujano')
	anesthesiologist_id = fields.Many2one('doctor.professional', string='Anestesiólogo')
	nurse_id = fields.Many2one('doctor.professional', string='Auxiliar Enfermería')
	#vital signs
	vital_sign_ids = fields.One2many('post.anhestesic.care.vital.signs', 'post_anhestesic_care_id', string='Signos Vitales', copy=False)
	#liquids
	liquids_ids = fields.One2many('post.anhestesic.care.liquids', 'post_anhestesic_care_id', string='Líquidos', copy=False)
	drugs_ids = fields.One2many('post.anhestesic.care.drugs','post_anhestesic_care_id', string='Drogas', copy=False )
	observations_ids = fields.One2many('post.anhestesic.care.observations','post_anhestesic_care_id', string='Observaciones', copy=False )
	aldrete_ids= fields.One2many('post.anhestesic.care.aldrete','post_anhestesic_care_id', string='Escala Aldrete', copy=False )
	medical_orders_ids= fields.One2many('post.anhestesic.care.medical.orders','post_anhestesic_care_id', u'Órdenes Médicas')
	#selection anhestesia
	anhestesia = fields.Selection([('inhalatoria','Inhalatoria'),('intravenosa','Intravenosa'),('regional','Regional'),('peridural','Peridural'),('raquidea','Raquidea'),('bloqueo','Bloqueo'),('local','Local C.')], string='Anestésia')
	#selection airway
	airway = fields.Selection([('res_espontanea','Respiración Espontánea'),('canulao2','Cánula O2 L/min'),('venturi','Venturi%'),('iot_int','IOT INT'),('t_en_t','T en T'),('venti_mecanica','Ventilación mecánica'),('fr','FR'),('fi_o2','Fi O2'),('peep','PEEP'),('vc','V.C.')], string='Vía Aérea')
	#drains
	nasogastric_tube = fields.Integer(string='Tubo Nasogástrico')
	chest_tube = fields.Integer(string='Tubo Tórax')
	hemovac = fields.Integer(string='Hemovac')
	urinary_tube = fields.Integer(string='Sonda Vesical')
	cystostomy = fields.Integer(string='Sonda Cistostomía')
	others = fields.Integer(string='Otros')
	total = fields.Integer(string='Total (cc)', compute='_get_sum', store=True, help="Total in cubic centimeters")
	room_id = fields.Many2one('doctor.waiting.room', string="Surgery Room/Appointment", copy=False)
	state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
	review_note = fields.Text('Review Note')
	review_active = fields.Boolean('Is Review Note?')
	review_readonly = fields.Boolean('set to readonly')
	background_edit_flag = fields.Boolean('Background Flag', default=False)
	professional_id = fields.Many2one('res.users', 'Professional', default=_default_professional)
	anhestesioligist = fields.Many2one('doctor.professional', 'Anestesiólogo', domain=[('profession_type','=','anesthesiologist')])
	put_nurse = fields.Many2one('doctor.professional', 'Put nurse', domain=[('profession_type','=','nurse')])
	get_nurse = fields.Many2one('doctor.professional', 'Get nurse', domain=[('profession_type','=','nurse')])
	chief_nurse = fields.Many2one('doctor.professional', 'Chief nurse', domain=[('profession_type','=','nurse')])
	sign_date_hour = fields.Datetime(string='Fecha y Hora')
	sign_date_hour_chief = fields.Datetime(string='Fecha y Hora salida')
	destiny = fields.Text('Destino')
	is_nurse_sheet = fields.Boolean('Formato de Enfermería')
	is_nurse_chief_sheet = fields.Boolean('Formato Jefe de Enfermería')
	is_recovery_sheet = fields.Boolean('Formato Recuperación')
	is_presurgical_record = fields.Boolean('Registro Preanestesico')
	is_anestesic_record = fields.Boolean('Registro Anestesico')
	is_quirurgical_check_list = fields.Boolean('Check List Quirúrgico')
	is_medical_evolution = fields.Boolean('Evolución Médica')
	is_epicrisis = fields.Boolean('Epicrisis')
	is_tecnical = fields.Boolean('Inst. Quirúrgico')
	is_prescription = fields.Boolean('prescripciones')
	is_quirurgic_sheet = fields.Boolean('Hoja Quirúrgica')

    
	@api.onchange('room_id')
	def onchange_room_id(self):
		if self.room_id:
			list_ids = []
			self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
			self.duration = self.room_id.duration or 0.00
			for procedure_ids in self.room_id.procedure_ids:
				for products in procedure_ids.product_id:
					list_ids.append(products.id)
			self.procedure = [(6, 0, list_ids)]
			#DevFree: Cierre de formato
			nurse_sheet_obj = self.env['clinica.nurse.sheet'].search([('room_id','=',self.room_id.id)],limit=1)
			if nurse_sheet_obj:
				self.is_nurse_sheet = True
			else:
				self.is_nurse_sheet = False				
			nurse_chief_sheet_obj = self.env['clinica.nurse.chief.sheet'].search([('room_id','=',self.room_id.id)],limit=1)
			if nurse_chief_sheet_obj:
				self.is_nurse_chief_sheet = True
			else:
				self.nurse_chief_sheet_obj = False							
			recovery_sheet_obj = self.env['clinica.recovery.sheet'].search([('room_id','=',self.room_id.id)],limit=1)
			if recovery_sheet_obj:
				self.is_recovery_sheet = True
			else:
				self.is_recovery_sheet = False							
			presurgical_record_obj = self.env['doctor.presurgical.record'].search([('lead_id','=',self.room_id.id)],limit=1)
			if presurgical_record_obj:
				self.is_presurgical_record = True
			else:
				self.is_presurgical_record = False							
			anestesic_record_obj = self.env['clinica.anhestesic.registry'].search([('room_id','=',self.room_id.id)],limit=1)
			if anestesic_record_obj:
				self.is_anestesic_record = True
			else:
				self.is_anestesic_record = False							
			quirurgical_check_list_obj = self.env['clinica.quirurgical.check.list'].search([('room_id','=',self.room_id.id)],limit=1)
			if quirurgical_check_list_obj:
				self.is_quirurgical_check_list = True
			else:
				self.is_quirurgical_check_list = False							
			medical_evolution_obj = self.env['clinica.medical.evolution'].search([('room_id','=',self.room_id.id)],limit=1)
			if medical_evolution_obj:
				self.is_medical_evolution = True
			else:
				self.is_medical_evolution = False							
			epicrisis_obj = self.env['doctor.epicrisis'].search([('room_id','=',self.room_id.id)],limit=1)
			if epicrisis_obj:
				self.is_epicrisis = True
			else:
				self.is_epicrisis = False							
			tecnical_obj = self.env['doctor.surgical.technologist'].search([('room_id','=',self.room_id.id)],limit=1)
			if tecnical_obj:
				self.is_tecnical = True
			else:
				self.is_tecnical = False							
			prescription_obj = self.env['doctor.prescription'].search([('room_id','=',self.room_id.id)],limit=1)
			if prescription_obj:
				self.is_prescription = True
			else:
				self.is_prescription = False							
			quirurgic_sheet_obj = self.env['doctor.quirurgic.sheet'].search([('room_id','=',self.room_id.id)],limit=1)
			if quirurgic_sheet_obj:
				self.is_quirurgic_sheet = True
			else:
				self.is_quirurgic_sheet = False				

	@api.onchange('professional_id')
	def onchange_professional_id(self):
		if self.professional_id:
			user_groups_list = []
			for user_groups in self.professional_id.groups_id:
				user_groups_list.append(user_groups.id)
			anhestesic_group = self.env.ref('clinica_doctor_data.anesthesiologist')
			nurse_group = self.env.ref('clinica_doctor_data.nursing_assistant')
			nurse_chief_group = self.env.ref('clinica_doctor_data.nursery_chief')
			if anhestesic_group.id in user_groups_list or nurse_group.id in user_groups_list or nurse_chief_group.id in user_groups_list:
				self.background_edit_flag = True

	def anhestesioligist_sign(self):
		ctx = self._context
		user_id = self._context.get('uid')
		user_obj = self.env['res.users'].search([('id','=',user_id)])
		professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_id)])
		self.sign_date_hour = datetime.now()
		user_groups_list = []
		for user_groups in user_obj:
			user_groups_list.append(user_groups.id)
		anhestesic_group = self.env.ref('clinica_doctor_data.anesthesiologist')
		self.anhestesioligist = professional_obj.id

	def chief_nurse_sign(self):
		ctx = self._context
		user_id = self._context.get('uid')
		user_obj = self.env['res.users'].search([('id','=',user_id)])
		professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_id)])
		self.sign_date_hour_chief = datetime.now()
		# user_groups_list = []
		# for user_groups in user_obj:
		# 	user_groups_list.append(user_groups.id)
		# anhestesic_group = self.env.ref('clinica_doctor_data.anesthesiologist')
		self.chief_nurse = professional_obj.id


	@api.onchange('patient_id')
	def onchange_patient_id(self):
		if self.patient_id:
			self.numberid = self.patient_id.ref
			self.numberid = self.patient_id._name
			self.document_type = self.patient_id.tdoc
			self.room_id = self.room_id and self.room_id.id or False
			self.surgeon_id = self.room_id.surgeon_id and self.room_id.surgeon_id.id or False
			self.nurse_id = self.room_id.circulating_id and self.room_id.circulating_id.id or False
			self.anesthesiologist_id = self.room_id.anesthesiologist_id and self.room_id.anesthesiologist_id.id or False
	


	@api.depends('nasogastric_tube','chest_tube','hemovac','urinary_tube','cystostomy','others')
	def _get_sum(self):
		for rec in self:
			rec.total= rec.nasogastric_tube+rec.chest_tube+rec.hemovac+rec.urinary_tube+rec.cystostomy+rec.others
	
	@api.multi
	def action_set_close(self):
		for record in self:
			record.state = 'closed'

	@api.multi
	def write(self, vals):
		if vals.get('review_note', False):
			self.review_readonly = True
		res = super(ClinicaPostAnhestesicCare, self).write(vals)
		return res

	def review_note_trigger(self):
		if not self.review_active:
			self.write({'review_active': True})

	@api.multi
	def _set_visualizer_default_values(self):
		vals = {
			'default_patient_id': self.patient_id and self.patient_id.id or False,
			'default_view_model': 'post_anhestesic',
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


class PostAnhestesicCareVitalSigns(models.Model):
	_name = "post.anhestesic.care.vital.signs"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	vital_signs_date_hour = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	vital_signs_tas = fields.Integer(string='TAS')
	vital_signs_tad = fields.Integer(string='TAD')
	vital_signs_fc = fields.Integer(string='FC')
	vital_signs_fr = fields.Integer(string='FR')
	vital_signs_sao2 = fields.Integer(string='SaO2')
	vital_signs_pain  = fields.Integer(string='Dolor(0-10)')
	vital_signs_queasiness  = fields.Boolean(string="Náuseas")
	vital_signs_vomit  = fields.Boolean(string="Vómito")


class PostAnhestesicCareLiquids(models.Model):
	_name = "post.anhestesic.care.liquids"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#liquids
	liquid_via = fields.Char(string='Via')
	liquid_site = fields.Char(string='Sitio')
	liquid_type = fields.Char(string='Tipo')
	liquid_initial_amount = fields.Integer(string='Cant. Inicial (cc)')
	liquid_amount_recovery = fields.Integer(string='Cant. Recuperación (cc)')

class PostAnhestesicCareDrugs(models.Model):
	_name = "post.anhestesic.care.drugs"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#drugs
	drug_time = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	drug_name = fields.Char(string='Droga')
	drug_quantity = fields.Float(string='Cantidad')
	drug_via = fields.Char(string='Via')
	drug_dr = fields.Char(string='D.R.')
	
class PostAnhestesicObservations(models.Model):
	_name = "post.anhestesic.care.observations"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#observation
	observation_time = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	observation = fields.Char('Observaciones')

class PostAnhestesicAldrete(models.Model):
	_name = "post.anhestesic.care.aldrete"
	_score = 0
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	#aldrete
	moment = fields.Selection([('1','Admisión'),('2','5'),('3','15'),('4','30'),('5','45'),('6','60'),('7','Alta')], string='Momento')
	conscience = fields.Selection([('2','Despierto'),('1','Responde Llamado'),('0','No Responde')], string='Conciencia')
	saturation = fields.Selection([('2','SO2 > 93% + Aire'),('1','SO2 > 90% + O2'),('0','SO > 90% + O2')], string='Saturación')
	breathing = fields.Selection([('2','Capaz de Toser'),('1','Disnea'),('0','Apnea')], string='Respiración')
	circulation = fields.Selection([('2','T/A ± 20%'),('1','T/A ± 20% - 50%'),('0','T/A ± 50%')], string='Circulación')
	activity = fields.Selection([('2','Mueve 4 Extremidades'),('1','Mueve 2 Extremidades'),('0','Inmóvil')], string='Actividad')
	aldrete_score = fields.Integer('Puntaje', compute='_compute_score')

	@api.one
	@api.depends('conscience','saturation','breathing','circulation','activity')
	def _compute_score(self):
		if self.conscience:
			if self.conscience == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.conscience == '1':
				self.aldrete_score = int(self.aldrete_score)+ 1
			elif self.conscience == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

	
		if self.saturation:
			if self.saturation == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.saturation == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.saturation == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

		if self.breathing:
			if self.breathing == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.breathing == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.breathing == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

		if self.circulation:
			if self.circulation == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.circulation == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.circulation == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

		if self.activity:
			if self.activity == '2':
				self.aldrete_score = int(self.aldrete_score)+2
			elif self.activity == '1':
				self.aldrete_score = int(self.aldrete_score)+1
			elif self.activity == '0':
				self.aldrete_score = int(self.aldrete_score)+0
		else:
			self.aldrete_score |= 0

class PostAnhestesicMedicalOrders(models.Model):

	_name = 'post.anhestesic.care.medical.orders'
	_rec_name = 'procedures_id'


	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	plantilla_id = fields.Many2one('post.anhestesic.care.medical.orders.temp', 'Plantillas')
	prescripcion = fields.Char(u'Prescripción')
	procedures_id = fields.Many2one('product.product', 'Medicamento/Otro elemento', required=True)
	recomendacion = fields.Text('Recomendaciones')


