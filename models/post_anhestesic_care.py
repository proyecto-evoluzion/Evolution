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

	patient_id = fields.Many2one('doctor.patient', 'Paciente', ondelete='restrict')
	medical_record= fields.Char(string='HC')
	bed = fields.Char(string='Cama')
	date = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	procedure = fields.Char(string='Procedimiento')
	duration = fields.Float(string='Duración (en horas)')
	surgeon_id = fields.Many2one('doctor.professional', string='Cirujano')
	anesthesiologist_id = fields.Many2one('doctor.professional', string='Anestesiólogo')
	nurse_id = fields.Many2one('doctor.professional', string='Auxiliar Enfermería')
	#vital signs
	vital_sign_ids = fields.One2many('post.anhestesic.care.vital.signs', 'post_anhestesic_care_id', string='Signos Vitales', copy=False)
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
	total = fields.Integer(string='Total', compute='_get_sum', store=True)


	@api.depends('nasogastric_tube','chest_tube','hemovac','urinary_tube','cystostomy','others')
	def _get_sum(self):
		for rec in self:
			rec.total= rec.nasogastric_tube+rec.chest_tube+rec.hemovac+rec.urinary_tube+rec.cystostomy+rec.others
			


class PostAnhestesicCareVitalSigns(models.Model):
	_name = "post.anhestesic.care.vital.signs"
	
	post_anhestesic_care_id = fields.Many2one('clinica.post.anhestesic.care', string='Post-Anhestesic Care', copy=False, ondelete='cascade')
	vital_signs_date_hour = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)
	vital_signs_ta = fields.Integer(string='TA')
	vital_signs_fc = fields.Integer(string='FC')
	vital_signs_fr = fields.Integer(string='FR')
	vital_signs_sao2 = fields.Integer(string='SaO2')
	vital_signs_pain  = fields.Integer(string='Dolor(0-10)')
	vital_signs_queasiness  = fields.Boolean(string="Náuseas")
	vital_signs_vomit  = fields.Boolean(string="Vómito")

