#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2018 D. de Vries

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This file contains the definition of the Sellar with design competences test cases.
"""
from __future__ import absolute_import, division, print_function

import logging
import os
import unittest

from openlego.core.problem import LEGOProblem
import openlego.test_suite.test_examples.sellar_competences.kb as kb

# Settings for logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDAO definitions that can be wrapped around the problem
mdao_definitions = ['unconverged-MDA-J',  # 0
                    'unconverged-MDA-GS',  # 1
                    'converged-DOE-GS',  # 2
                    'converged-DOE-J',  # 3
                    'converged-MDA-J',  # 4
                    'converged-MDA-GS',  # 5
                    'MDF-GS',  # 6
                    'MDF-J',  # 7
                    'IDF',  # 8
                    'CO']  # 9


def get_loop_items(analyze_mdao_definitions):
    if isinstance(analyze_mdao_definitions, int):
        mdao_defs_loop = [mdao_definitions[analyze_mdao_definitions]]
    elif isinstance(analyze_mdao_definitions, list):
        mdao_defs_loop = [mdao_definitions[i] for i in analyze_mdao_definitions]
    elif isinstance(analyze_mdao_definitions, str):
        if analyze_mdao_definitions == 'all':
            mdao_defs_loop = mdao_definitions
        else:
            raise ValueError(
                'String value {} is not allowed for analyze_mdao_definitions.'.format(analyze_mdao_definitions))
    else:
        raise IOError(
            'Invalid input {} provided of type {}.'.format(analyze_mdao_definitions, type(analyze_mdao_definitions)))
    return mdao_defs_loop


def run_openlego(analyze_mdao_definitions):
    # Check and analyze inputs
    mdao_defs_loop = get_loop_items(analyze_mdao_definitions)

    for mdao_def in mdao_defs_loop:
        print('\n-----------------------------------------------')
        print('Running the OpenLEGO of Mdao_{}.xml...'.format(mdao_def))
        print('------------------------------------------------')
        """Solve the Sellar problem using the given CMDOWS file."""
        # 1. Create Problem
        prob = LEGOProblem(
            cmdows_path=os.path.join('cmdows_files', 'Mdao_{}.xml'.format(mdao_def)),  # CMDOWS file
            kb_path='kb',
            data_folder='',  # Output directory
            base_xml_file='sellar-output.xml')  # Output file
        # prob.driver.options['debug_print'] = ['desvars', 'nl_cons', 'ln_cons', 'objs']  # Set printing of debug info
        prob.set_solver_print(0)  # Set printing of solver information

        # 2. Initialize the Problem and export N2 chart
        prob.store_model_view(open_in_browser=False)
        prob.initialize_from_xml('sellar-input.xml')

        # 3. Create and attach some Recorders (Optional)
        """
        from openlego.recorders import NormalizedDesignVarPlotter, ConstraintsPlotter, SimpleObjectivePlotter

        desvar_plotter = NormalizedDesignVarPlotter()                   # Create a plotter for the design variables
        desvar_plotter.options['save_on_close'] = True                  # Should this plot be saved automatically?
        desvar_plotter.save_settings['path'] = 'desvar.png'             # Set the filename of the image file

        convar_plotter = ConstraintsPlotter()                           # Create a plotter for the constraints
        convar_plotter.options['save_on_close'] = True                  # Should this plot be saved automatically?
        convar_plotter.save_settings['path'] = 'convar.png'             # Set the filename of the image file

        objvar_plotter = SimpleObjectivePlotter()                       # Create a plotter for the objective
        objvar_plotter.options['save_on_close'] = True                  # Should this plot be saved automatically?
        objvar_plotter.save_settings['path'] = 'objvar.png'             # Set the filename of the image file

        prob.driver.add_recorder(desvar_plotter)                             # Attach the design variable plotter
        prob.driver.add_recorder(convar_plotter)                             # Attach the constraint variable plotter
        prob.driver.add_recorder(objvar_plotter)                             # Attach the objective variable plotter
        """

        # 4. Run the Problem
        prob.run_driver()  # Run the driver (optimization, DOE, or convergence)

        # 5. Read out the case reader
        prob.print_results()

        # 6. Collect test results
        x = [prob['/dataSchema/geometry/x1']]
        y = [prob['/dataSchema/analyses/y1'], prob['/dataSchema/analyses/y2']]
        z = [prob['/dataSchema/geometry/z1'], prob['/dataSchema/geometry/z2']]
        f = [prob['/dataSchema/analyses/f']]
        g = [prob['/dataSchema/analyses/g1'], prob['/dataSchema/analyses/g2']]

        # 8. Cleanup and invalidate the Problem afterwards
        prob.invalidate()

        return x, y, z, f, g


class TestSellarCompetences(unittest.TestCase):

    def __call__(self, *args, **kwargs):
        kb.deploy()
        super(TestSellarCompetences, self).__call__(*args, **kwargs)

    def assertion(self, x, y, z, f, g):
        self.assertAlmostEqual(x[0], 0.00, 2)
        self.assertAlmostEqual(y[0], 3.16, 2)
        self.assertAlmostEqual(y[1], 3.76, 2)
        self.assertAlmostEqual(z[0], 1.98, 2)
        self.assertAlmostEqual(z[1], 0.00, 2)
        self.assertAlmostEqual(f[0], 3.18, 2)
        self.assertAlmostEqual(g[0], 0.00, 2)
        self.assertAlmostEqual(g[1], 0.84, 2)

    def test_unc_mda_gs(self):
        """Test run the Sellar system using a sequential tool execution."""
        run_openlego(0)

    def test_unc_mda_j(self):
        """Test run the Sellar system using a parallel tool execution."""
        run_openlego(1)

    def test_doe_gs(self):
        """Solve the Sellar system using a DOE architecture and a Gauss-Seidel convergence scheme."""
        run_openlego(2)

    def test_doe_j(self):
        """Solve the Sellar system using a DOE architecture and a Jacobi convergence scheme."""
        run_openlego(3)

    def test_mda_j(self):
        """Solve the Sellar system using a Jacobi convergence scheme."""
        run_openlego(4)

    def test_mda_gs(self):
        """Solve the Sellar system using Gauss-Seidel convergence scheme."""
        run_openlego(5)

    def test_mdf_gs(self):
        """Solve the Sellar problem using the MDF architecture and a Gauss-Seidel convergence scheme."""
        self.assertion(*run_openlego(6))

    def test_mdf_j(self):
        """Solve the Sellar problem using the MDF architecture and a Jacobi converger."""
        self.assertion(*run_openlego(7))

    def test_idf(self):
        """Solve the Sellar problem using the IDF architecture."""
        self.assertion(*run_openlego(8))

    def __del__(self):
        kb.clean()
        # TODO: Add function to remove output files also...


if __name__ == '__main__':
    unittest.main()
