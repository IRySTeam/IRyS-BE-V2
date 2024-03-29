import cv2
import fitz
import imutils
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes

# import matplotlib.pyplot as plt
from PIL import Image
from pytesseract import Output


class OCRUtil:
    """
    OCRUtil is an utility class that provided several static methods to do OCR using tesseract
    OCR engine and OpenCV.
    """

    TEXT_PERCENTAGE_THRESHOLD = 0.01

    @classmethod
    def get_skew_angle(cls, cv_image: np.ndarray) -> float:
        """
        Function to find the skew angle (the angle between the text and the horizontal axis) of
        the image using OpenCV.
        [Parameters]
            cvImage: np.ndarray -> The image to be processed.
        [Returns]
            float: The skew angle of the image.
        """

        # Prep image, copy, convert to gray scale, blur, and threshold
        new_image = cv_image.copy()
        gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Apply dilate to merge text into meaningful lines/paragraphs.
        # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
        # But use smaller kernel on Y axis to separate between different blocks of text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 3))
        dilate = cv2.dilate(thresh, kernel, iterations=2)

        # Find all contours
        contours, _ = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        for c in contours:
            rect = cv2.boundingRect(c)
            x, y, w, h = rect
            cv2.rectangle(new_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Find largest contour and surround in min area box
        largest_contour = contours[0]
        minAreaRect = cv2.minAreaRect(largest_contour)
        cv2.imwrite("temp/boxes.jpg", new_image)
        # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
        return -1.0 * angle

    @classmethod
    def rotate_image(cls, cvImage: np.ndarray, angle: float) -> np.ndarray:
        """
        Function to rotate the image using OpenCV.
        [Parameters]
            cvImage: np.ndarray -> The image to be processed.
            angle: float -> The angle to rotate the image.
        [Returns]
            np.ndarray: The rotated image.
        """
        new_image = cvImage.copy()
        (h, w) = new_image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        new_image = cv2.warpAffine(
            new_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return new_image

    @classmethod
    def deskew(cls, cvImage: np.ndarray) -> np.ndarray:
        """
        Function to deskew (straighten) the image using OpenCV.
        [Parameters]
            cvImage: np.ndarray -> The image to be processed.
        [Returns]
            np.ndarray: The deskewed image.
        """
        results = pytesseract.image_to_osd(cvImage, output_type=Output.DICT)
        rotated = imutils.rotate_bound(cvImage, angle=results["rotate"])
        return rotated
        angle = cls.get_skew_angle(cvImage)
        return cls.rotate_image(cvImage, -1.0 * angle)

    @classmethod
    def pil2cv(cls, pilImage: Image) -> np.ndarray:
        """
        Function to convert PIL image to OpenCV image.
        [Parameters]
            pilImage: Image -> The image to be processed.
        [Returns]
            np.ndarray: The converted image.
        """
        return cv2.cvtColor(np.array(pilImage), cv2.COLOR_RGB2BGR)

    @classmethod
    def cv2pil(cls, cvImage: np.ndarray) -> Image:
        """
        Function to convert OpenCV image to PIL image.
        [Parameters]
            cvImage: np.ndarray -> The image to be processed.
        [Returns]
            Image: The converted image.
        """
        return Image.fromarray(cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB))

    @classmethod
    def show_image(cls, cvImage: np.ndarray):
        """
        Function to show the image using OpenCV.
        [Parameters]
            cvImage: np.ndarray -> The image to be processed.
        """
        # cv2.imshow("Image", cvImage)
        # cv2.waitKey(0)
        # #
        cv2.namedWindow("output", cv2.WINDOW_NORMAL)
        cv2.imshow("output", cvImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @classmethod
    def ocr(cls, pdf_file: bytes) -> str:
        """
        Function to convert PDF file to text using OCR.
        [Parameters]
            pdf_file: bytes -> The PDF file to be processed.
        [Returns]
            str: The text extracted from the PDF file.
        """
        images = convert_from_bytes(pdf_file)
        ocr_texts = []

        for img in images:
            # Image preprocessing.
            cv2img = cls.pil2cv(img)
            cv2img = cls.deskew(cv2img)
            original_image = cv2img.copy()
            cv2img = cv2.cvtColor(cv2img, cv2.COLOR_BGR2GRAY)
            # cv2img = cv2.fastNlMeansDenoising(cv2img, None, 10, 7, 21)

            copied_image = original_image.copy()
            ret, cv2img = cv2.threshold(
                cv2img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV
            )
            rectangular_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 60))
            dilated_image = cv2.dilate(cv2img, rectangular_kernel, iterations=1)
            contours, hierarchy = cv2.findContours(
                dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            # Assume there are 2 columns in the PDF file.
            # Separate contours based on their x-axis value.
            contours_1 = [
                cnt
                for cnt in contours
                if cv2.boundingRect(cnt)[0] < original_image.shape[1] / 2
            ]
            contours_2 = [
                cnt
                for cnt in contours
                if cv2.boundingRect(cnt)[0] >= original_image.shape[1] / 2
            ]
            # Sort contour based on their y-axis value
            contours_1 = sorted(contours_1, key=lambda cnt: cv2.boundingRect(cnt)[1])
            contours_2 = sorted(contours_2, key=lambda cnt: cv2.boundingRect(cnt)[1])
            # Combine contours into
            contours = contours_1 + contours_2

            mask = np.zeros(original_image.shape, np.uint8)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)

                # Cropping the text block for giving input to OCR
                cropped = copied_image[y : y + h, x : x + w]

                # Apply OCR on the cropped image
                text = pytesseract.image_to_string(cropped, config="--oem 3 --psm 1")
                ocr_texts.append(text)

                masked = cv2.drawContours(mask, [cnt], 0, (255, 255, 255), -1)

            # OCRUtil.show_image(masked)
            # plt.figure(figsize=(25, 15))
            # plt.imshow(masked, cmap='gray')
            # plt.show()

            # OCR.
            # cv2img = cv2.cvtColor(cv2img, cv2.COLOR_BGR2RGB)
            # ocr_text = pytesseract.image_to_string(cv2img)
            # ocr_texts.append(ocr_text)
        return " ".join(ocr_texts)

    @classmethod
    def get_text_percentage(
        self,
        file_bytes: bytes,
    ) -> float:
        """
        Calculate the percentage of document that is covered by (searchable) text.
        If the returned percentage of text is very low, the document is
        most likely a scanned PDF
        [Parameters]
            file_bytes: bytes -> The PDF file to be processed.
        [Returns]
            float: The percentage of text in the PDF file.
        """
        total_page_area = 0.0
        total_text_area = 0.0

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for _, page in enumerate(doc):
            total_page_area = total_page_area + abs(page.rect)
            text_area = 0.0
            for b in page.get_text_blocks():
                r = fitz.Rect(b[:4])  # rectangle where block text appears
                text_area = text_area + abs(r)
            total_text_area = total_text_area + text_area
        doc.close()
        if total_page_area == total_text_area:
            return OCRUtil.TEXT_PERCENTAGE_THRESHOLD - 0.0001
        return total_text_area / total_page_area


if __name__ == "__main__":
    # Read PDF file.
    with open("./tests/data/cv_1col_blackwhite.pdf", "rb") as f:
        ocr_text = OCRUtil.ocr(f.read())
        print(ocr_text)
