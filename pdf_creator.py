import fpdf

pdf = fpdf.FPDF()
pdf.add_page()
pdf.set_font('Times','', 12)
pdf.cell(0, 10, 'Dossier Médical', 0, 1,  'C')
pdf.cell(60, 10, 'Powered by FPDF.', 0, 1, 'C')
pdf.output('tuto1.pdf', 'F')