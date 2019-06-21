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

import datetime as dt
from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import calendar
from odoo.exceptions import ValidationError


class DoctorSchedule(models.Model):
    _name = "doctor.schedule"
    _description= 'Doctor Schedule'
    _rec_name = 'professional_id'
    _order = 'id desc'
    
    professional_id = fields.Many2one('doctor.professional', string='Doctor')
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now, copy=False)
    duration = fields.Float(string='Duration (in hours)')
    end_date = fields.Datetime(string='End Date', copy=False)
    room_ids = fields.One2many('doctor.waiting.room', 'schedule_id', string='Waiting Rooms/Appointments', copy=False)
    
    @api.onchange('start_date','duration')
    def onchange_start_date_duration(self):
        if self.start_date:
            start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
            self.end_date = start_date + timedelta(hours=self.duration)

class DoctorWaitingRoom(models.Model):
    _name = "doctor.waiting.room"
    _description= 'Doctor Waiting Room'
    
    name = fields.Char(string='Name', copy=False)
    schedule_id = fields.Many2one('doctor.schedule', string='Schedule', copy=False)
    procedure_date = fields.Datetime(string='Procedure Date', default=fields.Datetime.now, copy=False)
    procedure_end_date = fields.Datetime(string='Procedure End Date', copy=False)
    document_type = fields.Selection([('cc','CC - ID Document'),('ce','CE - Aliens Certificate'),
                                      ('pa','PA - Passport'),('rc','RC - Civil Registry'),('ti','TI - Identity Card'),
                                      ('as','AS - Unidentified Adult'),('ms','MS - Unidentified Minor')], string='Type of Document')
    numberid = fields.Char(string='Number ID')
    numberid_integer = fields.Integer(string='Number ID for TI or CC Documents')
    patient_id = fields.Many2one('doctor.patient', 'Patient', ondelete='restrict')
    first_name = fields.Char(string='First Name')
    first_last_name = fields.Char(string='First Last Name')
    second_name = fields.Char(string='Second Name')
    second_last_name = fields.Char(string='Second Last Name')
    gender = fields.Selection([('male','Male'), ('female','Female')], string='Gender')
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age_meassure_unit')
    age_meassure_unit = fields.Selection([('1','Years'),('2','Months'),('3','Days')], string='Unit of Measure of Age',
                                         compute='_compute_age_meassure_unit')
    phone = fields.Char(string='Telephone')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.doctor', string='Anesthesiologist')
    anesthesia_type = fields.Selection([('general','General'),('sedation','Sedación'),('local','Local')], 
                                        string='Type of Anesthesia')
    procedure = fields.Text(string='Procedure')
    notes = fields.Text(string='Observations or Notes')
    programmer_id = fields.Many2one('res.users', string='Programmer', default=lambda self: self.env.user)
    procedure_ids = fields.One2many('doctor.waiting.room.procedures', 'room_id', string='Helath Procedures', copy=False)
    state = fields.Selection([('new','New'),('confirmed','Confirmed'),('ordered','SO Created')], 
                                        string='Status', default='new')
    nurse_sheet_created = fields.Boolean(string='Nurse Sheet Created', compute='_compute_nurse_sheet_creation')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
    
    @api.multi
    @api.depends('birth_date')
    def _compute_age_meassure_unit(self):
        for room in self:
            if room.birth_date:
                today_datetime = datetime.today()
                today_date = today_datetime.date()
                birth_date_format = datetime.strptime(room.birth_date, DF).date()
                date_difference = today_date - birth_date_format
                difference = int(date_difference.days)
                month_days = calendar.monthrange(today_date.year, today_date.month)[1]
                date_diff = relativedelta.relativedelta(today_date, birth_date_format)
                if difference < 30:
                    room.age_meassure_unit = '3'
                    room.age = int(date_diff.days)
                elif difference < 365:
                    room.age_meassure_unit = '2'
                    room.age = int(date_diff.months)
                else:
                    room.age_meassure_unit = '1'
                    room.age = int(date_diff.years)
                    
    @api.multi
    def _compute_nurse_sheet_creation(self):
        for room in self:
            nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('room_id','=',room.id)])
            if nurse_sheet_ids:
                room.nurse_sheet_created = True
                    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.first_name = self.patient_id.first_name
            self.first_last_name = self.patient_id.first_last_name
            self.second_name = self.patient_id.second_name
            self.second_last_name = self.patient_id.second_last_name
            self.gender = self.patient_id.gender
            self.birth_date = self.patient_id.birth_date
            self.phone = self.patient_id.phone
            self.document_type = self.patient_id.document_type
            self.numberid = self.patient_id.name
            self.numberid_integer = self.patient_id.numberid_integer
            
    @api.onchange('schedule_id')
    def onchange_schedule_id(self):
        if self.schedule_id:
            self.surgeon_id = self.schedule_id.professional_id and self.schedule_id.professional_id.id or False
            
    @api.onchange('document_type','numberid_integer','numberid')
    def onchange_numberid(self):
        if self.document_type and self.document_type not in ['cc','ti']:
            self.numberid_integer = 0
        if self.document_type and self.document_type in ['cc','ti'] and self.numberid_integer:
            self.numberid = self.numberid_integer
            
    @api.onchange('procedure_date')
    def onchange_procedure_date(self):
        if self.procedure_date:
            procedure_date = datetime.strptime(self.procedure_date, DEFAULT_SERVER_DATETIME_FORMAT)
            self.procedure_end_date = procedure_date + timedelta(hours=4)
    
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
        for room in self:
            if room.age_meassure_unit == '3' and room.document_type not in ['rc','ms']:
                raise ValidationError(_("You can only choose 'RC' or 'MS' documents, for age less than 1 month."))
            if room.age > 17 and room.age_meassure_unit == '1' and room.document_type in ['rc','ms']:
                raise ValidationError(_("You cannot choose 'RC' or 'MS' document types for age greater than 17 years."))
            if room.age_meassure_unit in ['2','3'] and room.document_type in ['cc','as','ti']:
                raise ValidationError(_("You cannot choose 'CC', 'TI' or 'AS' document types for age less than 1 year."))
            if room.document_type == 'ms' and room.age_meassure_unit != '3':
                raise ValidationError(_("You can only choose 'MS' document for age between 1 to 30 days."))
            if room.document_type == 'as' and room.age_meassure_unit == '1' and room.age <= 17:
                raise ValidationError(_("You can choose 'AS' document only if the age is greater than 17 years."))
      
    @api.multi
    def _validate_surgeon_room(self):
        for room in self:
            if self.surgeon_id:
                start_date = self.procedure_date
                end_date = self.procedure_end_date
                if end_date and start_date:
                    if end_date <= start_date:
                        raise ValidationError(_("End date should be greater than start date!"))
                    start_time_between_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','<=',start_date),
                                                ('procedure_end_date','>',start_date),
                                                ])
                    if len(start_time_between_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                    end_time_between_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','<',end_date),
                                                ('procedure_end_date','>=',end_date),
                                                ])
                    if len(end_time_between_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                    
                    overlap_rooms = self.search([('surgeon_id','=',self.surgeon_id.id),
                                                ('procedure_date','>=',start_date),
                                                ('procedure_end_date','<=',end_date),
                                                ])
                    if len(overlap_rooms) > 1:
                        raise ValidationError(_("%s has another appointment in this date range! Please choose another. ") % self.surgeon_id.partner_id.name)
                
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('doctor.waiting.room') or '/'
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
        res = super(DoctorWaitingRoom, self).create(vals)
        res._check_document_types()
        res._validate_surgeon_room()
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
        
        res = super(DoctorWaitingRoom, self).write(vals)
        self._check_document_types()
        self._validate_surgeon_room()
        return res
    
    @api.multi
    def action_confirm(self):
        for room in self:
            room.state = 'confirmed'
            
    @api.multi
    def _set_nurse_sheet_values(self):
        vals = {
            'default_patient_id': self.patient_id and self.patient_id.id or False,
            'default_room_id' : self.id
        }
        if self.sale_order_id and self.sale_order_id.picking_ids:
            procedure_list = []
            for picking in self.sale_order_id.picking_ids:
                for move in picking.move_lines:
                    procedure_list.append((0,0,{'product_id': move.product_id and move.product_id.id or False,
                                                'product_uom_qty': move.product_uom_qty,
                                                'quantity_done': move.quantity_done,
                                                'move_id': move.id}))
            if procedure_list:
                vals.update({'default_procedure_ids': procedure_list})
        return vals
            
    @api.multi
    def action_view_nurse_sheet(self):
        action = self.env.ref('clinica_doctor_data.action_clinica_nurse_sheet')
        result = action.read()[0]
        #override the context to get rid of the default filtering
        result['context'] = self._set_nurse_sheet_values()
        nurse_sheet_ids = self.env['clinica.nurse.sheet'].search([('room_id','=',self.id)])
        
        #choose the view_mode accordingly
        if len(nurse_sheet_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(nurse_sheet_ids.ids) + ")]"
        elif len(nurse_sheet_ids) == 1:
            res = self.env.ref('clinica_doctor_data.view_clinica_nurse_sheet_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = nurse_sheet_ids.id
        return result
    
    @api.multi
    def _create_so(self):
        for room in self:
            so_vals = {
                    'partner_id': room.patient_id and room.patient_id.partner_id and room.patient_id.partner_id.id or False
                }
            sale_order = self.env['sale.order'].create(so_vals)
            for procedure in room.procedure_ids:
                so_line_vals = {
                    'product_id': procedure.product_id and procedure.product_id.id or False,
                    'product_uom_qty': procedure.quantity,
                    'order_id': sale_order.id,
                    }
                self.env['sale.order.line'].create(so_line_vals)
        return sale_order
    
    @api.multi
    def action_create_so(self):
        for room in self:
            room.sale_order_id = room._create_so().id
            room.state = 'ordered'
        return self.action_view_sale_order()
            
    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_quotations')
        result = action.read()[0]
        res = self.env.ref('sale.view_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.sale_order_id.id
        return result
    

class DoctorWaitingRoomProcedures(models.Model):
    _name = "doctor.waiting.room.procedures"
    
    room_id = fields.Many2one('doctor.waiting.room', string='Waiting Room', copy=False)
    product_id = fields.Many2one('product.product', string='Health Procedure')
    quantity = fields.Float(string='Quantity')
    surgeon_id = fields.Many2one('doctor.professional', string='Surgeon')
    anesthesiologist_id = fields.Many2one('doctor.professional', string='Anesthesiologist')
    
    @api.onchange('surgeon_id','anesthesiologist_id')
    def onchange_surgeon_anesthesiologist(self):
        product_list = []
        domain = {}
        if self.surgeon_id and self.surgeon_id.product_ids:
            product_list += self.surgeon_id.product_ids.ids
        if self.anesthesiologist_id and self.anesthesiologist_id.product_ids:
            product_list += self.anesthesiologist_id.product_ids.ids
        domain.update({'product_id': [('id','in',product_list)]})
        return {'domain': domain}
            
    
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:

