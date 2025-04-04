from enum import Enum as PythonEnum

class UserRole(str, PythonEnum):
    USER = "USER"
    ADMIN = "ADMIN"

class Month(str, PythonEnum):
    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"

class DocumentStatus(str, PythonEnum):
    UPLOADED = "Uploaded"
    APPROVED = "Approved"
    REJECTED = "Rejected"
