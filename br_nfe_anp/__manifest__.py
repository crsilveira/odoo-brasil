# © 2021 Carlos Rodrigues Silveira <crsilveira@gmail.com>, ATSti
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Envio de NF-e combustivel',
    'description': 'Envio de NF-e',
    'version': '12.0.1.0.0',
    'category': 'account',
    'author': 'ATSti',
    'license': 'AGPL-3',
    'website': 'http://www.atsti.com.br',
    'contributors': [
        'Carlos Rodrigues Silveira <danimaribeiro@gmail.com>',
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
        'views/product_view.xml',
    ],
    'installable': True,
    'application': True,
}
