const fs = require("fs");
const path = require("path");
const { imageSize } = require("image-size");
const glob = require("glob");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, HeadingLevel, AlignmentType, BorderStyle, WidthType,
  PageBreak, Header, Footer, PageNumber, LevelFormat, ShadingType,
  VerticalAlign, ExternalHyperlink
} = require("docx");

// --- Config ---
const MD_PATH = path.resolve(__dirname, "../bao-cao-dinh-ky-tien-do.md");
const IMAGES_DIR = path.resolve(__dirname, "../images");
const OUTPUT_PATH = path.resolve(__dirname, "bao-cao.docx");

// --- Read source ---
const mdContent = fs.readFileSync(MD_PATH, "utf-8");
const lines = mdContent.split("\n");

// --- Helpers ---
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
let bulletRef = 0;

function findImage(num) {
  const pad = String(num).padStart(2, "0");
  // Use forward slashes for glob on Windows
  const dir = IMAGES_DIR.replace(/\\/g, "/");
  const patterns = [`${dir}/hinh-${pad}*.png`, `${dir}/hinh-${pad}*.jpg`, `${dir}/hinh-${num}-*.png`];
  for (const p of patterns) {
    const found = glob.sync(p);
    if (found.length > 0) return found[0];
  }
  return null;
}

function makeImage(imgPath, caption) {
  const buf = fs.readFileSync(imgPath);
  const ext = path.extname(imgPath).slice(1).toLowerCase();
  const dims = imageSize(buf);
  let w = dims.width, h = dims.height;
  const maxW = 550;
  if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, after: 80 },
      children: [new ImageRun({
        type: ext === "jpg" ? "jpeg" : ext,
        data: buf,
        transformation: { width: w, height: h },
        altText: { title: caption, description: caption, name: caption }
      })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: [new TextRun({ text: caption, italics: true, size: 22, font: "Times New Roman" })]
    })
  ];
}

function makePlaceholder(caption) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 200 },
    children: [new TextRun({ text: `[${caption}]`, italics: true, color: "999999", size: 24, font: "Times New Roman" })]
  });
}

function processImageLine(line) {
  const m = line.match(/\[📷\s*HÌNH\s*(\d+):\s*(.+?)\]/);
  if (!m) return null;
  const num = parseInt(m[1]);
  const caption = `Hình ${num}: ${m[2].trim()}`;
  const imgPath = findImage(num);
  if (imgPath) return makeImage(imgPath, caption);
  return [makePlaceholder(caption)];
}

function isUnicodeTableBorder(line) {
  return /^[┌├└─┬┼┴┘┐│\s]+$/.test(line.trim());
}

function isUnicodeTableRow(line) {
  return line.includes("│") && !isUnicodeTableBorder(line);
}

function parseUnicodeTableBlock(tableLines) {
  const rows = tableLines
    .filter(l => isUnicodeTableRow(l))
    .map(l => l.split("│").slice(1, -1).map(c => c.trim()));
  if (rows.length === 0) return null;

  const numCols = rows[0].length;
  const totalW = 9360;
  const colW = Math.floor(totalW / numCols);
  const colWidths = Array(numCols).fill(colW);

  const makeCell = (text, isHeader) => new TableCell({
    borders: cellBorders,
    width: { size: colW, type: WidthType.DXA },
    shading: isHeader ? { fill: "D9E2F3", type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({
      spacing: { before: 40, after: 40 },
      children: [new TextRun({ text: text || "", bold: isHeader, size: 22, font: "Times New Roman" })]
    })]
  });

  const tableRows = rows.map((row, idx) => new TableRow({
    tableHeader: idx === 0,
    children: row.map(cell => makeCell(cell, idx === 0))
  }));

  return new Table({ columnWidths: colWidths, rows: tableRows });
}

function textRun(text, opts = {}) {
  return new TextRun({ text, font: "Times New Roman", size: 26, ...opts });
}

// --- Parse & Build ---
const children = [];
const numbering = {
  config: [{
    reference: "bullets",
    levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
  }]
};

let i = 0;
while (i < lines.length) {
  const line = lines[i];
  const trimmed = line.trim();

  // Skip empty lines
  if (trimmed === "") { i++; continue; }

  // === HEADING 1: ═══ lines ===
  if (trimmed.startsWith("═══")) {
    // Next non-empty line is the heading text
    i++;
    while (i < lines.length && lines[i].trim() === "") i++;
    if (i < lines.length) {
      const headingText = lines[i].trim();
      // Skip next ═══ line
      i++;
      while (i < lines.length && lines[i].trim().startsWith("═══")) i++;
      if (headingText && !headingText.startsWith("═══")) {
        children.push(new Paragraph({ children: [new PageBreak()] }));
        children.push(new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [textRun(headingText, { bold: true, size: 28 })]
        }));
      }
    }
    continue;
  }

  // === TITLE (first lines) ===
  if (i < 20 && /^[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ\s]+$/.test(trimmed) && trimmed.length > 10) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, after: 100 },
      children: [textRun(trimmed, { bold: true, size: 36 })]  // 18pt (from ref Title style)
    }));
    i++; continue;
  }

  // === Image placeholder ===
  if (trimmed.startsWith("[📷")) {
    const imgs = processImageLine(trimmed);
    if (imgs) { children.push(...imgs); }
    i++; continue;
  }

  // === Chú thích / Gợi ý lines (skip, part of image context) ===
  if (trimmed.startsWith("Chú thích:") || trimmed.startsWith("Gợi ý:")) {
    i++; continue;
  }

  // === HEADING 2: N.N. Title ===
  if (/^\d+\.\d+\./.test(trimmed)) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_2,
      children: [textRun(trimmed, { bold: true, size: 26 })]
    }));
    i++; continue;
  }

  // === HEADING 3: N.N.N. Title ===
  if (/^\d+\.\d+\.\d+\./.test(trimmed)) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_3,
      children: [textRun(trimmed, { bold: true, italics: true, size: 26 })]
    }));
    i++; continue;
  }

  // === Unicode Table ===
  if (trimmed.startsWith("┌") || (isUnicodeTableRow(line) && i > 0 && lines[i-1].trim().startsWith("┌"))) {
    const tableLines = [];
    while (i < lines.length && (lines[i].includes("│") || lines[i].includes("┌") || lines[i].includes("├") || lines[i].includes("└") || lines[i].includes("─"))) {
      tableLines.push(lines[i]);
      i++;
    }
    const table = parseUnicodeTableBlock(tableLines);
    if (table) children.push(table);
    continue;
  }

  // === Bullet points ===
  if (trimmed.startsWith("•") || trimmed.startsWith("- ") || trimmed.startsWith("  •") || trimmed.startsWith("  -")) {
    const text = trimmed.replace(/^[•\-]\s*/, "").replace(/^\s+[•\-]\s*/, "");
    children.push(new Paragraph({
      numbering: { reference: "bullets", level: 0 },
      children: [textRun(text)]
    }));
    i++; continue;
  }

  // === Indented block (code-like or description) ===
  if (line.startsWith("  ") && !trimmed.startsWith("•") && !trimmed.startsWith("-")) {
    // Check if it's a checkbox line
    if (trimmed.startsWith("✅") || trimmed.startsWith("⚠") || trimmed.startsWith("❌") || trimmed.startsWith("❓")) {
      children.push(new Paragraph({
        indent: { left: 360 },
        spacing: { before: 40, after: 40 },
        children: [textRun(trimmed)]
      }));
    } else {
      children.push(new Paragraph({
        indent: { left: 360 },
        spacing: { before: 20, after: 20 },
        children: [textRun(trimmed, { size: 24 })]
      }));
    }
    i++; continue;
  }

  // === Section divider ─── ===
  if (/^───/.test(trimmed)) {
    i++; continue;
  }

  // === "Trạng thái:" line ===
  if (trimmed.startsWith("Trạng thái:")) {
    children.push(new Paragraph({
      spacing: { before: 100, after: 100 },
      children: [
        textRun("Trạng thái: ", { bold: true }),
        textRun(trimmed.replace("Trạng thái:", "").trim())
      ]
    }));
    i++; continue;
  }

  // === URL link ===
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://") || trimmed.startsWith("Mã nguồn:")) {
    const url = trimmed.replace("Mã nguồn: ", "").trim();
    children.push(new Paragraph({
      children: [new ExternalHyperlink({
        children: [new TextRun({ text: url, style: "Hyperlink", font: "Times New Roman", size: 26 })],
        link: url
      })]
    }));
    i++; continue;
  }

  // === Tài liệu tham khảo [N] ===
  if (/^\[\d+\]/.test(trimmed)) {
    // Collect multi-line reference
    let refText = trimmed;
    i++;
    while (i < lines.length && lines[i].startsWith("     ")) {
      refText += " " + lines[i].trim();
      i++;
    }
    children.push(new Paragraph({
      spacing: { before: 60, after: 60 },
      indent: { left: 360, hanging: 360 },
      children: [textRun(refText, { size: 22 })]
    }));
    continue;
  }

  // === --- Section header --- ===
  if (trimmed.startsWith("---") && trimmed.endsWith("---") && trimmed.length > 6) {
    const headerText = trimmed.replace(/^-+\s*/, "").replace(/\s*-+$/, "");
    children.push(new Paragraph({
      spacing: { before: 200, after: 100 },
      children: [textRun(headerText, { bold: true, italics: true })]
    }));
    i++; continue;
  }

  // === "Xem file riêng:" line ===
  if (trimmed.startsWith("Xem file")) {
    children.push(new Paragraph({
      spacing: { before: 100, after: 100 },
      children: [textRun(trimmed, { italics: true, color: "666666" })]
    }));
    i++; continue;
  }

  // === MỤC LỤC heading ===
  if (trimmed === "MỤC LỤC") {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 300, after: 200 },
      children: [textRun("MỤC LỤC", { bold: true, size: 28 })]
    }));
    i++; continue;
  }

  // === Ghi chú: ===
  if (trimmed.startsWith("Ghi chú:")) {
    children.push(new Paragraph({
      spacing: { before: 200, after: 100 },
      children: [textRun(trimmed, { italics: true, size: 22 })]
    }));
    i++; continue;
  }

  // === Default: plain paragraph ===
  if (trimmed.length > 0) {
    children.push(new Paragraph({
      spacing: { before: 60, after: 60 },
      children: [textRun(trimmed)]
    }));
  }

  i++;
}

// --- Build Document (styles matched from bao_cao_de_xuat_de_tai_v1.docx) ---
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Times New Roman", size: 26 },  // 13pt (Normal style)
        paragraph: { spacing: { line: 276 } }  // 1.15 line spacing (from ref)
      }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Times New Roman" },  // 14pt bold
        paragraph: { spacing: { before: 480, after: 0 }, outlineLevel: 0 } },  // before=480 (from ref)
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Times New Roman" },  // 13pt bold
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Times New Roman" },  // 12pt bold (from ref, no italic)
        paragraph: { spacing: { before: 200, after: 0 }, outlineLevel: 2 } }
    ]
  },
  numbering,
  sections: [{
    properties: {
      page: {
        margin: {
          top: 1417,     // 2.5cm (from ref)
          bottom: 1247,  // 2.2cm (from ref)
          left: 1701,    // 3.0cm (from ref, đóng gáy)
          right: 1247    // 2.2cm (from ref)
        }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "Báo cáo tiến độ ĐATN", font: "Times New Roman", size: 20, italics: true })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Trang ", font: "Times New Roman", size: 20 }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Times New Roman", size: 20 })
        ]
      })] })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log(`Created: ${OUTPUT_PATH}`);
  console.log(`Size: ${(buffer.length / 1024).toFixed(0)} KB`);
  console.log(`Pages (est): ~${Math.ceil(children.length / 35)}`);
});
