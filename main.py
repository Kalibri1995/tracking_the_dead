import os
import time

from lib.data_utils import get_deceased_persons, get_deceased_person_info
from lib.email_utils import send_email


def main():
    while True:
        deceased_persons = get_deceased_persons()

        if deceased_persons:
            message = "List of recent deceased individuals:\n\n"
            for idx, (name, link, age) in enumerate(deceased_persons, start=1):
                person_info_and_url = get_deceased_person_info(link)

                if person_info_and_url:
                    person_info, url = person_info_and_url
                    person_message = f"{idx}.\nName: {name}\nAge: {age}\nAbout the deceased: {person_info}\nPage link: {url}\n\n"
                else:
                    url = f"{os.environ.get('DEATHS_BASE_URL', 'https://en.wikipedia.org/wiki/Deaths_in_2023')}{link}"
                    person_message = f"{idx}.\nName: {name}\nAge: {age}\nPage link: {url}\n\n"

                message += person_message

            # Send the email
            subject = "List of Recent Deceased Individuals"
            send_email(subject, message)

        # Pause before the next iteration
        time.sleep(300)


if __name__ == "__main__":
    main()
