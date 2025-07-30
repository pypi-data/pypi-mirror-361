#
#   Copyright (c) 2021 eGauge Systems LLC
# 	1644 Conestoga St, Suite 2
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
"""This module provides helper functions outputting the BOM as a CSV
file."""

from collections import OrderedDict
from types import SimpleNamespace

import io

from epic.base import Enum, format_part_number

from .error import Error
from .parts_cache import PartsCache


def _bom_sort(bom):
    """Sort a dictionary of components by part number and return the
    resulting list.

    """
    bom_list = []
    for component in bom.values():
        bom_list.append(component)
    bom_list.sort(key=lambda x: x[0].part_id)
    return bom_list


def _quote(string):
    """CSV quote a string.  DigiKey doesn't handle commas correctly even
    if they're inside double quotes so we also replace commas with
    colons.

    """
    string = string.replace('"', '"')
    string = string.replace(",", ":")
    return '"' + string + '"'


def _is_orderable(vp):
    """A vendor part VP is orderable only if its status indicates its
    orderable and also it corresponding part is also orderable.

    """
    if vp.status not in Enum.STATUS_ORDERABLE:
        return False
    part = PartsCache.get(vp.part)
    if part.status not in Enum.STATUS_ORDERABLE:
        return False
    return True


def _best_vendor_parts(epic_api, component, vendors, preferred_vendors):
    """Find the best vendor parts for a given COMPONENT.  Orderable parts
    are better than deprecated or obsolete parts.  Lower cost parts
    are better than higher cost parts.  Note that all vendor parts
    from equivalent parts (substitutes) are considered, not just the
    vendor parts for the part specified directly by COMPONENT.

    VENDORS must be a dictionary of vendors to consider, indexed by
    vendor id.

    If PREFERRED_VENDORS is None, a dictionary of best parts for all
    VENDORS is returned, indexed by vendor.  Otherwise, the returned
    dictionary is guaranteed to have an entry for each vendor in
    VENDORS.  The entry may have a value of None if a particular
    VENDOR does not carry the part.

    """
    ret = OrderedDict()
    if preferred_vendors is not None:
        for vendor in vendors.values():
            ret[vendor.id] = None

    parts = ["%d" % part_number for part_number in component.part.equivalents]

    reply = epic_api.get("vendor_part/?part_id=%s" % ",".join(parts))
    if not reply:
        return ret

    for vp in reply:
        part = SimpleNamespace(**vp)
        vendor = vendors.get(part.vendor)
        if vendor is None:
            continue
        if vendor.id in vendors:
            if vendor.id in ret and ret[vendor.id] is not None:
                if _is_orderable(ret[vendor.id]) and not _is_orderable(part):
                    continue
                if (
                    not _is_orderable(ret[vendor.id])
                    and _is_orderable(part)
                    or ret[vendor.id].price < part.price
                ):
                    continue
            ret[vendor.id] = part
    return ret


def _output_list(
    outfile,
    epic_api,
    bom_list,
    with_vendor_pn=False,
    vendors=None,
    preferred_vendors=None,
):
    """Output the components in BOM_LIST in CSV format to file OUTFILE.
    EPIC_API is the EPIC-API-client to use for fetching EPIC info.
    WITH_VENDOR_PN must be True if vendor part numbers should be
    output to the CSV file.  VENDORS is a dictionary of vendors,
    indexed by vendor-id.  PREFERRED_VENDORS should by a value other
    than None if vendor part-number for each of the VENDORS must be
    output.

    """
    for components in bom_list:
        c = components[0]
        if c.part:
            for sub_id in c.part.equivalents:
                PartsCache.prefetch(sub_id)

    for components in bom_list:
        qty = len(components)
        refdes = ",".join(sorted([c.refdes for c in components]))
        c = components[0]

        substitutes = ""
        if c.part:
            sep = ""
            for sub_id in c.part.equivalents:
                sub = PartsCache.get(sub_id)
                if sub_id == c.part_id:
                    continue
                substitutes += sep
                substitutes += "%s (%s %s)" % (
                    format_part_number(sub.id),
                    sub.mfg,
                    sub.mfg_pn,
                )
                sep = ", "

        row = "%s,%s,%s,%s,%s,%s,%s,%s" % (
            qty,
            c.value,
            c.footprint,
            format_part_number(c.part_id),
            c.mfg,
            _quote(c.mfg_pn),
            _quote(substitutes),
            _quote(refdes),
        )

        if with_vendor_pn:
            vps = _best_vendor_parts(epic_api, c, vendors, preferred_vendors)
            if preferred_vendors is None:
                for vid, part in vps.items():
                    row += ",%s,%s" % (
                        vendors[vid].name,
                        part.vendor_pn if part else "n/a",
                    )
            else:
                for part in vps.values():
                    row += ",%s" % (part.vendor_pn if part else "n/a")
        print(row, file=outfile)


def write(
    filename, epic_api, bom, include_vendor_pn=False, preferred_vendors=None
):
    """Output the BOM to a file named FILENAME in CSV format.  EPIC_API is
    the EPIC-API-client to use for fetching EPIC info.
    INCLUDE_VENDOR_PN should be True if vendor part information should
    be output.  PREFERRED_VENDORS can be set to a list to output
    vendor part numbers only for the specified vendors.

    """
    reply = epic_api.get("vendor/")
    if not reply:
        raise Error("Unable to get vendor list.")
    vendors = OrderedDict()
    for v in reply:
        vendor = SimpleNamespace(**v)
        if preferred_vendors is None:
            vendors[vendor.id] = vendor
        else:
            for preferred in preferred_vendors:
                if preferred.lower() in vendor.name.lower():
                    vendors[vendor.id] = vendor

    with io.open(filename, "w", encoding="utf-8") as out:
        hdr = (
            "Qty,Value,Footprint,%s PN,Mfg,Mfg PN," % bom.manufacturer
        ) + "Approved Substitutes,Refdes"
        if include_vendor_pn:
            if preferred_vendors is None:
                hdr += ",Vendor,Vendor PN..."
            else:
                for vendor in vendors.values():
                    hdr += ",%s" % _quote(vendor.name + " PN")
        print(hdr, file=out)

        comp_list = _bom_sort(bom.comps)
        _output_list(
            out,
            epic_api,
            comp_list,
            include_vendor_pn,
            vendors,
            preferred_vendors,
        )

        dnp_list = _bom_sort(bom.dnps)
        if dnp_list:
            print("\nDO NOT PLACE parts:", file=out)
            _output_list(
                out,
                epic_api,
                dnp_list,
                include_vendor_pn,
                vendors,
                preferred_vendors,
            )
