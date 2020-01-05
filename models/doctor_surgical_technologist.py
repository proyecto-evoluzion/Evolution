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

class SurgicalTechnologist(models.Model):
	_name = "doctor.surgical.technologist"

	def _get_professional(self):
		ctx = self._context
		user_id = self._context.get('uid')
		user_obj = self.env['res.users'].search([('id','=',user_id)])
		professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_obj.id)])
		if professional_obj:
			return professional_obj.id	

	document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
									  ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
									  ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
	patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
	numberid = fields.Char(string='Number ID', compute="_compute_numberid", store="true")
	surgeon_id = fields.Many2one('doctor.professional', string='Surgeon', default=_get_professional)
	room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment')
	recount_ids = fields.One2many('doctor.surgical.technologist.recount', 'surgical_technologist_id', string='Recount')
	state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
	review_note = fields.Text('Review Note')
	review_active = fields.Boolean('Is Review Note?')
	review_readonly = fields.Boolean('set to readonly')
	name = fields.Char('Name')
	surgical_date = fields.Date(string='Date', default=fields.Date.context_today)
	# product_ids = fields.Many2many('product.product',ondelete='restrict', domain=[('is_health_procedure','=', True)])
	product_ids = fields.Many2many('product.product',ondelete='restrict')

	@api.onchange('room_id')
	def onchange_room_id(self):
		if self.room_id:
			list_ids = []
			self.surgeon_id = self.room_id.surgeon_id and self.room_id.surgeon_id.id or False
			self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
			for procedure_ids in self.room_id.procedure_ids:
				for products in procedure_ids.product_id:
					list_ids.append(products.id)
			self.product_ids = [(6, 0, list_ids)]
	
	@api.onchange('patient_id')
	def onchange_patient_id(self):
		if self.patient_id:
			self.document_type = self.patient_id.tdoc
			
	@api.multi
	def action_set_close(self):
		for record in self:
			record.state = 'closed' 

	@api.depends('patient_id')
	def _compute_numberid(self):
		for rec in self:
			rec.numberid = rec.patient_id.name if rec.patient_id else False

	@api.model
	def create(self, vals):
		vals['name'] = 'Inst. Quirúrgico'		
		res = super(SurgicalTechnologist, self).create(vals)
		return res			

	@api.multi
	def write(self, vals):
		res = super(SurgicalTechnologist, self).write(vals)
		if vals.get('review_note', False):
			self.review_readonly = True
		return vals

	def review_note_trigger(self):
		if not self.review_active:
			self.write({'review_active': True})

	@api.multi
	def _set_visualizer_default_values(self):
		vals = {
			'default_patient_id': self.patient_id and self.patient_id.id or False,
			'default_view_model': 'surgical_technologist',
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

class SurgicalTechnologistRecount(models.Model):
	_name = "doctor.surgical.technologist.recount"

	surgical_technologist_id = fields.Many2one('doctor.surgical.technologist', string='Surgical technologist', ondelete='restrict')
	recount = fields.Many2one('doctor.surgical.technologist.element', string='Recount')
	start = fields.Integer(string='Starts')
	end = fields.Integer(string='End')
	note = fields.Char(string='Note')

class SurgicalTechnologistElements(models.Model):
	_name = "doctor.surgical.technologist.element"
	_rec_name="name"

	name = fields.Char(string="Name", required="1")
	active = fields.Boolean(string="Active", default=True)
