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

STATE = {'edit': [('readonly', False)]}


class InvoiceEletronic(models.Model):
    _inherit = 'invoice.eletronic'

    @api.multi
    def _prepare_eletronic_invoice_item(self, item, invoice):
        res = super(InvoiceEletronic, self)._prepare_eletronic_invoice_item(
            item, invoice)
        if self.model not in ('55', '65'):
            return res
        #import pudb;pu.db
        if item.product_id.prodanp:
            comb = []
            codif = ''
            qtemp = ''
            if item.product_id.qtemp:
                qtemp = item.product_id.qtemp
            if item.product_id.codif:
                codif = item.product_id.codif
            comb.append({
                'cProdANP':item.product_id.prodanp,
                'descANP':item.product_id.descanp,
                'UFCons':item.product_id.ufcons,
                'pGLP':item.product_id.pglp,
                'pGNn':item.product_id.pgnn,
                'pGNi':item.product_id.pgni,
                'vPart': "%.02f" % item.product_id.vpart,
                'CODIF':codif,
                'qtemp':qtemp,
            })
            res["prod"]["comb"] = comb
        return res
