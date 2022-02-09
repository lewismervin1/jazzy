"""Test cases for the free energy contributions."""
import numpy as np

from jazzy.core import any_hydrogen_neighbors
from jazzy.core import calculate_delta_apolar
from jazzy.core import calculate_delta_interaction
from jazzy.core import calculate_delta_polar
from jazzy.core import calculate_polar_strength_map
from jazzy.core import get_charges_from_kallisto_molecule
from jazzy.core import get_covalent_atom_idx
from jazzy.core import interaction_strength
from jazzy.core import kallisto_molecule_from_rdkit_molecule
from jazzy.core import rdkit_molecule_from_smiles


def test_calculate_delta_apolar():
    """Correctly calculates apolar free energy contributions."""
    want = [
        5.180897348132029,
        6.745466587759121,
        3.174140716422391,
        -2.2701402554482835,
    ]
    smiles = ["CC", "CCC", "C=C", "C#C"]
    # parameter: g0, gs, gr, gpi1, gpi2
    parameter = [0.95, 0.066, -4.27, -1.74, -1.00]
    for idx, smile in enumerate(smiles):
        rdkit_molecule = rdkit_molecule_from_smiles(
            smiles=smile, minimisation_method="MMFF94"
        )
        kallisto_molecule = kallisto_molecule_from_rdkit_molecule(
            rdkit_molecule=rdkit_molecule
        )
        eeq = get_charges_from_kallisto_molecule(kallisto_molecule, 0)
        aan = get_covalent_atom_idx(rdkit_molecule)
        mol_map = calculate_polar_strength_map(
            rdkit_molecule, kallisto_molecule, aan, eeq
        )
        got = calculate_delta_apolar(
            rdkit_molecule=rdkit_molecule,
            mol_map=mol_map,
            g0=parameter[0],
            gs=parameter[1],
            gr=parameter[2],
            gpi1=parameter[3],
            gpi2=parameter[4],
        )
        assert np.isclose(got, want[idx])


def test_calculate_delta_polar():
    """Correctly calculates polar free energy contributions."""
    want = [
        -0.567024,
        -0.811146,
        -1.120395,
        -1.452418,
        -1.946007,
        -20.641093,
        -24.704935,
        -4.899230,
        -44.577632,
    ]
    smiles = ["CC", "CCC", "CCCC", "C=C", "C#C", "COC", "CCO", "C(Cl)#C", "CNCCO"]
    # parameter: gd, ga, expd, expa
    parameter = [-1.659, -8.43, 0.60, 0.37]
    for idx, smile in enumerate(smiles):
        rdkit_molecule = rdkit_molecule_from_smiles(
            smiles=smile, minimisation_method="MMFF94"
        )
        kallisto_molecule = kallisto_molecule_from_rdkit_molecule(
            rdkit_molecule=rdkit_molecule
        )
        eeq = get_charges_from_kallisto_molecule(kallisto_molecule, 0)
        aan = get_covalent_atom_idx(rdkit_molecule)
        mol_map = calculate_polar_strength_map(
            rdkit_molecule, kallisto_molecule, aan, eeq
        )
        got = calculate_delta_polar(
            mol_map=mol_map,
            atoms_and_nbrs=aan,
            gd=parameter[0],
            ga=parameter[1],
            expd=parameter[2],
            expa=parameter[3],
        )
        assert np.isclose(got, want[idx], 3)


def test_correct_interaction_strength():
    """Correctly calculates interaction strength."""
    want = 4
    mol_map = {0: {"sa": 2, "num_lp": 2}}
    acceptor_exp = 1.0
    atom_idx = 0
    result = interaction_strength(atom_idx, mol_map, acceptor_exp)
    assert result == want


def test_any_hydrogen():
    """Correctly checks for hydrogen partner."""
    # no Hydrogen partners
    smile = "C(Cl)#CCl"
    rdkit_molecule = rdkit_molecule_from_smiles(
        smiles=smile, minimisation_method="MMFF94"
    )
    for _, atom in enumerate(rdkit_molecule.GetAtoms()):
        assert any_hydrogen_neighbors(atom) is False
    # one Carbon atom has one Hydrogen partner
    smile = "C(Cl)#C"
    rdkit_molecule = rdkit_molecule_from_smiles(
        smiles=smile, minimisation_method="MMFF94"
    )
    atoms = rdkit_molecule.GetAtoms()
    assert any_hydrogen_neighbors(atoms[0]) is False
    assert any_hydrogen_neighbors(atoms[1]) is False
    assert any_hydrogen_neighbors(atoms[2]) is True


def test_alpha_neighbors_interactions():
    """Correctly calculates alpha neighbor contributions."""
    smile = "FF"
    rdkit_molecule = rdkit_molecule_from_smiles(smiles=smile, minimisation_method=None)
    aan = get_covalent_atom_idx(rdkit_molecule)
    # fake mol_map
    want = 0.0
    mol_map = {0: {"sa": 1.0, "num_lp": 0}, 1: {"sa": 1.0, "num_lp": 0}}
    result = calculate_delta_interaction(rdkit_molecule, mol_map, aan, 1.0, 1.0)
    assert result == want
    # fake another mol_map
    want = 2
    mol_map = {0: {"sa": 1.0, "num_lp": 1}, 1: {"sa": 1.0, "num_lp": 1}}
    result = calculate_delta_interaction(rdkit_molecule, mol_map, aan, 1.0, 1.0)
    assert result == want


def test_gamma_neighbors_interactions():
    """Correctly calculates gamma neighbor contributions."""
    smile = "C#CN(O)C"
    # parameter: gi, expa
    parameter = [2.35, 0.37]
    rdkit_molecule = rdkit_molecule_from_smiles(smiles=smile, minimisation_method=None)
    kallisto_molecule = kallisto_molecule_from_rdkit_molecule(
        rdkit_molecule=rdkit_molecule
    )
    eeq = get_charges_from_kallisto_molecule(kallisto_molecule, 0)
    aan = get_covalent_atom_idx(rdkit_molecule)
    mol_map = calculate_polar_strength_map(rdkit_molecule, kallisto_molecule, aan, eeq)
    want = 0.0
    result = calculate_delta_interaction(
        rdkit_molecule, mol_map, aan, parameter[0], parameter[1]
    )
    assert result == want
    smile = "C#CN(OC)C(F)(F)F"
    rdkit_molecule = rdkit_molecule_from_smiles(smiles=smile, minimisation_method=None)
    kallisto_molecule = kallisto_molecule_from_rdkit_molecule(
        rdkit_molecule=rdkit_molecule
    )
    eeq = get_charges_from_kallisto_molecule(kallisto_molecule, 0)
    aan = get_covalent_atom_idx(rdkit_molecule)
    mol_map = calculate_polar_strength_map(rdkit_molecule, kallisto_molecule, aan, eeq)
    want = 25.578745
    result = calculate_delta_interaction(
        rdkit_molecule, mol_map, aan, parameter[0], parameter[1]
    )
    assert np.isclose(result, want, 3)
