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

class ClinicaRecoverySheet(models.Model):
    _name = "clinica.recovery.sheet"
    _order = 'id desc'

    def _current_uid(self):
        ctx = self._context
        uid = ctx.get('uid')
        actual_user = self.env['res.users'].search([('id','=',uid)])
        for groups in actual_user.groups_id:
            if groups.id == self.env.ref('clinica_doctor_data.nursing_assistant').id or groups.id == self.env.ref('clinica_doctor_data.surgical_technologist').id:
                return True
        return False

    def _get_professional(self):
        ctx = self._context
        user_id = self._context.get('uid')
        user_obj = self.env['res.users'].search([('id','=',user_id)])
        professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_obj.id)], limit=1)
        if professional_obj:
            return professional_obj.id        

    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    doctor_id = fields.Many2one('doctor.professional', string='Professional', default=_get_professional)
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    procedure_date = fields.Date(string='Procedure Date', default=fields.Date.context_today)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    birth_date = fields.Date(string='Birth Date')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    name = fields.Char(string='Name', copy=False)
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')    
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    vital_sign_ids = fields.One2many('nurse.sheet.vital.signs', 'recovery_sheet_id', string='Vital signs', copy=False)
    readonly_bool = fields.Boolean('Actual User', default=_current_uid)
    diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
    pathological = fields.Text(string="Pathological", related='patient_id.pathological')
    surgical = fields.Text(string="Surgical", related='patient_id.surgical')
    smoke = fields.Boolean(string="Smoke", related='patient_id.smoke')
    cigarate_daily = fields.Integer(string="Cigarettes / Day", related='patient_id.cigarate_daily')
    smoke_uom = fields.Selection([('day','per Day'), ('week','per Week'),('month','per Month'), 
                                  ('year','per Year')], string="Smoke Unit of Measure", default='day', related='patient_id.smoke_uom')
    is_alcoholic = fields.Boolean(string="Alcoholic Drinks", related='patient_id.is_alcoholic')
    alcohol_frequency = fields.Integer(string="Frequency", related='patient_id.alcohol_frequency')
    alcohol_frequency_uom = fields.Selection([('day','per Day'), ('week','per Week'), ('month','per Month'), 
                                              ('year','per Year')], string="Alcoholic Frequency Unit of Measure", default='day', 
                                             related='patient_id.alcohol_frequency_uom')
    marijuana = fields.Boolean(string="Marijuana", related='patient_id.marijuana')
    cocaine = fields.Boolean(string="Cocaine", related='patient_id.cocaine')
    ecstasy = fields.Boolean(string="Ecstasy", related='patient_id.ecstasy')
    body_background_others = fields.Text(string="Body Background Others", related='patient_id.body_background_others')
    pharmacological = fields.Text(string="Pharmacological", related='patient_id.pharmacological')
    allergic = fields.Text(string="Allergic", related='patient_id.allergic')
    pregnancy_number = fields.Integer(string="Number of Pregnancies", related='patient_id.pregnancy_number')
    child_number = fields.Integer(string="Number of Children", related='patient_id.child_number')
    abortion_number = fields.Integer(string="Number of Abortions", related='patient_id.abortion_number')
    last_birth_date = fields.Date(string="Date of Last Birth", related='patient_id.last_birth_date')
    last_menstruation_date = fields.Date(string="Date of Last Menstruation", related='patient_id.last_menstruation_date')
    contrtaceptive_methods = fields.Text(string="Contrtaceptive Methods", related='patient_id.contrtaceptive_methods')
    review_note = fields.Text('Review Note')
    review_active = fields.Boolean('Is Review Note?')
    review_readonly = fields.Boolean('set to readonly')

    # anhestesic_registry_id = fields.Many2one('clinica.anhestesic.registry', 'Anhestesic Registry')   
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for nurse_sheet in self:
            if nurse_sheet.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(nurse_sheet.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    nurse_sheet.age_meassure_unit = '3'
                    nurse_sheet.age = int(date_diff.days)
                elif difference < 365:
                    nurse_sheet.age_meassure_unit = '2'
                    nurse_sheet.age = int(date_diff.months)
                else:
                    nurse_sheet.age_meassure_unit = '1'
                    nurse_sheet.age = int(date_diff.years)
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.document_type = self.patient_id.tdoc
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh

    
    # def _set_change_room_id(self, room):
    #     vals = {}
    #     if room.sale_order_id:
    #         procedure_list = []
    #         invc_procedure_list = []
    #         if room.sale_order_id.picking_ids:
    #             for picking in room.sale_order_id.picking_ids:
    #                 for move in picking.move_lines:
    #                     procedure_list.append((0,0,{'product_id': move.product_id and move.product_id.id or False,
    #                                                 'product_uom_qty': move.product_uom_qty,
    #                                                 'quantity_done': move.quantity_done,
    #                                                 'move_id': move.id}))
    #         sequence = 0
    #         first_line = False
    #         for sale_line in room.sale_order_id.order_line:
    #             sequence += 1
    #             invc_procedure_dict = {
    #                 'product_id': sale_line.product_id and sale_line.product_id.id or False,
    #                 'sequence': sequence,
    #                 'sale_line_id': sale_line.id}
    #             invc_procedure_list.append((0,0, invc_procedure_dict))
    #         if procedure_list or invc_procedure_list:
    #             vals.update({'procedure_ids': procedure_list, 'invoice_procedure_ids': invc_procedure_list})
    #     return vals
        
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
            
    # def _update_invoice_procedure_time(self):
    #     if self.invoice_procedure_ids:
    #         invc_proc_num = len(self.invoice_procedure_ids)
    #         first_procedure = self.invoice_procedure_ids[0]
    #         last_procedure = self.invoice_procedure_ids[invc_proc_num-1]
    #         first_procedure.procedure_start_time = self.surgery_start_time
    #         last_procedure.procedure_end_time = self.surgery_end_time
            
    # @api.onchange('anhestesic_registry_id')
    # def onchange_anhestesic_registry_id(self):
    #     if self.anhestesic_registry_id:
    #         self.surgery_start_time = self.anhestesic_registry_id.anesthesia_start_time
    #         self.surgery_end_time = self.anhestesic_registry_id.end_time
            
    # @api.onchange('surgery_start_time', 'surgery_end_time', 'invoice_procedure_ids')
    # def onchange_surgery_time(self):
    #     if self.invoice_procedure_ids:
    #         if self.surgery_start_time or self.surgery_end_time:
    #             self._update_invoice_procedure_time()
            
    
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

    # @api.multi
    # def _set_invoice_procedure_vals(self, invoice_procedure_ids):
    #     for nurse_sheet in self:
    #         invc_procedures = self.env['nurse.sheet.invoice.procedures'].search([('nurse_sheet_id','=',nurse_sheet.id)], order='sequence')
    #         start_time = 0
    #         load_previous = True
    #         start_time = nurse_sheet.surgery_start_time
    #         for invc_proc_line in invc_procedures:
    #             if load_previous:
    #                 invc_proc_line.procedure_start_time = start_time
    #             if invc_proc_line.load_start_time:
    #                 start_time = invc_proc_line.procedure_end_time
    #                 load_previous = True
    #             else:
    #                 load_previous = False
    #             if invc_proc_line.last_procedure and nurse_sheet.anhestesic_registry_id:
    #                 invc_proc_line.procedure_end_time = nurse_sheet.surgery_end_time
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('recovery.sheet') or '/'
        vals['state'] = 'closed'
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(ClinicaRecoverySheet, self).create(vals)
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('review_note', False):
            self.review_readonly = True
        if vals.get('state', False):
            self.state = 'closed'
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(ClinicaRecoverySheet, self).write(vals)
        return res
    
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.room_id and self.room_id.surgeon_id and self.room_id.surgeon_id.id or False,
            'default_view_model': 'recovery_sheet',
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
        
    @api.multi
    def action_set_close(self):
        for record in self:
            record.state = 'closed'

    def review_note_trigger(self):
        if not self.review_active:
            self.write({'review_active': True})
    
  
class NurseSheetVitalSigns(models.Model):
    _inherit = "nurse.sheet.vital.signs"
    
    recovery_sheet_id = fields.Many2one('clinica.recovery.sheet', string='Recovery Sheet', copy=False, ondelete='cascade')

