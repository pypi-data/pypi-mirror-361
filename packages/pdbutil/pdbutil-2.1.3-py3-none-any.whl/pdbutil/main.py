def pdb_rmsd():
    """
    Command line interface for calculating RMSD.

    This function calculates the Root Mean Square Deviation (RMSD) between two sets of PDB files.

    Args:
        pdb1 (List[str]): First group of PDB files.
        pdb2 (Optional[List[str]]): Second group of PDB files. If not provided, the first group is used.
        csv (bool): Flag to output results in CSV format.

    Raises:
        ValueError: If the number of CA atoms in the PDB files is inconsistent.

    Returns:
        None
    """
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='Calculate RMSD between two PDB files.', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-1', '--pdb1', type=str, nargs='+', help='First group of PDB files.')
    parser.add_argument('-2', '--pdb2', type=str, nargs='+', help='Second group of PDB files.')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format.')
    args = parser.parse_args()

    import numpy as np
    from pdbutil.pdb_io import read_pdb    
    from pdbutil.rmsd import calc_rmsd
    from itertools import product

    xyz1, file1 = [read_pdb(f, sidechain_warnings=False)['xyz_ca'] for f in args.pdb1], args.pdb1

    if not np.all(np.array([len(x) == len(xyz1[0]) for x in xyz1], dtype=bool)):
        raise ValueError("All input PDB files must have the same number of CA atoms.")

    xyz2, file2 = ([read_pdb(f, sidechain_warnings=False)['xyz_ca'] for f in args.pdb2], args.pdb2) if args.pdb2 is not None else (xyz1, file1)

    if not np.all(np.array([len(x) == len(xyz1[0]) for x in xyz2], dtype=bool)):
        raise ValueError("All input PDB files must have the same number of CA atoms.")

    rmsd_mat = calc_rmsd(np.stack(xyz1, axis=0), np.stack(xyz2, axis=0))
    
    if args.csv:
        print("RMSD,File1,File2")
    else:
        print(f" {'RMSD':>8}   File1,File2")
    for rmsd, (f1, f2) in zip(rmsd_mat.flatten(), product(file1, file2)):
        if args.csv:
            vals = [f"{rmsd:.5f}"] + [f1, f2]
            print(",".join(vals))
        else:
            print(f" {rmsd:8.5f}   {f1},{f2}")


def pdb_superpose():
    """
    Command line interface for superposing PDB structures onto a reference.

    This function superposes PDB structures onto a reference structure and writes the superposed structures to files.

    Args:
        pdbs (List[str]): Target PDB files.
        reference (Optional[str]): Reference PDB file. If not provided, the first PDB file is used as the reference.
        output_dir (str): Directory to save the superposed PDB files.

    Raises:
        ValueError: If the number of backbone atoms in the PDB files is inconsistent.

    Returns:
        None
    """
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    parser = ArgumentParser(description='Superpose two PDB files.', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('pdbs', type=str, nargs='+', help='Target PDB files.')
    parser.add_argument('-r', '--reference', type=str, default=None, help='Reference PDB file.')
    parser.add_argument('-o', '--output_dir', type=str, default="", help='Output directory.')
    args = parser.parse_args()

    from pathlib import Path
    import numpy as np
    from pdbutil.pdb_io import read_pdb, write_pdb
    from pdbutil.rmsd import superpose
    from itertools import product

    datadicts, names = [read_pdb(f, sidechain_warnings=False) for f in args.pdbs], [str(Path(f).stem) for f in args.pdbs]

    xyz_ref = datadicts[0]['xyz_bb'] if args.reference is None else read_pdb(args.reference, sidechain_warnings=False)['xyz_bb']

    if not np.all(np.array([len(d['xyz_bb']) == len(xyz_ref) for d in datadicts], dtype=bool)):
        raise ValueError("All input PDB files must have the same number of CA atoms.")

    xyz_trg = np.stack([d['xyz_bb'] for d in datadicts])
    xyz_sup = superpose(xyz_ref, xyz_trg)

    for xyz, name, data in zip(xyz_sup, names, datadicts):
        data['xyz_bb'] = xyz
        data['xyz_ca'] = None
        new_file_name = args.output_dir + name + "_sup.pdb"
        with open(new_file_name, 'w') as f:
            f.write(write_pdb(**data))


if __name__ == '__main__':
    from pathlib import Path
    import sys
    sys.path.append(str(Path(__file__).parent.parent))

    pdb_superpose()