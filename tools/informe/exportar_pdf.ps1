# Abre el informe en Word, actualiza índices y campos, guarda y exporta a PDF.
param([string]$Docx, [string]$Pdf)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open($Docx)
  $doc.Fields.Update() | Out-Null
  foreach ($t in $doc.TablesOfContents) { $t.Update() }
  foreach ($t in $doc.TablesOfFigures) { $t.Update() }
  $doc.Fields.Update() | Out-Null
  $doc.Save()
  $doc.ExportAsFixedFormat($Pdf, 17)
  "Paginas: " + $doc.ComputeStatistics(2)
  $doc.Close()
} finally {
  $word.Quit()
}
