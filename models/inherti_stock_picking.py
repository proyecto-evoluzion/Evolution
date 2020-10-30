# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _

from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter

from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


class InheritStockPicking(models.Model):
    _inherit = "stock.picking"

    total_cost = fields.Float(string="Costo Total")
    pivot_invisible = fields.Boolean(string="Vista invisible")
    aux_move_lines = fields.Boolean(string="Auxiliar move_lines", default=False)
    out_move_lines = fields.One2many('copy.stock.move', 'picking_id', string="Stock Moves OUT")
    in_move_lines = fields.One2many('copy.stock.move2', 'picking_id', string="Stock Moves IN")

    
    @api.multi
    def cost_calculation(self):
        for moves in self.move_lines:
        	qty = 1
        	cost = 0
        	if moves.quantity_done > 0:
        		moves.product_cost = moves.product_tmpl_id.standard_price * moves.quantity_done
        		self.total_cost += moves.product_cost

    @api.model
    def create(self, vals):
    	res = super(InheritStockPicking, self).create(vals)

    	for picking_type in res.picking_type_id:
    		if picking_type.code != 'outgoing':
    			res.pivot_invisible = True
    		else:
    			res.pivot_invisible = False
    	return res

    @api.multi
    def mirror_data(self):
        copy_vals = {}
        for pick in self.env['stock.picking'].search([('id','>',0)]):
            for move in pick.move_lines:
                copy_vals = {
                    'name': move.name,
                    'product_id': move.product_id.id,
                    'product_uom_qty': move.product_qty,
                    'product_uom': move.product_uom.id,
                    'state': move.state,
                    'date_expected': move.date_expected,
                    'date': move.date,
                    'partner_id': move.partner_id.id,
                    'picking_id': move.picking_id.id,
                    'origin': move.origin,
                    'reference': move.reference,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'picking_type_id': move.picking_type_id.id,
                }
                if pick.picking_type_id.code == 'outgoing':
                    self.env['copy.stock.move'].create(copy_vals)
                elif pick.picking_type_id.code == 'incoming':
                    self.env['copy.stock.move2'].create(copy_vals)
                copy_vals = {}



class InheritStockMove(models.Model):
    _inherit = "stock.move"

    product_cost = fields.Float(string="Costo")
    no_mirror_data = fields.Boolean(string="No Mirror Data")

    @api.model
    def create(self, vals):
        copy_vals = {}
        res = super(InheritStockMove, self).create(vals)
        if not res.no_mirror_data:
        	copy_vals = {
	            'name': res.name,
	            'product_id': res.product_id.id,
	            'product_uom_qty': res.product_qty,
	            'product_uom': res.product_uom.id,
	            'state': res.state,
	            'date_expected': res.date_expected,
	            'date': res.date,
	            'partner_id': res.partner_id.id,
	            'origin': res.origin,
	            'reference': res.reference,
	            'location_id': res.location_id.id,
	            'location_dest_id': res.location_dest_id.id,
	            'picking_type_id': res.picking_type_id.id,
	            'no_mirror_data': True,
	        }
	        print('aaa')

	        for picking_type in res.picking_type_id:
	        	if picking_type.code == 'outgoing':
	        		self.env['copy.stock.move'].create(copy_vals)
	        	elif picking_type.code == 'incoming':
	        		self.env['copy.stock.move2'].create(copy_vals)
        return res

    # @api.multi
    # def write(self, vals):
    # 	res = super(InheritStockMove, self).write(vals)
    # 	move_obj = self.env['copy.stock.move'].search([('picking_id','=',self.picking_id.id),('product_id','=',self.product_id.id)])

    # 	if move_obj:
    # 		if vals.get('quantity_done', False):
    # 			for moves in move_obj:
    # 				moves.write({'quantity_done':vals.get('quantity_done')})

    # 	return res

class CopyStockMove(models.Model):
    _name = "copy.stock.move"

    @api.depends('picking_id', 'name')
    def _compute_reference(self):
        for move in self:
            move.reference = move.picking_id.name if move.picking_id else move.name

    name = fields.Char('Description')
    product_id = fields.Many2one(
        'product.product', 'Producto',
        domain=[('type', 'in', ['product', 'consu'])],
        states={'done': [('readonly', True)]})
    product_uom_qty = fields.Float(
        'Demanda inicial',
        digits=dp.get_precision('Product Unit of Measure'),
        default=0.0, states={'done': [('readonly', True)]})
    product_uom = fields.Many2one('product.uom', 'Unidad de Medida')
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status', default='draft')
    date_expected = fields.Datetime(
        'Expected Date', default=fields.Datetime.now, 
        states={'done': [('readonly', True)]})
    date = fields.Datetime(
        'Date', default=fields.Datetime.now,
        states={'done': [('readonly', True)]})
    partner_id = fields.Many2one(
        'res.partner', 'Destination Address ',
        states={'done': [('readonly', True)]})
    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', states={'done': [('readonly', True)]})
    origin = fields.Char("Source Document")
    reference = fields.Char(compute='_compute_reference', string="Reference", store=True)
    # sale_line_id = fields.Many2one('sale.order', 'Venta Asociada')
    location_id = fields.Many2one(
        'stock.location', 'Source Location')
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')

    product_cost = fields.Float(string="Costo")
    product_delivered = fields.Float(string="Entregado")
    # product_return = fields.Float(string='Devuelto')
    product_return = fields.Float(string='Devuelto', compute='_compute_product_return')
    quantity_done = fields.Float('Gastado', digits=dp.get_precision('Product Unit of Measure'))
    no_mirror_data = fields.Boolean(string="No Mirror Data")

    @api.depends('product_delivered', 'quantity_done')
    def _compute_product_return(self):
        for move in self:
            move.product_return = move.product_delivered - move.quantity_done

    @api.multi
    def write(self, vals):
    	res = super(CopyStockMove, self).write(vals)
    	for moves in self:
    		move_obj = self.env['stock.move'].search([('picking_id','=',moves.picking_id.id),('product_id','=',moves.product_id.id)])
    		if vals.get('quantity_done', False):
    			if move_obj:
    				for lines in move_obj:
    					lines.write({'quantity_done':vals.get('quantity_done')})

    	return res

    @api.model
    def create(self, vals):
        copy_vals = {}
        res = super(CopyStockMove, self).create(vals)
        if not res.no_mirror_data:
        	copy_vals = {
	            'name': 'Mirror',
	            'product_id': res.product_id.id,
	            'product_uom_qty': res.product_uom_qty,
	            'quantity_done': res.quantity_done,
	            'product_uom': 1,
	            'partner_id': res.picking_id.partner_id.id,
	            'picking_id': res.picking_id.id,
	            'origin': res.picking_id.origin,
	            'location_id': 15,
	            'location_dest_id': 9,
	            'picking_type_id': 4,
	            'no_mirror_data': True,
	        }
        	self.env['stock.move'].create(copy_vals)
        return res

    @api.multi
    def unlink(self):
    	for moves in self:
    		move_obj = self.env['stock.move'].search([('picking_id','=',moves.picking_id.id),('product_id','=',moves.product_id.id)])
    		if move_obj:
    			for lines in move_obj[0]:
    				lines.unlink()

    	return super(CopyStockMove, self).unlink()


class CopyStockMove2(models.Model):
    _name = "copy.stock.move2"

    @api.depends('picking_id', 'name')
    def _compute_reference(self):
        for move in self:
            move.reference = move.picking_id.name if move.picking_id else move.name

    name = fields.Char('Description')
    product_id = fields.Many2one(
        'product.product', 'Producto',
        domain=[('type', 'in', ['product', 'consu'])],
        states={'done': [('readonly', True)]})
    product_uom_qty = fields.Float(
        'Demanda inicial',
        digits=dp.get_precision('Product Unit of Measure'),
        default=0.0, states={'done': [('readonly', True)]})
    product_uom = fields.Many2one('product.uom', 'Unidad de Medida')
    state = fields.Selection([
        ('draft', 'New'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Move'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done')], string='Status', default='draft')
    date_expected = fields.Datetime(
        'Expected Date', default=fields.Datetime.now, 
        states={'done': [('readonly', True)]})
    date = fields.Datetime(
        'Date', default=fields.Datetime.now,
        states={'done': [('readonly', True)]})
    partner_id = fields.Many2one(
        'res.partner', 'Destination Address ',
        states={'done': [('readonly', True)]})
    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', states={'done': [('readonly', True)]})
    origin = fields.Char("Source Document")
    reference = fields.Char(compute='_compute_reference', string="Reference", store=True)
    # sale_line_id = fields.Many2one('sale.order', 'Venta Asociada')
    location_id = fields.Many2one(
        'stock.location', 'Source Location')
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')

    product_cost = fields.Float(string="Costo")
    quantity_done = fields.Float('Cantidad recibida', digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def write(self, vals):
    	res = super(CopyStockMove2, self).write(vals)
    	move_obj = self.env['stock.move'].search([('picking_id','=',self.picking_id.id),('product_id','=',self.product_id.id)])

    	if vals.get('quantity_done', False):
    		if move_obj:
    			for lines in move_obj:
    				lines.write({'quantity_done':vals.get('quantity_done')})

    	return res