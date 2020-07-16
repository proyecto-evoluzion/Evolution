# -*- coding: utf-8 -*-

# Se importan todas las utilidades requeridas.
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL


class PatientAuthController(http.Controller):

	@http.route('/page/patienAuth', auth='public', website=True)
	def patient_auth(self, **kw):
		cat = http.request.env['clinica.patient.auth']
		
		return http.request.render('clinica_doctor_data.patient_auth_template', {
			'auth': cat.search([])
			})