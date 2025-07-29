import copy
import re
import typing
from typing import Optional
from collections import defaultdict

import numpy as np

import mskit.multi_kits as rk
from mskit.constants.mass import CompoundMass, Mass

__all__ = [
    "calc_ion_mz",
    "calc_prec_mz",
    "calc_fragment_mz",
    "calc_fragment_mz_old",
    "get_fragment_mz_dict",
]


def calc_ion_mz(
    pep: str,
    ion_charge: typing.Union[int, list[int]],
    /,
    ion_type: typing.Union[None, str, list] = None,
    ion_series_num: typing.Union[None, int, list] = None,
    ion_loss_type: typing.Union[None, str, list] = None,
    *,
    mod_mould: str = "brackets",
    mods: typing.Union[str, list] = None,
    no_mod: bool = False,
    c_with_fixed_mod: bool = False,
    pep_preprocess_func: typing.Union[str, bool, typing.Callable] = None,
    mass_offset: float = None,
    return_single_value_if_one_input: bool = True,
    fill_na_if_unsupported: bool = False,
    return_when_series_outofrange: Optional[float] = None,
) -> typing.Union[float, np.ndarray]:
    """
     :param pep:
         Peptide with modification annotated, or stripped peptide sequence with modifications provided by param `mods`
         supported modification moulds are UniMod, Spectronaut style, MaxQuant style, OpenSwath inner style
     :param ion_type:
         Type of on-going calc ion. Can be None for precursor, b/y for fragments.
         Can be None, 'b', 'y', or list of None/'b'/'y'.
         When a list is passed, `ion_series_num` should have same number of components, and `ion_loss_type` should also or be None.
     :param ion_charge:
         Ion charge state (precursor or fragment)
         Should have same number of components as `ion_type`
         Use `0` to calculate mass instead of m/z
     :param ion_series_num:
         If `ion_type` is not None, this param should be provided to calc mz for certain fragments.
         Can be None, int, or list of None/int. Mz of multi ions will be returned if list is provided.
         Should have same number of components as `ion_type`, and use None to indicate precursor
     :param ion_loss_type:
         The loss type of each on-going calc ions.
         When set to None, all ions, even a list of ions are passed, will be Noloss.
         Else this param should have same number of components like `ion_type`
     :param mod_mould:
         How to parse modification annotations in peptide.
         Should be one of the followings to parse modifications, and any char included in the mould will be combined and regarded as one modification:
         'parentheses' or 'pare' or '(':
             will use '(' as the starting char and ')' as the ending one
         'brackets' or 'square brackets' or 'medium brackets' or 'brac' or '[':
             will use '[' as the starting char and ']' as the ending one
         'curly brackets' or 'curly' or '{':
             will use '{' as the starting char and '}' as the ending one
     :param mods:
         Explicitly provided modifications. When this param is not None, modifications will not be parsed from input peptide text.
         Can be str like
             `1,Carbamidomethyl;3,Oxidation;`,
             or list like `[(1, 'Carbamidomethyl'), (3, 'Oxidation')]`,
             or list with float as mod mass `[(1, 57.0214637), (3, 79.9663304084)]`
     :param no_mod:
         If set to True, input `pep` will be regarded as stripped peptide, and no modification on it (param `c_with_fixed_mod` will still have effect)
     :param c_with_fixed_mod:
         Explicitly set any C as Carbamidomethyl modified C.
         And if any Carbamidomethyl is also parsed from pep or provided in param `mods`, the modification mass will be double
     :param pep_preprocess_func:
         A function to preprocess input peptide before any other action
         For example: use `lambda x: x.replace('_', '').replace('.', '')` to remove all `.` and `_` at first
         The above example can also be used by setting this param to 'underscore_dot' or set to True
     :param mass_offset:

     :param return_single_value_if_one_input:
         If True, will return a single value but not ndarray when input is single
         If False, multi inputs will lead to multi outputs as an n-d numpy array, and single input will lead to a 1-d array
     :param fill_na_if_unsupported:

     :return: float or ndarray
         ion m/z

     Examples:
     calc_ion_mz(
         'LGRPSLSSEVGVIICDISNPASLDEMAK',
         3,
         mods='15,Carbamidomethyl;26,Oxidation;'
     )
     -> 992.1668488027999

     calc_ion_mz(
         '_VQISPDS[Phospho (STY)]GGLPER_',
         2,
         pep_preprocess_func='underscore_dot'
     )
     -> 717.8348630473499

     calc_ion_mz(
         '_TPPRDLPT[Phospho (STY)]IPGVTSPSSDEPPM[Oxidation (M)]EAS[Phospho (STY)]QSHLRNSPEDK_',
         4,
         pep_preprocess_func='underscore_dot'
     )
     -> 1012.2026098812998

     calc_ion_mz(
         'VIHDNFGIVEGLM[Oxidation (M)]TTVHAITAT[Phospho (STY)]QK',
         1,
         ion_type='y',
         ion_series_num=16,
         ion_loss_type='1,H3PO4'
     )
     -> 1697.8890815221

     calc_ion_mz(
         '_[Acetyl (Protein N-term)]SGSS[Phospho (STY)]SVAAMKK_',
         2,
         ion_type='y',
         ion_series_num=10,
         ion_loss_type=None,
         pep_preprocess_func='underscore_dot'
     )
     -> 523.24102464735

     calc_ion_mz(
         '_[Acetyl (Protein N-term)]SGSS[Phospho (STY)]SVAAMKK_',
         1,
         ion_type='b',
         ion_series_num=6,
         ion_loss_type='1,H3PO4',
         pep_preprocess_func='underscore_dot'
     )
     -> 529.2252677999999

     mskit.calc.calc_ion_mz(
         '_[Acetyl (Protein N-term)]SGSS[Phospho (STY)]SVAAMKK_',
         [3, 4, 1, 1, 1, 2, 1, 1],
         ion_type=[None, None, 'y', 'y', 'b', 'y', 'b', 'y'],
         ion_series_num=[None, None, 8, 5, 6, 10, 10, 3],
         ion_loss_type=[None, None, 'Noloss', '1,H3PO4', '1,H3PO4', 'noloss', '1,H3PO4', None],
         pep_preprocess_func='underscore_dot'
     )
     -> array([392.17730633, 294.3847989 , 901.42128059, 450.34558439,
        529.2252678 , 523.24102465, 930.434943  , 406.24825189])

    # The previous one equals to the following two ways to set modifications
     mskit.calc.calc_ion_mz(
         'SGSSSVAAMKK',
         [3, 4, 1, 1, 1, 2, 1, 1],
         ion_type=[None, None, 'y', 'y', 'b', 'y', 'b', 'y'],
         ion_series_num=[None, None, 8, 5, 6, 10, 10, 3],
         ion_loss_type=[None, None, 'Noloss', '1,H3PO4', '1,H3PO4', 'noloss', '1,H3PO4', None],
         mods=[(0, 'Acetyl (Protein N-term)'), (4, 'Phospho (STY)')],
         pep_preprocess_func='underscore_dot'
     )
     mskit.calc.calc_ion_mz(
         'SGSSSVAAMKK',
         [3, 4, 1, 1, 1, 2, 1, 1],
         ion_type=[None, None, 'y', 'y', 'b', 'y', 'b', 'y'],
         ion_series_num=[None, None, 8, 5, 6, 10, 10, 3],
         ion_loss_type=[None, None, 'Noloss', '1,H3PO4', '1,H3PO4', 'noloss', '1,H3PO4', None],
         mods=[(0, 42.0105646863), (4, 79.9663304084)],
         pep_preprocess_func='underscore_dot'
     )

    """

    if pep_preprocess_func is not None:
        if pep_preprocess_func == "underscore_dot" or pep_preprocess_func is True:
            pep = pep.replace("_", "").replace(".", "")
        else:
            pep = pep_preprocess_func(pep)

    if no_mod:
        stripped_pep = pep
        mod_poss, mod_names = tuple(), tuple()

    elif mods is None:
        if mod_mould in ["parentheses", "pare", "("]:
            mould_chars = ("(", ")")
        elif mod_mould in ["brackets", "square brackets", "medium brackets", "brac", "["]:
            mould_chars = ("[", "]")
        elif mod_mould in ["curly brackets", "curly", "{"]:
            mould_chars = ("{", "}")
        else:
            raise ValueError(f"Current value {mod_mould} for param `mod_mould` is not supported")

        stripped_pep, mod_poss, mod_names = rk.find_substring(
            pep,
            *mould_chars,
            keep_start_end_char=False,
        )

    else:
        stripped_pep = pep
        if isinstance(mods, str):
            mod_poss, mod_names = list(zip(*[_.split(",") for _ in mods.strip(";").split(";")]))
            mod_poss = [int(_) for _ in mod_poss]
        elif isinstance(mods, list):
            mod_poss, mod_names = list(zip(*mods))
            mod_poss = [int(_) for _ in mod_poss]
        else:
            raise ValueError(
                f"When param `mods` is explicitly provided, this should be either string like xxx or list like xxx"
            )

    pep_len = len(stripped_pep)

    if ion_type is None or isinstance(ion_type, str):
        if not isinstance(ion_charge, (int, np.integer)):
            raise ValueError(f"Expect an integer as `ion_charge`. Now is {ion_charge} with type as {type(ion_charge)}")
        if ion_series_num is not None and not isinstance(ion_series_num, (int, np.integer)):
            raise ValueError(
                f"Expect None or an integer as `ion_series_num`. Now is {ion_series_num} with type as {type(ion_series_num)}"
            )
        ion_type = ("b",) if ion_type is None else (ion_type,)
        ion_charge = (ion_charge,)
        ion_series_num = (pep_len,) if ion_series_num is None else (ion_series_num,)
        ion_loss_type = (ion_loss_type,)
    else:
        if len(ion_type) != len(ion_charge):
            raise ValueError(f"When multi `ion_type` is defined, same number of `ion_charge` should also be passed")
        if len(ion_type) != len(ion_series_num):
            raise ValueError(f"When multi `ion_type` is defined, same number of `ion_series_num` should also be passed")
        if ion_loss_type is None or isinstance(ion_loss_type, str):
            ion_loss_type = [ion_loss_type] * len(ion_type)
        if len(ion_type) != len(ion_loss_type):
            raise ValueError(f"When multi `ion_type` is defined, same number of `ion_loss_type` should also be passed")

        if None in ion_type:
            _prec_idx = [i for i, i_t in enumerate(ion_type) if i_t is None]
            # this needs to be adjusted if a/c/x/z should be supported
            if "b" in ion_type:
                for i in _prec_idx:
                    ion_type[i] = "b"
                    ion_series_num[i] = pep_len
            else:
                for i in _prec_idx:
                    ion_type[i] = "y"
                    ion_series_num[i] = pep_len

    needed_ions = {"b": defaultdict(list), "y": defaultdict(list)}
    for idx, (i_t, i_sn, i_c, i_l) in enumerate(zip(ion_type, ion_series_num, ion_charge, ion_loss_type)):
        needed_ions[i_t][i_sn].append((i_c, i_l, idx))

    result = np.zeros(len(ion_type))

    needed_ions_subset = needed_ions["b"]
    if len(needed_ions_subset) != 0:
        _pos_to_mod_name = defaultdict(list)
        for _p, _n in zip(mod_poss, mod_names):
            _pos_to_mod_name[_p].append(_n)

        _mass = (
            sum([(m if isinstance(m, float) else Mass.ModMass[m]) for m in _mods])
            if (_mods := _pos_to_mod_name.get(0)) is not None
            else 0.0
        )
        _mass = _mass + mass_offset if mass_offset is not None else _mass
        for pos in range(1, max(needed_ions_subset.keys()) + 1):
            _mass += Mass.ResMass[stripped_pep[pos - 1]]
            if c_with_fixed_mod and stripped_pep[pos - 1] == "C":
                _mass += Mass.ModMass["Carbamidomethyl"]
            if (_mods := _pos_to_mod_name.get(pos)) is not None:
                _mass += sum([(m if isinstance(m, float) else Mass.ModMass[m]) for m in _mods])
            if pos == pep_len:
                _mass += CompoundMass.CompoundMass["H2O"]  # diff with y

            for i_c, i_l, idx in needed_ions_subset[pos]:
                this_mass = _mass + Mass.ProtonMass * i_c
                if i_l is None:
                    pass
                elif isinstance(i_l, str) and (i_l.lower() == "noloss" or i_l == ""):
                    pass
                elif isinstance(i_l, (float, int, np.inexact, np.integer)):
                    this_mass -= i_l
                else:
                    for loss in i_l.strip(";").split(";"):
                        loss_num, loss_compound = loss.split(",") if "," in loss else (1, loss)
                        this_mass -= int(loss_num) * Mass.ModLossMass[loss_compound]
                result[idx] = this_mass / i_c if i_c != 0 else this_mass

    needed_ions_subset = needed_ions["y"]
    if len(needed_ions_subset) != 0:
        stripped_pep = stripped_pep[::-1]  # diff with b
        _pos_to_mod_name = defaultdict(list)
        for _p, _n in zip(mod_poss, mod_names):
            if _p == 0:
                _pos_to_mod_name[pep_len].append(_n)  # diff with b
            else:
                _pos_to_mod_name[pep_len + 1 - _p].append(_n)  # diff with b

        _mass = (
            sum([(m if isinstance(m, float) else Mass.ModMass[m]) for m in _mods])
            if (_mods := _pos_to_mod_name.get(0)) is not None
            else 0.0
        )
        _mass += CompoundMass.CompoundMass["H2O"]  # diff with b
        _mass = _mass + mass_offset if mass_offset is not None else _mass
        for pos in range(1, max(needed_ions_subset.keys()) + 1):
            _mass += Mass.ResMass[stripped_pep[pos - 1]]
            if c_with_fixed_mod and stripped_pep[pos - 1] == "C":
                _mass += Mass.ModMass["Carbamidomethyl"]
            if (_mods := _pos_to_mod_name.get(pos)) is not None:
                _mass += sum([(m if isinstance(m, float) else Mass.ModMass[m]) for m in _mods])

            for i_c, i_l, idx in needed_ions_subset[pos]:
                this_mass = _mass + Mass.ProtonMass * i_c
                if i_l is None:
                    pass
                elif isinstance(i_l, str) and (i_l.lower() == "noloss" or i_l == ""):
                    pass
                elif isinstance(i_l, (float, int, np.inexact, np.integer)):
                    this_mass -= i_l
                else:
                    for loss in i_l.strip(";").split(";"):
                        loss_num, loss_compound = loss.split(",") if "," in loss else (1, loss)
                        this_mass -= int(loss_num) * Mass.ModLossMass[loss_compound]
                result[idx] = this_mass / i_c if i_c != 0 else this_mass

    if return_single_value_if_one_input and len(ion_type) == 1:
        return result[0]
    else:
        return result


def ion_mz_from_mass(mass: float, charge: int):
    pass


class MassCalc(object):
    ResMass = copy.deepcopy(Mass.ResMass)
    ModMass = copy.deepcopy(Mass.ModMass)

    def __init__(self):
        """ """

        self._cache = dict()

        # if c_with_fix_mod:
        #     self.ResMass['C'] = self.ResMass['C+']

    def valid_mass(self):
        """
        candidate_mods
        mass_tol
        mz_tol

        :return:
        """
        pass


def calc_prec_mz(pep: str, charge: int = None, mod=None) -> float:
    """
    Example:
    pep = 'LGRPSLSSEVGVIICDISNPASLDEMAK'
    charge = 3
    mod = '15,Carbamidomethyl;26,Oxidation;'
    -> 992.1668502694666

    calc_prec_mz('_VQISPDS[Phospho (STY)]GGLPER_.2')
    -> 717.83486304735

    calc_prec_mz('_TPPRDLPT[Phospho (STY)]IPGVTSPSSDEPPM[Oxidation (M)]EAS[Phospho (STY)]QSHLRNSPEDK_.4')
    -> 1012.2026098813

    :param pep: peptide that is modified with num, e.g. ACDM1M, where 1 equals to M[Oxidation]
    :param charge: precursor charge
    :param mod: str like 1,Carbamidomethyl;3,Oxidation; or list like [(1, 'Carbamidomethyl'), (3, 'Oxidation')]
    :return: Precursor m/z

    """
    if "." in pep:
        pep, charge = rk.split_prec(pep)
    if "[" in pep:
        stripped_pep = re.sub(r"\[.+?\]", "", pep).replace("_", "")
        mod_in_pep = re.findall(r"\[(.+?) \(.+?\)\]", pep)
    else:
        stripped_pep = pep.replace("_", "")
        mod_in_pep = None

    pep_mass = 0.0
    for aa in stripped_pep:
        pep_mass += Mass.ResMass[aa]
    pep_mass += CompoundMass.CompoundMass["H2O"]
    pep_mass += Mass.ProtonMass * charge

    if mod:
        if isinstance(mod, str):
            mod = [_.split(",") for _ in mod.strip(";").split(";")]
        for _each_mod in list(zip(*mod))[1]:
            pep_mass += Mass.ModMass[_each_mod] if _each_mod != "Carbamidomethyl" else 0.0
    if mod_in_pep:
        for each_mod in mod_in_pep:
            if "Carbamidomethyl" in each_mod:
                continue
            else:
                pep_mass += Mass.ModMass[each_mod]
    return pep_mass / charge


def calc_fragment_mz(pep, frag_type, frag_num, frag_charge, loss_type=None) -> float:
    """
    Example:
    calc_fragment_mz('_VIHDNFGIVEGLM[Oxidation (M)]TTVHAITAT[Phospho (STY)]QK_', 'y', 16, 1, '1,H3PO4')
    -> 1697.8890815221002

    calc_fragment_mz('_[Acetyl (Protein N-term)]SGSS[Phospho (STY)]SVAAMKK_', 'y', 8, 1, '1,H3PO4')
    -> 803.4443855000001

    calc_fragment_mz('_[Acetyl (Protein N-term)]SGSS[Phospho (STY)]SVAAMKK_', 'y', 10, 2, )
    -> 523.24102464735

    calc_fragment_mz('_[Acetyl (Protein N-term)]SGSS[Phospho (STY)]SVAAMKK_', 'b', 6, 1, '1,H3PO4')
    -> 529.2252678

    pep = 'LGRPSLSSEVGVIICDISNPASLDEMAK'
    frag_type = 'y'
    frag_num = 10
    frag_charge = 1
    mod = '15,Carbamidomethyl;26,Oxidation;'
    -> 1091.5037505084001

    :param pep: peptide sequence
    :param frag_type: support b and y ion
    :param frag_num:
    :param frag_charge:
    :param loss_type:
    :return: Fragment m/z
    """

    # TODO 重复使用已经得到的 pep 信息
    stripped_pep, mod_sites, mods = rk.find_substring(pep.replace("_", ""))
    mods = [mod.strip("[]()").split(" ")[0] for mod in mods]
    mod_sites = list(map(int, mod_sites))
    frag_num = int(frag_num)
    frag_charge = int(frag_charge)
    frag_mass = Mass.ProtonMass * frag_charge
    if frag_type == "b":
        mod_dict = dict(zip(mod_sites, mods))
        if 0 in mod_dict:
            frag_mass += Mass.ModMass[mod_dict[0]]

    elif frag_type == "y":
        stripped_pep = stripped_pep[::-1]
        frag_mass += CompoundMass.CompoundMass["H2O"]
        pep_len = len(stripped_pep)
        mod_sites = [pep_len - site + 1 for site in mod_sites]
        mod_dict = dict(zip(mod_sites, mods))
        if frag_num >= pep_len and (pep_len + 1) in mod_sites:
            frag_mass += Mass.ModMass[mod_dict[pep_len + 1]]
    else:
        raise NameError("Only b and y ion are supported")
    for i in range(frag_num):
        frag_mass += Mass.ResMass[stripped_pep[i]]
        if i + 1 in mod_dict:
            mod_type = mod_dict[i + 1]
            if "Carbamidomethyl" in mod_type:
                continue
            frag_mass += Mass.ModMass[mod_type]

    if loss_type is None or loss_type.lower() == "noloss":
        pass
    else:
        for loss_num, loss_compound in [loss.split(",") for loss in loss_type.split(";")]:
            frag_mass -= int(loss_num) * Mass.ModLossMass[loss_compound]

    return frag_mass / frag_charge


def calc_fragment_mz_old(pep, frag_type, frag_num, frag_charge, mod=None) -> float:
    """
    Example:
    pep = 'LGRPSLSSEVGVIICDISNPASLDEMAK'
    frag_type = 'y'
    frag_num = 10
    frag_charge = 1
    mod = '15,Carbamidomethyl;26,Oxidation;'
    -> 1091.5037505084001

    :param pep: peptide sequence
    :param frag_type: support b and y ion
    :param frag_num:
    :param frag_charge:
    :param mod:
    :return: Fragment m/z
    """
    frag_num = int(frag_num)
    frag_charge = int(frag_charge)
    frag_mass = Mass.ProtonMass * frag_charge

    if mod:
        if isinstance(mod, str):
            mod = [_.split(",") for _ in mod.strip(";").split(";")]
            mod = [(int(_[0]), _[1]) for _ in mod]
        mod_dict = dict(mod)
    else:
        mod_dict = dict()

    if frag_type == "b":
        for i in range(frag_num):
            frag_mass += Mass.ResMass[pep[i]]
            if i + 1 in mod_dict:
                frag_mass += Mass.ModMass[mod_dict[i + 1]]
        if 0 in mod_dict:
            frag_mass += Mass.ModMass[mod_dict[0]]

    elif frag_type == "y":
        frag_mass += CompoundMass.CompoundMass["H2O"]
        pep_len = len(pep)
        for i in range(pep_len - 1, pep_len - 1 - frag_num, -1):
            frag_mass += Mass.ResMass[pep[i]]
            if i + 1 in mod_dict:
                frag_mass += Mass.ModMass[mod_dict[i + 1]]
        if frag_num == pep_len:
            frag_mass += Mass.ModMass[mod_dict[0]]
    else:
        raise NameError("Only b and y ion are supported")
    return frag_mass / frag_charge


def get_fragment_mz_dict(pep, fragments, mod=None):
    """
    :param pep:
    :param fragments:
    :param mod:
    :return:
    """
    mz_dict = dict()
    for each_fragment in fragments:
        frag_type, frag_num, frag_charge = rk.split_fragment_name(each_fragment)
        mz_dict[each_fragment] = calc_fragment_mz(pep, frag_type, frag_num, frag_charge, mod)
    return mz_dict
