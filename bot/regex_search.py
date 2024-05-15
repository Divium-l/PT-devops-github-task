from typing import Union
import re

def find_email(text: str) -> Union[list[str], None]:
    emailRegex = re.compile(r"[-\w.]+@.[\w\d\-\.]+\.[\w]+")
    return find_by_regex(text, emailRegex)

def find_phone(text: str) -> Union[list[str], None]:
    phoneRegex = re.compile(r"(8|\+7)([- ])?(\()?(\d{3})(\))?([ -])?(\d{3})([ -])?(\d{2})([ -])?(\d{2})")
    return find_by_regex(text, phoneRegex)

def find_by_regex(text: str, regex: re.Pattern) -> Union[list[str], None]:
    matches = regex.findall(text)

    if not matches:
        return None

    resultList = []
    for match in matches:
        tempString = ''

        for group in match:
            tempString += group

        resultList.append(tempString)

    return resultList