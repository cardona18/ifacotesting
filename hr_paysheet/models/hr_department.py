# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx) >
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_department_gi(models.Model):
    _inherit = 'hr.department'

    dtype = fields.Selection(
        string='Tipo',
        size=2,
        index=True,
        selection=[
            ('UN', 'Unidad'),
            ('DE', 'Departamento'),
            ('AR', 'Área')
        ]
    )

    @api.model_cr
    def init(self):

        self._cr.execute("""
            CREATE OR REPLACE FUNCTION find_department(department_id INTEGER) RETURNS VARCHAR
            language plpgsql
            AS $$
            DECLARE dep_type VARCHAR;
            DECLARE parent_dep INTEGER;
            DECLARE found_name VARCHAR;
            begin

                IF department_id IS NULL THEN
                    return NULL;
                END IF;

                SELECT "name", dtype, parent_id  INTO found_name, dep_type, parent_dep FROM hr_department WHERE id = department_id;

                IF dep_type = 'DE' THEN
                    return found_name;
                END IF;

                IF dep_type = 'UN' THEN
                    return found_name;
                END IF;

                RETURN find_department(parent_dep);

            end $$;

            CREATE OR REPLACE FUNCTION find_department_id(department_id INTEGER) RETURNS INTEGER
            language plpgsql
            AS $$
            DECLARE dep_type VARCHAR;
            DECLARE parent_dep INTEGER;
            DECLARE found_id INTEGER;
            begin

                IF department_id IS NULL THEN
                    return NULL;
                END IF;

                SELECT id, dtype, parent_id  INTO found_id, dep_type, parent_dep FROM hr_department WHERE id = department_id;

                IF dep_type = 'DE' THEN
                    return found_id;
                END IF;

                IF dep_type = 'UN' THEN
                    return found_id;
                END IF;

                RETURN find_department_id(parent_dep);

            end $$;
        """)