import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path
import os


def generate(invoices_path, pdfs_path, product_id, product_name, 
    amount_purchased, price_per_unit, total_price, product_image_path
):
    """
    Genera una factura en formato PDF para cada archivo Excel en la carpeta
    especificada.

    Parameters
    ----------
    invoices_path : str
        Ruta de la carpeta que contiene los archivos Excel.
    pdfs_path : str
        Ruta de la carpeta donde se guardaran los archivos PDF.
    product_id : str
        Identificador del producto.
    product_name : str
        Nombre del producto.
    amount_purchased : int
        Cantidad de productos comprados.
    price_per_unit : float
        Precio del producto por unidad.
    total_price : float
        Precio total de la compra.
    product_image_path : str
        Ruta del archivo de imagen del producto.
    """
    filepaths = glob.glob(f"{invoices_path}/*.xlsx")

    for filepath in filepaths:

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        filename = Path(filepath).stem
        invoice_nr, date = filename.split("-")

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Invoice nr.{invoice_nr}", ln=1)

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)

        df = pd.read_excel(filepath, sheet_name="Sheet 1")

        # Add a header
        columns = df.columns
        columns = [item.replace("_", " ").title() for item in columns]
        pdf.set_font(family="Times", size=10, style="B")
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt=columns[0], border=1)
        pdf.cell(w=70, h=8, txt=columns[1], border=1)
        pdf.cell(w=30, h=8, txt=columns[2], border=1)
        pdf.cell(w=30, h=8, txt=columns[3], border=1)
        pdf.cell(w=30, h=8, txt=columns[4], border=1, ln=1)

        # Add rows to the table
        for index, row in df.iterrows():
            pdf.set_font(family="Times", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(product_id), border=1)
            pdf.cell(w=70, h=8, txt=str(product_name), border=1)
            pdf.cell(w=30, h=8, txt=str(amount_purchased), border=1)
            pdf.cell(w=30, h=8, txt=str(price_per_unit), border=1)
            pdf.cell(w=30, h=8, txt=str(total_price), border=1, ln=1)

        total_sum = df["total_price"].sum()
        pdf.set_font(family="Times", size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), border=1, ln=1)

        # Add total sum sentence
        pdf.set_font(family="Times", size=10, style="B")
        pdf.cell(w=30, h=8, txt=f"The total price is {total_sum}", ln=1)

        # Add company name and logo
        pdf.set_font(family="Times", size=14, style="B")
        pdf.cell(w=25, h=8, txt=f"PythonHow")
        pdf.image(product_image_path, w=10)

        os.makedirs(pdfs_path, exist_ok=True)
        pdf.output(f"{pdfs_path}/{filename}.pdf")
