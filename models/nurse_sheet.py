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

class ClinicaNurseSheet(models.Model):
    _name = "clinica.nurse.sheet"
    _order = 'id desc'

    def _current_uid(self):
        ctx = self._context
        uid = ctx.get('uid')
        actual_user = self.env['res.users'].search([('id','=',uid)])
        for groups in actual_user.groups_id:
            if groups.id == self.env.ref('clinica_doctor_data.nursing_assistant').id or groups.id == self.env.ref('clinica_doctor_data.surgical_technologist').id:
                return True
        return False

    def _default_professional(self):
        ctx = self._context
        user_id = self._context.get('uid')
        user_obj = self.env['res.users'].search([('id','=',user_id)])
        return user_obj.id

    def _default_doctor(self):
        ctx = self._context
        user_id = self._context.get('uid')
        professional_obj = self.env['doctor.professional'].search([('res_user_id','=',user_id)], limit=1)
        return professional_obj.id
    
    name = fields.Char(string='Name', copy=False)
    procedure_date = fields.Date(string='Procedure Date', default=fields.Date.context_today)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID', compute="_compute_numberid", store="true")
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents', compute="_compute_numberid_integer", store="true")
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
    professional_id = fields.Many2one('res.users', 'Professional', default=_default_professional)
    doctor_id = fields.Many2one('doctor.professional', 'Doctor', default=_default_doctor)
    background_edit_flag = fields.Boolean('Background Flag', default=False)
    middlename = fields.Char(string='Second Name')
    surname = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')], string='Blood Type')
    blood_rh = fields.Selection([('positive','+'),('negative','-')], string='Rh')
    
    room_id = fields.Many2one('doctor.waiting.room', string='Surgery Room/Appointment', copy=False)
    procedure_ids = fields.One2many('nurse.sheet.procedures', 'nurse_sheet_id', string='Health Procedures', copy=False)
    updated_stock = fields.Boolean(string='Stock Updated', copy=False)
    vital_sign_ids = fields.One2many('nurse.sheet.vital.signs', 'nurse_sheet_id', string='Vital signs', copy=False)
    
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
    diabetes = fields.Boolean(string="Diabetes", related='patient_id.diabetes')
    hypertension = fields.Boolean(string="Hypertension", related='patient_id.hypertension')
    arthritis = fields.Boolean(string="Arthritis", related='patient_id.arthritis')
    thyroid_disease = fields.Boolean(string="Thyroid Disease", related='patient_id.thyroid_disease')
    various_procedures = fields.Boolean(string="Various Procedures", copy=False)
    invoice_procedure_ids = fields.One2many('nurse.sheet.invoice.procedures', 'nurse_sheet_id', string='Health Procedures for Invoice', copy=False)
    anhestesic_registry_id = fields.Many2one('clinica.anhestesic.registry', 'Anhestesic Registry')
    readonly_bool = fields.Boolean('Actual User', default=_current_uid)
    
    surgery_start_time = fields.Float(string="Surgery Start Time")
    surgery_end_time = fields.Float(string="Surgery End Time")
    state = fields.Selection([('open','Open'),('closed','Closed')], string='Status', default='open')
    review_note = fields.Text('Review Note')
    review_active = fields.Boolean('Is Review Note?')
    review_readonly = fields.Boolean('set to readonly')

    @api.depends('patient_id')
    def _compute_numberid_integer(self):
        for rec in self:
            try:
                rec.numberid_integer = int(rec.patient_id.name) if rec.patient_id else False
            except:
                rec.numberid_integer = 0

    @api.onchange('professional_id')
    def onchange_professional_id(self):
        if self.professional_id:
            user_groups_list = []
            for user_groups in self.professional_id.groups_id:
                user_groups_list.append(user_groups.id)
            surgery_group = self.env.ref('clinica_doctor_data.surgeon')
            anhestesic_group = self.env.ref('clinica_doctor_data.anesthesiologist')
            if anhestesic_group.id in user_groups_list:
                self.background_edit_flag = True
            if surgery_group.id in user_groups_list:
                self.background_edit_flag = True

    @api.depends('patient_id')
    def _compute_numberid(self):
        for rec in self:
            rec.numberid = rec.patient_id.name if rec.patient_id else False


    @api.onchange('invoice_procedure_ids')
    def onchange_procedure_ids(self):
        if self.invoice_procedure_ids:
            count = 0
            for rec in self.invoice_procedure_ids:
                count += 1
            if count > 1:
                self.various_procedures = True
    
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
            self.firstname = self.patient_id.firstname
            self.lastname = self.patient_id.lastname
            self.middlename = self.patient_id.middlename
            self.surname = self.patient_id.surname
            self.gender = self.patient_id.sex
            self.birth_date = self.patient_id.birth_date
            self.document_type = self.patient_id.tdoc
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.ref
            self.blood_type = self.patient_id.blood_type
            self.blood_rh = self.patient_id.blood_rh

    
    def _set_change_room_id(self, room):
        vals = {}
        if room.sale_order_id:
            procedure_list = []
            invc_procedure_list = []
            if room.sale_order_id.picking_ids:
                for picking in room.sale_order_id.picking_ids:
                    for move in picking.move_lines:
                        procedure_list.append((0,0,{'product_id': move.product_id and move.product_id.id or False,
                                                    'product_uom_qty': move.product_uom_qty,
                                                    'quantity_done': move.quantity_done,
                                                    'move_id': move.id}))
            sequence = 0
            first_line = False
            for sale_line in room.sale_order_id.order_line:
                sequence += 1
                invc_procedure_dict = {
                    'product_id': sale_line.product_id and sale_line.product_id.id or False,
                    'sequence': sequence,
                    'sale_line_id': sale_line.id}
                invc_procedure_list.append((0,0, invc_procedure_dict))
            if procedure_list or invc_procedure_list:
                vals.update({'procedure_ids': procedure_list, 'invoice_procedure_ids': invc_procedure_list})
        return vals 
        
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            room_change_vals = self._set_change_room_id(self.room_id)
            print (room_change_vals)
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
            # self.professional_id = self.room_id.circulating_id and self.room_id.circulating_id.id or False
            self.procedure_ids = room_change_vals.get('procedure_ids', False)
            self.invoice_procedure_ids = room_change_vals.get('invoice_procedure_ids', False)
            
    def _update_invoice_procedure_time(self):
        if self.invoice_procedure_ids:
            invc_proc_num = len(self.invoice_procedure_ids)
            first_procedure = self.invoice_procedure_ids[0]
            last_procedure = self.invoice_procedure_ids[invc_proc_num-1]
            first_procedure.procedure_start_time = self.surgery_start_time
            last_procedure.procedure_end_time = self.surgery_end_time

    def review_note_trigger(self):
        self.review_active = True
            
    @api.onchange('anhestesic_registry_id')
    def onchange_anhestesic_registry_id(self):
        if self.anhestesic_registry_id:
            self.surgery_start_time = self.anhestesic_registry_id.anesthesia_start_time
            self.surgery_end_time = self.anhestesic_registry_id.end_time
            
    @api.onchange('surgery_start_time', 'surgery_end_time', 'invoice_procedure_ids')
    def onchange_surgery_time(self):
        if self.invoice_procedure_ids:
            if self.surgery_start_time or self.surgery_end_time:
                self._update_invoice_procedure_time()
            
    
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
    def _set_invoice_procedure_vals(self, invoice_procedure_ids):
        for nurse_sheet in self:
            invc_procedures = self.env['nurse.sheet.invoice.procedures'].search([('nurse_sheet_id','=',nurse_sheet.id)], order='sequence')
            start_time = 0
            load_previous = True
            start_time = nurse_sheet.surgery_start_time
            for invc_proc_line in invc_procedures:
                if load_previous:
                    invc_proc_line.procedure_start_time = start_time
                if invc_proc_line.load_start_time:
                    start_time = invc_proc_line.procedure_end_time
                    load_previous = True
                else:
                    load_previous = False
                if invc_proc_line.last_procedure and nurse_sheet.anhestesic_registry_id:
                    invc_proc_line.procedure_end_time = nurse_sheet.surgery_end_time
    
    @api.model
    def create(self, vals):
        vals['state'] = 'closed'
        vals['name'] = self.env['ir.sequence'].next_by_code('nurse.sheet') or '/'
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(ClinicaNurseSheet, self).create(vals)
        if vals.get('invoice_procedure_ids', False):
            res._set_invoice_procedure_vals(vals['invoice_procedure_ids'])
        return res
    
    @api.multi
    def write(self, vals):
        if vals.get('review_note', False):
            self.review_readonly = True
        if vals.get('birth_date', False):
            warn_msg = self._check_birth_date(vals['birth_date'])
            if warn_msg:
                raise ValidationError(warn_msg)
        res = super(ClinicaNurseSheet, self).write(vals)
        if vals.get('invoice_procedure_ids', False):
            self._set_invoice_procedure_vals(vals['invoice_procedure_ids'])
        return res
    
    @api.multi
    def action_update_stock(self):
        for nurse_sheet in self:
            for procedure_line in nurse_sheet.procedure_ids:
                if procedure_line.move_id:
                    procedure_line.move_id.quantity_done = procedure_line.quantity_done
            nurse_sheet.updated_stock = True
        return True
    
    @api.multi
    def _set_visualizer_default_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_doctor_id': self.room_id and self.room_id.surgeon_id and self.room_id.surgeon_id.id or False,
            'default_view_model': 'nurse_sheet',
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
        

class NurseSheetProcedures(models.Model):
    _name = "nurse.sheet.procedures"
    
    nurse_sheet_id = fields.Many2one('clinica.nurse.sheet', string='Nurse Sheet', copy=False)
    product_id = fields.Many2one('product.product', string='Health Procedure')
    product_uom_qty = fields.Float(string='Initial Demand')
    quantity_done = fields.Float(string='Used Products')
    move_id = fields.Many2one('stock.move', string='Stock Move', copy=False)
    
  
class NurseSheetVitalSigns(models.Model):
    _name = "nurse.sheet.vital.signs"
    
    nurse_sheet_id = fields.Many2one('clinica.nurse.sheet', string='Nurse Sheet', copy=False, ondelete='cascade')
    vital_signs_date_hour = fields.Datetime(string='Vital Signs Date Hour', default=fields.Datetime.now)
    vital_signs_fc = fields.Integer(string='FC')
    sistolic_arteric_pressure = fields.Integer(string='Sistolic Arteric Pressure')
    diastolic_arteric_pressure = fields.Integer(string='Diastolic Arteric Pressure')
    oximetry = fields.Integer(string='Oximetry')
    diuresis = fields.Integer(string='Diuresis')
    bleeding = fields.Integer(string='Bleeding')
    note = fields.Text(string='Nursing Note')
    
class NurseSheetInvoiceProcedures(models.Model):
    _name = "nurse.sheet.invoice.procedures"
    _order = 'sequence'
    
    nurse_sheet_id = fields.Many2one('clinica.nurse.sheet', string='Nurse Sheet', copy=False)
    product_id = fields.Many2one('product.product', string='Health Procedure')
    sequence = fields.Integer('Sequence')
    procedure_start_time = fields.Float('Procedure Start Time')
    procedure_end_time = fields.Float('Procedure End Time')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', copy=False)
    load_start_time = fields.Boolean(string='Load to Next Procedure Start', copy=False)
    last_procedure = fields.Boolean(string='Last Procedure', copy=False, compute='_set_last_procedure')
    
    @api.multi
    def _set_last_procedure(self):
        for invc_procedure in self:
            nurse_invc_procedure_obj = self.search([('nurse_sheet_id','=',invc_procedure.nurse_sheet_id.id)], order='sequence desc', limit=1)
            if nurse_invc_procedure_obj == invc_procedure:
                invc_procedure.last_procedure = True
            else:
                invc_procedure.last_procedure = False
                
    
                
        
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:



