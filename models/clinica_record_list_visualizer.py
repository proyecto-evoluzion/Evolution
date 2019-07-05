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


class ClinicaRecordVisualizer(models.Model):
    _name = "clinica.record.list.visualizer"
    _order = 'id desc'
    _description = 'Clinica Record Visualizer'
    _rec_name = 'patient_id'
    
    patient_id = fields.Many2one('doctor.patient', 'Patient')
    doctor_id = fields.Many2one('doctor.professional', string='Doctor')
    start_period = fields.Datetime(string='Start Period')
    end_period = fields.Datetime(string='End Period')
    nurse_sheet_ids = fields.Many2many('clinica.nurse.sheet', 'nurse_sheet_visualizer_rel', 'visualizer_id', 'nurse_sheet_id', 
                                   string="Nurse Sheets", copy=False)
    
    def _get_nurse_sheet_ids(self, search_domain, doctor, start_period, end_period):
        nurse_sheet_ids = []
        if start_period:
            search_domain.append(('procedure_date','>=',start_period))
        if end_period:
            search_domain.append(('procedure_date','<=',end_period))
        if doctor:
            search_domain.append(('room_id.surgeon_id','=',doctor.id))
            
        nurse_sheet_objs = self.env['clinica.nurse.sheet'].search(search_domain)
        if nurse_sheet_objs:
            nurse_sheet_ids = nurse_sheet_objs.ids
        return nurse_sheet_ids
    
    @api.onchange('patient_id','start_period','end_period','doctor_id')
    def onchange_visualizer_filter(self):
        search_domain = []
        nurse_sheet_ids = []
        if self.patient_id:
            search_domain.append(('patient_id','=',self.patient_id.id))
            nurse_sheet_ids = self._get_nurse_sheet_ids(search_domain, self.doctor_id, self.start_period, self.end_period)
        self.nurse_sheet_ids = nurse_sheet_ids

            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:





