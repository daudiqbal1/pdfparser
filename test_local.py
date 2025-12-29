from pdfparser import parse_pdf

result = parse_pdf("example_pdf.pdf")

print(result.metadata)
print(result.transactions[:5])
