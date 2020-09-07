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


class Partner(models.Model):
    _inherit = "res.partner"
    
    professional_created = fields.Boolean(string="Professional Created", copy=False)
    is_assurance = fields.Boolean(string="Is it an Assurance Company?", copy=False)
    insurer_id = fields.Many2one('res.partner',string='Assurance Company')

    @api.model 
    def from_partner_to_patient(self):
    	partner_obj = self.search([('id','=',1318)])
    	vals = {
    		'firstname': partner_obj.x_name1,
    		'lastname': partner_obj.x_lastname1,
    		'middlename': partner_obj.x_name2,
    		'surname': partner_obj.x_lastname2,
    		'name': partner_obj.xidentification,
    		'ref': partner_obj.xidentification,
    		'tdoc': 'pa',
    		'email': partner_obj.email,
    		'phone': partner_obj.mobile or partner_obj.phone,
    	}
    	self.env['doctor.patient'].create(vals)
    	print('holamundo')
    	print('holamundo')
    	print('holamundo')
    	print('holamundo')
    	print('holamundo')
    	return True