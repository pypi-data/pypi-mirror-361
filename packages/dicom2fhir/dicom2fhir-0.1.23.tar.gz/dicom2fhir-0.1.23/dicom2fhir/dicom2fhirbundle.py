import uuid
from fhir.resources.R4B import bundle
from fhir.resources.R4B import imagingstudy
from fhir.resources.R4B import patient
from fhir.resources.R4B import device
from fhir.resources.R4B.reference import Reference
#from pydicom import dataset
import logging
from dicom2fhir.dicom2fhirutils import gen_coding, SOP_CLASS_SYS, ACQUISITION_MODALITY_SYS, gen_bodysite_coding, gen_accession_identifier, gen_studyinstanceuid_identifier, dcm_coded_concept, gen_procedurecode_array, gen_started_datetime, gen_reason
from dicom2fhir.dicom2patient import build_patient_resource
from dicom2fhir.dicom2observation import build_observation_resources
from dicom2fhir.dicom2device import build_device_resource
from dicom2fhir.helpers import get_or
from dicom2fhir.dicom_json_proxy import DicomJsonProxy

class Dicom2FHIRBundle():

    def __init__(self, config: dict = {}):
        """
        Initialize the Dicom2FHIRBundle with an optional configuration.
        """
        self.study: imagingstudy.ImagingStudy | None = None
        self.series = {}
        self.instances = {}
        # Device
        self.device: device.Device | None = None
        # Patient
        self.pat: patient.Patient | None = None
        self.obs = []
        self.config = config
        
    def add(self, ds: DicomJsonProxy):
        """
        Add a DICOM dataset to the ImagingStudy.
        """
        if not isinstance(ds, DicomJsonProxy):
            raise TypeError("Expected a DicomJsonProxy object")

        # is first instance?
        if self.study is None:
            self.device = build_device_resource(ds, self.config)
            self.pat = build_patient_resource(ds, self.config)
            self._create_imaging_study(ds)
            if get_or(self.config, "generator.observation.add_vital_signs", True):
                self.obs = build_observation_resources(ds, self.pat, self.study, self.config) or []

        self._add_imaging_study_series(ds)
        self._add_instance(ds)

    def _create_imaging_study(self, ds):

        study_data = {}
        study_data["resource_type"] = "ImagingStudy"
        study_data["id"] = self.config['id_function']("ImagingStudy", ds)
        study_data["status"] = "available"
        
        if ds.non_empty("StudyDescription"):
            study_data["description"] = str(ds.StudyDescription)
        
        study_data["identifier"] = []
        if ds.non_empty("AccessionNumber"):
            study_data["identifier"].append(gen_accession_identifier(str(ds.AccessionNumber)))
        if ds.non_empty("StudyInstanceUID"):
            study_data["identifier"].append(gen_studyinstanceuid_identifier(str(ds.StudyInstanceUID)))

        # Set the patient reference
        study_data["subject"] = Reference.model_construct(reference=f"Patient/{self.pat.id}") if self.pat else None

        # procedure codes
        if ds.non_empty("ProcedureCodeSequence"):
            procedures = dcm_coded_concept(ds.ProcedureCodeSequence)
            study_data["procedureCode"] = gen_procedurecode_array(procedures)        

        if ds.non_empty("StudyDate") and ds.non_empty("StudyTime"):
            study_data["started"] = gen_started_datetime(str(ds.StudyDate), str(ds.StudyTime), self.config["dicom_timezone"])

        # reason codes
        if ds.non_empty("ReferencedRequestSequence"):
            for seq in ds.ReferencedRequestSequence:

                reason = None
                reasonStr = None 

                if seq.non_empty("ReasonForRequestedProcedureCodeSequence"):
                    reason = dcm_coded_concept(ds.ReasonForRequestedProcedureCodeSequence)
                if seq.non_empty("ReasonForTheRequestedProcedure"):
                    reasonStr = str(ds.ReasonForTheRequestedProcedure)
                if reason is not None and reasonStr is not None:
                    study_data["reasonCode"] = gen_reason(reason, reasonStr)

        study_data["numberOfSeries"] = 0
        study_data["numberOfInstances"] = 0

        # instantiate study here, when all required fields are available
        self.study = imagingstudy.ImagingStudy(**study_data)
        
    def _add_imaging_study_series(self, ds: DicomJsonProxy):

        series_instance_uid = str(ds.SeriesInstanceUID)

        if series_instance_uid in self.series:
            return  # Series already exists

        # inti data container
        self.series[series_instance_uid] = {}
        self.series[series_instance_uid]["uid"] = series_instance_uid
        self.series[series_instance_uid]["numberOfInstances"] = 0

        if ds.non_empty("SeriesDescription"):
            self.series[series_instance_uid]["description"] = str(ds.SeriesDescription)

        if ds.non_empty("SeriesNumber"):
            try:
                series_number = int(float(str(ds.SeriesNumber)))  # handles both int and scientific notation

                if series_number >= 0 and series_number < 2147483647:
                    self.series[series_instance_uid]["number"] = series_number
                else:
                    # SeriesNumber is out of range, log a warning and store original value as extension
                    logging.warning(f"Invalid SeriesNumber {ds.SeriesNumber}: out of range")
                    self.series[series_instance_uid]["extension"] = [
                        {
                            "url": "http://dicom.nema.org/resources/ontology/DCM/series-number",
                            "valueString": str(ds.SeriesNumber)
                        }
                    ]
            except Exception as e:
                logging.warning(f"Invalid SeriesNumber {ds.SeriesNumber}: {e}")

        if ds.non_empty("Modality"):
            self.series[series_instance_uid]["modality"] = gen_coding(
                code=str(ds.Modality),
                system=ACQUISITION_MODALITY_SYS
            )
        
        if ds.non_empty("SeriesDate") and ds.non_empty("SeriesTime"):
            self.series[series_instance_uid]["started"] = gen_started_datetime(
                str(ds.SeriesDate), str(ds.SeriesTime), self.config["dicom_timezone"]
            )

        if ds.non_empty("BodyPartExamined"):
            self.series[series_instance_uid]["bodySite"] = gen_bodysite_coding(str(ds.BodyPartExamined))

        if ds.non_empty("Laterality"):
            self.series[series_instance_uid]["laterality"] = gen_coding(str(ds.Laterality))
    
    def _add_instance(self, ds: DicomJsonProxy):

        series_instance_uid = str(ds.SeriesInstanceUID)
        sop_instance_uid = str(ds.SOPInstanceUID)

        if series_instance_uid not in self.instances:
            self.instances[series_instance_uid] = {}

        if sop_instance_uid in self.instances[series_instance_uid]:
            print("Error: SOP Instance UID already exists in the series")
            print(self.instances[series_instance_uid][sop_instance_uid].as_json())
            return

        self.instances[series_instance_uid][sop_instance_uid] = {}
       
        self.instances[series_instance_uid][sop_instance_uid]["uid"] = sop_instance_uid
        self.instances[series_instance_uid][sop_instance_uid]["sopClass"] = gen_coding(
            code="urn:oid:" + ds.SOPClassUID,
            system=SOP_CLASS_SYS
        )

        if ds.non_empty("InstanceNumber"):
            self.instances[series_instance_uid][sop_instance_uid]["number"] = str(ds.InstanceNumber)

        try:
            if str(ds.Modality) == "SR":
                seq = ds.ConceptNameCodeSequence
                if isinstance(seq, list) and len(seq) > 0:
                    self.instances[series_instance_uid][sop_instance_uid]["title"] = str(seq[0].CodeMeaning)
            else:
                self.instances[series_instance_uid][sop_instance_uid]["title"] = '\\'.join(str(ds.ImageType))
        except Exception:
            pass  # print("Unable to set instance title")

    def _build_imaging_study(self) -> imagingstudy.ImagingStudy:
        """
        Build the ImagingStudy resource from the collected data.
        """
        if self.study is None:
            raise ValueError("No ImagingStudy data has been added")

        # Add series to the study
        self.study.series = []
        for series_uid, series_data in self.series.items():

            # only add sop instance data if configured
            if get_or(self.config, "generator.imaging_study.add_instances", False):
                series_data["instance"] = []
                for instance_uid, instance_data in self.instances.get(series_uid, {}).items():
                    series_data["instance"].append(imagingstudy.ImagingStudySeriesInstance(**instance_data))
                series_data["numberOfInstances"] = len(series_data["instance"])
            else:
                series_data["numberOfInstances"] = len(self.instances[series_uid])

            # Create ImagingStudySeries object
            series = imagingstudy.ImagingStudySeries(**series_data)
            self.study.series.append(series)

        # Set the number of series and instances
        self.study.numberOfSeries = len(self.study.series)
        self.study.numberOfInstances = sum(s.numberOfInstances for s in self.study.series)

        # Set the modalities
        modality_set = {
            s.modality.code: s.modality
            for s in self.study.series or []
            if s.modality is not None
        }
        self.study.modality = list(modality_set.values())

        return self.study
    
    def create_bundle(self) -> bundle.Bundle:
        """
        Create the final transaction bundle.
        """

        def _to_entry(resource):
            return {
                #'fullUrl': f"urn:uuid:{resource.id}",
                'resource': resource,
                'request': {
                    'method': 'PUT',
                    'url': f"{resource.__resource_type__}/{resource.id}"
                }
            }

        if not self.study:
            raise ValueError("No ImagingStudy data has been added")

        # Build the ImagingStudy resource
        _study = self._build_imaging_study()
    
        # wrap entries in a transaction Bundle and return
        return bundle.Bundle.model_validate({
            'resourceType': 'Bundle',
            'type': "transaction",
            'id': str(uuid.uuid4()),
            'entry': [
                _to_entry(_study),
                _to_entry(self.pat),
                _to_entry(self.device)
            ] + [_to_entry(o) for o in self.obs]
        })