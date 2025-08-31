from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("patient-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class PatientDetails(enum.Enum):
    ID = "id"
    Name = "name"
    Age = "age"
    Gender = "gender"
    ContactInformation = "contact_information"
    BloodGroup = "blood_group"
    Height = "height"
    Weight = "weight"
    

class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        
        self._patient_details = {
            PatientDetails.ID: "",
            PatientDetails.Name: "",
            PatientDetails.Age: "",
            PatientDetails.Gender: "",
            PatientDetails.ContactInformation: "",
            PatientDetails.BloodGroup: "",
            PatientDetails.Height: "",
            PatientDetails.Weight: ""
        }
    
    def get_patient_str(self):
        patient_str = ""
        for key, value in self._patient_details.items():
            patient_str += f"{key}: {value}\n"
            
        return patient_str
    
    @llm.ai_callable(description="lookup a patient by their id")
    def lookup_patient(self, id: Annotated[int, llm.TypeInfo(description="The ID of the patient to lookup")]):
        logger.info("lookup patient - id: %s", id)
        
        result = DB.get_patient_by_id(id)
        if result is None:
            return "Patient not found"
        
        self._patient_details = {
            PatientDetails.ID: result.id,
            PatientDetails.Name: result.name,
            PatientDetails.Age: result.age,
            PatientDetails.Gender: result.gender,
            PatientDetails.ContactInformation: result.contact_information,
            PatientDetails.BloodGroup: result.blood_group,
            PatientDetails.Height: result.height,
            PatientDetails.Weight: result.weight
        }
        
        return f"The patient details are: {self.get_patient_str()}"
    
    @llm.ai_callable(description="get the details of the current patient")
    def get_patient_details(self):
        logger.info("get patient details")
        return f"The patient details are: {self.get_patient_str()}"
    
    @llm.ai_callable(description="create a new patient")
    def create_patient(
        self, 
        id: Annotated[int, llm.TypeInfo(description="The ID of the patient")],
        name: Annotated[str, llm.TypeInfo(description="The name of the patient")],
        age: Annotated[int, llm.TypeInfo(description="The age of the patient")],
        gender: Annotated[str, llm.TypeInfo(description="The gender of the patient")],
        contact_information: Annotated[str, llm.TypeInfo(description="The contact information of the patient")],
        blood_group: Annotated[str, llm.TypeInfo(description="The blood group of the patient")],
        height: Annotated[int, llm.TypeInfo(description="The height of the patient")],
        weight: Annotated[int, llm.TypeInfo(description="The weight of the patient")]
    ):
        logger.info("create patient - id: %s, name: %s, age: %s, gender: %s, contact_information: %s, blood_group: %s, height: %s, weight: %s", 
                    id, name, age, gender, contact_information, blood_group, height, weight)
        result = DB.create_patient(id, name, age, gender, contact_information, blood_group, height, weight)
        if result is None:
            return "Failed to create patient"
        
        self._patient_details = {
            PatientDetails.ID: result.id,
            PatientDetails.Name: result.name,
            PatientDetails.Age: result.age,
            PatientDetails.Gender: result.gender,
            PatientDetails.ContactInformation: result.contact_information,
            PatientDetails.BloodGroup: result.blood_group,
            PatientDetails.Height: result.height,
            PatientDetails.Weight: result.weight
        }
        
        return "Patient created!"
    
    def has_patient(self):
        return self._patient_details[PatientDetails.ID] != ""
