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


class InheritSaleOrderEv(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def action_confirm(self):
        res = super(InheritSaleOrderEv, self).action_confirm()
        bom_dir = {}
        move_new_name = ''
        pick_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
        for move_to_delete in pick_obj:
            for moves in move_to_delete.move_lines:
                moves.state = 'draft'
                move_new_name = moves.name
            move_to_delete.move_lines.unlink()

            bom_obj = self.env['mrp.bom'].search([('id', '=', 14)])
            for bom_line in bom_obj.bom_line_ids:
                bom_dir = {
                    'name': bom_obj.product_tmpl_id.name,
                    'product_id': bom_line.product_id.id,
                    'product_uom_qty': bom_line.product_qty,
                    'product_uom': bom_line.product_uom_id.id,
                    'state': 'assigned',
                    'date_expected': move_to_delete.date,
                    'date': move_to_delete.date,
                    'partner_id': self.partner_id.id,
                    'picking_id': move_to_delete.id,
                    'origin': self.name,
                    'reference': move_to_delete.name,
                    'sale_line_id': self.id,
                    'location_id': move_to_delete.location_id.id,
                    'location_dest_id': move_to_delete.location_dest_id.id,
                    'picking_type_id': move_to_delete.picking_type_id.id,
                }
                self.env['stock.move'].create(bom_dir)
        self.picking_ids = [(6,0,pick_obj.ids)]

        return res