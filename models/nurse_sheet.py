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
    
    name = fields.Char(string='Name', copy=False)
    procedure_date = fields.Date(string='Procedure Date', default=fields.Date.context_today)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    firstname = fields.Char(string='First Name')
    lastname = fields.Char(string='First Last Name')
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
            
    @api.onchange('document_type','numberid_integer','numberid')
    def onchange_numberid(self):
        if self.document_type and self.document_type not in ['cc','ti']:
            self.numberid_integer = 0
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
            self.numberid = self.numberid_integer
    
    def _set_change_room_id(self, room):
        vals = {}
        if room.sale_order_id and room.sale_order_id.picking_ids:
            procedure_list = []
            for picking in room.sale_order_id.picking_ids:
                for move in picking.move_lines:
                    procedure_list.append((0,0,{'product_id': move.product_id and move.product_id.id or False,
                                                'product_uom_qty': move.product_uom_qty,
                                                'quantity_done': move.quantity_done,
                                                'move_id': move.id}))
            if procedure_list:
                vals.update({'procedure_ids': procedure_list})
        return vals 
        
    @api.onchange('room_id')
    def onchange_room_id(self):
        if self.room_id:
            room_change_vals = self._set_change_room_id(self.room_id)
            self.patient_id = self.room_id.patient_id and self.room_id.patient_id.id or False
            self.procedure_ids = room_change_vals.get('procedure_ids', False)
            
    def _check_assign_numberid(self, numberid_integer):
        if numberid_integer == 0:
            raise ValidationError(_('Please enter non zero value for Number ID'))
        else:
            numberid = str(numberid_integer)
            return numberid
    
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
        for nurse_sheet in self:
            if nurse_sheet.age_meassure_unit == '3' and nurse_sheet.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if nurse_sheet.age > 17 and nurse_sheet.age_meassure_unit == '1' and nurse_sheet.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if nurse_sheet.age_meassure_unit in ['2','3'] and nurse_sheet.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if nurse_sheet.document_type == 'ms' and nurse_sheet.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if nurse_sheet.document_type == 'as' and nurse_sheet.age_meassure_unit == '1' and nurse_sheet.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('nurse.sheet') or '/'
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
        res = super(ClinicaNurseSheet, self).create(vals)
        res._check_document_types()
        return res
    
    @api.multi
    def write(self, vals):
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
         
        res = super(ClinicaNurseSheet, self).write(vals)
        self._check_document_types()
        return res
    
    @api.multi
    def action_update_stock(self):
        for nurse_sheet in self:
            for procedure_line in nurse_sheet.procedure_ids:
                if procedure_line.move_id:
                    procedure_line.move_id.quantity_done = procedure_line.quantity_done
            nurse_sheet.updated_stock = True
        return True

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
        
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:



