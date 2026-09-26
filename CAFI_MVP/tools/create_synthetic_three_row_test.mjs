import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputPath = "/Users/melanybrito/Desktop/Maria Emilia (QuickWins) /CAFI_MVP/ejemplos/Prueba_RPA_SIAC_3_filas_sinteticas.xlsx";

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Hoja 1");
sheet.showGridLines = false;

sheet.getRange("A1:G4").values = [
  ["COD. ALUMNO", "NOMBRE ESTUDIANTE", "TITULO", "DETALLE", "CÓDIGO:", "GPA:", "CRED.APROB:"],
  [17, "ESTUDIANTE PRUEBA UNO", "PRUEBA RPA SIAC 01", "Registro sintético para validar el flujo de impresión, confirmación humana y actualización de resultados.", "", "", ""],
  [28, "ESTUDIANTE PRUEBA DOS", "PRUEBA RPA SIAC 02", "Registro sintético para validar que el RPA limpia el formulario y continúa con la segunda fila.", "", "", ""],
  [39, "ESTUDIANTE PRUEBA TRES", "PRUEBA RPA SIAC 03", "Registro sintético para validar la tercera fila, la impresión y la actualización posterior de resultados.", "", "", ""],
];

sheet.getRange("A1:G1").format = {
  fill: "#8A1538",
  font: { name: "Aptos", size: 11, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange("A2:G4").format = {
  font: { name: "Aptos", size: 11, color: "#26343C" },
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange("A1:G4").format.borders = { preset: "all", style: "thin", color: "#D9CFD3" };
sheet.getRange("A2:A4").format.numberFormat = "0000000000";
sheet.getRange("E2:G4").format.fill = "#FFF8FA";
sheet.getRange("A1").format.columnWidth = 17;
sheet.getRange("B1").format.columnWidth = 25;
sheet.getRange("C1").format.columnWidth = 24;
sheet.getRange("D1").format.columnWidth = 58;
sheet.getRange("E1:G1").format.columnWidth = 17;
sheet.getRange("A1:G1").format.rowHeight = 28;
sheet.getRange("A2:G4").format.rowHeight = 55;
sheet.freezePanes.freezeRows(1);

await workbook.recalculate();
await fs.mkdir(new URL("../ejemplos/", import.meta.url), { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const check = await workbook.inspect({
  kind: "region",
  sheetId: "Hoja 1",
  range: "A1:G4",
  maxChars: 3000,
});
console.log(check.ndjson);

const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 20 },
  summary: "formula error scan",
});
console.log(formulaErrors.ndjson);

const preview = await workbook.render({ sheetName: "Hoja 1", range: "A1:G4", scale: 2 });
await fs.writeFile("/private/tmp/cafi-sheet-build/Prueba_RPA_SIAC_3_filas_sinteticas.png", new Uint8Array(await preview.arrayBuffer()));
