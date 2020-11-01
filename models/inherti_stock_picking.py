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

    # TO-DO: Delete this method after use
    # Para restar elementos entre listas
    def Diff(self, li1, li2):
    	return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))


    def stock_quant_update(self):
    	move_lines_products = []
    	out_move_lines_products = []
    	new_list = []
    	for move_product in self.move_lines:
    		move_lines_products.append(move_product.product_id.id)
    	for out_move_product in self.out_move_lines:
    		out_move_lines_products.append(out_move_product.product_id.id)
    	new_list = self.Diff(move_lines_products, out_move_lines_products)
    	if new_list:
    		for id_product in new_list:
    			quant = self.env['stock.quant'].search([('product_id', '=', id_product),('location_id','=',15)], limit=1)
    			out_cpy_obj = self.env['copy.stock.move'].search([('product_id', '=', id_product),('picking_id','=',self.id)], limit=1)
    			result = abs(quant.quantity) - out_cpy_obj.quantity_done
    			quant.update({'quantity': result})



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
    show_details_visible = fields.Boolean('Details Visible', compute='_compute_show_details_visible')
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking', readonly=True)
    move_line_ids = fields.One2many('stock.move.line', 'move_id')
    origin_returned_move_id = fields.Many2one('stock.move', 'Origin return move', copy=False, help='Move that created the return move')
    returned_move_ids = fields.One2many('stock.move', 'origin_returned_move_id', 'All returned moves', help='Optional: all returned moves created from this move')

    @api.depends('product_id', 'has_tracking', 'move_line_ids', 'location_id', 'location_dest_id')
    def _compute_show_details_visible(self):
        """ According to this field, the button that calls `action_show_details` will be displayed
        to work on a move from its picking form view, or not.
        """
        for move in self:
            if not move.product_id:
                move.show_details_visible = False
                continue

            multi_locations_enabled = False
            if self.user_has_groups('stock.group_stock_multi_locations'):
                multi_locations_enabled = move.location_id.child_ids or move.location_dest_id.child_ids
            has_package = move.move_line_ids.mapped('package_id') | move.move_line_ids.mapped('result_package_id')
            consignment_enabled = self.user_has_groups('stock.group_tracking_owner')
            if move.picking_id.picking_type_id.show_operations is False\
                    and (move.state != 'draft' or (not self._context.get('planned_picking') and move.state == 'draft'))\
                    and (multi_locations_enabled or move.has_tracking != 'none' or len(move.move_line_ids) > 1 or has_package or consignment_enabled):
                move.show_details_visible = True
            else:
                move.show_details_visible = False

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

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        move_obj = self.env['stock.move'].search([('picking_id','=',self.picking_id.id),('product_id','=',self.product_id.id)], limit=1)
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.location_id.child_ids,
                show_destination_location=self.location_dest_id.child_ids,
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done'
            ),
        }


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
    show_details_visible = fields.Boolean('Details Visible', compute='_compute_show_details_visible')
    has_tracking = fields.Selection(related='product_id.tracking', string='Product with Tracking', readonly=True)
    move_line_ids = fields.One2many('stock.move.line', 'move_id')
    origin_returned_move_id = fields.Many2one('stock.move', 'Origin return move', copy=False, help='Move that created the return move')
    returned_move_ids = fields.One2many('stock.move', 'origin_returned_move_id', 'All returned moves', help='Optional: all returned moves created from this move')

    @api.depends('product_id', 'has_tracking', 'move_line_ids', 'location_id', 'location_dest_id')
    def _compute_show_details_visible(self):
        """ According to this field, the button that calls `action_show_details` will be displayed
        to work on a move from its picking form view, or not.
        """
        for move in self:
            if not move.product_id:
                move.show_details_visible = False
                continue

            multi_locations_enabled = False
            if self.user_has_groups('stock.group_stock_multi_locations'):
                multi_locations_enabled = move.location_id.child_ids or move.location_dest_id.child_ids
            has_package = move.move_line_ids.mapped('package_id') | move.move_line_ids.mapped('result_package_id')
            consignment_enabled = self.user_has_groups('stock.group_tracking_owner')
            if move.picking_id.picking_type_id.show_operations is False\
                    and (move.state != 'draft' or (not self._context.get('planned_picking') and move.state == 'draft'))\
                    and (multi_locations_enabled or move.has_tracking != 'none' or len(move.move_line_ids) > 1 or has_package or consignment_enabled):
                move.show_details_visible = True
            else:
                move.show_details_visible = False

    @api.multi
    def write(self, vals):
    	res = super(CopyStockMove2, self).write(vals)
    	move_obj = self.env['stock.move'].search([('picking_id','=',self.picking_id.id),('product_id','=',self.product_id.id)])

    	if vals.get('quantity_done', False):
    		if move_obj:
    			for lines in move_obj:
    				lines.write({'quantity_done':vals.get('quantity_done')})

    	return res

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        move_obj = self.env['stock.move'].search([('picking_id','=',self.picking_id.id),('product_id','=',self.product_id.id)], limit=1)

        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': move_obj.id,
            'context': dict(
                move_obj.env.context,
                show_lots_m2o=move_obj.has_tracking != 'none' and (picking_type_id.use_existing_lots or move_obj.state == 'done' or move_obj.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=move_obj.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and move_obj.state != 'done' and not move_obj.origin_returned_move_id.id,
                show_source_location=move_obj.location_id.child_ids,
                show_destination_location=move_obj.location_dest_id.child_ids,
                show_package=not move_obj.location_id.usage == 'supplier',
                show_reserved_quantity=move_obj.state != 'done'
            ),
        }

class InheritStockMoveLine(models.Model):
    _inherit = "stock.move.line"

    invima = fields.Char('Registro Invima')
    expiration_date = fields.Datetime('Fecha de Vencimiento')