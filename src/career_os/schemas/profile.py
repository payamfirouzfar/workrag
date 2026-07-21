from pydantic import BaseModel
from enum import Enum


class Provenance(str, Enum):
    CONFIRMED_FACT = "CONFIRMED_FACT"
    INFERRED_SKILL = "INFERRED_SKILL"
    POSSIBLE_SKILL = "POSSIBLE_SKILL"
    MISSING_INFORMATION = "MISSING_INFORMATION"


class SkillItem(BaseModel):
    name: str
    category: str
    provenance: Provenance
    confidence: float = 1.0
    source: str = ""


class ExperienceItem(BaseModel):
    company: str
    role: str
    start: str | None = None
    end: str | None = None
    description: str | None = None
    provenance: Provenance = Provenance.CONFIRMED_FACT


class EducationItem(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    start: str | None = None
    end: str | None = None
    thesis_title: str | None = None
    thesis_abstract: str | None = None


class CareerPreferences(BaseModel):
    desired_countries: list[str] = []
    desired_cities: list[str] = []
    remote_preference: str | None = None     # remote | hybrid | on-site
    salary_expectation: dict | None = None
    visa_requirements: list[str] = []
    relocation: bool | None = None
    seniority: str | None = None
    target_industries: list[str] = []


class ProfileStructured(BaseModel):
    identity: dict = {}
    education: list[EducationItem] = []
    skills: list[SkillItem] = []
    experience: list[ExperienceItem] = []
    projects: list[dict] = []
    research: list[dict] = []
    thesis: dict = {}
    certifications: list[dict] = []
    languages: list[dict] = []
    career_preferences: CareerPreferences = CareerPreferences()
    missing_information: list[str] = []
