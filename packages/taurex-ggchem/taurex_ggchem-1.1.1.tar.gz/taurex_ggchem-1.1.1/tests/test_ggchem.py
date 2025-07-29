import taurex_ggchem


def test_ggchem():
    """Test GGChem class if it functions properly"""
    from taurex_ggchem import GGChem
    from taurex.constants import AMU

    import numpy as np
    import math

    gg = GGChem()
    tp = np.logspace(math.log10(2500), math.log10(2000), 100)

    pp = np.ones(100) * 1e5
    pp
    gg.initialize_chemistry(nlayers=100, temperature_profile=tp, pressure_profile=pp)
    assert np.all(gg.muProfile / AMU != 0.0)


def test_ggchem():
    """Test GGChem class if it functions properly"""
    from taurex_ggchem import GGChem
    from taurex.constants import AMU

    import numpy as np
    import math

    gg = GGChem(equilibrium_condensation=True)
    tp = np.ones(1) * 2500

    pp = np.ones(1) * 1e7
    pp
    gg.initialize_chemistry(nlayers=1, temperature_profile=tp, pressure_profile=pp)
    assert np.all(gg.muProfile / AMU != 0.0)


def test_ggchem_unsafe():
    """Test GGChem Non-Safe class if it functions properly"""
    from taurex_ggchem import GGChemNonSafe as GGChem
    from taurex.constants import AMU

    import numpy as np
    import math

    gg = GGChem(equilibrium_condensation=True)
    tp = np.ones(1) * 2500

    pp = np.ones(1) * 1e7
    pp
    gg.initialize_chemistry(nlayers=1, temperature_profile=tp, pressure_profile=pp)
    assert np.all(gg.muProfile / AMU != 0.0)


def test_ggchem_abundances_custom(tmp_path):
    """Test GGChem class if it functions properly with custom abundances"""
    from taurex_ggchem import GGChem
    from taurex_ggchem.chemistry.ggchemistry_safe import selected
    from taurex.constants import AMU

    import numpy as np
    import math

    # Create a custom abundance file
    num_elements = len(selected)
    random_abundances = np.random.uniform(0, 1, size=num_elements)
    random_abundances[0] = 0.99
    random_abundances /= random_abundances[0]
    with open(tmp_path / "custom_abund.dat", "w") as f:
        for i, element in enumerate(selected):
            f.write(f"{element} {random_abundances[i]}\n")

    gg = GGChem(abundance_profile=tmp_path / "custom_abund.dat")

    gg_abunds = np.array(
        [gg._initial_abundances[gg.get_element_index(x)] for x in selected]
    )

    # Sort them both so that they can be compared
    np.testing.assert_allclose(gg_abunds, random_abundances, rtol=1e-5)
