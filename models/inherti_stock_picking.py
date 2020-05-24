# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from odoo import models, fields, api, _


class InheritStockPicking(models.Model):
    _inherit = "stock.picking"

    
    @api.multi
    def cost_calculation(self):
        for moves in self.move_lines:
        	qty = 1
        	if moves.quantity_done > 0:
        		moves.product_cost = moves.product_tmpl_id.standard_price * moves.quantity_done


class InheritStockMove(models.Model):
    _inherit = "stock.move"

    product_cost = fields.Float(string="Costo")