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


class InheritPurchaseOrderEv(models.Model):
    _inherit = "purchase.order"
    
    @api.multi
    def button_confirm(self):
        res = super(InheritPurchaseOrderEv, self).button_confirm()
        pick_obj = self.env['stock.picking'].search([('origin', '=', self.name)])
        in_move_obj = self.env['copy.stock.move2'].search([('origin', '=', self.name)])
        for move_in in in_move_obj:
            move_in.write({'picking_id': pick_obj.id})

        return res