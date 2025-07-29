# GGchem

(c) Peter Woitke & Christiane Helling 2017

Fast thermo-chemical equilibrium code with or without equilibrium
condensation down to 100K.

Please cite our A&A paper "Equilibrium chemistry down to 100 K. 
Impact of silicates and phyllosilicates on carbon/oxygen ratio"; 
P. Woitke, Ch. Helling, G. H. Hunter, J. D. Millard, 
G. E. Turner, M. Worters, J. Blecic, J. W. Stock; 
2018; Astronomy & Astrophysics 614, 1; 
see GGchemPaper.pdf in this folder. 

We would be interested to hear from you about what kind of applications
you would like to use ggchem for, please let us know via email
Peter Woitke (pw31@st-and.ac.uk) 
as well as if you have any questions or problems. 

If your research results in any publications, please cite the above
article and consider to give us co-author-ship.

### To checkout the git repository and compile the code, use 

> git clone https://github.com/pw31/GGchem  
> cd GGchem/src16  
> cp makefile.prodimo makefile  
> make  

The makefile.prodimo is for ifort compiler, adjust your own makefile if
you want to compile e.g. with gfortran.

### To run the code, type 

> cd ..  
> ./ggchem input/default.in

It will create the output file "Static_Conc.dat", which contains all
computed molecular, atom and ion particle densities, the electron
density, solid and liquid particle densities, and supersaturation
ratios:

  * Tg: gas temperature [K],  
  * nHtot: total hydrogen nuclei particle density [cm-3],  
  * pges: total gas pressure [dyn/cm2]  
  * el ... W: atomic particle densities log10(natom)[cm-3]  
  * {mol}: molecular particle densities log10(nmol)[cm-3]  
  * S{cond}: supersaturation ratios log10(S) [-] of condensates  
  * n{cond}: concentration of condensed units per H nuclues log10(ncond/nHtot) [-]  
  * eps{el}: remainig element abundances in the gas phase [-]  
  * dust/gas: dust to gas mass ratio log10(rho_dust/rho_gas) [-]  
  * dustVol/H: dust volume per H nucleus log10(dust_volume) [cm3]  

S{cond} and n{cond} are used in the header to distinguish between 
supersaturation ratio and concentration of condensed units, whereas
{mol} (without the leading "n") is a molecular particle density.

### To visualise the results, use e.g.

> python tools/Plot_T.py  
> evince ggchem.pdf &  

### Customise your own model

To create your own model, make a copy of default.in and customize it to 
tell GGchem what it should do. You can also look at some of the other *.in 
files to lean from examples. Select or deselect elements by modifying 
the first line, default choice is

 H He C N O Na Mg Si Fe Al Ca Ti S Cl K Li F P V Cr Mn Ni Zr W el

where "el" means to include atomic and molecular ions, and the
electron density as well, assuming charge equilibrium.  Molecules are
included if they are made of the selected elements, otherwise they
will be ignored.

Choose element abundances with parameter abund_pick. The default
choice is abund_pick=3 for solar abundances from Asplund et
al.(2009). There are additional pre-installed options to use data from
"Abundances.dat", including "EarthCrust" (abund_pick=1), "Ocean"
(abund_pick=2) and "Meteorites" (abund_pick=4) as listed in
"Abundances.dat".  If you want any other element abundances, use
(abund_pick=0) followed by a name of a custom file with abundances,
see, e.g. input/model_Crich.in.

Choose sources for equilibrium constants kp(T)-data, default choice is 
dispol_new.dat. There are 6 different fit-formulas implemented, see
details in src16/smchem16.f (function gk). Data files having kp-data
are in folder data:

dispol_StockKitzmann.dat               : 2008, Diplomarbeit TU Berlin  
dispol_StockKitzmann_withoutTsuji.dat  : same, without Tsuji refits  
dispol_BarklemCollet.dat               : 2016, A&A 588, A96  
dispol_SharpHuebner.dat                : 1990, ApJSS 72, 417  
dispol_Tsuji.dat                       : 1973, A&A 23, 411  
dispol_GGchem.dat                      : old NIST-Janaf fits  
dispol_fast.dat                        : 9-molecules from Heng&Tsai 2016  

You can use combinations by setting dispol_file, dispol_file2, 
dispol_file3, dispol_file4 in your MyModel.in file, in which case 
the latter have preference over the former, and will overwrite 
previous data.

Choose whether you want to constrain the pressure (model_pconst=.true.)
or the mass density (model_pconst=.false.).

You can run single point model (model_dim=0), linear track
(model_dim=1) or 2D coverage (model_dim=2). Set parameters Tmin, Tmax
and then pmax, pmin or nHmax, nHmin for model_pconst=.true. or
.false., respectively. In the default model_dim=1 mode, ggchem will
make a linear track in (logp, logT) parameter space with Npoints
points.

If you want to switch on equilibrium condensation, set
model_eqcond=.true. In that mode, the code will be much slower, and
also possibly unstable. Always start from large T and then lower T
SLOWLY with successive calls. The code will create and expand
"database.dat" automatically from the results of every successful
call, such that once you have filled in the (p,T)-plane with many
points, the results will be faster and more reliable. The Gibbs-free
energy data files are in folder data:

DustChem_GGchem.dat      : old GGchem NIST-Janaf fits  
DustChem_SUPCRTBL.dat    : dG-fits from the SUPCRTBL database  
      (Zimmer et al. 2016, Computers and Geosciences, 90, 97)  
DustChem.dat             : currently used collection from both  

The pure gas phase chemistry needs about 0.4 ms per call for T > 1000 K
(real*8 version) and about 3 ms per call for T < 1000 K (real*16
version). These time measurements are for 16 elements + charge. Time
requirement roughly scale as N^3, if N is the number of elements.
The equilibrium condensation code requires many calls of the gas-phase
equilibrium chemistry routine, and takes about 0.02-0.09 sec per call,
depending on how much useful information is found in database.dat.
 
# TauREx-GGchem plugin

A Python wrapper built using the [TauREx](https://github.com/ucl-exoplanets/TauREx3_public) is available.
The wrapper also installs all available datafiles included with GGchem

## Installation


You can install one of the prebuilt binary wheels for Windows, macOS and manylinux through pip:
```bash
pip install taurex_ggchem
```

### Installing from source


To install from source a valid C/C++ and FORTRAN compiler must be present. You can compile it by doing:
```bash
git clone https://github.com/ucl-exoplanets/GGchem.git
cd GGchem
pip install .
```

## Running in TauREx

Once installed you can select the chemical model through the **chemistry_type** keyword under
Chemistry.
```
[Chemistry]
chemistry_type = ggchem
metallicity = 1.0
selected_elements = H, He, C, N, O, Ti, V, S, K
ratio_elements = C, N, Ti
ratios_to_O = 0.5,0.001, 1e-4
equilibrium_condensation = True

[Fitting]
Ti_O_ratio:fit = True
Ti_O_ratio:prior = "LogUniform(bounds=(-6,2))"
S_O_ratio:fit = True
S_O_ratio:prior = "LogUniform(bounds=(-6,2))"
metallicity:fit = True
metallicity:prior = "LogUniform(bounds=(-6,2))"
```

### Input arguments:

|Argument| Description| Type| Default | Required |
---------|------------|-----|---------|----------|
dispol_files| Path to thermochemical data | list of strings | Built-in (BarklemCollet,StockKitzmann_withoutTsuji, WoitkeRefit ) | |
abundance_profile| Initial abundance profile. Either *solar*, *meteor*, *ocean* or *earth*  | string | 'solar' | |
selected_elements| List of elements to include | list of string | All elements in GGchem | |
ratio_elements| List of elements to set the ratio | list of string | | |
ratios_to_O| ratio of each 'ratio_element' relative to oxygen | array | | |
he_h_ratio| He/H ratio | float | 0.083 | |
metallicity| Metallicity relative to initial abundance | float | 1.0 | |
include_charge| Include ions | bool | False | |
equilibrium_condensation| Include condenstation | bool | False | |
dustchem_file| Dust chemistry file | string | Built-in (DustChem.dat) | |
Tfast| Lowest temperature (K) to use faster method  | float | 1000 | |
new_back_it| | integer | 6 | |
new_back_fac| | float | 1e5 | |
new_pre_method| | integer | 2 | |
new_full_it| | bool | False | |
new_fast_level| | integer | 1 | |

### Retrieval Parameters:

|Fitting Parameter| Description| 
---------|------------|
metallicity|Metallicity relative to solar|

The wrapper will generate oxygen retrieval parameters for all metallic elements within the
chemical model. If Ti is present (either by default or specifing in **selected_elements**)
then a **Ti_O_ratio** retrieval parameter will be available.
Using the default **selected_parameters** will give access to:

|Fitting Parameter| Description| 
---------|------------|
C_O_ratio | C/O ratio |
N_O_ratio | N/O ratio |
Na_O_ratio | Na/O ratio |
Mg_O_ratio | Mg/O ratio |
Si_O_ratio | Si/O ratio |
Fe_O_ratio | Fe/O ratio |
Al_O_ratio | Al/O ratio |
Ca_O_ratio | Ca/O ratio |
Ti_O_ratio | Ti/O ratio |
S_O_ratio | S/O ratio |
Cl_O_ratio | Cl/O ratio |
K_O_ratio | K/O ratio |
Li_O_ratio | Li/O ratio |
F_O_ratio | F/O ratio |
P_O_ratio | P/O ratio |
V_O_ratio | V/O ratio |
Cr_O_ratio | Cr/O ratio |
Mn_O_ratio | Mn/O ratio |
Ni_O_ratio | Ni/O ratio |
Zr_O_ratio | Zr/O ratio |
W_O_ratio | W/O ratio |


## Running in Python

You can import the chemistry scheme in Python pretty easily

```python
>>> from taurex_ggchem import GGChem
>>> gg = GGChem(metallicity=1.0,  
         selected_elements=['H','He','C','O','N','K'], 
         abundance_profile='earthcrust', 
         equilibrium_condensation=True) 
```
You can either pass it into a TauREx forward model like so:
```python
>>> tm = TransmissionModel(chemistry=gg)
```
Or use it independently to compute volume mixing ratios for gas-phase and condensates by passing in
temperature and pressure ( Pascal ) arrays:
```python
>>> nlayers = 100
>>> T = numpy.linspace(400,1000,nlayers)
>>> P = numpy.logspace(1,5, nlayers)
>>> gg.initialize_chemistry(nlayers=nlayers, temperature_profile=T, pressure_profile=P)
>>> gg.gases
['H', 'He', 'C', 'O', 'N',..., 'N3', 'O3', 'C3H']
>>> gg.mixProfile
array([[4.75989782e-04, 4.93144149e-04, 5.10561665e-04, ...,
        2.89575385e-05, 2.47386006e-05, 2.10241059e-05],
       ...,
       [2.49670621e-16, 1.44224904e-16, 8.29805526e-17, ...,
        9.48249338e-42, 4.75884162e-42, 2.37999459e-42]])
>>> gg.condensates
['C[s]', 'H2O[s]', 'H2O[l]', 'NH3[s]', 'CH4[s]', 'CO[s]', 'CO2[s]']
>>> gg.condensateMixProfile
array([[0.00000000e+00, 0.00000000e+00, 0.00000000e+00,...,
        0.00000000e+00, 0.00000000e+00],
       [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, ...,
        0.00000000e+00, 9.82922802e-10, 1.88551848e-10, 2.88471985e-11,
        4.40651877e-12, 6.95597887e-13],
        ...,
        [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, ...,
        0.00000000e+00, 0.00000000e+00]])
```

## Bibliography

If you use the plugin please cite the relevant articles. TauREx will output
it at program end. You can get the citation from Python like so:

```python
from taurex import __citations__
print(__citations__)
print(gg.nice_citation())
```

Which gives:
```
TauREx III: A fast, dynamic and extendable framework for retrievals
Al-Refaie, Ahmed F., Changeat, Quentin, Waldmann, Ingo P., Tinetti, Giovanna
arXiv, 1912.07759, 2019

Equilibrium chemistry down to 100 K - Impact of silicates and phyllosilicates on the carbon to oxygen ratio
Woitke, P., Helling, Ch., Hunter, G. H., Millard, J. D., Turner, G. E., Worters, M., Blecic, J., Stock, J. W.
A&A, 614, A1, 2018
```

You can also generate bibtex from the input file like so:
```bash
taurex -i myinput.par --bibtex mybib.bib
```
