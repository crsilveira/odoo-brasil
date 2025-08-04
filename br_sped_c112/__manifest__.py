# © 2021 Carlos Rodrigues Silveira <crsilveira@gmail.com>, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Guia GNRE',
    'description': 'Arquivo C112 do sped fiscal',
    'version': '12.0.1.0.0',
    'category': 'account',
    'author': 'ATSti',
    'license': 'AGPL-3',
    'website': 'http://www.atsti.com.br',
    'contributors': [
        'Carlos Rodrigues Silveira <crsilveira@gmail.com>',
    ],
    'depends': [
        'br_nfe',
    ],
    'external_dependencies': {
        'python': [
            'pytrustnfe', 'pytrustnfe.nfe',
            'pytrustnfe.certificado', 'pytrustnfe.utils'
        ],
    },
    'data': [
        'views/invoice_eletronic.xml',
    ],
    'installable': True,
    'application': True,
}
