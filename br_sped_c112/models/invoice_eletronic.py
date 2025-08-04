# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import io
import base64
import logging
import hashlib
from lxml import etree
from datetime import datetime
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

try:
    from pytrustnfe.nfe import autorizar_nfe
    from pytrustnfe.nfe import xml_autorizar_nfe
    from pytrustnfe.nfe import retorno_autorizar_nfe
    from pytrustnfe.nfe import recepcao_evento_cancelamento
    from pytrustnfe.nfe import consultar_protocolo_nfe
    from pytrustnfe.certificado import Certificado
    from pytrustnfe.utils import ChaveNFe, gerar_chave, gerar_nfeproc, \
        gerar_nfeproc_cancel
    from pytrustnfe.nfe.danfe import danfe
    from pytrustnfe.xml.validate import valida_nfe
    from pytrustnfe.urls import url_qrcode, url_qrcode_exibicao
except ImportError:
    _logger.error('Cannot import pytrustnfe', exc_info=True)


class InvoiceEletronic(models.Model):
    _inherit = 'invoice.eletronic'

    cod_da = fields.Selection(
        selection=[
            ('0', 'DEA'),
            ('1', 'GNRE'),
            ],
        string="Código Documento 1"
    )
    uf = fields.Char(string="UF 1" )
    num_da = fields.Char(string="Número documento 1")
    cod_aut = fields.Char(string="Código Autenticação 1")
    vl_da = fields.Monetary(string="Valor documento 1")
    dt_vcto = fields.Date(string="Data vencimento 1")
    dt_pgto = fields.Date(string="Data pagamento 1")
    cod_da2 = fields.Selection(
        selection=[
            ('0', 'DEA'),
            ('1', 'GNRE'),
            ],
        string="Código Documento 2"
    )
    uf_da2 = fields.Char(string="UF 2")
    num_da2 = fields.Char(string="Número documento 2")
    cod_aut2 = fields.Char(string="Código Autenticação 2")
    vl_da2 = fields.Monetary(string="Valor documento 2")
    dt_vcto2 = fields.Date(string="Data vencimento 2")
    dt_pgto2 = fields.Date(string="Data pagamento 2")
