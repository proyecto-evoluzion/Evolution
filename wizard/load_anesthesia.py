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

class LoadAnesthesiaTime(models.TransientModel):
    _name = "load.anesthesia.wizard"
    _description = "Load Anesthesia Wizard"
    
    @api.model
    def default_get(self, fields):
        res = super(LoadAnesthesiaTime, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', False)
        print ("-----active_ids",active_ids)
        nurse_sheet_obj = self.env['clinica.nurse.sheet'].browse(active_ids)
        print ("-nurse_sheet_obj",nurse_sheet_obj)
        res.update({
            'room_id': nurse_sheet_obj.room_id and nurse_sheet_obj.room_id.id or False,
            'anhestesic_registry_id': nurse_sheet_obj.anhestesic_registry_id and nurse_sheet_obj.anhestesic_registry_id.id or False})
        return res
    
    anhestesic_registry_id = fields.Many2one('clinica.anhestesic.registry', 'Anhestesic Registry')
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment')
    
    @api.multi
    def action_update_anesthesia_registry(self):
        for wizard in self:
            if wizard.anhestesic_registry_id:
                active_ids = self.env.context.get('active_ids', False)
                nurse_sheet_obj = self.env['clinica.nurse.sheet'].browse(active_ids)
                nurse_sheet_obj.anhestesic_registry_id = wizard.anhestesic_registry_id.id
                nurse_sheet_obj.surgery_start_time = wizard.anhestesic_registry_id.anesthesia_start_time
                nurse_sheet_obj.surgery_end_time = wizard.anhestesic_registry_id.end_time
                nurse_sheet_obj._update_invoice_procedure_time()
    
    
    