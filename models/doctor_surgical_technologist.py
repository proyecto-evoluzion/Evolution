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

	document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
									  ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
									  ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
	patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
	numberid = fields.Char(string='Number ID', compute="_compute_numberid", store="true")
	surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
	room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment')
	recount_ids = fields.One2many('doctor.surgical.technologist.recount', 'surgical_technologist_id', string='Recount')
	state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
	
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

class SurgicalTechnologistRecount(models.Model):
	_name = "doctor.surgical.technologist.recount"

	surgical_technologist_id = fields.Many2one('doctor.surgical.technologist', string='Surgical technologist', ondelete='restrict')
	recount = fields.Many2one('doctor.surgical.technologist.element', string='Recount')
	start = fields.Integer(string='Starts')
	end = fields.Integer(string='End')

class SurgicalTechnologistElements(models.Model):
	_name = "doctor.surgical.technologist.element"
	_rec_name="name"

	name = fields.Char(string="Name", required="1")
	active = fields.Boolean(string="Active", default=True)
