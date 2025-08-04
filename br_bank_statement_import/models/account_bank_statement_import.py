# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import io
import uuid
import logging
import unidecode
import datetime
import random
from datetime import date

from odoo import fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from ofxparse import OfxParser
except ImportError:
    _logger.error('Cannot import ofxparse dependencies.', exc_info=True)


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    force_format = fields.Boolean(string=u'Forçar formato', default=False)
    file_format = fields.Selection([('ofx', 'Extrato OFX')],
                                   string="Formato do Arquivo",
                                   default='ofx')
    unique_transaction = fields.Boolean(
        string='Gerar ID Único', default=False,
        help="Apenas marque esta opção em caso do arquivo OFX conter \
        registros duplicados (campo FITID), alguns bancos exportam \
        o arquivo OFX com dois registros diferentes com mesmo número \
        de transação (o que não deveria). O comportamento padrão do Odoo \
        caso exista duplicados é ignorar os duplicados (mesmo FITID) \
        e se forem todos duplicados dizer que o arquivo já foi importado. \
        Se alguma dessas situações estiver ocorrendo ao importar o arquivo \
        talvez você precise marcar esta opção.")
    force_journal_account = fields.Boolean(string=u"Forçar conta bancária?")
    journal_id = fields.Many2one('account.journal', string=u"Conta Bancária",
                                 domain=[('type', '=', 'bank')])

    def _parse_file(self, data_file):
        try:
            data_file = unidecode.unidecode(data_file.decode('cp1252'))
        except:
            data_file = unidecode.unidecode(data_file.decode('utf-8')) 
        data_file = io.BytesIO(data_file.encode('utf-8'))
        if self.force_format:
            self._check_ofx(data_file, raise_error=True)
            return self._parse_ofx(data_file)
        else:
            if self._check_ofx(data_file):
                return self._parse_ofx(data_file)
            return super(AccountBankStatementImport, self)._parse_file(
                data_file)

    def _check_ofx(self, data_file, raise_error=False):
        try:
            #OfxParser.parse(io.BytesIO(data_file))
            OfxParser.parse(data_file)
            return True
        except Exception as e:
            if raise_error:
                raise UserError(_("Arquivo formato inválido:\n%s") % str(e))
            return False

    def _parse_ofx(self, data_file):
        #ofx = OfxParser.parse(io.BytesIO(data_file))
        ofx = OfxParser.parse(data_file)
        transacoes = []
        total = 0.0
        conta_fornecedor = self.env['account.account'].search([
            ('name', '=', 'Fornecedores (a Pagar)'),
            ('user_type_id', '=', 'A Pagar'),
        ], limit=1).id
        conta_cliente = self.env['account.account'].search([
            ('name', '=', 'Clientes (a receber)'),
            ('user_type_id', '=', 'A Receber'),
        ], limit=1).id
        inicio = date(2018, 1, 1)
        fim = date.today()
        index = (fim-inicio).days
        index = int(str(random.randrange(1,999)) + str(index) + '001')
        #num_trans = 0
        #'unique_import_id': num_transacao,
        for account in ofx.accounts:
            for transacao in account.statement.transactions:
                nosso_numero = transacao.memo[-11:]
                # se e banco inter entao este e o nosso numero
                ord = self.env['account.move.line'].search([
                    ('nosso_numero','=',nosso_numero)
                ])
                ref = transacao.id
                invoice = ''
                partner_id = ''
                if ord:
                    ref = ord.invoice_id.number
                    invoice = ord.invoice_id.account_id.id
                    partner_id = ord.partner_id.id
                else:
                    data_a = transacao.date - datetime.timedelta(days=10)
                    data_b = transacao.date + datetime.timedelta(days=10)
                    if transacao.amount > 0.0 and conta_cliente:                    
                        partner_id = self.env['account.move.line'].search([
                            ('debit', '=', float(transacao.amount)),
                            ('account_id', '=', conta_cliente),
                            ('reconciled', '=', False),
                            ('date_maturity', '>', data_a),
                            ('date_maturity', '<', data_b),
                        ])
                    else:
                        if conta_fornecedor:
                            partner_id = self.env['account.move.line'].search([
                                ('credit', '=', float(transacao.amount)*(-1)),
                                ('account_id', '=', conta_fornecedor),
                                ('reconciled', '=', False),
                                ('date_maturity', '>', data_a),
                                ('date_maturity', '<', data_b),
                            ])
                    if partner_id:
                        if len(partner_id) > 1:
                            partner_id = ''
                        else:
                            partner_id = partner_id.partner_id.id

                transacoes.append({
                    'date': transacao.date,
                    'name': transacao.payee + (
                        transacao.memo and ': ' + transacao.memo or ''),
                    'ref': ref,
                    'amount': transacao.amount,
                    'unique_import_id': "%s-%s" % (transacao.id, index),
                    'sequence': len(transacoes) + 1,
                    'partner_id': partner_id or '',
                    'account_id': invoice,
                })
                index += 1
                total += float(transacao.amount)
        # Really? Still using Brazilian Cruzeiros :/
        if ofx.account.statement.currency.upper() == "BRC":
            ofx.account.statement.currency = "BRL"

        journal = self.journal_id
        if not self.force_journal_account:
            dummy, journal = self._find_additional_data(
                ofx.account.statement.currency, ofx.account.number)

        name = u"%s - %s até %s" % (
            journal.name,
            ofx.account.statement.start_date.strftime('%d/%m/%Y'),
            ofx.account.statement.end_date.strftime('%d/%m/%Y')
        )
        total = round(total, 2)
        vals_bank_statement = {
            'name': name,
            'transactions': transacoes,
            'balance_start': round(
                float(ofx.account.statement.balance) - total, 2),
            'balance_end_real': round(ofx.account.statement.balance, 2),
        }

        account_number = ofx.account.number
        if self.force_journal_account:
            account_number = self.journal_id.bank_acc_number
        return (
            ofx.account.statement.currency,
            account_number,
            [vals_bank_statement]
        )
