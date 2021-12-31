#!/usr/bin/env python3
"""Commandline scripts to parse/validate/summarize SMART Health Cards."""
import json
import warnings
from os import listdir
from os.path import isfile, join
from typing import List

import click
from fhirclient.models.bundle import Bundle
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.immunization import Immunization
from fhirclient.models.patient import Patient

from smart_health_card_reader.parse import extract_jws_data_from_qr_data, img_to_qr_data, validate_jws_data

from .config import VACCINE_PROPRIETARY_NAMES


@click.command()
@click.argument("qr_image", type=click.Path(exists=True, readable=True))
def validate_one(qr_image: click.Path):
    """Validate SMART Health Card and if successful, show contents.

    Parameters:
        qr_image: Image file containing a single SMART Health Card QR code.
    """
    qr_img_fn = click.format_filename(qr_image)
    qr_data = img_to_qr_data(qr_img_fn)
    doc, header, payload, sig = extract_jws_data_from_qr_data(qr_data)
    is_valid = validate_jws_data(doc, header, payload, sig)
    if is_valid:
        print(f"Card found in {qr_img_fn} and is valid.")  # noqa: T001
        pp = json.dumps(json.loads(payload), indent=4, sort_keys=True)
        print(pp)  # noqa: T001
    else:
        warnings.warn(f"WARNING: Card found in {qr_img_fn} is NOT valid.")


@click.command()
@click.argument("qr_dir", type=click.Path(exists=True, readable=True))
def extract_many(qr_dir: click.Path):
    """Get SMART Health Cards from a directory and summarize them as TSV to STDOUT."""
    qr_dir_path = click.format_filename(qr_dir)
    files = [join(qr_dir_path, f) for f in listdir(qr_dir_path) if isfile(join(qr_dir_path, f))]
    qr_files = [f for f in files if f.endswith((".bmp", ".jpg", ".png", ".jpeg", ".JPG", ".PNG"))]
    for qr_file in qr_files:
        qr_data = img_to_qr_data(qr_file)
        try:
            doc, header, payload, sig = extract_jws_data_from_qr_data(qr_data)
        except Exception as e:
            warnings.warn(f"Could not extract JWS data for {qr_file}")
            raise e
        is_valid = validate_jws_data(doc, header, payload, sig)
        result: List[str] = [qr_file]
        if is_valid:
            payload_json = json.loads(payload)
            fhir_bundle = Bundle(payload_json["vc"]["credentialSubject"]["fhirBundle"])
            pat: Patient
            found_pat: bool = False
            immunizations: List[Immunization] = []
            for entry in fhir_bundle.entry:
                resource = entry.resource
                if isinstance(resource, Patient):
                    if found_pat:
                        raise Exception(f"Multiple patients in {qr_file}!")
                    else:
                        pat = resource
                        found_pat = True
                elif isinstance(resource, Immunization):
                    immunizations.append(resource)
                else:
                    raise Exception(f"Unknown entry-type: {resource} in {qr_file}")
            if not found_pat:
                raise Exception(f"No patient found in {qr_file}")
            imm_index: int = 0
            if len(immunizations) < 1:
                raise Exception(f"No immunizations found in {qr_file}")
            for imm in immunizations:
                imm_pat = imm.patient
                imm_index += 1
                if isinstance(imm_pat, FHIRReference):
                    imm_pat = imm_pat.resolved(Patient)
                if imm_pat is not pat:
                    raise Exception(f"Patient {imm_pat} for immunization #{imm_index} is not the bundle-patient {pat}!")
            result.append(" ".join(pat.name[0].given))
            result.append(pat.name[0].family)
            result.append(pat.birthDate.isostring)
            result.append(immunizations[0].occurrenceDateTime.isostring)  # when
            try:
                result.append(immunizations[0].performer[0].actor.display)  # where
            except TypeError:
                result.append("UNKNOWN PERFORMER")
            result.append(vaccine_human_readable(immunizations[0].vaccineCode.coding[0]))
            if len(immunizations) > 1:
                result.append(immunizations[1].occurrenceDateTime.isostring)  # when
                try:
                    result.append(immunizations[1].performer[0].actor.display)  # where
                except TypeError:
                    result.append("UNKNOWN PERFORMER")
                result.append(vaccine_human_readable(immunizations[1].vaccineCode.coding[0]))
        else:
            result.append("INVALID")
        print("\t".join(result))  # noqa: T001


def vaccine_human_readable(coding) -> str:
    """Return the proprietary name for a COVID-19 vaccination, given a FHIR CodingType object.

    The proprietary name is looked up from smart_health_card_reader.config.VACCINE_PROPRIETARY_NAMES.
    """
    return VACCINE_PROPRIETARY_NAMES[coding.system][coding.code]


if __name__ == "__main__":
    validate_one()
