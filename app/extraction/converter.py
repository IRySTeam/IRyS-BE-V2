import os
import re
import subprocess

from core.utils.string_helper import StringHelper

dir_path = os.path.dirname(os.path.realpath(__file__))


# Modified from https://michalzalecki.com/converting-docx-to-pdf-using-python/
class Converter:
    """
    Convert doc or docx file to pdf file
    """

    def doc_to_pdf(self, file: bytes, extension: str) -> bytes:
        """
        Convert doc or docx file to pdf file

        [Arguments]
            file: bytes -> File to convert
        [Returns]
            bytes -> Converted file
        """

        file_name = StringHelper.random_string(10)

        file_path = os.path.join(dir_path, "temp", f"{file_name}{extension}")

        # Save file
        with open(file_path, "wb") as f:
            f.write(file)

        pdf_path = os.path.join(dir_path, "temp", "pdf")

        args = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            pdf_path,
            file_path,
        ]

        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        filename = re.search("-> (.*?) using filter", process.stdout.decode())

        if filename is None:
            raise Exception(process.stdout.decode())
        else:
            # Read filename
            with open(filename.group(1), "rb") as f:
                pdf_file = f.read()

            # Delete temp
            os.remove(file_path)
            os.remove(filename.group(1))

            return pdf_file
