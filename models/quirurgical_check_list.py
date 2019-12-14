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
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
from odoo.exceptions import ValidationError

class ClinicaQuirurgicalCheckList(models.Model):
	_name = 'clinica.quirurgical.check.list'
	_description= 'Quirurgical Check List'

	def _default_professional(self):
		ctx = self._context
		user_id = self._context.get('uid')
		user_obj = self.env['res.users'].search([('id','=',user_id)])
		# professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_obj.id)])
		# if professional_obj:
		return user_obj.id	
	
	name = fields.Char(string='Name', copy=False)
	procedure_datetime = fields.Datetime(string='Procedure Date/Time')
	procedure_id = fields.Many2one('product.product', string='Procedure')
	procedure_ids = fields.Many2many('product.product', 'quirurgical_checklist_procedures_rel', string='Procedure', ondelete='restrict', domain=[('is_health_procedure','=', True)])
	document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
									  ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
									  ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
	numberid = fields.Char(string='Number ID', compute="_compute_numberid", store="true")
	numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', compute="_compute_numberid_integer", store="true")
	patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
	firstname = fields.Char(string='First Name')
	lastname = fields.Char(string='First Last Name')
	middlename = fields.Char(string='Second Name')
	surname = fields.Char(string='Second Last Name')
	signing_doctor = fields.Char(string='Signing Doctor')
	procedures = fields.Char(string='Procedures')
	gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
	birth_date = fields.Date(string='Birth Date')
	age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
	age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
										 compute='_compute_age_meassure_unit')
	surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
	anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
	anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
										string='Type of Anesthesia')
	technologist_id = fields.Many2one('doctor.professional', string='Surgical Technologists')
	nurse_id = fields.Many2one('doctor.professional', string='Auxiliary Nurse')
	
	#PRE-OPERATORY fields
	confirm_patient_name = fields.Selection([('yes','Yes'),('no', 'No')], string="Confirm Patient Name")
	confirm_bracelet_data = fields.Selection([('yes','Yes'),('no', 'No')], string="Bracelet data is verified: Name, Type and Identification Number, HR, Allergies")
	confirm_procedure = fields.Selection([('yes','Yes'),('no', 'No')], string="Confirm Procedure")
	surgical_concent_filled = fields.Selection([('yes','Yes'),('no', 'No')], string='Surgical informed consent fully filled out')
	pre_anesthetic_assessment_complete = fields.Selection([('yes','Yes'),('no', 'No')], string='Pre-anesthetic assessment and informed consent Anesthetic fully completed')
	removed_dental_aceesories = fields.Selection([('yes','Yes'),('no', 'No')], string='Removal of: Dental prostheses, jewelry, lenses, enamel, tampons, etc.')
	pre_surgical_lab_exams = fields.Selection([('yes','Yes'),('no', 'No')], string='Pre-surgical clinical laboratory exams.')
	patient_belongins_locked = fields.Selection([('yes','Yes'),('no', 'No')], string="The patient's personal belongings are locked in the locker held by the relative")
	fasting_time_greater = fields.Selection([('yes','Yes'),('no', 'No')], string="Fasting time greater than 8 hours")
	flu_symptoms_enquired = fields.Selection([('yes','Yes'),('no', 'No')], string="I inquire about flu symptoms in the last week")
	allergic_enquired = fields.Selection([('yes','Yes'),('no', 'No')], string="Does the patient have allergies ?")
	allergic_text = fields.Text(string="Which?")
	medication_text = fields.Text(string="Which?")
	prophylaxis_text = fields.Text(string="Which?")
	enquired_proc_medication = fields.Selection([('yes','Yes'),('no', 'No')], string="Did the patient consume medications prior to the procedure?")
	enquired_proc_medication_note = fields.Text(string="medication note")
	investigated_drug_consumption = fields.Selection([('yes','Yes'),('no', 'No')], string="Did the patient consume alcoholic beverages and / or narcotic drugs prior to the procedure?")
	antiembolicas_stockings = fields.Selection([('yes','Yes'),('no', 'No')], string="Antiembolicas stockings")
	operational_site_marking = fields.Selection([('yes','Yes'),('no', 'No')], string="Operational site marking")
	special_preparation = fields.Selection([('yes','Yes'),('no', 'No')], string="Special preparations ?")
	special_preparations_text = fields.Text(string="Special preparations")
	
	#INTRA-OPERATORY fields
	recording_vital_signs = fields.Selection([('yes','Yes'),('no', 'No')], string="Taking and recording vital signs")
	antibiotic_prophylaxis = fields.Selection([('yes','Yes'),('no', 'No')], string="Antibiotic prophylaxis before surgery")
	antibiotic_prophylaxis_note = fields.Text(string="Prophylaxis note")
	full_staff_in_room = fields.Selection([('yes','Yes'),('no', 'No')], string="Full staff is found inside the room to start the procedure")
	monitoring_induction_complete = fields.Selection([('yes','Yes'),('no', 'No')], string="Monitoring and induction is complete to start")
	monitor_indu_anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
	is_scheduled = fields.Selection([('yes','Yes'),('no', 'No')], string="Is scheduled to ?")
	scheduled_surgeon_id = fields.Many2one('doctor.professional', string='Scheduled Surgeon')
	scheduled_patient_id = fields.Many2one('doctor.patient', 'Scheduled Patient')
	equipments_in_room = fields.Selection([('yes','Yes'),('no', 'No')], string="The requirements for equipment requested by you are in the room")
	equipments_room_surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
	materials_in_room = fields.Selection([('yes','Yes'),('no', 'No')], string="Instrumentation the materials, medications and special supplies requested by the surgeon are in the room")
	equipments_in_order = fields.Selection([('yes','Yes'),('no', 'No')], string="Instrumentadora all the equipment is suitably sterile and in order")
	venous_pressure_working = fields.Selection([('yes','Yes'),('no', 'No')], string="Intermittent venous pressure working")
	supplies_delivered = fields.Selection([('yes','Yes'),('no', 'No')], string="Additional items or supplies were delivered")
	pay = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Pay")
	proc_bill_pay = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Procedure bill is paid by")
	scheduled_nurse_id = fields.Many2one('doctor.professional', string='Surgery Assistant Nurse')
	
	#POST OPERATORY fields
	doctor_done_additionaly = fields.Selection([('yes','Yes'),('no', 'No')], string="Doctor something was done additionally or changed the procedure")
	sample_delivered = fields.Selection([('yes','Yes'),('no', 'No')], string="Samples were delivered to the laboratory")
	sample_delivered_text = fields.Text(string="Delivered Samples Details")
	sample_delivered_pay = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Who pay the samples delivered to the laboratory")
	delivered_recovery_exam = fields.Selection([('yes','Yes'),('no', 'No')], string="Recovery exams are delivered")
	reported_disfunction_equip = fields.Selection([('yes','Yes'),('no', 'No')], string="I have reported the dysfunctional equipment or elements to the head of surgery")
	blood_returned = fields.Selection([('yes','Yes'),('no', 'No')], string="The requested blood was returned to the Blood Bank, which for any reason was not used")
	add_items_delivered = fields.Selection([('yes','Yes'),('no', 'No')], string="Additional items delivered?")
	add_items_delivered_text = fields.Text(string="Were are the additional items delivered?")
	pay_add_items_delivered = fields.Selection([('doctor','Medico'),('patient', 'Paciente')], string="Who pay the aditional items delivered?")
	history_complete = fields.Selection([('yes','Yes'),('no', 'No')], string="History completed and signed")
	delivered_nurse_id = fields.Many2one('doctor.professional', string='Delivered Nurse')
	received_nurse_id = fields.Many2one('doctor.professional', string='Received Nurse')
	deliver_receive_time = fields.Datetime(string="Time")
	
	#RECOVERY fields
	recovery = fields.Text(string="Recovery")
	history_received = fields.Selection([('yes','Yes'),('no', 'No')], string="Full medical history is received")
	equipment_working = fields.Selection([('yes','Yes'),('no', 'No')], string="All equipment for monitoring and resuscitation of the patient working")
	informed_family = fields.Selection([('yes','Yes'),('no', 'No')], string="The patient's family member is informed of their status and evolution")
	patient_out_with = fields.Selection([('nurse','Enfermera'),('family', 'Familiar')], string="The patient goes out with?")
	add_supplies = fields.Selection([('yes','Yes'),('no', 'No')], string="The patient comes out with additional supplies")
	add_supplies_text = fields.Text(string="Additional supplies")

	observations = fields.Text(string="Observaciones")
	room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
	state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
	review_note = fields.Text('Review Note')
	review_active = fields.Boolean('Is Review Note?')
	review_readonly = fields.Boolean('set to readonly')
	presurgery_active = fields.Boolean('Presurgery?')
	intra_surgery_active = fields.Boolean('Intra surgery?')
	post_surgery_active = fields.Boolean('Post surgery?')
	recovery_active = fields.Boolean('Recovery?')
	professional_id = fields.Many2one('res.users', 'Professional', default=_default_professional)	

	@api.onchange('professional_id')
	def onchange_professional_id(self):
		if self.professional_id:
			user_groups_list = []
			for user_groups in self.professional_id.groups_id:
				user_groups_list.append(user_groups.id)
			nursing_assistant_group = self.env.ref('clinica_doctor_data.nursing_assistant')
			nursery_chief_group = self.env.ref('clinica_doctor_data.nursery_chief')
			if nursing_assistant_group.id in user_groups_list:
				self.presurgery_active = True
			if nursery_chief_group.id in user_groups_list:
				self.intra_surgery_active = True
			if nursing_assistant_group.id in user_groups_list:
				self.intra_surgery_active = True

	@api.onchange('room_id')
	def onchange_room_id(self):
		if self.room_id:
			list_ids = []
			self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
			for procedure_ids in self.room_id.procedure_ids:
				for products in procedure_ids.product_id:
					list_ids.append(products.id)
			self.procedure_ids = [(6, 0, list_ids)]
			self.surgeon_id = self.room_id.surgeon_id.id
			# self.technologist_id = self.room_id.technologist_id.id
			# self.nurse_id = self.room_id.circulating_id.id
			self.anesthesiologist_id = self.room_id.anesthesiologist_id.id
			self.anesthesia_type = self.room_id.anesthesia_type
			#DevFree: Asigning current doctor user to signing_doctor field.
			user = self.env.user
			professional = self.env['doctor.professional'].search([('res_user_id','=',user.id)])
			if professional:
				self.signing_doctor = professional.firstname +' '+ professional.lastname
			#DevFree: Asigning current surgery procedures
			for proc in self.room_id:
				for proc_ids in proc.procedure_ids:
					if not self.procedures:
						self.procedures = ''
					print(proc_ids.product_id.name)
					if not proc_ids.product_id:
						continue
					else:
						self.procedures = str(self.procedures) +' '+ str(proc_ids.product_id.name)

	@api.multi
	@api.depends('birth_date')
	def _compute_age_meassure_unit(self):
		for check_list in self:
			if check_list.birth_date:
				today_datetime = datetime.today()
				today_date = today_datetime.date()
				birth_date_format = datetime.strptime(check_list.birth_date, DF).date()
				date_difference = today_date - birth_date_format
				difference = int(date_difference.days)
				month_days = calendar.monthrange(today_date.year, today_date.month)[1]
				date_diff = relativedelta.relativedelta(today_date, birth_date_format)
				if difference < 30:
					check_list.age_meassure_unit = '3'
					check_list.age = int(date_diff.days)
				elif difference < 365:
					check_list.age_meassure_unit = '2'
					check_list.age = int(date_diff.months)
				else:
					check_list.age_meassure_unit = '1'
					check_list.age = int(date_diff.years)
	
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
		for check_list in self:
			if check_list.age_meassure_unit == '3' and check_list.document_type not in ['rc','ms']:
				raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
			if check_list.age > 17 and check_list.age_meassure_unit == '1' and check_list.document_type in ['rc','ms']:
				raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
			if check_list.age_meassure_unit in ['2','3'] and check_list.document_type in ['cc','as','ti']:
				raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
			if check_list.document_type == 'ms' and check_list.age_meassure_unit != '3':
				raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
			if check_list.document_type == 'as' and check_list.age_meassure_unit == '1' and check_list.age <= 17:
				raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))

	@api.onchange('document_type','numberid_integer','numberid')
	def onchange_number_id(self):
		if self.document_type and self.document_type not in ['cc','ti']:
			self.numberid_integer = 0
		if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
			self.numberid = self.numberid_integer

	@api.onchange('patient_id')
	def onchange_patient_id(self):
		if self.patient_id:
			self.firstname = self.patient_id.firstname
			self.lastname = self.patient_id.lastname
			self.middlename = self.patient_id.middlename
			self.surname = self.patient_id.surname
			self.gender = self.patient_id.sex
			self.birth_date = self.patient_id.birth_date
			self.blood_type = self.patient_id.blood_type
			self.blood_rh = self.patient_id.blood_rh
			self.document_type = self.patient_id.tdoc
			self.numberid = self.patient_id.name
			self.numberid_integer = self.patient_id.ref

	@api.model
	def create(self, vals):
		# if vals.get('confirm_patient_name', False):
		# 	vals['presurgery_active'] = True
		# if vals.get('recording_vital_signs', False):
		# 	vals['intra_surgery_active'] = True
		if vals.get('doctor_done_additionaly', False):
			vals['post_surgery_active'] = True
		if vals.get('history_received', False):
			vals['recovery_active'] = True
		vals['name'] = self.env['ir.sequence'].next_by_code('quirurgical.check.list') or '/'
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
		res = super(ClinicaQuirurgicalCheckList, self).create(vals)
		res._check_document_types()
		return res

	@api.multi
	def write(self, vals):
		# if vals.get('review_note', False):
		# 	self.review_readonly = True
		# if vals.get('confirm_patient_name', False):
		# 	vals['presurgery_active'] = True
		if vals.get('recording_vital_signs', False):
			vals['intra_surgery_active'] = True
		if vals.get('doctor_done_additionaly', False):
			vals['post_surgery_active'] = True
		if vals.get('history_received', False):
			vals['recovery_active'] = True
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
		res = super(ClinicaQuirurgicalCheckList, self).write(vals)
		self._check_document_types()
		return res
	
	@api.multi
	def action_set_close(self):
		for record in self:
			record.state = 'closed'

	def review_note_trigger(self):
		if not self.review_active:
			self.write({'review_active': True})


	
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:


