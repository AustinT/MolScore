import os
import json
import unittest
import subprocess

from molscore.tests import test_files
from molscore.tests.base_tests import BaseTests
from molscore.tests.mock_generator import MockGenerator
from molscore.scoring_functions import GlideDock, SminaDock, GninaDock, VinaDock, PLANTSDock, GOLDDock, ChemPLPGOLDDock, ASPGOLDDock, ChemScoreGOLDDock, GoldScoreGOLDDock, OEDock, rDock


class TestGlideDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('SCHRODINGER' in list(os.environ.keys())):
            raise unittest.SkipTest("Schrodinger installation not found")
        # Check license
        license_check = subprocess.run("$SCHRODINGER/licadmin STAT", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().split("\n")
        for line in license_check:
            if 'Error getting status:' in line:
                raise unittest.SkipTest(line)

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Prepare a grid file
        input_file = os.path.join(cls.output_directory, 'glide.in')
        with open(input_file, 'w') as f:
            f.write(f"GRIDFILE   {test_files['GlideDock_grid']}\n")
            f.write(f"PRECISION    SP\n")
        # Instantiate
        cls.obj = GlideDock
        cls.inst = GlideDock(
            prefix='test',
            glide_template=input_file,
            ligand_preparation='LigPrep',
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGlideDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestGlideDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('SCHRODINGER' in list(os.environ.keys())):
            raise unittest.SkipTest("Schrodinger installation not found")
        # Check license
        license_check = subprocess.run("$SCHRODINGER/licadmin STAT", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().split("\n")
        for line in license_check:
            if 'Error getting status:' in line:
                raise unittest.SkipTest(line)

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Prepare a grid file
        input_file = os.path.join(cls.output_directory, 'glide.in')
        with open(input_file, 'w') as f:
            f.write(f"GRIDFILE   {test_files['GlideDock_grid']}\n")
            f.write(f"PRECISION    SP\n")
        # Instantiate
        cls.obj = GlideDock
        cls.inst = GlideDock(
            prefix='test',
            glide_template=input_file,
            ligand_preparation='LigPrep',
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGlideDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestSminaDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = SminaDock
        cls.inst = SminaDock(
            prefix='test',
            receptor=test_files['DRD2_receptor_pdbqt'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            cpus=8,
            ligand_preparation='GypsumDL',
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nSminaDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestSminaDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = SminaDock
        cls.inst = SminaDock(
            prefix='test',
            receptor=test_files['DRD2_receptor_pdbqt'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            cpus=1,
            ligand_preparation='GypsumDL',
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nSminaDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestGninaDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if not ('gnina' in list(os.environ.keys())):
            raise unittest.SkipTest("Gnina installation not found, please install and add to os environment (e.g., export gnina=<path_to_exe>)")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = GninaDock
        cls.inst = GninaDock(
            prefix='test',
            receptor=test_files['DRD2_receptor_pdbqt'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            cpus=8,
            ligand_preparation='GypsumDL',
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=True)
        print(f"\nGninaDock Output:\n{json.dumps(cls.output, indent=2)}\n")
    
    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestGninaDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if not ('gnina' in list(os.environ.keys())):
            raise unittest.SkipTest("Gnina installation not found, please install and add to os environment (e.g., export gnina=<path_to_exe>)")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = GninaDock
        cls.inst = GninaDock(
            prefix='test',
            receptor=test_files['DRD2_receptor_pdbqt'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            cpus=1,
            ligand_preparation='GypsumDL',
            cluster=1
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=True)
        print(f"\nGninaDock Output:\n{json.dumps(cls.output, indent=2)}\n")
    
    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestVinaDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if not ('vina' in list(os.environ.keys())):
            raise unittest.SkipTest("Vina installation not found, please install and add to os environment (e.g., export vina=<path_to_exe>)")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = VinaDock
        cls.inst = VinaDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            file_preparation='mgltools',
            cpus=2,
            ligand_preparation='GypsumDL',
            dock_scoring='vina'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=False)
        print(f"\nVinaDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")
    

class TestVinaDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if not ('vina' in list(os.environ.keys())):
            raise unittest.SkipTest("Vina installation not found, please install and add to os environment (e.g., export vina=<path_to_exe>)")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = VinaDock
        cls.inst = VinaDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            file_preparation='mgltools',
            cpus=1,
            cluster=4,
            ligand_preparation='GypsumDL',
            dock_scoring='vina'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=False)
        print(f"\nVinaDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestPLANTSDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('PLANTS' in list(os.environ.keys())):
            raise unittest.SkipTest("PLANTS installation not found, please install and add to os environment (e.g., export PLANTS=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = PLANTSDock
        cls.inst = PLANTSDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nPLANTSDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestPLANTSDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('PLANTS' in list(os.environ.keys())):
            raise unittest.SkipTest("PLANTS installation not found, please install and add to os environment (e.g., export PLANTS=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = PLANTSDock
        cls.inst = PLANTSDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            cluster=4,
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nPLANTSDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestGOLDDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('GOLD' in list(os.environ.keys())):
            raise unittest.SkipTest("GOLD installation not found, please install and add gold_auto to os environment (e.g., export GOLD=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = GOLDDock
        cls.inst = GOLDDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGOLDDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestGOLDDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('GOLD' in list(os.environ.keys())):
            raise unittest.SkipTest("GOLD installation not found, please install and add gold_auto to os environment (e.g., export GOLD=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = GOLDDock
        cls.inst = GOLDDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            cluster=4,
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGOLDDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestChemPLPGOLDDock(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('GOLD' in list(os.environ.keys())):
            raise unittest.SkipTest("GOLD installation not found, please install and add gold_auto to os environment (e.g., export GOLD=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = ChemPLPGOLDDock
        cls.inst = ChemPLPGOLDDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            cluster=4,
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGOLDDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestASPGOLDDock(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('GOLD' in list(os.environ.keys())):
            raise unittest.SkipTest("GOLD installation not found, please install and add gold_auto to os environment (e.g., export GOLD=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = ASPGOLDDock
        cls.inst = ASPGOLDDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            cluster=4,
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGOLDDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestChemScoreGOLDDock(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('GOLD' in list(os.environ.keys())):
            raise unittest.SkipTest("GOLD installation not found, please install and add gold_auto to os environment (e.g., export GOLD=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = ChemScoreGOLDDock
        cls.inst = ChemScoreGOLDDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            cluster=4,
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGOLDDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestGoldScoreGOLDDock(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('GOLD' in list(os.environ.keys())):
            raise unittest.SkipTest("GOLD installation not found, please install and add gold_auto to os environment (e.g., export GOLD=<path_to_plants_exe>)")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = GoldScoreGOLDDock
        cls.inst = GoldScoreGOLDDock(
            prefix='test',
            receptor=test_files["DRD2_receptor"],
            ref_ligand=test_files["DRD2_ref_ligand"],
            cluster=4,
            ligand_preparation='GypsumDL'
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nGOLDDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestOEDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('OE_LICENSE' in list(os.environ.keys())):
            raise unittest.SkipTest("OpenEye license not found, please install license and export to \'OE_LICENSE\'")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = OEDock
        cls.inst = OEDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nOEDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestOEDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):

        # Check installation
        if not ('OE_LICENSE' in list(os.environ.keys())):
            raise unittest.SkipTest("OpenEye license not found, please install license and export to \'OE_LICENSE\'")

        # Clean the output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = OEDock
        cls.inst = OEDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nOEDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestrDockSerial(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if rDock.check_installation() is None:
            raise unittest.SkipTest("No rDock installation found, please ensure proper installation and executable paths")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = rDock
        cls.inst = rDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
            n_runs=2,
            cluster=1
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nrDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")
    

class TestrDockParallel(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if rDock.check_installation() is None:
            raise unittest.SkipTest("No rDock installation found, please ensure proper installation and executable paths")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = rDock
        cls.inst = rDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
            n_runs=2,
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names)
        print(f"\nrDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestrDockParallelPH4(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if rDock.check_installation() is None:
            raise unittest.SkipTest("No rDock installation found, please ensure proper installation and executable paths")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = rDock
        cls.inst = rDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
            dock_constraints=test_files['DRD2_rdock_constraint'],
            n_runs=2,
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + mg.sample(4)
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=True)
        print(f"\nrDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestrDockParallelScaff1(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if rDock.check_installation() is None:
            raise unittest.SkipTest("No rDock installation found, please ensure proper installation and executable paths")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = rDock
        cls.inst = rDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
            dock_substructure_constraints="Fc1cc2oncc2cc1",
            dock_substructure_max_trans=0.0,
            dock_substructure_max_rot=0.0,
            n_runs=5,
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + ["Fc1cc2onc(CC)c2cc1", "Fc1cc2onc(CCC(=O))c2cc1", "Fc1cc2onc(C(=O)N)c2cc1", "Fc1cc2onc(CCCCC)c2cc1"]
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=True)
        print(f"\nrDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


class TestrDockParallelScaff2(BaseTests.TestScoringFunction):
    # Only set up once per class, otherwise too long
    @classmethod
    def setUpClass(cls):
        # Check installation
        if rDock.check_installation() is None:
            raise unittest.SkipTest("No rDock installation found, please ensure proper installation and executable paths")
        # Clean output directory
        os.makedirs(cls.output_directory, exist_ok=True)
        # Instantiate
        cls.obj = rDock
        cls.inst = rDock(
            prefix='test',
            receptor=test_files['DRD2_receptor'],
            ref_ligand=test_files['DRD2_ref_ligand'],
            ligand_preparation='GypsumDL',
            dock_substructure_constraints="Fc1cc2oncc2cc1.Cc1nc2CCCCn2c(=O)c1",
            dock_substructure_max_trans=0.0,
            dock_substructure_max_rot=0.0,
            n_runs=5,
            cluster=4
        )
        # Call
        mg = MockGenerator(seed_no=123)
        cls.input = [test_files['DRD2_ref_smiles']] + ["Cc1nc2CCCCn2c(=O)c1CCCCCc1noc2cc(F)ccc21", "Cc1nc2CCCCn2c(=O)c1CCCCc1noc2cc(F)ccc21", "Cc1nc2CCCCn2c(=O)c1CCCCCCc1noc2cc(F)ccc21", "Cc1nc2CCCCn2c(=O)c1CCOCCc1noc2cc(F)ccc21"]
        file_names = [str(i) for i in range(len(cls.input))]
        cls.output = cls.inst(smiles=cls.input, directory=cls.output_directory, file_names=file_names, cleanup=True)
        print(f"\nrDock Output:\n{json.dumps(cls.output, indent=2)}\n")

    @classmethod
    def tearDownClass(cls):
        cls.inst.client.close()
        cls.inst.client.cluster.close()
        os.system(f"rm -r {os.path.join(cls.output_directory, '*')}")


if __name__ == '__main__':
    unittest.main()