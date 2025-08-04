# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    prodanp = fields.Char(string="Código ANP")
    descanp = fields.Char(string="Desc. ANP")
    ufcons = fields.Char(string="UF cons.")
    pglp = fields.Char(string="GLP %")
    pgnn = fields.Char(string="Gás nacional %")
    pgni = fields.Char(string="Gás importado %")
    vpart = fields.Monetary(string="Valor partida")
    codif = fields.Char(string="Código autorização")
    qtemp = fields.Char(string="Quant. combustível")
