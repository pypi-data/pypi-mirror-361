# Copyright 2025 Som IT Cooperatiu SCCL - Nicolás Ramos <nicolas.ramos@somit.coop>
{
    'name': 'Auto_save_extend',
    'version': '16.0.1.0.0',
    'summary': """ Mejora el comportamiento de auto-guardado de Odoo con mejores diálogos y opciones """,
    'author': 'Som IT Cooperatiu SCCL',
    'website': 'https://somit.coop',
    'category': 'Technical Settings/API',
    'depends': ['base', 'web'],
    'conflicts': ['auto_save_restrict'],  # No puede coexistir con el módulo original
    'data': [

    ],
    'assets': {
              'web.assets_backend': [
                  'auto_save_extend/static/src/js/custom_confirmation_dialog.js',
                  'auto_save_extend/static/src/js/form_controller.js',
                  'auto_save_extend/static/src/js/list_controller.js',
                  'auto_save_extend/static/src/xml/custom_confirmation_dialog.xml',
              ],
          },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'maintainers': ['nicolasramos'],
    'development_status': 'Beta',
}
